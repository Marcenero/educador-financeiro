from __future__ import annotations

import pytest

from data_loader import (
    ErroCarregamentoDados,
    carregar_cliente,
    carregar_clientes,
    carregar_contexto_cliente,
    carregar_produtos,
    carregar_transacoes_dataframe,
    listar_clientes_para_interface,
    validar_integridade_referencial,
)

def teste_carregar_tres_clientes():
    clientes = carregar_clientes()

    assert len(clientes) == 3
    assert {cliente.cliente_id for cliente in clientes} == {
        "CLI-0001",
        "CLI-0002",
        "CLI-0003",
    }

def teste_carregar_cliente_existente(cliente_joao_id):
    cliente = carregar_cliente(cliente_joao_id)

    assert cliente.cliente_id == "CLI-0001"
    assert cliente.nome_ficticio == "João Silva"
    assert cliente.renda.renda_mensal_media == 5000.0

def teste_cliente_inexistente_gera_erro():
    with pytest.raises(
        ErroCarregamentoDados,
        match="Cliente não encontrado",
    ):
        carregar_cliente("CLI-9999")

def teste_listar_clientes_para_interface():
    clientes = listar_clientes_para_interface()

    assert len(clientes) == 3
    assert clientes[0].keys() == {"cliente_id", "nome"}

def teste_integridade_referencial_sem_erros():
    avisos = validar_integridade_referencial(corrigir_inconsistencias=True)

    assert isinstance(avisos, list)

def teste_contexto_de_cada_cliente():
    quantidades_esperadas = {
        "CLI-0001": (80, 2, 1),
        "CLI-0002": (75, 2, 0),
        "CLI-0003": (91, 2, 2),
    }

    for cliente_id, esperado in quantidades_esperadas.items():
        contexto = carregar_contexto_cliente(cliente_id)

        assert contexto.cliente.cliente_id == cliente_id
        assert len(contexto.transacoes) == esperado[0]
        assert len(contexto.metas) == esperado[1]
        assert len(contexto.dividas) == esperado[2]

        assert all(
            transacao.cliente_id == cliente_id
            for transacao in contexto.transacoes
        )

def teste_carregar_produtos():
    produtos = carregar_produtos()

    assert len(produtos) >= 1
    assert all("produto_id" in produto for produto in produtos)
    assert all("nome" in produto for produto in produtos)
    assert all(
        produto["risco"] in {"baixo", "medio", "médio", "alto"}
        for produto in produtos
    )