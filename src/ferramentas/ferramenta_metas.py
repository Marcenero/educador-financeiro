from __future__ import annotations

from datetime import date
from typing import Any
from langchain_core.tools import BaseTool, tool

from data_loader import carregar_metas_cliente
from servicos.servico_metas import (
    buscar_meta,
    calcular_aporte_mensal_necessario,
    calcular_progresso_meta,
    listar_progresso_metas,
    simular_meta_sem_rentabilidade,
)

def criar_ferramentas_metas(cliente_id: str) -> list[BaseTool]:
    """Cria ferramentas de metas vinculadas ao cliente selecionado."""

    @tool
    def consultar_metas_financeiras() -> dict[str, Any]:
        """
        Lista metas, progresso, valor faltante, prazo e prioridade.

        Use esta ferramenta para consultar as metas financeiras do cliente.
        """
        metas = carregar_metas_cliente(cliente_id)
        return {
            "cliente_id": cliente_id,
            "metas": listar_progresso_metas(metas),
            "fonte": "metas.json",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    def consultar_meta_por_id(meta_id: str) -> dict[str, Any]:
        """
        Consulta uma meta específica pelo identificador.

        Use esta ferramenta quando o usuário informar um código de meta,
        como META-0001.
        """
        metas = carregar_metas_cliente(cliente_id)
        meta = buscar_meta(metas, meta_id)
        return {
            **calcular_progresso_meta(meta),
            "cliente_id": cliente_id,
            "fonte": "metas.json",
            "tipo_resultado": "calculo_deterministico",
        }

    @tool
    def simular_conclusao_de_meta(
        valor_meta: float,
        valor_atual: float,
        aporte_mensal: float,
        data_referencia: str | None = None,
    ) -> dict[str, Any]:
        """
        Simula a conclusão de uma meta sem considerar rentabilidade.

        Use esta ferramenta para estimar quando uma meta será atingida
        com aportes mensais constantes.
        """
        referencia = (
            date.fromisoformat(data_referencia)
            if data_referencia
            else None
        )
        resultado = simular_meta_sem_rentabilidade(
            valor_meta=valor_meta,
            valor_atual=valor_atual,
            aporte_mensal=aporte_mensal,
            data_referencia=referencia,
        )
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "simulacao_python",
            "tipo_resultado": "simulacao_educativa",
            "aviso": (
                "A simulação não considera rentabilidade, "
                "inflação ou mudanças futuras."
            ),
        }

    @tool
    def calcular_aporte_para_meta(
        valor_meta: float,
        valor_atual: float,
        meses_restantes: int,
    ) -> dict[str, Any]:
        """
        Calcula o aporte mensal necessário para atingir uma meta.

        Use esta ferramenta para estimar quanto deve ser guardado por mês
        dentro de um prazo definido, sem considerar rentabilidade.
        """
        resultado = calcular_aporte_mensal_necessario(
            valor_meta=valor_meta,
            valor_atual=valor_atual,
            meses_restantes=meses_restantes,
        )
        return {
            **resultado,
            "cliente_id": cliente_id,
            "fonte": "simulacao_python",
            "tipo_resultado": "simulacao_educativa",
            "aviso": (
                "O cálculo não considera rentabilidade, "
                "inflação ou mudanças futuras."
            ),
        }

    return [
        consultar_metas_financeiras,
        consultar_meta_por_id,
        simular_conclusao_de_meta,
        calcular_aporte_para_meta,
    ]