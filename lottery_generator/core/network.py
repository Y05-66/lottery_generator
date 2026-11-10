"""
网络数据获取模块 —— 从 kaijiang.zhcw.com 抓取近期开奖结果，
用于热门号码统计参考。仅在用户明确点击「联网获取」时触发，
所有请求均有超时保护，失败时静默降级为本地随机生成。
"""

import re
import ssl
import urllib.request
from collections import Counter
from typing import Dict, List, Optional, Tuple

_TIMEOUT = 8

_CTX = ssl.create_default_context()
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.baidu.com",
}


def _fetch(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        r = urllib.request.urlopen(req, timeout=_TIMEOUT, context=_CTX)
        raw = r.read()
        for enc in ("gbk", "utf-8"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return None


# ── 双色球 ───────────────────────────────────────────────────────
_SSQ_URL = "http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html"


def fetch_ssq_history(count: int = 30) -> List[Dict[str, object]]:
    body = _fetch(_SSQ_URL)
    if not body:
        return []
    results: List[Dict[str, object]] = []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.DOTALL)
    for row in rows:
        date_m = re.search(r'<td align="center">(\d{4}-\d{2}-\d{2})</td>', row)
        period_m = re.search(r'<td align="center">(\d+)</td>', row)
        if not date_m or not period_m:
            continue
        nums = re.findall(r"<em(?:\s+class=\"[^\"]+\")?>(\d+)</em>", row)
        if len(nums) >= 7:
            results.append({
                "period": period_m.group(1),
                "date": date_m.group(1),
                "red": [int(n) for n in nums[:6]],
                "blue": int(nums[6]),
            })
        if len(results) >= count:
            break
    return results


# ── 大乐透 ───────────────────────────────────────────────────────
# 多个备用 URL，尝试直到找到一个可用的
_DLT_CANDIDATES = [
    # zhcw DLT（不同子路径）
    "http://kaijiang.zhcw.com/zhcw/dlt/list_1.html",
    "http://www.zhcw.com/dlt/kjgg/index.shtml",
    # 其他可能的来源
    "http://kaijiang.zhcw.com/dlt/list_1.html",
]


def fetch_dlt_history(count: int = 30) -> List[Dict[str, object]]:
    for url in _DLT_CANDIDATES:
        body = _fetch(url)
        if not body:
            continue
        results: List[Dict[str, object]] = []
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.DOTALL)
        for row in rows:
            date_m = re.search(r'<td align="center">(\d{4}-\d{2}-\d{2})</td>', row)
            period_m = re.search(r'<td align="center">(\d+)</td>', row)
            if not date_m or not period_m:
                continue
            # 查找 rr（前区红球）和 rq（后区蓝球）
            fronts = re.findall(r'class="rr">(\d+)', row)
            backs = re.findall(r'class="rq">(\d+)', row)
            if len(fronts) >= 5 and len(backs) >= 2:
                results.append({
                    "period": period_m.group(1),
                    "date": date_m.group(1),
                    "front": [int(n) for n in fronts[:5]],
                    "back": [int(n) for n in backs[:2]],
                })
            else:
                # fallback：取行中所有数字
                all_nums = re.findall(r"<em(?:\s+class=\"[^\"]+\")?>(\d+)</em>", row)
                if len(all_nums) >= 7:
                    results.append({
                        "period": period_m.group(1),
                        "date": date_m.group(1),
                        "front": [int(n) for n in all_nums[:5]],
                        "back": [int(n) for n in all_nums[5:7]],
                    })
            if len(results) >= count:
                break
        if results:
            return results
    return []


# ── 热门号码统计 ──────────────────────────────────────────────────

def compute_hot_numbers(
    ssq_history: List[Dict[str, object]],
    dlt_history: List[Dict[str, object]],
    top_n: int = 10,
) -> Dict[str, List[int]]:
    """根据历史开奖记录，统计各号码出现频次，返回最热门的号码列表。"""
    from core import rules

    ssq_red_ctr: Counter = Counter()
    ssq_blue_ctr: Counter = Counter()
    dlt_front_ctr: Counter = Counter()
    dlt_back_ctr: Counter = Counter()

    for rec in ssq_history:
        for n in rec["red"]:
            ssq_red_ctr[n] += 1
        ssq_blue_ctr[rec["blue"]] += 1

    for rec in dlt_history:
        for n in rec["front"]:
            dlt_front_ctr[n] += 1
        for n in rec["back"]:
            dlt_back_ctr[n] += 1

    def top(counter: Counter, lo: int, hi: int) -> List[int]:
        return [
            n for n, _ in sorted(
                [(k, v) for k, v in counter.items() if lo <= k <= hi],
                key=lambda x: (-x[1], x[0]),
            )[:top_n]
        ]

    return {
        "ssq_red": top(ssq_red_ctr, rules.SSQ_RED_MIN, rules.SSQ_RED_MAX),
        "ssq_blue": top(ssq_blue_ctr, rules.SSQ_BLUE_MIN, rules.SSQ_BLUE_MAX),
        "dlt_front": top(dlt_front_ctr, rules.DLT_FRONT_MIN, rules.DLT_FRONT_MAX),
        "dlt_back": top(dlt_back_ctr, rules.DLT_BACK_MIN, rules.DLT_BACK_MAX),
    }


def format_hot_numbers(hot: Dict[str, List[int]]) -> str:
    """将热门号码字典格式化为可读字符串。"""
    parts = []
    labels = [
        ("ssq_red", "双色球红球"),
        ("ssq_blue", "双色球蓝球"),
        ("dlt_front", "大乐透前区"),
        ("dlt_back", "大乐透后区"),
    ]
    for key, label in labels:
        nums = hot.get(key, [])
        if nums:
            nums_str = " ".join(f"{n:02d}" for n in nums)
            parts.append(f"{label}：{nums_str}")
    return "　│　".join(parts) if parts else "暂无数据"


# ── 对外接口 ─────────────────────────────────────────────────────

def fetch_all_history(count: int = 30) -> Tuple[
    List[Dict[str, object]],
    List[Dict[str, object]],
    str,
]:
    """
    同时获取两种彩种的历史数据。
    返回 (ssq_results, dlt_results, status_msg)。
    """
    ssq = fetch_ssq_history(count)
    dlt = fetch_dlt_history(count)
    msgs = []
    if ssq:
        msgs.append(f"双色球已获取 {len(ssq)} 期")
    else:
        msgs.append("双色球数据暂不可用")
    if dlt:
        msgs.append(f"大乐透已获取 {len(dlt)} 期")
    else:
        msgs.append("大乐透数据暂不可用（该网络环境可能不支持访问）")
    return ssq, dlt, "；".join(msgs)
