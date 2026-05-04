#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
COMMON_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(COMMON_ROOT))

from common.runner import execute_checks  # noqa: E402  # type: ignore


if __name__ == "__main__":
    sys.exit(execute_checks("002"))
