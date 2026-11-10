# 双色球 / 大乐透号码生成器

个人自用、离线为主 + 可选联网参考的彩票号码生成工具。支持将生日、纪念日等重要日期作为「偏好数字」，生成时尽量包含这些数字；也可联网获取近期开奖热门号码作为参考（完全可选）。

> **合规声明**：本工具仅供个人参考，不投注、不预测、不保证中奖概率。彩票是随机事件，请理性购彩。

---

## 功能特性

- **彩种选择**：双色球（红球 1–33 + 蓝球 1–16）、大乐透（前区 1–35 + 后区 1–12），可单选或全选；
- **注数设置**：1—20 注；
- **偏好日期输入**：多行文本框，每行一个日期（如 `1990-05-20`、`19900520`、`05-20`、`520`）；
- **偏好数字提取**：自动从日期中提取合法号码，按区域过滤、去重、排序；
- **偏好开关**：关闭后完全随机，不再尝试包含偏好数字；
- **联网热门参考**：点击「联网获取历史数据」后，展示近 30 期热门号码，并优先匹配热号（仅影响顺序倾向，不改变中奖概率）；
- **彩色结果渲染**：GUI 中以红/蓝色区分球号（红球红色 / 蓝球蓝色 / 前区红色 / 后区蓝色），CLI 保持纯文本；
- **复制 / 保存**：一键复制到剪贴板，或保存为 `.txt` / `.csv`。

## 安装

```bash
cd lottery_generator_dev
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

GUI 需要 PySide6；CLI 无任何第三方依赖。

## 运行

### GUI 模式（默认）

```bash
python main.py
```

### CLI 模式

```bash
python main.py --cli --types ssq,dlt --count 2 --dates "1990-05-20"
python main.py --cli --types ssq --count 1 --no-prefer
python main.py --cli --types dlt --count 3 --dates-file dates.txt --output result.txt
```

| 参数 | 说明 |
| ---- | ---- |
| `--types` | `ssq`、`dlt` 或 `ssq,dlt` |
| `--count` | 注数，1—20，越界自动限制 |
| `--dates` | 偏好日期文本，换行分隔 |
| `--dates-file` | 从文件读取偏好日期 |
| `--prefer` / `--no-prefer` | 是否尽量包含偏好数字（默认开启） |
| `--output` | 输出文件路径，可选 |

## 项目结构

```text
lottery_generator/
├── main.py                 # 程序入口，--gui 自动选择 GUI 或 CLI
├── requirements.txt        # PySide6>=6.6
├── README.md               # 本文件
├── core/
│   ├── __init__.py
│   ├── rules.py            # 彩票规则常量（范围、数量）
│   ├── models.py           # 数据模型（LotteryType、SSQResult、DLTResult 等）
│   ├── date_parser.py      # 偏好日期解析与池构建
│   ├── generator.py        # 号码生成核心算法
│   ├── formatter.py        # 纯文本 / HTML / CSV 格式化
│   └── network.py          # 联网获取历史开奖 & 热门号码统计
├── cli/app.py              # 命令行入口
├── gui/app.py              # PySide6 图形界面（Catppuccin Mocha 深色主题）
└── tests/                  # pytest 单元测试
    ├── conftest.py
    ├── test_date_parser.py
    ├── test_formatter.py
    └── test_generator.py
```

## 号码规则

| 彩种 | 区域 | 选号数量 | 范围 |
| ---- | ---- | -------- | ---- |
| 双色球 | 红球 | 6 | 1–33 |
| 双色球 | 蓝球 | 1 | 1–16 |
| 大乐透 | 前区 | 5 | 1–35 |
| 大乐透 | 后区 | 2 | 1–12 |

## 偏好日期解析逻辑

1. 去除所有非数字字符后，按字符串长度解析：
   - 8 位 `YYYYMMDD`、6 位 `YYMMDD`：提取年%100、月、日及月日组合；
   - 4 位 `MMDD`：提取月、日及月日组合；
   - 3 位（如 `520`）：提取 `5、20、520`；
   - 同时保留连续两位分组的候选数字；
2. 过滤到对应号码范围，去重、升序排序；
3. 示例：`1990-05-20` → 双色球红球池 `[5, 19, 20]`，蓝球池 `[5]`。

## 热门号码逻辑（联网功能）

点击「联网获取历史数据」后：

1. 从 `kaijiang.zhcw.com` 抓取近 30 期双色球、大乐透开奖记录；
2. 统计各位置号码出现频次，取 Top 8 作为热门号码；
3. 热门号码合并入偏好池，生成时优先匹配（去重排序后参与算法）；
4. 网络失败时静默降级为本地纯随机模式，不影响正常使用。

## 技术细节

- **随机算法**：`random.sample` 无放回抽样，确保号码不重复；
- **偏好优先级**：开启偏好且偏好池非空时，每注至少包含 1 个偏好数字；
- **热门融合**：联网成功后，热门号码作为额外偏好项与原偏好池合并，统一进入生成流程；
- **彩色渲染**：GUI 使用 `format_results_html()` 生成带内联样式的 HTML，通过 `QTextBrowser.setHtml()` 渲染；红球/前区用 `#e74c3c`，蓝球/后区用 `#3498db`。

## 测试

```bash
pip install pytest
pytest
```

## 打包为可执行文件

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name LotteryGenerator lottery_generator/main.py
```

打包后得到单文件可执行程序，无需安装 Python 环境。
