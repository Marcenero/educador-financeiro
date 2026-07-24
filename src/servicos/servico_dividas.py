from __future__ import annotations

from typing import Any

from schemas import Divida

class ErroServicoDividas(ValueError):
    """Erro de validação ou cálculo relacionado às dívidas"""

def calcular_resumo_dividas(
    dividas: list[Divida],
    renda_mensal_media: float,
) -> dict[str, Any]:
    if renda_mensal_media < 0:
        raise ErroServicoDividas("renda_mensal_media não pode ser negativa.")

    ativas = [
        divida
        for divida in dividas
        if divida.status.value != "quitada"
    ]

    saldo_total = sum (
        divida.saldo_devedor
        for divida in ativas
    )

    parcelas_mensais = sum(
        divida.parcela_mensal
        for divida in ativas
    )

    comprometimento = (
        parcelas_mensais / renda_mensal_media * 100
        if renda_mensal_media > 0
        else None
    )

    return {
        "quantidade_dividas_ativas": len(ativas),
        "saldo_devedor_total": round(saldo_total, 2),
        "parcelas_mensais_total": round(
            parcelas_mensais,
            2,
        ),
        "comprometimento_renda_percentual": (
            round(comprometimento, 2)
            if comprometimento is not None
            else None
        ),
    }

def listar_dividas_ordenadas_por_taxa(
    dividas: list[Divida],
) -> list[dict[str, Any]]:
    ordenadas = sorted(
        dividas,
        key=lambda divida: (
            divida.taxa_mensal is None,
            -(divida.taxa_mensal or 0),
        ),
    )

    return [
        {
            "divida_id": divida.divida_id,
            "tipo": divida.tipo,
            "saldo_devedor": round(
                divida.saldo_devedor,
                2,
            ),
            "taxa_mensal_percentual": (
                round(divida.taxa_mensal * 100, 2)
                if divida.taxa_mensal is not None
                else None
            ),
            "parcelas_restantes": divida.parcelas_restantes,
            "parcela mensal": round(
                divida.parcela_mensal,
                2,
            ),
            "status": divida.status.value,
        }
        for divida in ordenadas
    ]

def identificar_divida_maior_taxa(
    dividas: list[Divida],
) -> dict[str, Any] | None:
    conhecidas = [
        divida
        for divida in dividas
        if divida.taxa_mensal is not None
        and divida.status.value != "quitada"
    ]

    if not conhecidas:
        return None

    divida = max(
        conhecidas,
        key=lambda item: item.taxa_mensal or 0,
    )

    return {
        "divida_id": divida.divida_id,
        "tipo": divida.tipo,
        "saldo_devedor": round(divida.saldo_devedor, 2),
        "taxa_mensal_percentual": round(
            (divida.taxa_mensal or 0) * 100,
            2,
        ),
        "observacao": (
            "A maior taxa é um critério ibjetivo de análise, "
            "não uma ordem automática de pagamento."
        ),
    }