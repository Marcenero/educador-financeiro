from __future__ import annotations

from typing import Any
from langchain_core.tools import BaseTool, tool

from data_loader import carregar_cliente, carregar_produtos
from servicos.servico_produtos import buscar_produtos_compativeis

RISCO_POR_PERFIL = {
    "conservador": "baixo",
    "moderado": "medio",
    "arrojado": "alto",
}

def criar_ferramentas_produtos(cliente_id: str) -> list[BaseTool]:
    """Cria ferramentas educativas de produtos vinculadas ao cliente."""

    @tool
    def consultar_produtos_educativos(
        aporte_disponivel: float,
        objetivo: str | None = None,
    ) -> dict[str, Any]:
        """
        Filtra produtos financeiros educativos compatíveis com o cliente.

        Use esta ferramenta para comparar produtos por perfil de risco,
        aporte disponível e objetivo financeiro. O resultado não constitui
        recomendação de investimento.
        """
        cliente = carregar_cliente(cliente_id)
        produtos = carregar_produtos()
        perfil = cliente.perfil_financeiro.perfil_investidor.value
        risco_maximo = RISCO_POR_PERFIL[perfil]
        objetivo_consulta = objetivo or cliente.objetivo_principal

        encontrados = buscar_produtos_compativeis(
            produtos=produtos,
            risco_maximo=risco_maximo,
            aporte_disponivel=aporte_disponivel,
            objetivo=objetivo_consulta,
        )

        return {
            "cliente_id": cliente_id,
            "perfil_investidor": perfil,
            "risco_maximo_usado": risco_maximo,
            "objetivo_considerado": objetivo_consulta,
            "produtos": encontrados,
            "fonte": "clientes.json e produtos_financeiros.json",
            "tipo_resultado": "filtro_educativo",
            "aviso": (
                "O resultado é educativo e não constitui "
                "recomendação de investimento."
            ),
        }

    return [consultar_produtos_educativos]