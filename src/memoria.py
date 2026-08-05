from __future__ import annotations

import re
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver

CHECKPOINTER = InMemorySaver()

_CARACTERES_INVALIDOS = re.compile(r"[^A-Za-z0-9_.:-]+")

def criar_id_sessao() -> str:
    """Cria um identificador aleatório para a sessão do navegador."""
    return uuid4().hex

def construir_thread_id(sessao_id: str, perfil_id: str) -> str:
    """Combina a sessão e o perfil para isolar a memória."""
    if not sessao_id or not sessao_id.strip():
        raise ValueError("sessao_id deve ser informado.")

    if not perfil_id or not perfil_id.strip():
        raise ValueError("perfil_id deve ser informado.")

    sessao = _normalizar_identificador(sessao_id)
    perfil = _normalizar_identificador(perfil_id.upper())

    return f"{sessao}:{perfil}"

def criar_thread_temporaria(perfil_id: str) -> str:
    """Cria uma conversa isolada para chamadas sem sessão persistente."""
    return construir_thread_id(
        sessao_id=f"temporaria-{uuid4().hex}",
        perfil_id=perfil_id,
    )

def criar_configuracao(thread_id: str) -> dict:
    """Monta a configuração exigida pelo checkpointer."""
    if not thread_id or not thread_id.strip():
        raise ValueError("thread_id deve ser informado.")

    return {
        "configurable": {
            "thread_id": thread_id.strip(),
        }
    }

def limpar_memoria(thread_id: str) -> None:
    """Apaga todos os checkpoints associados à conversa."""
    if thread_id and thread_id.strip():
        CHECKPOINTER.delete_thread(thread_id.strip())

def _normalizar_identificador(valor: str) -> str:
    normalizado = valor.strip().replace(" ", "-")
    normalizado = _CARACTERES_INVALIDOS.sub("-", normalizado)
    return normalizado.strip("-")