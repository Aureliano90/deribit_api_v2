from typing import Any, Dict, List, Optional
from web3.types import Literal, RPCResponse, TypedDict


class Authentication(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: Literal['bearer']


class Currency(TypedDict):
    coin_type: str
    currency: str
    currency_long: str
    fee_precision: int
    min_confirmations: int
    min_withdrawal_fee: float
    withdrawal_fee: float
    withdrawal_priorities: List


class ChartData(TypedDict):
    close: List[float]
    cost: List[float]
    high: List[float]
    low: List[float]
    open: List[float]
    status: Literal['ok', 'no_data']
    ticks: List[int]
    volume: List[float]
