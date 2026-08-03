from __future__ import annotations

from langchain.tools import BaseTool

from ferramentas.ferramenta_dividas import criar_ferramentas_dividas
from ferramentas.ferramenta_metas import criar_ferramentas_metas
from ferramentas.ferramenta_produtos import criar_ferramentas_produtos
from ferramentas.ferramenta_transacoes import criar_ferramentas_transacoes

def criar_ferramentas_cliente(cliente_id: str) -> list[BaseTool]:
    """Reúne todas as ferramentas autorizadas para um cliente"""
    return [
        *criar_ferramentas_transacoes(cliente_id),
        *criar_ferramentas_metas(cliente_id),
        *criar_ferramentas_dividas(cliente_id),
        *criar_ferramentas_produtos(cliente_id),
    ]