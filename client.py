import asyncio
import os
from aiohttp import ClientSession, ClientTimeout
from typing import Any, Dict, Optional, Union
from datetime import datetime
import json
from dotenv import load_dotenv
from web3 import AsyncHTTPProvider
from web3._utils.request import _get_async_session as get_async_session
from pprint import pprint

load_dotenv()
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


class HTTPProvider(AsyncHTTPProvider):

    def __init__(
            self, endpoint_uri: Optional[str] = None,
            request_kwargs: Optional[Any] = None
    ) -> None:
        super().__init__(endpoint_uri, request_kwargs)

    def get_request_headers(self) -> Dict[str, str]:
        return {'Content-Type': 'application/json'}

    async def make_request(self, method: str, params: Optional[Dict] = None):
        self.logger.debug(f'Making request HTTP. URI: {self.endpoint_uri}, Method: {method}')
        session = await get_async_session(self.endpoint_uri)
        session = ClientSession('https://www.deribit.com', timeout=ClientTimeout(5))
        print(session)
        print(session._base_url)
        print(self.endpoint_uri + method)
        print(params)
        print(self.get_request_kwargs())
        async with session.get(
                '/api/v2' + method,
                params=params,
                **self.get_request_kwargs()
        ) as response:
            raw_response = await response.read()
        response = self.decode_rpc_response(raw_response)
        self.logger.debug(f'Getting response HTTP. URI: {self.endpoint_uri}, Method: {method}, Response: {response}')
        return response


class Client:
    provider = ClientSession('https://www.deribit.com', timeout=ClientTimeout(5), headers={'Content-Type': 'application/json'})
    # provider = HTTPProvider('https://www.deribit.com/api/v2')

    def __init__(self, client_id, client_secret, test=False):
        self.client_id = client_id
        self.client_secret = client_secret
        # if test:
        #     self.provider = ClientSession(base_url='https://test.deribit.com/api/v2', timeout=ClientTimeout(5))

    async def close(self):
        await self.provider.close()

    async def get_currencies(self):
        async with self.provider.get('/api/v2/public/get_currencies') as resp:
            res = await resp.json()
        # res = await self.provider.make_request('/public/get_currencies')
        return res['result']

    async def authenticate(self):
        method = 'public/auth'
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        print(await self.provider.make_request(method, params))


async def test():
    client = Client(CLIENT_ID, CLIENT_SECRET)
    pprint(await client.get_currencies())
    await client.close()


if __name__ == '__main__':
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(test())
