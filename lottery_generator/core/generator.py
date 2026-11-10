import random
from typing import List

from core import rules
from core.date_parser import build_prefer_pools
from core.models import DLTResult, DrawResult, GenerateOptions, LotteryType, SSQResult


def clamp_count(value) -> int:
    try:
        n = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return rules.DEFAULT_COUNT
    return max(rules.MIN_COUNT, min(rules.MAX_COUNT, n))


def normalize_types(types) -> List[LotteryType]:
    ordered: List[LotteryType] = []
    for t in types or []:
        try:
            lt = LotteryType(t)
        except ValueError:
            continue
        if lt not in ordered:
            ordered.append(lt)
    return ordered


def generate_zone(count: int, min_num: int, max_num: int,
                  pref_pool: List[int], prefer: bool) -> List[int]:
    all_numbers = list(range(min_num, max_num + 1))
    pref = [n for n in pref_pool if min_num <= n <= max_num]
    chosen: List[int] = []

    if prefer and pref:
        max_k = min(len(pref), count)
        k = 1 if count == 1 else random.randint(1, max_k)
        chosen.extend(random.sample(pref, k))

    remaining = [n for n in all_numbers if n not in chosen]
    need = count - len(chosen)
    chosen.extend(random.sample(remaining, need))
    return sorted(chosen)


def generate_ssq(pref_red: List[int], pref_blue: List[int],
                 prefer: bool) -> SSQResult:
    red = generate_zone(rules.SSQ_RED_COUNT, rules.SSQ_RED_MIN, rules.SSQ_RED_MAX, pref_red, prefer)
    blue = generate_zone(rules.SSQ_BLUE_COUNT, rules.SSQ_BLUE_MIN, rules.SSQ_BLUE_MAX, pref_blue, prefer)[0]
    return SSQResult(red=red, blue=blue)


def generate_dlt(pref_front: List[int], pref_back: List[int],
                 prefer: bool) -> DLTResult:
    front = generate_zone(rules.DLT_FRONT_COUNT, rules.DLT_FRONT_MIN, rules.DLT_FRONT_MAX, pref_front, prefer)
    back = generate_zone(rules.DLT_BACK_COUNT, rules.DLT_BACK_MIN, rules.DLT_BACK_MAX, pref_back, prefer)
    return DLTResult(front=front, back=back)


def generate_draws(options: GenerateOptions) -> List[DrawResult]:
    types = normalize_types(options.types)
    if not types:
        raise ValueError("请至少勾选一种彩票类型")
    count = clamp_count(options.count)
    pools = build_prefer_pools(options.prefer_dates or "")

    results: List[DrawResult] = []
    index = 1
    for lt in types:
        for _ in range(count):
            if lt == LotteryType.SSQ:
                ssq = generate_ssq(pools["ssq_red"], pools["ssq_blue"], options.prefer)
                results.append(DrawResult(lottery_type=lt, index=index, ssq=ssq))
            else:
                dlt = generate_dlt(pools["dlt_front"], pools["dlt_back"], options.prefer)
                results.append(DrawResult(lottery_type=lt, index=index, dlt=dlt))
            index += 1
    return results
