from typing import Any, Dict, List, Optional
from web3.types import Literal, RPCResponse, TypedDict

Authentication = TypedDict('Authentication', {
    'access_token': str,
    'expires_in': int,
    'refresh_token': str,
    'scope': str,
    'token_type': Literal['bearer']
})

Currency = TypedDict('Currency', {
    'coin_type': str,
    'currency': str,
    'currency_long': str,
    'fee_precision': int,
    'min_confirmations': int,
    'min_withdrawal_fee': float,
    'withdrawal_fee': float,
    'withdrawal_priorities': List
})

ChartData = TypedDict('ChartData', {
    'close': List[float],
    'cost': List[float],
    'high': List[float],
    'low': List[float],
    'open': List[float],
    'status': Literal['ok', 'no_data'],
    'ticks': List[int],
    'volume': List[float]
})
