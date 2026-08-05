from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage

from model_config import criar_modelo_ollama
from prompts import SYSTEM_PROMPT
from ferramentas.toolkit import criar_ferramentas_cliente

class ErroAgenteFinanceiro(RuntimeError):
    """Erro ao criar ou executar o agente financeiro."""

def criar_agente_financeiro(cliente_id: str):
    if not cliente_id or not cliente_id.strip():
        raise ValueError("cliente_id deve ser informado.")

    modelo = criar_modelo_ollama()
    ferramentas = criar_ferramentas_cliente(cliente_id)

    return create_agent(
        model=modelo,
        tools=ferramentas,
        system_prompt=SYSTEM_PROMPT,
        name=f"finguia-{cliente_id.lower()}",
    )

def extrair_resposta_final(resultado: dict[str, Any]) -> str:
    mensagens = resultado.get("messages")

    if not mensagens:
        raise ErroAgenteFinanceiro("O agente não retornou uma mensagem.")

    conteudo = getattr(mensagens[-1], "content", "")

    if isinstance(conteudo, str):
        resposta = conteudo.strip()
    elif isinstance(conteudo, list):
        partes: list[str] = []

        for bloco in conteudo:
            if isinstance(bloco, str):
                partes.append(bloco)
            elif isinstance(bloco, dict) and bloco.get("text"):
                partes.append(str(bloco["text"]))

        resposta = "\n".join(partes).strip()
    else:
        resposta = str(conteudo or "").strip()

    if not resposta:
        raise ErroAgenteFinanceiro("O agente retornou uma resposta final vazia.")

    return resposta

def executar_pergunta(cliente_id: str, pergunta: str) -> str:
    if not pergunta or not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    agente = criar_agente_financeiro(cliente_id)

    try:
        resultado = agente.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": pergunta.strip()
                    }
                ]
            }
        )
    except Exception as erro:
        raise ErroAgenteFinanceiro(
            f"Não foi possível executar o agente: {erro}"
        ) from erro

    return extrair_resposta_final(resultado)

def executar_conversa(
    agente,
    mensagens: Sequence[BaseMessage | dict[str, Any]],
) -> dict[str, Any]:
    if not mensagens:
        raise ValueError("O histórico de mensagens não pode estar vazio.")

    try:
        return agente.invoke({"messages": list(mensagens)})
    except Exception as erro:
        raise ErroAgenteFinanceiro(
            f"Não foi possível executar a conversa: {erro}"
        ) from erro