from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

@pytest.fixture
def client_joao_id() -> str:
    return "CLI-0001"

@pytest.fixture
def client_mariana_id() -> str:
    return "CLI-0002"

@pytest.fixture
def client_carlos_id() -> str:
    return "CLI-0003"