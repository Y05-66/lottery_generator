import argparse
import sys

from core.formatter import format_results
from core.generator import clamp_count, generate_draws
from core.models import GenerateOptions, LotteryType

VALID_TYPES = {
    "ssq": LotteryType.SSQ,
    "dlt": LotteryType.DLT,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lottery-generator",
        description="双色球/大乐透号码生成器（离线运行，不联网、不投注，仅供个人参考）",
    )
    parser.add_argument("--types", help="彩种：ssq、dlt 或 ssq,dlt")
    parser.add_argument("--count", type=int, default=1, help="注数，1—20，默认 1")
    parser.add_argument("--dates", default="", help="偏好日期文本，换行分隔")
    parser.add_argument("--dates-file", dest="dates_file", help="从文件读取偏好日期")
    parser.add_argument("--prefer", dest="prefer", action="store_true", help="尽量包含偏好数字（默认开启）")
    parser.add_argument("--no-prefer", dest="prefer", action="store_false", help="完全随机，不包含偏好数字")
    parser.set_defaults(prefer=True)
    parser.add_argument("--output", help="输出文件路径，可选")
    return parser


def resolve_dates(args) -> str:
    dates = args.dates or ""
    if args.dates_file:
        try:
            with open(args.dates_file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            raise ValueError(f"无法读取偏好日期文件：{e}") from e
        dates = content + ("\n" + dates if dates else "")
    return dates


def parse_types(raw: str, parser: argparse.ArgumentParser) -> list:
    types = []
    for part in (raw or "").replace("，", ",").split(","):
        key = part.strip().lower()
        if not key:
            continue
        if key not in VALID_TYPES:
            parser.error(f"未知彩种：{part.strip()}（支持 ssq / dlt）")
        types.append(VALID_TYPES[key])
    if not types:
        parser.error("请至少指定一种彩票类型：--types ssq、dlt 或 ssq,dlt")
    return types


def run_cli(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    types = parse_types(args.types, parser)
    try:
        dates = resolve_dates(args)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1

    options = GenerateOptions(
        types=types,
        count=clamp_count(args.count),
        prefer_dates=dates,
        prefer=args.prefer,
    )
    try:
        results = generate_draws(options)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1

    text = format_results(results)
    print(text)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            print(f"已保存到：{args.output}")
        except OSError as e:
            print(f"错误：保存文件失败：{e}", file=sys.stderr)
            return 1
    return 0
