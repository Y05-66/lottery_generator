import csv
import io

import pytest

from core.formatter import format_result_text, format_results, results_to_csv
from core.models import DLTResult, DrawResult, LotteryType, SSQResult


def make_ssq(index=1):
    return DrawResult(
        lottery_type=LotteryType.SSQ,
        index=index,
        ssq=SSQResult(red=[5, 12, 19, 20, 23, 31], blue=8),
    )


def make_dlt(index=2):
    return DrawResult(
        lottery_type=LotteryType.DLT,
        index=index,
        dlt=DLTResult(front=[3, 5, 19, 20, 28], back=[5, 11]),
    )


def test_format_ssq_line():
    assert format_result_text(make_ssq()) == "第1注 双色球：红球 05 12 19 20 23 31 + 蓝球 08"


def test_format_dlt_line():
    assert format_result_text(make_dlt()) == "第2注 大乐透：前区 03 05 19 20 28 + 后区 05 11"


def test_format_results_multi_line():
    text = format_results([make_ssq(), make_dlt()])
    assert text == (
        "第1注 双色球：红球 05 12 19 20 23 31 + 蓝球 08\n"
        "第2注 大乐透：前区 03 05 19 20 28 + 后区 05 11"
    )


def test_format_invalid_result_raises():
    with pytest.raises(ValueError):
        format_result_text(DrawResult(lottery_type=LotteryType.SSQ, index=1))


def test_csv_output():
    csv_text = results_to_csv([make_ssq(), make_dlt()])
    rows = list(csv.reader(io.StringIO(csv_text)))
    assert rows[0] == ["注号", "彩种", "红球/前区", "蓝球/后区"]
    assert rows[1] == ["1", "双色球", "05 12 19 20 23 31", "08"]
    assert rows[2] == ["2", "大乐透", "03 05 19 20 28", "05 11"]


def test_pad_single_digit():
    result = DrawResult(lottery_type=LotteryType.SSQ, index=1,
                        ssq=SSQResult(red=[1, 2, 3, 4, 5, 6], blue=1))
    assert format_result_text(result) == "第1注 双色球：红球 01 02 03 04 05 06 + 蓝球 01"
