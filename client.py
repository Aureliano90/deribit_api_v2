import asyncio
import os
from aiohttp import ClientTimeout
from dotenv import load_dotenv
from eth_utils import to_bytes
from web3 import AsyncHTTPProvider
from web3.types import RPCResponse
from web3._utils.encoding import FriendlyJsonSerde
from web3._utils.request import _get_async_session as get_async_session
from dtypes import *
from pprint import pprint

load_dotenv()
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


class HTTPProvider(AsyncHTTPProvider):
    """`HTTPProvider` derived from `Web3.py`'s `AsyncHTTPProvider` to interact with Deribit's HTTP API
    """

    def __init__(
            self, endpoint_uri: Optional[str] = None,
            request_kwargs: Optional[Any] = None
    ) -> None:
        super().__init__(endpoint_uri, request_kwargs)

    def get_request_headers(self) -> Dict[str, str]:
        return {'Content-Type': 'application/json'}

    def encode_rpc_request(self, method: str, params: Optional[Dict]) -> bytes:
        rpc_dict = {
            'jsonrpc': '2.0',
            'method': method,
            'id': next(self.request_counter),
        }
        # `params` field must be skipped if empty
        if params: rpc_dict['params'] = params
        encoded = FriendlyJsonSerde().json_encode(rpc_dict)
        return to_bytes(text=encoded)

    async def make_request(self, method: str, params: Optional[Dict] = None) -> RPCResponse:
        self.logger.debug(f'Making request HTTP. URI: {self.endpoint_uri}, Method: {method}')
        session = await get_async_session(self.endpoint_uri)
        # Can use straight GET HTTP requests
        # async with session.get(
        #         self.endpoint_uri + method,
        #         params=params,
        #         **self.get_request_kwargs()
        # ) as response:
        #     raw_response = await response.read()

        # Or encoded POST RPC requests similar to Ethereum's
        request_data = self.encode_rpc_request(method, params)
        async with session.post(
                self.endpoint_uri,
                data=request_data,
                **self.get_request_kwargs()
        ) as response:
            raw_response = await response.read()
        response = self.decode_rpc_response(raw_response)
        self.logger.debug(f'Getting response HTTP. URI: {self.endpoint_uri}, Method: {method}, Response: {response}')
        return response


class Client:
    provider = HTTPProvider('https://www.deribit.com/api/v2', {'timeout': ClientTimeout(5)})

    def __init__(self, client_id, client_secret, testnet=False):
        if testnet:
            self.provider = HTTPProvider('https://test.deribit.com/api/v2', {'timeout': ClientTimeout(5)})
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = ''

    async def make_request(self, method: str, params: Optional[Dict] = None) -> Any:
        return (await self.provider.make_request(method, params))['result']

    async def authenticate(self) -> Authentication:
        """Retrieve an Oauth access token, to be used for authentication of 'private' requests.

        Two methods of authentication are supported:

        client_credentials - using the access key and access secret that can be found on the API page on the website

        refresh_token - using a refresh token that was received from an earlier invocation
        """
        method = '/public/auth'
        if self.refresh_token:
            params = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        else:
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        res = await self.make_request(method, params)
        self.refresh_token = res['refresh_token']
        return res

    async def exchange_token(self, subject_id: int) -> Authentication:
        """Generates token for new subject id. This method can be used to switch between subaccounts.
        """
        res = await self.make_request('/public/exchange_token', {
            'subject_id': subject_id,
            'refresh_token': self.refresh_token
        })
        self.refresh_token = res['refresh_token']
        return res

    async def get_currencies(self) -> List[Currency]:
        """Retrieves all cryptocurrencies supported by the API.
        """
        return await self.make_request('/public/get_currencies')

    async def get_historical_volatility(self, currency: Literal['BTC', 'ETH', 'USDC']) -> List:
        """Provides information about historical volatility for given cryptocurrency.

        :param currency: 'BTC', 'ETH', 'USDC'
        :return: List[[timestamp, value]]
        """
        return await self.make_request('/public/get_historical_volatility', {'currency': currency})

    async def get_index_price(self, index_name: str) -> Dict:
        """Retrieves the current index price value for given index name.

        :param index_name: Index identifier, matches (base) cryptocurrency with quote currency
        :return: TypedDict('IndexPrice', {
            'estimated_delivery_price': float,
            'index_price': float
        })
        """
        return await self.make_request('/public/get_index_price', {'index_name': index_name})

    async def get_instrument(self, instrument_name: str):
        """Retrieves information about instrument

        :param instrument_name: Instrument name
        """
        params = {'instrument_name': instrument_name}
        return await self.make_request('/public/get_instrument', params)

    async def get_instruments(
            self,
            currency: Literal['BTC', 'ETH', 'USDC'],
            kind: Literal['future', 'option', 'future_combo', 'option_combo'] = '',
            expired=False
    ) -> List[Dict]:
        """Retrieves available trading instruments.
        This method can be used to see which instruments are available for trading,
        or which instruments have recently expired.
        """
        params = {'currency': currency}
        if kind: params['kind'] = kind
        if expired: params['expired'] = expired
        return await self.make_request('/public/get_instruments', params)

    async def get_tradingview_chart_data(
            self,
            instrument_name: str,
            start_timestamp: int,
            end_timestamp: int,
            resolution: Literal['1', '3', '5', '10', '15', '30', '60', '120', '180', '360', '720', '1D']
    ) -> ChartData:
        """Publicly available market data used to generate a TradingView candle chart.

        :param instrument_name: Instrument name
        :param start_timestamp: The earliest timestamp to return result for (milliseconds since the UNIX epoch)
        :param end_timestamp: The most recent timestamp to return result for (milliseconds since the UNIX epoch)
        :param resolution: Chart bars resolution given in full minutes or keyword `1D`
        :return: `ChartData`
        """
        params = {
            'instrument_name': instrument_name,
            'start_timestamp': int(start_timestamp),
            'end_timestamp': int(end_timestamp),
            'resolution': resolution
        }
        return await self.make_request('/public/get_tradingview_chart_data', params)

    async def ticker(self, instrument_name: str) -> Ticker:
        """Get ticker for an instrument.

        :param instrument_name: Instrument name
        :return:
        """
        params = {'instrument_name': instrument_name}
        return await self.make_request('/public/ticker', params)


async def test():
    client = Client(CLIENT_ID, CLIENT_SECRET)
    pprint(await client.authenticate())
    # pprint(await client.get_currencies())
    # pprint(await client.get_historical_volatility('BTC'))
    # pprint(await client.get_instruments('BTC', kind='future'))
    pprint(await client.ticker('BTC-PERPETUAL'))


if __name__ == '__main__':
    asyncio.run(test())
