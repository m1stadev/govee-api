from cachetools import cached, TTLCache
from typing import Optional
from utils import colors, errors

import requests


API_URL = 'https://developer-api.govee.com/v1/devices/'
API_CONTROL_URL = API_URL + 'control/'
API_STATE_URL = API_URL + 'state/'

class Govee:
    def __init__(self, api_key):
        self.headers = {'Govee-API-Key': api_key}

    @property
    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def devices(self) -> Optional[list[dict]]:
        r = requests.get(API_URL, headers=self.headers)
        if r.status_code == 403:
            raise errors.AuthError('Invalid API key provided.')

        elif r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.')

        return r.json()['data']['devices']

    def _get_state(self, device: dict) -> Optional[dict]:
        data = {
            'device': device['device'],
            'model': device['model']
        }

        r = requests.get(API_STATE_URL, params=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.')

        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')

        return r.json()['data']

    def get_brightness(self, device: dict) -> Optional[int]:
        device_state = self._get_state(device)

        return next(_['brightness'] for _ in device_state['properties'] if 'brightness' in _.keys())

    def get_color(self, device: dict) -> Optional[int]:
        device_state = self._get_state(device)

        return next(_['color'] for _ in device_state['properties'] if 'color' in _.keys())

    def set_brightness(self, device: dict, brightness: int) -> None:
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

        r = requests.put(API_CONTROL_URL, json=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.')

        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')

    def set_color(self, device: dict, color: str) -> None:
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

        r = requests.put(API_CONTROL_URL, json=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.')

        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')
