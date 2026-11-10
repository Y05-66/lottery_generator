import pytest

from core.date_parser import build_prefer_pools, date_candidates, parse_prefer_numbers


def test_ssq_red_pool_for_full_date():
    pools = build_prefer_pools("1990-05-20")
    assert pools["ssq_red"] == [5, 19, 20]


def test_ssq_blue_pool_for_full_date():
    pools = build_prefer_pools("1990-05-20")
    assert pools["ssq_blue"] == [5]


def test_dlt_pools_for_full_date():
    pools = build_prefer_pools("1990-05-20")
    assert pools["dlt_front"] == [5, 19, 20]
    assert pools["dlt_back"] == [5]


def test_dlt_back_pool_excludes_out_of_range():
    pools = build_prefer_pools("05-20")
    assert 5 in pools["dlt_back"]
    assert 20 not in pools["dlt_back"]


def test_empty_text_returns_empty():
    assert parse_prefer_numbers("") == []
    assert parse_prefer_numbers("\n   \n") == []
    assert parse_prefer_numbers(None) == []


def test_invalid_characters_do_not_crash():
    assert parse_prefer_numbers("abc-def!!") == []
    assert parse_prefer_numbers("！！！") == []


def test_supported_full_formats_equivalent():
    for text in ["1990-05-20", "1990/5/20", "19900520", "1990.05.20"]:
        pools = build_prefer_pools(text)
        assert pools["ssq_red"] == [5, 19, 20], text
        assert pools["ssq_blue"] == [5], text


def test_short_year_format():
    pools = build_prefer_pools("900520")
    assert pools["ssq_red"] == [5, 20]
    assert pools["ssq_blue"] == [5]


def test_short_formats_three_digits():
    for text in ["520", "5-20", "5/20"]:
        pools = build_prefer_pools(text)
        assert pools["ssq_red"] == [5, 20], text
    assert date_candidates("520") == {5, 20, 520}


def test_month_day_combo_numbers_filtered_out():
    pools = build_prefer_pools("1990-05-20")
    for bad in [90, 520, 2005]:
        assert bad not in pools["ssq_red"]


def test_multiple_lines_dedup_sorted():
    pools = build_prefer_pools("1990-05-20\n2015-10-01\n1990/5/20")
    assert pools["ssq_red"] == sorted(set(pools["ssq_red"]))
    assert pools["ssq_red"] == [1, 5, 10, 15, 19, 20]


def test_structured_dates_with_slash():
    pools = build_prefer_pools("1990/5/20")
    assert pools["ssq_red"] == [5, 19, 20]
    assert pools["ssq_blue"] == [5]


def test_part_date_with_slash_equivalent_to_plain():
    assert build_prefer_pools("5/20")["ssq_red"] == build_prefer_pools("520")["ssq_red"]


def test_invalid_month_falls_back_to_pair_candidates():
    pools = build_prefer_pools("19901340")
    assert pools["ssq_red"] == [13, 19]


def test_two_digit_input():
    assert date_candidates("20") == {20}


def test_chinese_date_line():
    pools = build_prefer_pools("生日：1990年05月20日")
    assert pools["ssq_red"] == [5, 19, 20]
