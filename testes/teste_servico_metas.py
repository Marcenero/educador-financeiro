from __future__ import annotations

from datetime import date

import pytest

from data_loader import carregar_contexto_cliente
from servicos.servico_metas import (
    ErroServicoMetas,
    buscar_meta,
    calcular_aporte_mensal_necessario,
    calcular_progresso_meta,
    listar_progresso_metas,
    simular_meta_sem_rentabilidade,
)

def teste_progresso_reserva_joao(cliente_joao_id):
    contexto = carregar_contexto_cliente(cliente_joao_id)
    meta = buscar_meta(contexto.metas, "META-0001")

    resultado = calcular_progresso_meta(meta)

    assert resultado["valor_alvo"] == 18000.0
    assert resultado["valor_atual"] == 10000.0
    assert resultado["valor_faltante"] == 8000.0
    assert resultado["percentual_concluido"] == 55.56

def teste_listar_duas_metas_por_cliente(cliente_mariana_id):
    contexto = carregar_contexto_cliente(cliente_mariana_id)

    resultado = listar_progresso_metas(contexto.metas)

    assert len(resultado) == 2
    assert all("percentual_concluido" in item for item in resultado)

def teste_buscar_meta_inexistente(cliente_joao_id):
    contexto = carregar_contexto_cliente(cliente_joao_id)

    with pytest.raises(
        ErroServicoMetas,
        match="Meta não encontrada",
    ):
        buscar_meta(contexto.metas, "META-9999")

def teste_simular_meta_sem_rentabilidade():
    resultado = simular_meta_sem_rentabilidade(
        valor_meta=15000,
        valor_atual=10000,
        aporte_mensal=500,
        data_referencia=date(2026, 7, 1),
    )

    assert resultado["valor_faltante"] == 5000.0
    assert resultado["meses_estimados"] == 10
    assert resultado["data_estimada"] == "2027-05-01"
    assert resultado["considera_rentabilidade"] is False

def teste_meta_ja_concluida_precisa_zero_meses():
    resultado = simular_meta_sem_rentabilidade(
        valor_meta=10000,
        valor_atual=12000,
        aporte_mensal=500,
        data_referencia=date(2026, 7, 1),
    )

    assert resultado["valor_faltante"] == 0.0
    assert resultado["meses_estimados"] == 0

@pytest.mark.parametrize(
    "valor_meta, valor_atual, aporte",
    [
        (0, 100, 50),
        (-1000, 100, 50),
        (1000, -1, 50),
        (1000, 100, 0),
        (1000, 100, -50),
    ],
)
def teste_simulacao_meta_valores_invalidos(
    valor_meta,
    valor_atual,
    aporte,
):
    with pytest.raises(ErroServicoMetas):
        simular_meta_sem_rentabilidade(
            valor_meta=valor_meta,
            valor_atual=valor_atual,
            aporte_mensal=aporte,
        )

def teste_calcular_aporte_mensal_necessario():
    resultado = calcular_aporte_mensal_necessario(
        valor_meta=18000,
        valor_atual=10000,
        meses_restantes=12,
    )

    assert resultado["valor_faltante"] == 8000.0
    assert resultado["aporte_mensal_necessario"] == 666.67

def teste_meses_restantes_invalido():
    with pytest.raises(
        ErroServicoMetas,
        match="meses_restantes",
    ):
        calcular_aporte_mensal_necessario(
            valor_meta=18000,
            valor_atual=10000,
            meses_restantes=0,
        )