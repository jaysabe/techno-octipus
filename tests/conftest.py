"""Pytest configuration shared by all test modules.

Sets up the repository root on ``sys.path`` and installs the MicroPython
``machine`` mock before any test module is collected, so individual test
files don't need to repeat this boilerplate.
"""

import sys
import os

# Ensure the repository root is importable so ``arm`` and ``tests`` resolve.
_repo_root = os.path.dirname(os.path.dirname(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Install the machine mock once for the whole session.
import tests.mock_machine  # noqa: F401, E402
