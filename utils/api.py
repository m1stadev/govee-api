from cachetools import cached, TTLCache
from typing import Optional
from utils.colors import Color
from utils import errors

import requests

API_URL = 'https://developer-api.govee.com/v1/devices/'
API_CONTROL_URL = API_URL + 'control/'
API_STATE_URL = API_URL + 'state/'


class Govee:
    def __init__(self, api_key: str):
        self.headers = {'Govee-API-Key': api_key}

    @property
    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def devices(self) -> Optional[list[dict]]:
        r = requests.get(API_URL, headers=self.headers)
        if r.status_code == 401:
            raise errors.AuthError('Invalid API key provided.')

        elif r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))

        return r.json()['data']['devices']

    def _get_state(self, device: dict) -> Optional[dict]:
        data = {_:device[_] for _ in ('device', 'model')}

        r = requests.get(API_STATE_URL, params=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))
        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')

        devices = r.json()['data']
        if len(devices) == 0:
            raise errors.DevicesError('No devices found.')

        return devices

    def disable(self, device: dict) -> None:
        data = {
            'device': device['device'],
            'model': device['model'],
            'cmd': {
                'name': 'turn',
                'value': 'off'
            }
        }

        r = requests.put(API_CONTROL_URL, json=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))
        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')
    
    def enable(self, device: dict) -> None:
        data = {
            'device': device['device'],
            'model': device['model'],
            'cmd': {
                'name': 'turn',
                'value': 'on'
            }
        }

        r = requests.put(API_CONTROL_URL, json=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))
        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')

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
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))
        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')

    def set_color(self, device: dict, color: str) -> None:
        try:
            getattr(Color, color.lower())
        except AttributeError as e:
            raise KeyError('Invalid color passed.') from e

        data = {
            'device': device['device'],
            'model': device['model'],
            'cmd': {
                'name': 'color',
                'value': getattr(Color, color.lower())
            }
        }

        r = requests.put(API_CONTROL_URL, json=data, headers=self.headers)
        if r.status_code == 429:
            raise errors.RatelimitError('Ratelimit reached.', int(r.headers['Rate-Limit-Reset']))
        elif r.status_code == 400:
            raise errors.APIError('Invalid data passed to API.')
