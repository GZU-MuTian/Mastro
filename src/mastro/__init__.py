"""Mastro - My AI Assistant for Astronomical Research."""

from . import ads, scihub
from .ads import ADSClient, EXPORT_FORMATS, extract_bibcode
from .scihub import SciHubClient

__all__ = [
    "ADSClient",
    "EXPORT_FORMATS",
    "SciHubClient",
    "ads",
    "extract_bibcode",
    "scihub",
]


def hello() -> str:
    return "Hello from mastro!"
