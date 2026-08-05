from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, AIMessage

from model_config import criar_modelo_ollama
from prompts import SYSTEM_PROMPT
from ferramentas.toolkit import criar_ferramentas_cliente

from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)

from seguranca import (
    ErroSeguranca,
    validar_entrada_usuario,
    validar_saida_agente,
)

class ErroAgenteFinanceiro(RuntimeError):
    """Erro ao criar ou executar o agente financeiro."""

def criar_agente_financeiro(
    cliente_id: str,
):
    if not cliente_id or not cliente_id.strip():
        raise ValueError(
            "cliente_id deve ser informado."
        )

    modelo = criar_modelo_ollama()
    ferramentas = criar_ferramentas_cliente(
        cliente_id
    )

    return create_agent(
        model=modelo,
        tools=ferramentas,
        system_prompt=SYSTEM_PROMPT,
        name=f"finguia-{cliente_id.lower()}",
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=6,
                exit_behavior="end",
            ),
            ToolCallLimitMiddleware(
                run_limit=6,
                exit_behavior="continue",
            ),
        ],
    )

def _converter_conteudo_em_texto(
    conteudo: Any,
) -> str:
    """Converte o conteúdo de uma mensagem para texto."""

    if isinstance(conteudo, str):
        return conteudo.strip()

    if isinstance(conteudo, list):
        partes: list[str] = []

        for bloco in conteudo:
            if isinstance(bloco, str):
                texto = bloco.strip()

                if texto:
                    partes.append(texto)

            elif isinstance(bloco, dict):
                texto = bloco.get("text")

                if isinstance(texto, str):
                    texto = texto.strip()

                    if texto:
                        partes.append(texto)

        return "\n".join(partes).strip()

    return ""

def extrair_resposta_final(
    resultado: dict[str, Any],
) -> str:
    """
    Retorna a última resposta textual não vazia do modelo.
    """
    mensagens = resultado.get("messages", [])

    if not mensagens:
        raise ErroAgenteFinanceiro(
            "O agente não retornou nenhuma mensagem."
        )

    for mensagem in reversed(mensagens):
        if not isinstance(mensagem, AIMessage):
            continue

        # Ignora AIMessage usada apenas para chamar ferramenta.
        if getattr(mensagem, "tool_calls", None):
            continue

        resposta = _converter_conteudo_em_texto(
            mensagem.content
        )

        if resposta:
            return resposta

    raise ErroAgenteFinanceiro(
        "O agente não produziu uma resposta textual final."
    )

def executar_pergunta(
    cliente_id: str,
    pergunta: str,
) -> str:
    pergunta_validada = validar_entrada_usuario(
        pergunta=pergunta,
        cliente_id=cliente_id,
    )

    agente = criar_agente_financeiro(cliente_id)

    try:
        resultado = agente.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": pergunta_validada,
                    }
                ]
            }
        )

        resposta_final = extrair_resposta_final(
            resultado
        )

        """
        print(
            "Resposta extraída:",
            repr(resposta_final),
        )
        """

        resposta_validada = validar_saida_agente(
            resposta=resposta_final,
            resultado=resultado,
            cliente_id=cliente_id,
        )

        return resposta_validada

    except ErroSeguranca:
        raise

    except ErroAgenteFinanceiro:
        raise

    except Exception as erro:
        raise ErroAgenteFinanceiro(
            f"Não foi possível executar o agente: {erro}"
        ) from erro

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