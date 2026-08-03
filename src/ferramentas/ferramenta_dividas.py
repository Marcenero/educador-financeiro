from __future__ import annotations

from typing import Any

from langchain.tools import BaseTool, tool

from data_loader import carregar_contexto_cliente
from servicos.servico_dividas import (
    calcular_resumo_dividas,
    identificar_divida_maior_taxa,
    listar_dividas_ordenadas_por_taxa,
)

def criar_ferramentas_dividas(cliente_id: str) -> list[BaseTool]:
    """Cria ferramentas de dívidas vinculadas ao cliente selecionado"""

    @tool
    # Consulta saldo devedor, parcelas mensais e renda comprometida
    def consultar_resumo_dividas() -> dict[str, Any]:
        contexto = carregar_contexto_cliente(cliente_id)
        resultado = calcular_resumo_dividas(
            dividas=contexto.dividas,
            renda_mensal_media=contexto.cliente.renda.renda_mensal_media,
        )
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "dividas.json e clientes.json",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Lista as dívidas da maior para a menor taxa mensal conhecida
    def consultar_dividas_por_taxa() -> dict[str, Any]:
        contexto = carregar_contexto_cliente(cliente_id)
        return {
            "cliente_id": cliente_id,
            "dividas": listar_dividas_ordenadas_por_taxa(contexto.dividas),
            "fonte": "dividas.json",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    # Identifica a dívida ativa com a maior taxa mensal conhecida
    def consultar_divida_com_maior_taxa() -> dict[str, Any]:
        contexto = carregar_contexto_cliente(cliente_id)
        return {
            "cliente_id": cliente_id,
            "divida_maior_taxa": identificar_divida_maior_taxa(contexto.dividas),
            "fonte": "dividas.json",
            "tipo_resultado": "calculo_deterministico",
        }

    return [
        consultar_resumo_dividas,
        consultar_dividas_por_taxa,
        consultar_divida_com_maior_taxa
    ]