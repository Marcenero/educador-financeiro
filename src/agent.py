from __future__ import annotations

from time import perf_counter
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain_core.messages import AIMessage

from auditoria import registrar_interacao
from ferramentas.toolkit import criar_ferramentas_cliente
from memoria import (
    CHECKPOINTER,
    criar_configuracao,
    criar_thread_temporaria,
)
from model_config import criar_modelo_ollama
from prompts import (
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_VISITANTE,
)
from seguranca import (
    ErroSeguranca,
    validar_entrada_usuario,
    validar_entrada_visitante,
    validar_saida_agente,
)

class ErroAgenteFinanceiro(RuntimeError):
    """Erro ao criar ou executar o agente financeiro."""

def criar_agente_financeiro(
    cliente_id: str,
):
    """Cria um agente com memória e ferramentas do cliente"""
    if not cliente_id or not cliente_id.strip():
        raise ValueError("cliente_id deve ser informado.")

    return create_agent(
        model=criar_modelo_ollama(),
        tools=criar_ferramentas_cliente(cliente_id),
        system_prompt=SYSTEM_PROMPT,
        name=f"finguia-{cliente_id.lower()}",
        checkpointer=CHECKPOINTER,
        middleware=[
            ModelCallLimitMiddleware(run_limit=8),
            ToolCallLimitMiddleware(run_limit=8),
        ]
    )

def criar_agente_visitante():
    """Cria um agente educativo sem acesso aos dados dos clientes."""
    return create_agent(
        model=criar_modelo_ollama(),
        tools=[],
        system_prompt=SYSTEM_PROMPT_VISITANTE,
        name="finguia-visitante",
        checkpointer=CHECKPOINTER,
        middleware=[
            ModelCallLimitMiddleware(run_limit=8),
        ],
    )

def executar_pergunta(
    cliente_id: str,
    pergunta: str,
    thread_id: str | None = None,
) -> str:
    """Executa uma pergunta com memória vinculada ao cliente."""
    conversa_id = (
        thread_id
        or criar_thread_temporaria(cliente_id)
    )

    return _executar(
        agente=criar_agente_financeiro(cliente_id),
        perfil_id=cliente_id,
        tipo_perfil="cliente",
        pergunta=pergunta,
        thread_id=conversa_id,
        validador_entrada=lambda texto: validar_entrada_usuario(
            pergunta=texto,
            cliente_id=cliente_id,
        ),
        cliente_id_seguranca=cliente_id,
    )


def executar_pergunta_visitante(
    pergunta: str,
    thread_id: str | None = None,
) -> str:
    """Executa uma pergunta educativa com memória de visitante."""
    conversa_id = (
        thread_id
        or criar_thread_temporaria("VISITANTE")
    )

    return _executar(
        agente=criar_agente_visitante(),
        perfil_id="VISITANTE",
        tipo_perfil="visitante",
        pergunta=pergunta,
        thread_id=conversa_id,
        validador_entrada=validar_entrada_visitante,
        cliente_id_seguranca="VISITANTE",
    )

def _executar(
    *,
    agente,
    perfil_id: str,
    tipo_perfil: str,
    pergunta: str,
    thread_id: str,
    validador_entrada,
    cliente_id_seguranca: str,
) -> str:
    inicio = perf_counter()
    resultado: dict[str, Any] | None = None

    try:
        pergunta_validada = validador_entrada(pergunta)

        resultado = agente.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": pergunta_validada,
                    }
                ]
            },
            config=criar_configuracao(thread_id),
        )

        resposta_final = extrair_resposta_final(resultado)

        resposta_validada = validar_saida_agente(
            resposta=resposta_final,
            resultado=resultado,
            cliente_id=cliente_id_seguranca,
        )

        registrar_interacao(
            perfil_id=perfil_id,
            tipo_perfil=tipo_perfil,
            thread_id=thread_id,
            pergunta=pergunta_validada,
            resposta=resposta_validada,
            status="sucesso",
            duracao_ms=_duracao_ms(inicio),
            resultado=resultado,
        )

        return resposta_validada

    except ErroSeguranca as erro:
        registrar_interacao(
            perfil_id=perfil_id,
            tipo_perfil=tipo_perfil,
            thread_id=thread_id,
            pergunta=pergunta,
            status="bloqueado",
            duracao_ms=_duracao_ms(inicio),
            resultado=resultado,
            erro=str(erro),
        )
        raise

    except ErroAgenteFinanceiro as erro:
        registrar_interacao(
            perfil_id=perfil_id,
            tipo_perfil=tipo_perfil,
            thread_id=thread_id,
            pergunta=pergunta,
            status="erro",
            duracao_ms=_duracao_ms(inicio),
            resultado=resultado,
            erro=str(erro),
        )
        raise

    except Exception as erro:
        registrar_interacao(
            perfil_id=perfil_id,
            tipo_perfil=tipo_perfil,
            thread_id=thread_id,
            pergunta=pergunta,
            status="erro",
            duracao_ms=_duracao_ms(inicio),
            resultado=resultado,
            erro=f"{type(erro).__name__}: {erro}",
        )

        raise ErroAgenteFinanceiro(
            "Não foi possível executar o agente: "
            f"{erro}"
        ) from erro

def extrair_resposta_final(
    resultado: dict[str, Any],
) -> str:
    """Retorna a última resposta textual não vazia do modelo."""
    mensagens = resultado.get("messages", [])

    if not mensagens:
        raise ErroAgenteFinanceiro(
            "O agente não retornou nenhuma mensagem."
        )

    for mensagem in reversed(mensagens):
        if not isinstance(mensagem, AIMessage):
            continue

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
            elif isinstance(bloco, dict):
                texto = str(
                    bloco.get("text", "")
                ).strip()
            else:
                texto=""

            if texto:
                partes.append(texto)

        return "\n".join(partes).strip()

    return ""

def _duracao_ms(inicio: float) -> int:
    return round((perf_counter() - inicio) * 1000)