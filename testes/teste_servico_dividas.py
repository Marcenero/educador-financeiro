from __future__ import annotations

import pytest

from data_loader import carregar_contexto_cliente
from servicos.servico_dividas import (
    ErroServicoDividas,
    calcular_resumo_dividas,
    identificar_divida_maior_taxa,
    listar_dividas_ordenadas_por_taxa,
)

def teste_resumo_dividas_carlos(cliente_carlos_id):
    contexto = carregar_contexto_cliente(cliente_carlos_id)

    resultado = calcular_resumo_dividas(
        contexto.dividas,
        contexto.cliente.renda.renda_mensal_media,
    )

    assert resultado["quantidade_dividas_ativas"] == 2
    assert resultado["saldo_devedor_total"] == 14800.0
    assert resultado["parcelas_mensais_total"] == 1260.0
    assert resultado["comprometimento_renda_percentual"] == 18.53

def teste_cliente_sem_dividas(cliente_mariana_id):
    contexto = carregar_contexto_cliente(cliente_mariana_id)

    resultado = calcular_resumo_dividas(
        contexto.dividas,
        contexto.cliente.renda.renda_mensal_media,
    )

    assert resultado["quantidade_dividas_ativas"] == 0
    assert resultado["saldo_devedor_total"] == 0
    assert resultado["parcelas_mensais_total"] == 0
    assert resultado["comprometimento_renda_percentual"] == 0.0

def teste_renda_negativa_gera_erro(cliente_carlos_id):
    contexto = carregar_contexto_cliente(cliente_carlos_id)

    with pytest.raises(
        ErroServicoDividas,
        match="renda_mensal_media",
    ):
        calcular_resumo_dividas(
            contexto.dividas,
            renda_mensal_media=-1,
        )

def teste_dividas_ordenadas_por_taxa(cliente_carlos_id):
    contexto = carregar_contexto_cliente(cliente_carlos_id)

    resultado = listar_dividas_ordenadas_por_taxa(
        contexto.dividas
    )

    assert len(resultado) == 2
    assert resultado[0]["taxa_mensal_percentual"] == 7.9
    assert resultado[1]["taxa_mensal_percentual"] == 2.6

def teste_identificar_maior_taxa_carlos(cliente_carlos_id):
    contexto = carregar_contexto_cliente(cliente_carlos_id)

    resultado = identificar_divida_maior_taxa(
        contexto.dividas
    )

    assert resultado is not None
    assert resultado["divida_id"] == "DIV-0002"
    assert resultado["taxa_mensal_percentual"] == 7.9

def teste_sem_divida_com_taxa_retorna_none(cliente_mariana_id):
    contexto = carregar_contexto_cliente(cliente_mariana_id)

    resultado = identificar_divida_maior_taxa(
        contexto.dividas
    )

    assert resultado is None