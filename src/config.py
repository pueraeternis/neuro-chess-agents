from __future__ import annotations

import logging
from pathlib import Path

# --- Paths & application metadata -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

APP_TITLE = "Neuro-Chess Agents"

STATIC_URL_PREFIX = "/static"
STATIC_DIR = BASE_DIR / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"


# --- Logging configuration --------------------------------------------------------

LOGGER_NAME = "neuro_chess"
LOGGER_LEVEL = logging.INFO

LOGGER_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"
LOGGER_DATEFMT = "%H:%M:%S"


# --- LLM / agent configuration ----------------------------------------------------

LLM_DEFAULT_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 16384

LLM_STRATEGIST_TEMPERATURE = 0.6
LLM_COMMENTATOR_TEMPERATURE = 0.8

LLM_STOP_TOKENS = ["<|im_end|>", "<|endoftext|>"]

MAX_RETRIES = 10
MAX_LEGAL_MOVES_LOG = 10
FALLBACK_COMMENTARY = "I am confused. Random move go!"


# --- Asset download configuration -------------------------------------------------

ASSETS_BASE_URL = "https://chessboardjs.com/img/chesspieces/wikipedia/"
ASSETS_PIECES = [
    "wP",
    "wN",
    "wB",
    "wR",
    "wQ",
    "wK",
    "bP",
    "bN",
    "bB",
    "bR",
    "bQ",
    "bK",
]
ASSETS_TARGET_DIR = STATIC_DIR / "img" / "chesspieces" / "wikipedia"
ASSETS_USER_AGENT = "Mozilla/5.0"
