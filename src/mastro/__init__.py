"""Mastro - My AI Assistant for Astronomical Research."""

from . import ads
from .ads import ADSClient, EXPORT_FORMATS, extract_bibcode

__all__ = [
    "ADSClient",
    "EXPORT_FORMATS",
    "ads",
    "extract_bibcode",
]


def hello() -> str:
    return "Hello from mastro!"
