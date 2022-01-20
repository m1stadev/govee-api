from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from utils.api import Govee
from utils import errors

import random
import time

API_KEY = ''

app = FastAPI()
api = Govee(API_KEY)


def _disable_lights():
    devices = api.devices
    api.disable(devices[0])

def _enable_lights():
    devices = api.devices
    api.enable(devices[0])

def _seizure():
    api.seizure_running = True
    devices = api.devices

    api.set_brightness(devices[0], 100)

    start_time = time.time()
    while (time.time() - start_time) < 10:
        colors = [_ for _ in Color.__dict__ if not _.startswith('__')]
        api.set_color(devices[0], random.choice(colors))

    api.seizure_running = False

@app.get('/govee/enable')
def enable_lights(task: BackgroundTasks):
    task.add_task(_enable_lights)

    return {'status': 'ok'}

@app.get('/govee/disable')
def disable_lights(task: BackgroundTasks):
    task.add_task(_disable_lights)

    return {'status': 'ok'}

@app.get('/govee/seizure')
def seizure(task: BackgroundTasks):
    if not api.seizure_running:
        task.add_task(_seizure)

        return {'status': 'ok'}
    else:
        raise HTTPException(status_code=425, detail='Seizure lights already running.')

@app.exception_handler(errors.AuthError)
def auth_error(request: Request, e: errors.APIError): return JSONResponse(status_code=401, content={'error': 'Invalid API key provided.'})

@app.exception_handler(errors.DevicesError)
def devices_error(request: Request, e: errors.DevicesError): return JSONResponse(status_code=404, content={'error': 'No devices found.'})

@app.exception_handler(errors.RatelimitError)
def ratelimit_error(request: Request, e: errors.RatelimitError):
    sleep = round((e.time - datetime.now()).total_seconds(), 3)
    return JSONResponse(status_code=429, content={'error': f'Ratelimit reached, please wait {sleep}s.'})
