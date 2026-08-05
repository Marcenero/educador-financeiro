from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, tool

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


def criar_ferramentas_transacoes(
    cliente_id: str,
) -> list[BaseTool]:
    """Cria ferramentas de transações vinculadas a um único cliente."""

    @tool
    def consultar_resumo_financeiro(
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta entradas, saídas, saldo e taxa de poupança do cliente.

        Use esta ferramenta quando o usuário perguntar sobre o resumo
        financeiro geral ou sobre o saldo em determinado período.
        As datas devem ser informadas no formato AAAA-MM-DD.
        """
        data_inicial = data_inicial or None
        data_final = data_final or None

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
    def consultar_gastos_por_categoria(
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta o total de despesas agrupadas por categoria.

        Use esta ferramenta para identificar as categorias nas quais
        o cliente mais gastou. As datas são opcionais e devem usar o
        formato AAAA-MM-DD.
        """
        data_inicial = data_inicial or None
        data_final = data_final or None

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
    def consultar_gasto_de_categoria(
        categoria: str,
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta quanto o cliente gastou em uma categoria específica.

        Use esta ferramenta quando o usuário mencionar uma categoria,
        como alimentação, transporte, moradia, saúde ou lazer.
        As datas são opcionais e devem usar o formato AAAA-MM-DD.
        """
        data_inicial = data_inicial or None
        data_final = data_final or None

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
    def consultar_maiores_gastos(
        quantidade: int = 5,
        data_inicial: str | None = None,
        data_final: str | None = None,
    ) -> dict[str, Any]:
        """
        Lista as maiores despesas individuais do cliente.

        Use esta ferramenta para responder quais foram os maiores
        gastos do período. A quantidade deve estar entre 1 e 20.
        As datas são opcionais e devem usar o formato AAAA-MM-DD.
        """
        data_inicial = data_inicial or None
        data_final = data_final or None

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
    def consultar_gastos_recorrentes() -> dict[str, Any]:
        """
        Consulta as despesas recorrentes do cliente.

        Use esta ferramenta para listar pagamentos que se repetem e
        apresentar o total, a média e o número de ocorrências.
        """
        data_inicial = data_inicial or None
        data_final = data_final or None

        transacoes = carregar_transacoes_dataframe(cliente_id)

        return {
            "cliente_id": cliente_id,
            "gastos_recorrentes": listar_gastos_recorrentes(
                transacoes
            ),
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    def consultar_despesas_essenciais() -> dict[str, Any]:
        """
        Calcula o total e o percentual das despesas essenciais.

        Use esta ferramenta para analisar quanto dos gastos do cliente
        está relacionado a necessidades essenciais.
        """
        transacoes = carregar_transacoes_dataframe(cliente_id)

        resultado = calcular_percentual_despesas_essenciais(
            transacoes
        )

        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "transacoes.csv",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    def consultar_comparacao_mensal() -> dict[str, Any]:
        """
        Compara entradas, saídas e saldo do cliente mês a mês.

        Use esta ferramenta para identificar evolução, melhora ou piora
        da situação financeira ao longo dos meses.
        """
        transacoes = carregar_transacoes_dataframe(cliente_id)

        return {
            "cliente_id": cliente_id,
            "comparacao_mensal": comparar_meses(
                transacoes
            ),
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