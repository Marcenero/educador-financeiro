from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import ToolMessage

class ErroSeguranca(ValueError):
    """Erro causado por uma violação das regras de segurança."""

PADRAO_CLIENTE = re.compile(
    r"\bCLI-\d{4}\b",
    flags=re.IGNORECASE,
)

PADROES_RACIOCINIO_INTERNO = [
    re.compile(r"<think>.*?</think>", flags=re.DOTALL | re.IGNORECASE),
    re.compile(
        r"^\s*okay,\s*the user",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"^\s*first,\s*i need",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"^\s*let me think",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"^\s*(analysis|reasoning):",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
]

PADROES_RECOMENDACAO_PERIGOSA = [
    re.compile(
        r"\b(você deve|eu recomendo|recomendo que você)\s+"
        r"(comprar|vender|investir)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\b(compre|venda|invista)\s+"
        r"(agora|imediatamente|todo|toda)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\b(lucro|retorno)\s+garantido\b",
        flags=re.IGNORECASE,
    ),
]

def validar_entrada_usuario(
    pergunta: str,
    cliente_id: str,
) -> str:
    """Valida a pergunta antes que ela seja enviada ao agente"""
    if not pergunta or not pergunta.strip():
        raise ErroSeguranca("A pergunta não pode estar vazia.")

    pergunta = pergunta.strip()

    if len(pergunta) > 2000:
        raise ErroSeguranca("A pergunta ultrapassa o limite de 2.000 caracteres.")

    cliente_atual = cliente_id.upper()

    clientes_mencionados = {
        identificador.upper()
        for identificador in PADRAO_CLIENTE.findall(pergunta)
    }

    clientes_nao_autorizados = (
        clientes_mencionados - {cliente_atual}
    )

    if clientes_nao_autorizados:
        raise ErroSeguranca("Não é permitido consultar dados de outro cliente.")

    return pergunta

def validar_saida_agente(
    resposta: str,
    resultado: dict[str, Any],
    cliente_id: str,
) -> str:
    if not isinstance(resposta, str):
        raise ErroSeguranca("A resposta do agente possui formato inválido.")

    resposta = resposta.strip()

    if not resposta:
        raise ErroSeguranca("O agente retornou uma resposta vazia.")

    resposta = _remover_bloco_think(resposta)

    if not resposta:
        raise ErroSeguranca("A resposta ficou vazia após a remoção do raciocínio interno.")

    for padrao in PADROES_RACIOCINIO_INTERNO:
        if padrao.search(resposta):
            raise ErroSeguranca("A resposta contém raciocínio interno do modelo.")

    _validar_isolamento_cliente(
        resposta=resposta,
        cliente_id=cliente_id,
    )

    _validar_recomendacao_financeira(
        resposta
    )

    fontes = extrair_fontes_ferramentas(
        resultado
    )

    if fontes and "fonte:" not in resposta.lower():
        resposta = adicionar_fontes(
            resposta=resposta,
            fontes=fontes,
        )

    return resposta

def _remover_bloco_think(
    resposta: str,
) -> str:
    """Remove blocos explícitos <think>...</think>"""
    resposta_limpa = re.sub(
        r"<think>.*?</think>",
        "",
        resposta,
        flags=re.DOTALL | re.IGNORECASE,
    )

    return resposta_limpa.strip()

def _validar_isolamento_cliente(
    resposta: str,
    cliente_id: str,
) -> None:
    cliente_atual = cliente_id.upper()

    clientes_mencionados = {
        identificador.upper()
        for identificador in PADRAO_CLIENTE.findall(resposta)
    }

    clientes_nao_autorizados = (
        clientes_mencionados - {cliente_atual}
    )

    if clientes_nao_autorizados:
        raise ErroSeguranca("A resposta contém dados ou identificadores de outro cliente.")

def _validar_recomendacao_financeira(
    resposta: str
) -> None:
    for padrao in PADROES_RECOMENDACAO_PERIGOSA:
        if padrao.search(resposta):
            raise ErroSeguranca("A resposta contém uma recomendação financeira inadequada.")

def extrair_fontes_ferramentas(
    resultado: dict[str, Any],
) -> list[str]:
    """Extrai os campos 'fonte' retornados pelas ferramentas"""
    fontes: list[str] = []

    for mensagem in resultado.get("messages", []):
        if not isinstance(mensagem, ToolMessage):
            continue

        conteudo = mensagem.content

        if isinstance(conteudo, dict):
            fonte = conteudo.get("fonte")

            if fonte:
                fontes.append(str(fonte))

        elif isinstance(conteudo, str):
            fontes.extend(_extrair_fontes_de_texto(conteudo))

    return list(dict.fromkeys(fontes))

def _extrair_fontes_de_texto(
    conteudo: str
) -> list[str]:
    """
    Procura campos como:
    "fonte": "transacoes.csv"
    """
    padrao = re.compile(
        r"""["']fonte["']\s*:\s*["']([^"']+)["']""",
        flags=re.IGNORECASE,
    )

    return [
        fonte.strip()
        for fonte in padrao.findall(conteudo)
        if fonte.strip()
    ]

def adicionar_fontes(
    resposta: str,
    fontes: list[str],
) -> str:
    fontes_formatadas = "; ".join(fontes)

    return (
        f"{resposta.rstrip()}\n\n"
        f"Fonte: {fontes_formatadas}."
    )

def validar_entrada_visitante(
    pergunta: str,
) -> str:
    """Valida perguntas realizadas pelo perfil visitante."""
    if not pergunta or not pergunta.strip():
        raise ErroSeguranca(
            "A pergunta não pode estar vazia."
        )

    pergunta = pergunta.strip()

    if len(pergunta) > 2000:
        raise ErroSeguranca(
            "A pergunta ultrapassa o limite de "
            "2.000 caracteres."
        )

    if PADRAO_CLIENTE.search(pergunta):
        raise ErroSeguranca(
            "O perfil visitante não pode consultar "
            "identificadores de clientes."
        )

    return pergunta