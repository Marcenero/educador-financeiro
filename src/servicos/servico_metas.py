from __future__ import annotations

import math
from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from schemas import MetaFinanceira

class ErroServicoMetas(ValueError):
    """Erro de validação ou cálculo relacionado às metas"""

def calcular_progresso_meta(
    meta: MetaFinanceira,
) -> dict[str, Any]:
    percentual = meta.valor_atual * meta.valor_alvo * 100
    valor_faltante = max(
        meta.valor_alvo - meta.valor_atual,
        0,
    )

    return {
        "meta_id": meta.meta_id,
        "nome": meta.nome,
        "categoria": meta.categoria,
        "valor_alvo": round(meta.valor_alvo, 2),
        "valor_atual": round(meta.valor_atual, 2),
        "valor_faltante": round(meta.valor_faltante, 2),
        "percentual_concluido": round(
            min(percentual, 100),
            2,
        ),
        "prazo": meta.prazo,
        "prioridade": meta.prioridade.value,
        "status": meta.status.value,
    }

def listar_progresso_metas(
    metas: list[MetaFinanceira],
) -> list[dict[str, Any]]:
    return [
        calcular_progresso_meta(meta)
        for meta in metas
    ]

def buscar_meta(
    metas: list[MetaFinanceira],
    meta_id: str,
) -> MetaFinanceira:
    for meta in metas:
        if meta.meta_id == meta_id:
            return meta

    raise ErroServicoMetas(f"Meta não encontrada:{meta_id}.")

def simular_meta_sem_rentabilidade(
    valor_meta: float,
    valor_atual: float,
    aporte_mensal: float,
    data_referencia: date | None = None,
) -> dict[str, Any]:
    if valor_meta <= 0:
        raise ErroServicoMetas("valor_meta deve ser maior que zero")

    if valor_atual < 0:
         raise ErroServicoMetas("valor_atual não pode ser negativo.")

    if aporte_mensal <= 0:
         raise ErroServicoMetas("aporte_mensal deve ser maior que zero.")

    referencia = data_referencia or date.today()
    faltante = max(valor_meta - valor_atual, 0)
    meses = (
        math.ceil(faltante / aporte_mensal)
        if faltante > 0
        else 0
    )

    data_estimada = referencia + relativedelta(months=meses)

    return {
        "valor_meta": round(valor_meta, 2),
        "valor_atual": round(valor_atual, 2),
        "valor_faltante": round(faltante, 2),
        "aporte_mensal": round(aporte_mensal, 2),
        "meses_estimados": meses,
        "data_estimada": data_estimada.isoformat(),
        "considera_rentabilidade": False,
        "aviso": ("Simulação educativa baseada em aporte mensal constante.")
    }

def calcular_aporte_mensal_necessario(
    valor_meta: float,
    valor_atual: float,
    meses_restantes: int,
) -> dict[str, float | int]:
    if valor_meta <= 0:
        raise ErroServicoMetas("valor_meta deve ser maior que zero.")

    if valor_atual < 0:
         raise ErroServicoMetas("valor_atual não pode ser negativo.")

    if meses_restantes <= 0:
         raise ErroServicoMetas("meses_restantes deve ser maior que zero.")

    faltante = max(valor_meta - valor_atual, 0)
    aporte = faltante / meses_restantes

    return {
        "valor_faltante": round(faltante, 2),
        "meses_restantes": meses_restantes,
        "aporte_mensal_necessario": round(aporte, 2),
    }