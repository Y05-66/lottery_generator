import re
from typing import Dict, List, Set

from core import rules

_NON_DIGIT = re.compile(r"\D+")

_FULL_DATE_RE = re.compile(r"(\d{4})[-/.年月\s]+(\d{1,2})[-/.年月日\s]+(\d{1,2})")
_PART_DATE_RE = re.compile(r"(\d{1,2})[-/.年月\s]+(\d{1,2})")


def _valid_month(m: int) -> bool:
    return 1 <= m <= 12


def _valid_day(d: int) -> bool:
    return 1 <= d <= 31


def _pair_candidates(digits: str) -> Set[int]:
    cands: Set[int] = set()
    i = 0
    n = len(digits)
    while i + 1 < n:
        cands.add(int(digits[i:i + 2]))
        i += 2
    if i < n:
        cands.add(int(digits[i]))
    return cands


def date_candidates(digits: str) -> Set[int]:
    n = len(digits)
    if n == 0:
        return set()
    if n <= 2:
        return {int(digits)}
    if n == 3:
        return {int(digits[0]), int(digits[1:]), int(digits)}
    cands = _pair_candidates(digits)
    if n == 4:
        mm, dd = int(digits[0:2]), int(digits[2:4])
        if _valid_month(mm) and _valid_day(dd):
            cands.update({mm, dd, mm * 100 + dd, dd * 100 + mm})
    elif n == 6:
        cands.add(int(digits[0:2]))
        mm, dd = int(digits[2:4]), int(digits[4:6])
        if _valid_month(mm) and _valid_day(dd):
            cands.update({mm, dd, mm * 100 + dd, dd * 100 + mm})
    elif n == 8:
        cands.add(int(digits[2:4]))
        mm, dd = int(digits[4:6]), int(digits[6:8])
        if _valid_month(mm) and _valid_day(dd):
            cands.update({mm, dd, mm * 100 + dd, dd * 100 + mm})
    return cands


def _in_spans(pos: int, spans: List[tuple]) -> bool:
    return any(s <= pos < e for s, e in spans)


def _line_candidates(line: str) -> Set[int]:
    cands: Set[int] = set()
    spans: List[tuple] = []

    for m in _FULL_DATE_RE.finditer(line):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid_month(mo) and _valid_day(d):
            cands.update(date_candidates(f"{y:04d}{mo:02d}{d:02d}"))
            spans.append(m.span())

    for m in _PART_DATE_RE.finditer(line):
        if _in_spans(m.start(), spans) or _in_spans(m.end() - 1, spans):
            continue
        mo, d = int(m.group(1)), int(m.group(2))
        if _valid_month(mo) and _valid_day(d):
            cands.update(date_candidates(f"{mo:02d}{d:02d}"))
            spans.append(m.span())

    rest = "".join(ch for i, ch in enumerate(line) if not _in_spans(i, spans))
    cands.update(date_candidates(_NON_DIGIT.sub("", rest)))
    return cands


def parse_prefer_numbers(text: str) -> List[int]:
    nums: Set[int] = set()
    for line in (text or "").splitlines():
        nums.update(_line_candidates(line))
    return sorted(nums)


def filter_pool(pool: List[int], min_num: int, max_num: int) -> List[int]:
    return sorted(n for n in pool if min_num <= n <= max_num)


def build_prefer_pools(text: str) -> Dict[str, List[int]]:
    nums = parse_prefer_numbers(text)
    return {
        "ssq_red": filter_pool(nums, rules.SSQ_RED_MIN, rules.SSQ_RED_MAX),
        "ssq_blue": filter_pool(nums, rules.SSQ_BLUE_MIN, rules.SSQ_BLUE_MAX),
        "dlt_front": filter_pool(nums, rules.DLT_FRONT_MIN, rules.DLT_FRONT_MAX),
        "dlt_back": filter_pool(nums, rules.DLT_BACK_MIN, rules.DLT_BACK_MAX),
    }
