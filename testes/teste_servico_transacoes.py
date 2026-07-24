from __future__ import annotations

import pandas as pd
import pytest

from data_loader import carregar_transacoes_dataframe
from servicos.servico_transacoes import (
    ErroServicoTransacoes,
    calcular_gastos_por_categoria,
    calcular_percentual_despesas_essenciais,
    calcular_resumo_financeiro,
    comparar_meses,
    consultar_gastos_categoria,
    filtrar_periodo,
    listar_gastos_recorrentes,
    listar_maiores_gastos,
)

def teste_resumo_financeiro_joao(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    resultado = calcular_resumo_financeiro(df)

    assert resultado["entradas"] == 30900.0
    assert resultado["saidas"] == 21351.61
    assert resultado["saldo"] == 9548.39
    assert resultado["quantidade_transacoes"] == 80

def teste_resumo_financeiro_mariana(cliente_mariana_id):
    df = carregar_transacoes_dataframe(cliente_mariana_id)

    resultado = calcular_resumo_financeiro(df)

    assert resultado["entradas"] == 27100.0
    assert resultado["saidas"] == 18702.94
    assert resultado["saldo"] == 8397.06


def teste_resumo_financeiro_carlos_negativo(cliente_carlos_id):
    df = carregar_transacoes_dataframe(cliente_carlos_id)

    resultado = calcular_resumo_financeiro(df)

    assert resultado["entradas"] == 41900.0
    assert resultado["saidas"] == 47303.57
    assert resultado["saldo"] == -5403.57

def teste_filtrar_periodo_reduz_transacoes(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    janeiro = filtrar_periodo(
        df,
        data_inicial="2026-01-01",
        data_final="2026-01-31",
    )

    assert not janeiro.empty
    assert janeiro["data"].min() >= pd.Timestamp("2026-01-01")
    assert janeiro["data"].max() <= pd.Timestamp("2026-01-31")
    assert len(janeiro) < len(df)

def teste_periodo_invertido_gera_erro(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    with pytest.raises(
        ErroServicoTransacoes,
        match="data_inicial",
    ):
        filtrar_periodo(
            df,
            data_inicial="2026-06-01",
            data_final="2026-01-01",
        )

def teste_gastos_por_categoria(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    resultado = calcular_gastos_por_categoria(df)

    assert "alimentacao" in resultado
    assert "moradia" in resultado
    assert resultado["alimentacao"] > 0
    assert resultado["moradia"] > 0

def teste_consultar_categoria_existente(cliente_mariana_id):
    df = carregar_transacoes_dataframe(cliente_mariana_id)

    resultado = consultar_gastos_categoria(
        df,
        categoria="alimentacao",
    )

    assert resultado["categoria"] == "alimentacao"
    assert resultado["valor_total"] > 0
    assert resultado["quantidade_transacoes"] > 0

def teste_consultar_categoria_inexistente_retorna_zero(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    resultado = consultar_gastos_categoria(
        df,
        categoria="categoria_inexistente",
    )

    assert resultado["valor_total"] == 0.0
    assert resultado["quantidade_transacoes"] == 0
    assert resultado["transacoes"] == []

def teste_categoria_vazia_gera_erro(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    with pytest.raises(
        ErroServicoTransacoes,
        match="categoria",
    ):
        consultar_gastos_categoria(df, categoria=" ")

def teste_listar_cinco_maiores_gastos(cliente_carlos_id):
    df = carregar_transacoes_dataframe(cliente_carlos_id)

    with pytest.raises(
            ErroServicoTransacoes,
            match="quantidade",
        ):
            listar_maiores_gastos(df, quantidade=0)

def teste_quantidades_maiores_gastos_invalida(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    with pytest.raises(
        ErroServicoTransacoes,
        match="quantidade"
    ):
        listar_maiores_gastos(df, quantidade=0)

def teste_gastos_recorrentes(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    resultado = listar_gastos_recorrentes(df)

    assert len(resultado) > 0
    assert all(item["ocorrencias"] >= 1 for item in resultado)
    assert any(item["descricao"] == "Aluguel" for item in resultado)

def teste_percentual_despesas_essenciais(cliente_joao_id):
    df = carregar_transacoes_dataframe(cliente_joao_id)

    resultado = calcular_percentual_despesas_essenciais(df)

    assert resultado["despesas_totais"] == 21351.61
    assert 0 <= resultado["percentual_essenciais"] <= 100

def teste_comparar_seis_meses(cliente_mariana_id):
    df = carregar_transacoes_dataframe(cliente_mariana_id)

    resultado = comparar_meses(df)

    assert len(resultado) == 6
    assert resultado[0]["mes"] == "2026-01"
    assert resultado[-1]["mes"] == "2026-06"

def teste_dataframe_sem_colunas_gera_erro():
    df = pd.DataFrame({"valor": [100]})

    with pytest.raises(
        ErroServicoTransacoes,
        match="Colunas ausentes",
    ):
        calcular_resumo_financeiro(df)