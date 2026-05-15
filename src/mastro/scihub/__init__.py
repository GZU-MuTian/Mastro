"""Sci-Hub client for paper access."""

from .scihub import SciHubClient
from .cli import app as cli

__all__ = ["SciHubClient", "cli"]
