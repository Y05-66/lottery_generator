from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LotteryType(str, Enum):
    SSQ = "ssq"
    DLT = "dlt"


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
