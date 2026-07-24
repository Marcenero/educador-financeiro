from __future__ import annotations

from typing import Any

ORDEM_RISCO = {
    "baixo": 1,
    "medio": 2,
    "médio": 2,
    "alto": 3,
}

class ErroServicoProdutos(ValueError):
    """Erro de validação ou busca relacionado aos produtos"""

def buscar_produtos_compativeis(
    produtos: list[dict[str, Any]],
    risco_maximo: str,
    aporte_disponivel: float,
    objetivo: str | None = None,
) -> list[dict[str, Any]]:
    risco_normalizado = risco_maximo.strip().lower()

    if risco_normalizado not in ORDEM_RISCO:
        raise ErroServicoProdutos("risco_maximo deve ser baixo, medio ou alto.")

    if aporte_disponivel < 0:
        raise ErroServicoProdutos("aporte_disponivel não pode ser negativo.")

    limite= ORDEM_RISCO[risco_normalizado]
    objetivo_normalizado = (
        objetivo.strip().lower()
        if objetivo
        else None
    )

    encontrados = []

    for produto in produtos:
        risco_produto = str(
            produto.get("risco", "")
        ).strip().lower()

        if risco_produto not in ORDEM_RISCO:
            continue

        aporte_minimo = float(
            produto.get("aporte_minimo", 0)
        )

        if ORDEM_RISCO[risco_produto] > limite:
            continue

        if aporte_minimo > aporte_disponivel:
            continue

        indicado_para = str(
            produto.get("indicado_para", "")
        ).lower()

        if objetivo_normalizado:
            termos = objetivo_normalizado.split()

            if not any(
                termo in indicado_para
                for termo in termos
            ):
                continue

        encontrados.append(
            {
                "nome": produto.get("nome"),
                "categoria": produto.get("caategoria"),
                "risco": produto.get("risco"),
                "aporte_minimo": aporte_minimo,
                "indicado_para": produto.get("indicado_para"),
                "carater_educativo": True,
            }
        )

    return encontrados