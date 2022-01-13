from utils.api import Govee
from utils import errors

import random
import time

API_KEY = ''


def seizure() -> None:
    api = Govee(API_KEY)
    
    if len(api.devices) == 0:
        raise IndexError('No devices found.')

    api.set_brightness(api.devices[0], 100)
    while True:
        colors = ('aqua', 'blue', 'green', 'orange', 'pink', 'purple', 'red', 'white', 'yellow')
        try:
            api.set_color(api.devices[0], random.choice(colors))
        except errors.RatelimitError:
            print('Ratelimit reached, sleeping for 5 seconds...')
            time.sleep(5) 
            continue


def main() -> None:
    api = Govee(API_KEY)
    print(f"There's {len(api.devices)} device{'' if len(api.devices) == 1 else 's'} connected to your Govee account.")


if __name__ == '__main__':
    main()
