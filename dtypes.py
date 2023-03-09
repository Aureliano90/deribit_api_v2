from typing import Any, Dict, List, Literal, Optional, TypedDict


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


class Greeks(TypedDict):
    delta: float
    gamma: float
    rho: float
    theta: float
    vega: float


class Stats(TypedDict, total=False):
    high: float
    low: float
    price_change: float
    volume: float
    volume_usd: float


class Ticker(TypedDict, total=False):
    ask_iv: float
    best_ask_amount: float
    best_ask_price: float
    best_bid_amount: float
    best_bid_price: float
    bid_iv: float
    current_funding: float
    delivery_price: float
    estimated_delivery_price: float
    funding_8h: float
    greeks: Greeks
    index_price: float
    instrument_name: str
    interest_rate: float
    interest_value: float
    last_price: float
    mark_iv: float
    mark_price: float
    max_price: float
    min_price: float
    open_interest: float
    settlement_price: float
    state: Literal['open', 'closed']
    timestamp: int
    underlying_index: str
    underlying_price: float


class ChartData(TypedDict):
    close: List[float]
    cost: List[float]
    high: List[float]
    low: List[float]
    open: List[float]
    status: Literal['ok', 'no_data']
    ticks: List[int]
    volume: List[float]
