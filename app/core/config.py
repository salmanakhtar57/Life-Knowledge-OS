"""All app settings in one place. Values come from environment variables
(loaded from .env); every setting except OPENROUTER_API_KEY has a default."""

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parents[2]

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
CHAT_MODEL = os.getenv("CHAT_MODEL", "~openai/gpt-sol-latest")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
CHAT_MAX_TOKENS = int(os.getenv("CHAT_MAX_TOKENS", "1500"))
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
AI_REQUEST_TIMEOUT_SECONDS = float(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "60"))

# Storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./life_knowledge_os.db")
DOCS_DIR = Path(os.getenv("DOCS_DIR", str(BASE_DIR / "FAQs")))

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "5"))
# Measured with text-embedding-3-small on the FAQs: on-topic questions score
# ~0.25-0.45, unrelated ones ~0.05-0.10.
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.15"))

# Answers
OWNER_NAME = os.getenv("OWNER_NAME", "Salman")

# Auth: a single owner account, no users table. Generate the hash and secret
# with the commands in app/core/security.py. Until all three are set, every
# login is rejected and protected routes stay locked.
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Web
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"http://(localhost|127\.0\.0\.1):\d+")
