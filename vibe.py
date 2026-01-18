#!/usr/bin/env python3
"""
Backward compatibility shim for Vibe-CLI.
Deprecation Notice: Please use 'python -m vibe' or 'vibe' command (after install) instead.
"""
import sys
import warnings
from vibe.cli.app import app

if __name__ == "__main__":
    warnings.warn(
        "Running via 'python vibe.py' is deprecated. Use 'python -m vibe' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    app()
