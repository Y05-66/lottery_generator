# 双色球 / 大乐透号码生成器（Python 版）开发文档

> **文档版本**：v1.1 — 2026-11-09  
> **项目定位**：个人自用、离线为主 + 可选联网参考的号码生成工具  
> **技术路线**：Python 3.10+，可选 PySide6 桌面界面  
> **合规边界**：不投注、不预测、不保证中奖概率。偏好日期与热门号码仅作本地参考，不影响真实中奖概率。彩票是随机事件，请理性购彩。

---

## 1. 项目概述

本项目用于每天生成双色球、大乐透号码，支持用户输入生日、结婚纪念日等重要日期作为「偏好数字」，生成时尽量包含这些数字。可选联网获取近期开奖历史数据，展示热门号码并在生成时优先匹配热号（仅影响顺序倾向，不改变中奖概率）。

用户可以选择：

- 只生成双色球；
- 只生成大乐透；
- 两种同时生成；
- 自定义生成注数；
- 是否尽量包含偏好数字；
- 是否开启联网热门号码参考；
- 复制或保存生成结果。

默认离线运行；联网功能仅在用户主动点击「联网获取历史数据」后触发，失败时静默降级为纯随机模式。

---

## 2. 合规与安全边界

开发与使用必须遵守以下边界：

1. **不实现互联网售彩、投注、支付、兑奖功能**；
2. **不提供号码预测、走势分析、中奖概率提升等误导性功能**；
3. **不接入任何彩票销售接口**；
4. 联网功能仅作历史数据读取（只读），不提交任何用户数据；
5. **偏好日期与热门号码只影响号码选择顺序，不改变中奖概率**；
6. 生成结果仅供个人参考，使用者需自行前往线下合法实体店购买；
7. 不在微信小程序等个人主体受限平台公开上架彩票相关类目。

### 联网安全设计

- 网络请求带超时保护（默认 8s），失败不抛异常，静默降级；
- `User-Agent` 伪装为常规浏览器，降低被反爬概率；
- DLT 提供多 URL 备用，任一可用即停止尝试；
- 所有联网逻辑封装在 `core/network.py`，调用方无需关心失败处理。

---

## 3. 功能需求

### 3.1 核心功能

| 编号 | 功能             | 说明                               |
| ---- | ---------------- | ---------------------------------- |
| F1   | 彩种选择         | 双色球、大乐透，可单选或全选       |
| F2   | 注数设置         | 1—20 注，默认 1 注                 |
| F3   | 偏好日期输入     | 多行输入，每行一个日期             |
| F4   | 偏好数字提取     | 从日期中提取合法号码并去重排序     |
| F5   | 尽量包含偏好数字 | 开关控制，关闭后完全随机           |
| F6   | 结果展示         | 按注展示红球/蓝球、前区/后区       |
| F7   | 复制结果         | 复制为纯文本                       |
| F8   | 保存结果         | 可选保存为 `.txt` 或 `.csv`        |
| F9   | 联网获取历史数据 | 点击按钮后从网络获取近 N 期开奖记录（可选） |
| F10  | 热门号码参考     | 展示近 N 期各位置热门号码，并优先匹配热号生成 |
| F11  | 彩色结果渲染     | GUI 中以红/蓝色区分球号，CLI 保持纯文本 |
| F12  | 参数校验         | 未选彩种、注数越界、日期为空等提示 |

### 3.2 非功能需求

- 默认离线运行；联网功能仅在用户主动触发后可用；
- 启动速度快，界面简洁（Catppuccin Mocha 深色主题）；
- 核心逻辑与界面分离，便于测试；
- 支持 Windows / macOS / Linux；
- 可通过 PyInstaller 打包为单文件可执行程序。

---

## 4. 技术选型

| 层级     | 推荐技术               | 说明                       |
| -------- | ---------------------- | -------------------------- |
| 语言     | Python 3.10+           | 标准库足够完成核心逻辑     |
| 随机     | `random.sample`        | 无放回抽样，适合选号       |
| 日期解析 | `re` + 自定义规则      | 不依赖第三方库             |
| 命令行   | `argparse`             | 可选 CLI 入口              |
| 桌面 GUI | PySide6                | 跨平台、控件成熟           |
| 打包     | PyInstaller            | 打包为 `.exe` / 可执行文件 |
| 测试     | `pytest` 或 `unittest` | 覆盖核心规则与解析逻辑     |

**推荐方案**：`Python + PySide6` 做桌面工具，核心逻辑放在 `core/` 包中，CLI 与 GUI 共用同一套生成逻辑。

---

## 5. 项目结构

```text
lottery_generator/
├── main.py                 # 程序入口，支持 --gui / --cli
├── requirements.txt        # PySide6>=6.6
├── README.md               # 使用说明
├── core/
│   ├── __init__.py
│   ├── rules.py            # 双色球/大乐透规则常量
│   ├── models.py           # 数据模型 dataclass
│   ├── date_parser.py      # 偏好日期解析
│   ├── generator.py        # 号码生成核心算法
│   ├── formatter.py        # 结果格式化（纯文本 / HTML / CSV）
│   └── network.py          # 联网获取历史开奖 & 热门号码统计
├── cli/
│   ├── __init__.py
│   └── app.py              # 命令行入口
├── gui/
│   ├── __init__.py
│   └── app.py              # PySide6 界面（Catppuccin Mocha 深色主题）
└── tests/
    ├── conftest.py
    ├── test_date_parser.py
    ├── test_formatter.py
    └── test_generator.py
```

---

## 6. 数据模型

建议使用 `dataclass` 定义：

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class LotteryType(str, Enum):
    SSQ = "ssq"   # 双色球
    DLT = "dlt"   # 大乐透

@dataclass
class GenerateOptions:
    types: List[LotteryType]
    count: int = 1
    prefer_dates: str = ""
    prefer: bool = True

@dataclass
class SSQResult:
    red: List[int]
    blue: int

@dataclass
class DLTResult:
    front: List[int]
    back: List[int]

@dataclass
class DrawResult:
    lottery_type: LotteryType
    index: int
    ssq: Optional[SSQResult] = None
    dlt: Optional[DLTResult] = None
```

---

## 7. 彩票规则常量

```python
SSQ_RED_COUNT = 6
SSQ_RED_MIN = 1
SSQ_RED_MAX = 33

SSQ_BLUE_COUNT = 1
SSQ_BLUE_MIN = 1
SSQ_BLUE_MAX = 16

DLT_FRONT_COUNT = 5
DLT_FRONT_MIN = 1
DLT_FRONT_MAX = 35

DLT_BACK_COUNT = 2
DLT_BACK_MIN = 1
DLT_BACK_MAX = 12
```

| 彩种   | 区域 | 选号数量 | 范围 |
| ------ | ---- | -------- | ---- |
| 双色球 | 红球 | 6        | 1—33 |
| 双色球 | 蓝球 | 1        | 1—16 |
| 大乐透 | 前区 | 5        | 1—35 |
| 大乐透 | 后区 | 2        | 1—12 |

---

## 8. 偏好日期解析规则

### 8.1 支持的输入格式

每行一个日期，支持但不限于：

```text
1990-05-20
1990/5/20
19900520
900520
05-20
0520
5-20
520
```

### 8.2 提取规则

1. 去除所有非数字字符；
2. 连续两位分组，例如 `19900520 -> 19, 90, 05, 20`；
3. 根据长度解析：
   - 8 位：按 `YYYYMMDD` 解析，提取 `年%100`、月、日、`月*100+日`、`日*100+月`；
   - 6 位：按 `YYMMDD` 解析；
   - 4 位：按 `MMDD` 解析，同时提取月、日、`月*100+日`、`日*100+月`；
   - 3 位：如 `520`，提取 `5、20、520`；
4. 过滤到对应号码范围 `[min, max]`；
5. 去重并升序排序。

### 8.3 示例

输入：

```text
1990-05-20
```

提取结果：

| 区域            | 偏好池        |
| --------------- | ------------- |
| 双色球红球 1—33 | `[5, 19, 20]` |
| 双色球蓝球 1—16 | `[5]`         |
| 大乐透前区 1—35 | `[5, 19, 20]` |
| 大乐透后区 1—12 | `[5]`         |

> 说明：偏好数字只是让号码对使用者更有意义，不会提高中奖概率。

---

## 9. 核心生成算法

### 9.1 单区域选号

```python
import random

def generate_zone(count: int, min_num: int, max_num: int,
                  pref_pool: list[int], prefer: bool) -> list[int]:
    all_numbers = list(range(min_num, max_num + 1))
    pref = [n for n in pref_pool if min_num <= n <= max_num]
    chosen: list[int] = []

    if prefer and pref:
        max_k = min(len(pref), count)
        k = 1 if count == 1 else random.randint(1, max_k)
        chosen.extend(random.sample(pref, k))

    remaining = [n for n in all_numbers if n not in chosen]
    need = count - len(chosen)
    chosen.extend(random.sample(remaining, need))
    return sorted(chosen)
```

### 9.2 双色球生成

```python
def generate_ssq(pref_red: list[int], pref_blue: list[int],
                 prefer: bool) -> SSQResult:
    red = generate_zone(6, 1, 33, pref_red, prefer)
    blue = generate_zone(1, 1, 16, pref_blue, prefer)[0]
    return SSQResult(red=red, blue=blue)
```

### 9.3 大乐透生成

```python
def generate_dlt(pref_front: list[int], pref_back: list[int],
                 prefer: bool) -> DLTResult:
    front = generate_zone(5, 1, 35, pref_front, prefer)
    back = generate_zone(2, 1, 12, pref_back, prefer)
    return DLTResult(front=front, back=back)
```

### 9.4 多注生成规则

- 每一注独立随机生成；
- 双色球与大乐透同时勾选时，按“每注依次生成”的方式展示；
- 注数限制 `1 <= count <= 20`；
- 未勾选任何彩种时，不生成并提示用户。

---

## 9.5 网络逻辑（可选功能）

本模块 `core/network.py` 负责从外部网站抓取历史开奖数据，供 GUI 中「联网获取」按钮使用。

### 数据来源

| 彩种 | URL | 备注 |
| ---- | --- | ---- |
| 双色球 | `http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html` | 主源 |
| 大乐透 | `http://kaijiang.zhcw.com/zhcw/dlt/list_1.html` | 备用两个 URL |

### 工作流程

1. **`fetch(url)`**：带 8s 超时与 SSL 上下文发起请求，GBK/UTF-8 自动解码，失败返回 `None`。
2. **`fetch_ssq_history(count)`**：解析 `<tr>` 行，提取日期、期号及 `<em>` 标签中的七个号码（前六红球 + 最后一蓝球）。
3. **`fetch_dlt_history(count)`**：优先匹配 class="rr"（前区）和 class="rq"（后区），fallback 取所有数字。
4. **`compute_hot_numbers()`**：用 `collections.Counter` 统计近 N 期各位置频次，按频率降序、号码升序排列，取 Top-N。
5. **`format_hot_numbers()`**：将热门字典格式化为可读字符串，展示在 GUI 的 `lbl_hot` 中。
6. **GUI 调用链**：`btn_network.clicked → _on_fetch_network() → fetch_all_history() → compute_hot_numbers() → format_hot_numbers()`，结果合并入偏好池后再调用 `generate_draws()`。

### 安全设计

- 只读访问，不提交任何用户数据；
- 每个请求独立超时（8s），失败静默降级为空列表；
- `User-Agent` 伪装为 Chrome 浏览器降低反爬概率；
- DLT 提供三个候选 URL，任一成功即停止尝试。

---

## 9.6 GUI 彩色 HTML 渲染

CLI 仅输出纯文本，GUI 使用 HTML 富文本实现彩色卡片式展示，通过 `QTextBrowser.setHtml()` 渲染。

### 颜色方案（Catppuccin Mocha 深色主题）

| 元素 | 颜色 | 色值 |
| ---- | ---- | ---- |
| 双色球红球 / 大乐透前区 | 红色 | `#e74c3c` |
| 双色球蓝球 / 大乐透后区 | 蓝色 | `#3498db` |
| 分隔符「+」 | 深灰 | `#45475a` |
| 注号标签 | 灰色 | `#6c7086` |
| 卡片背景 | 深黑 | `#1e1e2e` |
| 左侧边框（SSQ） | 红色 | `#e74c3c` |
| 左侧边框（DLT） | 蓝色 | `#3498db` |

### 实现要点

- `formatter.format_result_html()` 返回单条结果的 HTML div，含内联样式；
- `formatter.format_results_html()` 拼接多条结果并加上总数汇总行；
- GUI 的 `_on_generate()` 必须调用 `format_results_html()` 而非 `format_results()`，否则只有纯文本无颜色；
- `QTextBrowser` 原生支持 HTML，无需额外配置。

---

## 10. 界面设计

### 10.1 GUI 控件建议（PySide6）

| 控件             | 用途                             |
| ---------------- | -------------------------------- |
| `QCheckBox`      | 双色球、大乐透、尽量包含偏好数字 |
| `QSpinBox`       | 注数，范围 1—20                  |
| `QPlainTextEdit` | 输入偏好日期，多行               |
| `QPushButton`    | 生成号码、复制结果、保存结果     |
| `QTextBrowser`   | 展示生成结果                     |
| `QLabel`         | 显示偏好数字识别结果             |

### 10.2 交互流程

1. 用户勾选彩种；
2. 设置注数；
3. 输入偏好日期；
4. 点击“生成号码”；
5. 界面显示识别到的偏好池和生成结果；
6. 用户可复制或保存结果。

### 10.3 CLI 可选参数

```bash
python main.py --cli --types ssq,dlt --count 3 --dates "1990-05-20\n2015-10-01" --prefer
python main.py --cli --types ssq --count 1 --no-prefer
```

参数说明：

| 参数                       | 说明                      |
| -------------------------- | ------------------------- |
| `--types`                  | `ssq`、`dlt` 或 `ssq,dlt` |
| `--count`                  | 注数，1—20                |
| `--dates`                  | 偏好日期文本，换行分隔    |
| `--dates-file`             | 从文件读取偏好日期        |
| `--prefer` / `--no-prefer` | 是否尽量包含偏好数字      |
| `--output`                 | 输出文件路径，可选        |

---

## 11. 结果格式化

纯文本示例：

```text
第1注 双色球：红球 05 12 19 20 23 31 + 蓝球 08
第2注 大乐透：前区 03 05 19 20 28 + 后区 05 11
```

复制文本与保存文本共用 `formatter.py`，避免 GUI 与 CLI 重复实现。

---

## 12. 运行与打包

### 12.1 安装依赖

```bash
pip install PySide6
```

### 12.2 运行 GUI

```bash
python main.py --gui
```

### 12.3 运行 CLI

```bash
python main.py --cli --types ssq,dlt --count 2 --dates "1990-05-20"
```

### 12.4 打包为可执行文件

```bash
pyinstaller --onefile --windowed --name LotteryGenerator main.py
```

打包后可得到单文件可执行程序，双击运行，无需安装 Python 环境。

---

## 13. 测试用例

### 13.1 日期解析测试

| 输入         | 区域       | 期望                     |
| ------------ | ---------- | ------------------------ |
| `1990-05-20` | 双色球红球 | 包含 `5、19、20`         |
| `1990-05-20` | 双色球蓝球 | 包含 `5`                 |
| `05-20`      | 大乐透后区 | 包含 `5`，不包含 `20`    |
| 空文本       | 任意       | 返回空列表               |
| 非法字符     | 任意       | 不崩溃，返回合法数字或空 |

### 13.2 生成逻辑测试

- 双色球红球数量恒为 6，且不重复；
- 双色球蓝球数量恒为 1；
- 大乐透前区数量恒为 5，且不重复；
- 大乐透后区数量恒为 2，且不重复；
- 所有号码在合法范围内；
- 开启偏好时，偏好池非空则结果至少包含一个偏好数字；
- 关闭偏好时，不强制包含偏好数字；
- 注数 0、21、非数字时被限制或提示。

### 13.3 界面测试

- 未勾选彩种时点击生成，提示“请至少勾选一种彩票类型”；
- 复制按钮在无结果时提示先生成；
- 保存按钮能正确写入文本文件。

---

## 14. 错误处理

| 场景             | 处理方式                           |
| ---------------- | ---------------------------------- |
| 未选择彩种       | 提示，不生成                       |
| 注数越界         | 自动限制到 1—20                    |
| 日期为空         | 偏好池为空，正常随机生成           |
| 日期格式无法识别 | 忽略该行，不崩溃                   |
| 剪贴板复制失败   | 回退到临时文本框复制或提示手动复制 |
| 文件保存失败     | 提示路径或权限错误                 |

---

## 15. 后续可选扩展

- 保存历史生成记录到本地 SQLite；
- 导出 CSV；
- 支持“避开全奇数/全偶数/过多连号”的可选过滤；
- 增加简单统计：已生成注数、号码频次；
- 增加多语言或主题切换。
