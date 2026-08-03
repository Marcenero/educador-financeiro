from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

DEFAULT_MODEL = "qwen3:4b-instruct"
DEFAULT_BASE_URL = "http://localhost:11434"

def criar_modelo_ollama() -> ChatOllama:
    """Cria e configura o modelo local usado pelo MVP"""
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", DEFAULT_MODEL),
        base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL),
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0")),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "500")),
        reasoning=False,
    )