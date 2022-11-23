from typing import NamedTuple


class Pixel(NamedTuple):
    """A pixel coordinate on a camera"""
    x: int
    y: int


class Translation(NamedTuple):
    """The position of something on the field"""
    x: float
    y: float
    absolute: bool = False
    """Whether the coordinates are relative to the field or the camera"""
