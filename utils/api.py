from aiocache import cached
from typing import Optional
from utils import colors, errors

import aiohttp


API_URL = 'https://developer-api.govee.com/v1/devices/'
API_CONTROL_URL = API_URL + 'control/'
API_STATE_URL = API_URL + 'state/'

class Govee:
    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        self.session = session
        self.headers = {'Govee-API-Key': api_key}

    @cached(ttl=60)
    async def get_devices(self) -> Optional[list[dict]]:
        async with self.session.get(API_URL, headers=self.headers) as s:
            if s.status == 403:
                raise errors.AuthError('Invalid API key provided.')

            elif s.status == 429:
                raise errors.RatelimitError('Ratelimit reached.', int(s.headers['Rate-Limit-Reset']))

            return (await s.json())['data']['devices']

    async def _get_state(self, device: dict) -> Optional[dict]:
        data = {
            'device': device['device'],
            'model': device['model']
        }

        async with self.session.get(API_STATE_URL, params=data, headers=self.headers) as s:
            if s.status == 429:
                raise errors.RatelimitError('Ratelimit reached.', int(s.headers['Rate-Limit-Reset']))
            elif s.status == 400:
                raise errors.APIError('Invalid data passed to API.')

            return (await s.json())['data']

    async def get_brightness(self, device: dict) -> Optional[int]:
        device_state = await self._get_state(device)

        return next(_['brightness'] for _ in device_state['properties'] if 'brightness' in _.keys())

    async def get_color(self, device: dict) -> Optional[int]:
        device_state = await self._get_state(device)

        return next(_['color'] for _ in device_state['properties'] if 'color' in _.keys())

    async def set_brightness(self, device: dict, brightness: int) -> None:
        if not 1 <= brightness <= 100:
            raise ValueError('Brightness must be between 1-100.')

        data = {
            'device': device['device'],
            'model': device['model'],
            'cmd': {
                'name': 'brightness',
                'value': brightness
            }
        }

        async with self.session.put(API_CONTROL_URL, json=data, headers=self.headers) as s:
            if s.status == 429:
                raise errors.RatelimitError('Ratelimit reached.', int(s.headers['Rate-Limit-Reset']))
            elif s.status == 400:
                raise errors.APIError('Invalid data passed to API.')

    async def set_color(self, device: dict, color: str) -> None:
        if getattr(colors, color.upper()) is None:
            raise KeyError('Invalid color passed.')

        data = {
            'device': device['device'],
            'model': device['model'],
            'cmd': {
                'name': 'color',
                'value': getattr(colors, color.upper())
            }
        }

        async with self.session.put(API_CONTROL_URL, json=data, headers=self.headers) as s:
            if s.status == 429:
                raise errors.RatelimitError('Ratelimit reached.', int(s.headers['Rate-Limit-Reset']))
            elif s.status == 400:
                raise errors.APIError('Invalid data passed to API.')
