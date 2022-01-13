from datetime import datetime
from utils.api import Govee
from utils import errors

import aiohttp
import asyncio
import random

API_KEY = ''


async def seizure() -> None:
    session = aiohttp.ClientSession()

    try:
        api = Govee(session, API_KEY)
        try:
            devices = await api.get_devices()
        except errors.RatelimitError as rl:
            sleep = round((rl.time - datetime.now()).total_seconds())
            if sleep > 1:
                print(f"Ratelimit reached, sleeping for {sleep} seconds...")
                await asyncio.sleep(sleep)


        if len(devices) == 0:
            raise IndexError('No devices found.')

        await api.set_brightness(devices[0], 100)
        while True:
            colors = ('aqua', 'blue', 'green', 'orange', 'pink', 'purple', 'red', 'white', 'yellow')
            try:
                await api.set_color(devices[0], random.choice(colors))
            except errors.RatelimitError as rl:
                sleep = round((rl.time - datetime.now()).total_seconds())
                if sleep > 1:
                    print(f"Ratelimit reached, sleeping for {sleep} seconds...")
                    await asyncio.sleep(sleep)

    finally:
        await session.close()


async def main() -> None:
    session = aiohttp.ClientSession()

    try:
        api = Govee(session, API_KEY)
        devices = await api.get_devices()
        print(f"There's {len(devices)} device{'' if len(devices) == 1 else 's'} connected to your Govee account.")

    finally:
        await session.close()


if __name__ == '__main__':
    asyncio.run(seizure())
