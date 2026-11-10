import pytest

from core import rules
from core.generator import (
    clamp_count,
    generate_draws,
    generate_dlt,
    generate_ssq,
    generate_zone,
)
from core.models import GenerateOptions, LotteryType


def test_zone_shape_sorted_and_unique():
    for _ in range(100):
        zone = generate_zone(6, 1, 33, [], False)
        assert len(zone) == 6
        assert len(set(zone)) == 6
        assert zone == sorted(zone)
        assert all(1 <= n <= 33 for n in zone)


def test_zone_pref_pool_filtered_to_range():
    zone = generate_zone(6, 1, 16, [3, 999, 0], True)
    assert len(zone) == 6 and len(set(zone)) == 6
    assert all(1 <= n <= 16 for n in zone)


def test_ssq_shape():
    for _ in range(100):
        r = generate_ssq([], [], False)
        assert len(r.red) == rules.SSQ_RED_COUNT
        assert len(set(r.red)) == rules.SSQ_RED_COUNT
        assert all(rules.SSQ_RED_MIN <= n <= rules.SSQ_RED_MAX for n in r.red)
        assert rules.SSQ_BLUE_MIN <= r.blue <= rules.SSQ_BLUE_MAX


def test_dlt_shape():
    for _ in range(100):
        r = generate_dlt([], [], False)
        assert len(r.front) == rules.DLT_FRONT_COUNT
        assert len(set(r.front)) == rules.DLT_FRONT_COUNT
        assert all(rules.DLT_FRONT_MIN <= n <= rules.DLT_FRONT_MAX for n in r.front)
        assert len(r.back) == rules.DLT_BACK_COUNT
        assert len(set(r.back)) == rules.DLT_BACK_COUNT
        assert all(rules.DLT_BACK_MIN <= n <= rules.DLT_BACK_MAX for n in r.back)


def test_prefer_zone_includes_preference():
    pool = [5, 19, 20]
    for _ in range(100):
        zone = generate_zone(6, 1, 33, pool, True)
        assert len(zone) == 6 and len(set(zone)) == 6
        assert any(n in pool for n in zone)


def test_prefer_single_number_zone_uses_preference():
    for _ in range(50):
        assert generate_zone(1, 1, 16, [5], True) == [5]


def test_no_prefer_still_valid():
    for _ in range(100):
        zone = generate_zone(6, 1, 33, [5, 19, 20], False)
        assert len(zone) == 6 and len(set(zone)) == 6


def test_draws_empty_types_raises():
    with pytest.raises(ValueError):
        generate_draws(GenerateOptions(types=[], count=1))
    with pytest.raises(ValueError):
        generate_draws(GenerateOptions(types=["xxx"], count=1))


def test_draws_count_clamped():
    assert len(generate_draws(GenerateOptions(types=[LotteryType.SSQ], count=0))) == 1
    results = generate_draws(GenerateOptions(types=[LotteryType.SSQ], count=21))
    assert len(results) == rules.MAX_COUNT
    assert [r.index for r in results] == list(range(1, rules.MAX_COUNT + 1))


def test_clamp_count_values():
    assert clamp_count(0) == 1
    assert clamp_count(-5) == 1
    assert clamp_count(21) == 20
    assert clamp_count("abc") == rules.DEFAULT_COUNT
    assert clamp_count(None) == rules.DEFAULT_COUNT
    assert clamp_count("7") == 7
    assert clamp_count(5) == 5


def test_draws_alternate_types_when_both_selected():
    options = GenerateOptions(
        types=[LotteryType.SSQ, LotteryType.DLT],
        count=2,
        prefer_dates="1990-05-20",
        prefer=True,
    )
    results = generate_draws(options)
    # each type gets count draws: SSQ×2 then DLT×2
    assert len(results) == 4
    assert [r.lottery_type for r in results] == [
        LotteryType.SSQ, LotteryType.SSQ,
        LotteryType.DLT, LotteryType.DLT,
    ]
    assert [r.index for r in results] == [1, 2, 3, 4]
    assert results[0].ssq is not None and results[0].dlt is None
    assert results[1].ssq is not None and results[1].dlt is None
    assert results[2].dlt is not None and results[2].ssq is None
    assert results[3].dlt is not None and results[3].ssq is None


def test_draws_with_preference_contains_preferred():
    options = GenerateOptions(types=[LotteryType.SSQ], count=10,
                              prefer_dates="1990-05-20", prefer=True)
    pool = {5, 19, 20}
    for r in generate_draws(options):
        assert any(n in pool for n in r.ssq.red)


def test_draws_prefer_off_valid():
    options = GenerateOptions(types=[LotteryType.SSQ], count=5,
                              prefer_dates="1990-05-20", prefer=False)
    for r in generate_draws(options):
        assert len(r.ssq.red) == 6
        assert 1 <= r.ssq.blue <= 16


def test_draws_duplicate_types_normalized():
    options = GenerateOptions(types=[LotteryType.SSQ, "ssq", LotteryType.DLT], count=4)
    results = generate_draws(options)
    # deduplicated to [SSQ, DLT], each gets count draws
    assert len(results) == 8
    assert [r.lottery_type for r in results] == [
        LotteryType.SSQ, LotteryType.SSQ, LotteryType.SSQ, LotteryType.SSQ,
        LotteryType.DLT, LotteryType.DLT, LotteryType.DLT, LotteryType.DLT,
    ]
