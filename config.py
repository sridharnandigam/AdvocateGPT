"""Runtime configuration for the text-only MVP."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Prefer a root .env, but keep compatibility with the current src/.env layout.
load_dotenv(BASE_DIR / ".env", override=False)
load_dotenv(BASE_DIR / "src" / ".env", override=False)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


LLAMA_SERVER_BIN = os.getenv("LLAMA_SERVER_BIN")
NEMOTRON_MODEL = os.getenv("NEMOTRON_MODEL")

LLAMA_SERVER_HOST = os.getenv("LLAMA_SERVER_HOST", "127.0.0.1")
LLAMA_SERVER_PORT = _get_int("LLAMA_SERVER_PORT", 8080)

LLAMA_CTX_SIZE = _get_int("LLAMA_CTX_SIZE", 4096)
LLAMA_N_GPU_LAYERS = _get_int("LLAMA_N_GPU_LAYERS", 999)
LLAMA_THREADS = _get_int("LLAMA_THREADS", 8)
LLAMA_BATCH = _get_int("LLAMA_BATCH", 512)
LLAMA_MAX_TOKENS = _get_int("LLAMA_MAX_TOKENS", 120)
LLAMA_TEMPERATURE = _get_float("LLAMA_TEMPERATURE", 0.2)
LLAMA_TOP_P = _get_float("LLAMA_TOP_P", 0.9)

AUTO_START_MODEL_SERVER = _get_bool("AUTO_START_MODEL_SERVER", default=False)

LLAMA_BASE_URL = os.getenv(
    "LLAMA_BASE_URL",
    f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}",
)
