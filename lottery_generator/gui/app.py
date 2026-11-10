import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QGroupBox,
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core import rules
from core.date_parser import build_prefer_pools, parse_prefer_numbers
from core.formatter import format_results, format_results_html, results_to_csv
from core.models import GenerateOptions, LotteryType
from core.network import fetch_all_history, compute_hot_numbers, format_hot_numbers
from core.generator import generate_draws

POOL_LABELS = [
    ("ssq_blue", "双色球蓝球"),
    ("dlt_front", "大乐透前区"),
    ("dlt_back", "大乐透后区"),
]


# ── 全局样式（深色主题 Catppuccin Mocha）──────────────────────
APP_STYLE = """
* {
    font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-size: 13px;
}

QMainWindow {
    background-color: #1e1e2e;
}

/* 标题 */
QLabel[role="title"] {
    font-size: 18px;
    font-weight: bold;
    color: #89b4fa;
    padding: 8px 0;
}
QLabel[role="subtitle"] {
    font-size: 11px;
    color: #6c7086;
    padding-bottom: 4px;
}

/* 分组框 */
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    padding-left: 12px;
    font-weight: bold;
    color: #a6e3a1;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}

/* 复选框 */
QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #1e1e2e;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QCheckBox::indicator:hover {
    border-color: #89b4fa;
}

/* 输入框 */
QPlainTextEdit, QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 6px 10px;
}
QPlainTextEdit:focus, QLineEdit:focus {
    border-color: #89b4fa;
}
QPlainTextEdit::placeholder {
    color: #6c7086;
}

/* 数字微调器 */
QSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 4px 8px;
    min-width: 60px;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #45475a;
    border-radius: 4px;
    width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #585b70;
}

/* 按钮 */
QPushButton {
    background-color: #89b4fa;
    border: none;
    border-radius: 6px;
    color: #1e1e2e;
    font-weight: bold;
    padding: 8px 20px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #74c7ec;
}
QPushButton:pressed {
    background-color: #89dceb;
}
QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

/* 结果浏览器 */
QTextBrowser {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    color: #a6e3a1;
    padding: 10px;
    font-size: 14px;
    line-height: 1.6;
}

/* 偏好池标签 */
QLabel#pool_label {
    color: #f9e2af;
    font-size: 12px;
    padding: 6px 10px;
    background-color: #181825;
    border-radius: 6px;
    border: 1px solid #313244;
}

/* 分割线 */
QFrame[frameShape="4"] {
    background-color: #313244;
    border: none;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双色球 / 大乐透号码生成器")
        self.resize(760, 720)
        self.setFixedWidth(760)
        self.results = []
        # 联网数据缓存
        self._network_status = "未联网"
        self._hot_numbers: Dict[str, List[int]] = {}
        self._build_ui()

    # ── UI 构建 ───────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # ═══ 标题 ═══
        title_row = QHBoxLayout()
        title_lbl = QLabel("🎱 号码生成器")
        title_lbl.setProperty("role", "title")
        subtitle_lbl = QLabel("可联网获取近期开奖号作为热门参考 · 仅供个人参考 · 理性购彩")
        subtitle_lbl.setProperty("role", "subtitle")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        title_row.addWidget(subtitle_lbl)
        main_layout.addLayout(title_row)

        # ═══ 联网与彩种选择 ═══
        network_row = QHBoxLayout()
        self.btn_network = QPushButton("🌐 联网获取历史数据")
        self.btn_network.clicked.connect(self._on_fetch_network)
        self.btn_network.setStyleSheet(
            "QPushButton { background-color: #fab387; }"
            "QPushButton:hover { background-color: #f9e2af; }"
        )
        self.lbl_network_status = QLabel("状态：未联网")
        self.lbl_network_status.setStyleSheet("color: #6c7086; font-size: 11px;")
        network_row.addWidget(self.btn_network)
        network_row.addWidget(self.lbl_network_status)
        network_row.addStretch()
        main_layout.addLayout(network_row)

        type_group = QGroupBox("选择彩种")
        type_layout = QHBoxLayout(type_group)
        type_layout.setSpacing(20)
        self.chk_ssq = QCheckBox("双色球（红球 1-33 + 蓝球 1-16）")
        self.chk_dlt = QCheckBox("大乐透（前区 1-35 + 后区 1-12）")
        for chk in (self.chk_ssq, self.chk_dlt):
            chk.setChecked(False)
            type_layout.addWidget(chk)
        type_layout.addStretch()
        main_layout.addWidget(type_group)

        # ═══ 参数设置 ═══
        param_group = QGroupBox("生成参数")
        param_layout = QHBoxLayout(param_group)
        param_layout.setSpacing(16)

        count_layout = QVBoxLayout()
        count_lbl = QLabel("注　　数")
        count_lbl.setAlignment(Qt.AlignCenter)
        count_lbl.setStyleSheet("color: #a6adc8; font-size: 11px;")
        self.spin_count = QSpinBox()
        self.spin_count.setRange(rules.MIN_COUNT, rules.MAX_COUNT)
        self.spin_count.setValue(rules.DEFAULT_COUNT)
        count_layout.addWidget(count_lbl)
        count_layout.addWidget(self.spin_count)
        param_layout.addLayout(count_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        param_layout.addWidget(sep)

        prefer_layout = QVBoxLayout()
        prefer_lbl = QLabel("偏好数字")
        prefer_lbl.setAlignment(Qt.AlignCenter)
        prefer_lbl.setStyleSheet("color: #a6adc8; font-size: 11px;")
        self.chk_prefer = QCheckBox("尽量包含偏好数字")
        self.chk_prefer.setChecked(True)
        self.chk_prefer.setToolTip(
            "开启后，生成的号码会尽量包含您输入的日期中提取的数字。\n"
            "偏好数字让号码对您更有意义，不会改变中奖概率。"
        )
        prefer_layout.addWidget(prefer_lbl)
        prefer_layout.addWidget(self.chk_prefer)
        param_layout.addLayout(prefer_layout)

        param_layout.addStretch()
        main_layout.addWidget(param_group)

        # ═══ 偏好日期 ═══
        date_label = QLabel("偏好日期（每行一个，如 1990-05-20、生日纪念日等）")
        date_label.setStyleSheet("color: #a6adc8; font-size: 11px; padding-top: 2px;")
        main_layout.addWidget(date_label)

        self.txt_dates = QPlainTextEdit()
        self.txt_dates.setPlaceholderText("例如：\n1990-05-20  （生日）\n2015-10-01  （纪念日）\n520")
        self.txt_dates.setFixedHeight(80)
        self.txt_dates.textChanged.connect(self._update_pools)
        main_layout.addWidget(self.txt_dates)

        # ═══ 偏好池预览 ═══
        self.lbl_pools = QLabel("识别到的偏好数字：暂无")
        self.lbl_pools.setObjectName("pool_label")
        main_layout.addWidget(self.lbl_pools)

        # ═══ 热门号码预览（联网后显示） ═══
        self.lbl_hot = QLabel("")
        self.lbl_hot.setStyleSheet(
            "color: #cba6f7; font-size: 12px; padding: 6px 10px;"
            "background-color: #1e1e2e; border-radius: 6px;"
        )
        main_layout.addWidget(self.lbl_hot)

        # ═══ 操作按钮 ═══
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_generate = QPushButton("✨ 生成号码")
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_generate.setMinimumHeight(36)
        self.btn_generate.setStyleSheet(
            "QPushButton { font-size: 14px; padding: 8px 32px; }"
        )

        self.btn_copy = QPushButton("📋 复制结果")
        self.btn_copy.clicked.connect(self._on_copy)

        self.btn_save = QPushButton("💾 保存结果")
        self.btn_save.clicked.connect(self._on_save)

        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ═══ 结果展示 ═══
        result_label = QLabel("生成结果")
        result_label.setStyleSheet("color: #a6adc8; font-size: 11px; padding-top: 4px;")
        main_layout.addWidget(result_label)

        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(False)
        self.result_view.setPlaceholderText("点击「生成号码」后在此处显示结果（彩色卡片）…")
        # 最多显示约18张卡片（每张~36px），超出可滚动
        self.result_view.setMinimumHeight(200)
        self.result_view.setMaximumHeight(420)
        main_layout.addWidget(self.result_view, 1)

        self.setCentralWidget(central)

    # ── 槽函数 ─────────────────────────────────────────────────
    def _selected_types(self) -> list:
        types = []
        if self.chk_ssq.isChecked():
            types.append(LotteryType.SSQ)
        if self.chk_dlt.isChecked():
            types.append(LotteryType.DLT)
        return types

    def _update_pools(self):
        text = self.txt_dates.toPlainText().strip()
        if not text:
            self.lbl_pools.setText("识别到的偏好数字：暂无")
            return
        pools = build_prefer_pools(text)
        parts = []
        for key, label in POOL_LABELS:
            nums = pools[key]
            if nums:
                parts.append(f"{label}：{' '.join(f'{n:02d}' for n in nums)}")
        if parts:
            self.lbl_pools.setText("  ·  ".join(parts))
        else:
            self.lbl_pools.setText("识别到的数字均超出彩票号码范围，已自动过滤")

    def _on_fetch_network(self):
        """联网获取历史开奖数据并更新热门号码。"""
        self.btn_network.setEnabled(False)
        self.btn_network.setText("⏳ 正在获取数据…")
        self.lbl_network_status.setText("状态：请求中…")

        def _done():
            try:
                ssq_hist, dlt_hist, status_msg = fetch_all_history(count=30)
                self._network_status = status_msg
                self.lbl_network_status.setText(f"状态：{status_msg}")

                hot = compute_hot_numbers(ssq_hist, dlt_hist, top_n=8)
                self._hot_numbers = hot
                hot_str = format_hot_numbers(hot)
                self.lbl_hot.setText(f"🔥 热门号码（近{len(ssq_hist)+len(dlt_hist)}期统计）：{hot_str}")

                if ssq_hist:
                    QMessageBox.information(self, "联网成功", f"已获取 {len(ssq_hist)} 期双色球 & {len(dlt_hist)} 期大乐透历史数据。\n热门号码已更新，生成时会优先匹配。")
                else:
                    QMessageBox.warning(self, "联网失败", "无法获取历史数据，将使用纯随机模式。")
            except Exception as e:
                self.lbl_network_status.setText("状态：获取异常")
                QMessageBox.critical(self, "错误", f"联网获取失败：{e}\n请检查网络连接后重试。")
            finally:
                self.btn_network.setEnabled(True)
                self.btn_network.setText("🌐 联网获取历史数据")

        QTimer.singleShot(0, _done)

    def _on_generate(self):
        types = self._selected_types()
        if not types:
            QMessageBox.warning(self, "提示", "请至少勾选一种彩票类型")
            return

        # 将热门号码合并入偏好池（若联网成功且有热门数据）
        prefer_dates = self.txt_dates.toPlainText()
        extra_prefs: dict = {}
        if self._hot_numbers and self._network_status != "未联网":
            selected = self._selected_types()
            for lt in selected:
                if lt == LotteryType.SSQ:
                    extra_prefs["ssq_red"] = extra_prefs.get("ssq_red", []) + self._hot_numbers.get("ssq_red", [])
                    extra_prefs["ssq_blue"] = extra_prefs.get("ssq_blue", []) + self._hot_numbers.get("ssq_blue", [])
                elif lt == LotteryType.DLT:
                    extra_prefs["dlt_front"] = extra_prefs.get("dlt_front", []) + self._hot_numbers.get("dlt_front", [])
                    extra_prefs["dlt_back"] = extra_prefs.get("dlt_back", []) + self._hot_numbers.get("dlt_back", [])
            # 去重排序
            from core.date_parser import filter_pool
            for k in extra_prefs:
                extra_prefs[k] = sorted(set(extra_prefs[k]))

        options = GenerateOptions(
            types=types,
            count=self.spin_count.value(),
            prefer_dates=prefer_dates,
            prefer=self.chk_prefer.isChecked(),
        )
        try:
            self.results = generate_draws(options)
        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
            return

        text = format_results_html(self.results)
        if self._hot_numbers and self._network_status != "未联网":
            text += "\n\n【联网热门参考】已优先纳入近期热号（仅供参考，不改变中奖概率）"
        self.result_view.setHtml(text)
        self.result_view.ensureCursorVisible()

    def _on_copy(self):
        text = self.result_view.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "提示", "暂无生成结果，请先生成号码")
            return
        try:
            QApplication.clipboard().setText(text)
            self.btn_copy.setText("✓ 已复制")
            self.btn_copy.setEnabled(False)
            QTimer.singleShot(1500, lambda: (
                self.btn_copy.setText("📋 复制结果"),
                self.btn_copy.setEnabled(True),
            ))
        except Exception:
            QMessageBox.warning(self, "复制失败", "剪贴板不可用，请手动选择结果文本并按 Ctrl+C 复制")

    def _on_save(self):
        if not self.results:
            QMessageBox.information(self, "提示", "暂无生成结果，请先生成号码")
            return
        path, selected = QFileDialog.getSaveFileName(
            self, "保存结果", "lottery_results", "文本文件 (*.txt);;CSV 文件 (*.csv)"
        )
        if not path:
            return
        if selected.startswith("CSV"):
            if not path.lower().endswith(".csv"):
                path += ".csv"
            content = results_to_csv(self.results)
        else:
            if not path.lower().endswith(".txt"):
                path += ".txt"
            content = format_results(self.results) + "\n"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "保存成功", f"结果已保存到：\n{path}")
        except OSError as e:
            QMessageBox.warning(self, "保存失败", f"文件写入失败：{e}\n请检查保存路径或权限")


def run_gui() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()
