from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Header, HTTPException, Request
from utils.api import Govee
from utils import errors, types

import os


API_KEY = os.environ.get('GOVEE_API_KEY')

app = FastAPI()
api = Govee(API_KEY)

@app.get('/govee/devices')
def get_devices(): return [_['device'] for _ in api.devices]

@app.post('/govee/actions/enable')
def enable_lights(device: types.DeviceData, api_key: str=Header(None)):
    if api_key != API_KEY:
        raise errors.AuthError('Invalid API key provided.')

    devices = api.devices

    try:
        device = next(_ for _ in devices if _['device'] == device.name)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"Device not found: '{device.name}'.")

    api.enable(device)
    return {'status': 'ok'}

@app.post('/govee/actions/disable')
def disable_lights(device: types.DeviceData, api_key: str=Header(None)):
    if api_key != API_KEY:
        raise errors.AuthError('Invalid API key provided.')

    devices = api.devices

    try:
        device = next(_ for _ in devices if _['device'] == device.name)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"Device not found: '{device.name}'.")

    api.disable(device)
    return {'status': 'ok'}

@app.post('/govee/set/brightness')
def set_brightness(device: types.DeviceData, brightness: types.BrightnessData, api_key: str=Header(None)):
    if api_key != API_KEY:
        raise errors.AuthError('Invalid API key provided.')

    devices = api.devices

    try:
        device = next(_ for _ in devices if _['device'] == device.name)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"Device not found: '{device.name}'.")

    api.set_brightness(device, brightness.level)
    return {'status': 'ok'}

@app.post('/govee/set/color')
def set_color(device: types.DeviceData, color: types.ColorData, api_key: str=Header(None)):
    if api_key != API_KEY:
        raise errors.AuthError('Invalid API key provided.')

    devices = api.devices

    try:
        device = next(_ for _ in devices if _['device'] == device.name)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"Device not found: '{device.name}'.")

    api.set_color(device, color.color)
    return {'status': 'ok'}

@app.exception_handler(errors.AuthError)
def auth_error(request: Request, e: errors.APIError): return JSONResponse(status_code=401, content={'error': 'Invalid API key provided.'})

@app.exception_handler(errors.DevicesError)
def devices_error(request: Request, e: errors.DevicesError): return JSONResponse(status_code=404, content={'error': 'No devices found.'})

@app.exception_handler(errors.RatelimitError)
def ratelimit_error(request: Request, e: errors.RatelimitError):
    sleep = round((e.time - datetime.now()).total_seconds(), 3)
    return JSONResponse(status_code=429, content={'error': f'Ratelimit reached, please wait {sleep}s.'})

@app.exception_handler(KeyError)
def keyerror_error(request: Request, e: KeyError): return JSONResponse(status_code=400, content={'error': str(e)})
