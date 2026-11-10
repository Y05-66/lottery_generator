# 双色球 / 大乐透号码生成器

个人自用、离线为主 + 可选联网参考的彩票号码生成工具。支持将生日、纪念日等重要日期作为「偏好数字」，生成时尽量包含这些数字；也可联网获取近期开奖热门号码作为参考（完全可选）。

> **合规声明**：本工具仅供个人参考，不投注、不预测、不保证中奖概率。彩票是随机事件，请理性购彩。

![GUI界面](./2b03fe6db66eff23b3900ebf2b9bded2.jpg)
![结果展示](./55d222ea48ef2fc586916a593d364f7d.jpg)

> 💡 如果各位老板用这个程序中了大奖，可以资助一下作者 😄

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

## 使用方式

### CLI（命令行）

```bash
# 基本用法
python -m lottery_generator.cli --types ssq --count 5

# 生成双色球和大乐透各 3 注，含偏好日期
python -m lottery_generator.cli \
  --types ssq,dlt \
  --count 3 \
  --dates "1990-05-20
           2015-10-01"

# 输出到文件
python -m lottery_generator.cli --types ssq --output result.csv
```

### GUI（图形界面）

```bash
python -m lottery_generator.main
# 或直接运行
python lottery_generator/main.py
```

启动后会弹出桌面窗口，勾选彩种、填写偏好日期后点击「生成号码」即可。

## 技术栈

- Python 3.10+
- PySide6（可选，用于 GUI）
- 标准库：`random`, `re`, `urllib`, `argparse`, `dataclasses`

## 项目结构

```
lottery_generator_dev/
├── lottery_generator/
│   ├── main.py                # 程序入口
│   ├── core/
│   │   ├── models.py          # 数据结构定义
│   │   ├── rules.py           # 规则常量
│   │   ├── generator.py       # 号码生成逻辑
│   │   ├── formatter.py       # 结果格式化（文本/HTML/CSV）
│   │   ├── date_parser.py     # 偏好日期解析
│   │   └── network.py         # 联网获取历史数据
│   ├── gui/
│   │   └── app.py             # PySide6 图形界面
│   ├── cli/
│   │   └── app.py             # argparse 命令行接口
│   └── tests/                 # pytest 单元测试
├── lottery_generator_dev.md   # 开发文档
└── requirements.txt
```
