from __future__ import annotations

from typing import Any

from langchain.tools import BaseTool, tool

from data_loader import carregar_transacoes_dataframe
from servicos.servico_transacoes import (
    calcular_gastos_por_categoria,
    calcular_percentual_despesas_essenciais,
    calcular_resumo_financeiro,
    comparar_meses,
    consultar_gastos_categoria,
    listar_gastos_recorrentes,
    listar_maiores_gastos,
)

def criar_ferramentas_transacoes(cliente_id: str) -> list[BaseTool]:
    """Cria ferramentas de transações vinculadas a um único cliente"""

    @tool
    # Consulta entadas, saídas,saldo e taxa de poupança do cliente selecionado
    def consultar_resumo_financeiro(
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        resultado = calcular_resumo_financeiro(
            transacoes=transacoes,
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Consulta o total de despesas agrupada por categoria
    def consultar_gastos_por_categoria(
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        categorias = calcular_gastos_por_categoria(
            transacoes=transacoes,
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return {
            "cliente_id": cliente_id,
            "categorias": categorias,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Consulta quanto o cliente gastou em uma categoria específica
    def consultar_gasto_de_categoria(
        categoria: str,
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        resultado = consultar_gastos_categoria(
            transacoes=transacoes,
            categoria=categoria,
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Lista as maiores despesas individuais do cliente, entre 1 e 20 itens
    def consultar_maiores_gastos(
        quantidade: int = 5,
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        gastos = listar_maiores_gastos(
            transacoes=transacoes,
            quantidade=quantidade,
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return {
            "cliente_id": cliente_id,
            "maiores_gastos": gastos,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Lista despesas recorrente, com total, média e ocorrências
    def consultar_gastos_recorrentes() -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        return {
            "cliente_id": cliente_id,
            "gastos_recorrentes": listar_gastos_recorrentes(transacoes),
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Calcula o total e o percentual das despesas essenciais
    def consultar_despesas_essenciais() -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        resultado = calcular_percentual_despesas_essenciais(transacoes)
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Compara entradas, saídas e saldo do cliente mês a mês
    def consultar_comparacao_mensal() -> dict[str, Any]:
        transacoes = carregar_transacoes_dataframe(cliente_id)
        return {
            "cliente_id": cliente_id,
            "comparacao_mensal": comparar_meses(transacoes),
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    return [
        consultar_resumo_financeiro,
        consultar_gastos_por_categoria,
        consultar_gasto_de_categoria,
        consultar_maiores_gastos,
        consultar_gastos_recorrentes,
        consultar_despesas_essenciais,
        consultar_comparacao_mensal,
    ]