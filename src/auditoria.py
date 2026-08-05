from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


ARQUIVO_PADRAO = (
    Path(__file__).resolve().parent.parent
    / "logs"
    / "interacoes.jsonl"
)

_LOCK = threading.Lock()


def conteudo_deve_ser_registrado() -> bool:
    """Lê a preferência de auditoria definida no ambiente."""
    valor = os.getenv("AUDITORIA_INCLUIR_CONTEUDO", "true")
    return valor.strip().lower() in {"1", "true", "sim", "yes"}


def registrar_interacao(
    *,
    perfil_id: str,
    tipo_perfil: str,
    thread_id: str,
    pergunta: str,
    status: str,
    duracao_ms: int,
    resposta: str | None = None,
    resultado: dict[str, Any] | None = None,
    erro: str | None = None,
    caminho: Path | None = None,
    incluir_conteudo: bool | None = None,
) -> dict[str, Any]:
    """Registra uma interação em JSON Lines."""
    registrar_conteudo = (
        conteudo_deve_ser_registrado()
        if incluir_conteudo is None
        else incluir_conteudo
    )

    registro: dict[str, Any] = {
        "evento_id": uuid4().hex,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "perfil_id": perfil_id,
        "tipo_perfil": tipo_perfil,
        "thread_id": thread_id,
        "status": status,
        "duracao_ms": max(int(duracao_ms), 0),
        "tamanho_pergunta": len(pergunta),
        "tamanho_resposta": len(resposta or ""),
        "ferramentas": extrair_ferramentas(resultado),
        "fontes": extrair_fontes(resultado),
    }

    if registrar_conteudo:
        registro["pergunta"] = pergunta
        registro["resposta"] = resposta

    if erro:
        registro["erro"] = erro

    arquivo = caminho or ARQUIVO_PADRAO
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    linha = json.dumps(registro, ensure_ascii=False)

    with _LOCK:
        with arquivo.open("a", encoding="utf-8") as destino:
            destino.write(linha + "\n")

    return registro


def extrair_ferramentas(
    resultado: dict[str, Any] | None,
) -> list[str]:
    """Extrai os nomes das ferramentas chamadas pelo agente."""
    if not resultado:
        return []

    ferramentas: list[str] = []

    for mensagem in resultado.get("messages", []):
        chamadas = getattr(mensagem, "tool_calls", None)

        if not chamadas:
            continue

        for chamada in chamadas:
            if isinstance(chamada, dict):
                nome = chamada.get("name")
            else:
                nome = getattr(chamada, "name", None)

            if nome:
                ferramentas.append(str(nome))

    return list(dict.fromkeys(ferramentas))


def extrair_fontes(
    resultado: dict[str, Any] | None,
) -> list[str]:
    """Extrai campos fonte dos retornos das ferramentas."""
    if not resultado:
        return []

    fontes: list[str] = []

    for mensagem in resultado.get("messages", []):
        if type(mensagem).__name__ != "ToolMessage":
            continue

        conteudo = getattr(mensagem, "content", None)
        dados: Any = conteudo

        if isinstance(conteudo, str):
            try:
                dados = json.loads(conteudo)
            except json.JSONDecodeError:
                continue

        if isinstance(dados, dict):
            fonte = dados.get("fonte")
            if fonte:
                fontes.append(str(fonte))

    return list(dict.fromkeys(fontes))