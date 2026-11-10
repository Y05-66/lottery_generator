import csv
import io
from typing import List

from core.models import DrawResult, LotteryType


def _pad(n: int) -> str:
    return f"{n:02d}"


def _join(nums: List[int], sep: str = "-") -> str:
    return sep.join(_pad(n) for n in nums)


def format_result_text(result: DrawResult) -> str:
    """返回一条结果的纯文本（用于 CLI）。"""
    if result.lottery_type == LotteryType.SSQ and result.ssq is not None:
        red = _join(result.ssq.red)
        blue = _pad(result.ssq.blue)
        return f"第{result.index}注 双色球：{red} + {blue}"
    if result.lottery_type == LotteryType.DLT and result.dlt is not None:
        front = _join(result.dlt.front)
        back = _join(result.dlt.back)
        return f"第{result.index}注 大乐透：{front} + {back}"
    raise ValueError("结果数据不完整，无法格式化")


def format_result_html(result: DrawResult) -> str:
    """返回一条结果的 HTML（用于 GUI QTextBrowser）。"""
    if result.lottery_type == LotteryType.SSQ and result.ssq is not None:
        red = _join(result.ssq.red)
        blue = _pad(result.ssq.blue)
        return (
            f'<div style="margin:8px 4px;padding:6px 10px;'
            f'background:#1e1e2e;border-radius:6px;'
            f'border-left:3px solid #e74c3c;">'
            f'<span style="color:#6c7086;font-size:11px;">第{result.index}注</span>'
            f'<span style="color:#e74c3c;font-weight:bold;margin-right:4px;">● 双色球</span>'
            f'<span style="color:#e74c3c;font-size:14px;font-weight:bold;">{red}</span>'
            f'<span style="color:#45475a;margin:0 4px;">+</span>'
            f'<span style="color:#3498db;font-size:14px;font-weight:bold;">{blue}</span>'
            f'</div>'
        )
    if result.lottery_type == LotteryType.DLT and result.dlt is not None:
        front = _join(result.dlt.front)
        back = _join(result.dlt.back)
        return (
            f'<div style="margin:8px 4px;padding:6px 10px;'
            f'background:#1e1e2e;border-radius:6px;'
            f'border-left:3px solid #3498db;">'
            f'<span style="color:#6c7086;font-size:11px;">第{result.index}注</span>'
            f'<span style="color:#3498db;font-weight:bold;margin-right:4px;">● 大乐透</span>'
            f'<span style="color:#e74c3c;font-size:14px;font-weight:bold;">{front}</span>'
            f'<span style="color:#45475a;margin:0 4px;">+</span>'
            f'<span style="color:#3498db;font-size:14px;font-weight:bold;">{back}</span>'
            f'</div>'
        )
    raise ValueError("结果数据不完整，无法格式化")


def format_results(results: List[DrawResult]) -> str:
    """默认返回纯文本（供 CLI 使用）。"""
    return "\n".join(format_result_text(r) for r in results)


def format_results_html(results: List[DrawResult]) -> str:
    """返回带颜色的 HTML 富文本（供 GUI QTextBrowser 使用）。"""
    inner = "<br/>\n".join(format_result_html(r) for r in results)
    total = len(results)
    return (
        f'<div style="font-family:Microsoft YaHei UI,sans-serif;padding:4px;">'
        f'<div style="color:#6c7086;font-size:11px;margin-bottom:4px;">'
        f'共生成 <b style="color:#89b4fa;">{total}</b> 注号码</div>'
        f'{inner}'
        f'</div>'
    )


def results_to_csv(results: List[DrawResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["注号", "彩种", "红球/前区", "蓝球/后区"])
    for r in results:
        if r.lottery_type == LotteryType.SSQ and r.ssq is not None:
            writer.writerow([r.index, "双色球", _join_nums(r.ssq.red), _pad(r.ssq.blue)])
        elif r.lottery_type == LotteryType.DLT and r.dlt is not None:
            writer.writerow([r.index, "大乐透", _join_nums(r.dlt.front), _join_nums(r.dlt.back)])
    return buf.getvalue()


def _join_nums(nums: List[int]) -> str:
    return " ".join(_pad(n) for n in nums)
