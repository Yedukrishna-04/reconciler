from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "reconciler" / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from api.main import app  # noqa: E402


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
