"""Provides a command-line interface for OpenDPM."""

import logging

from .commands import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

__all__ = ["main"]
