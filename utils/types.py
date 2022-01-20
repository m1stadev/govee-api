from pydantic import BaseModel


class DeviceData(BaseModel):
    name: str


class BrightnessData(BaseModel):
    level: int


class ColorData(BaseModel):
    color: str

