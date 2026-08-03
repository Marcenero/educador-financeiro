from __future__ import annotations

from langchain.agents import create_agent

from model_config import criar_modelo_ollama
from prompts import SYSTEM_PROMPT
from ferramentas.toolkit import criar_ferramentas_cliente

def criar_agente(cliente_id: str):
    modelo = criar_modelo_ollama()

    ferramentas = criar_ferramentas_cliente(cliente_id)

    agente = create_agent(
        model=modelo,
        tools=ferramentas,
        system_prompt=SYSTEM_PROMPT,
    )

    return agente