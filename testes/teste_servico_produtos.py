from __future__ import annotations

import pytest

from data_loader import carregar_produtos
from servicos.servico_produtos import (
    ErroServicoProdutos,
    buscar_produtos_compativeis,
)

def teste_produtos_para_risco_baixo():
    produtos = carregar_produtos()

    resultado = buscar_produtos_compativeis(
        produtos=produtos,
        risco_maximo="baixo",
        aporte_disponivel=1000,
    )

    assert len(resultado) > 0
    assert all(item["risco"] == "baixo" for item in resultado)
    assert all(item["aporte_minimo"] <= 1000 for item in resultado)

def teste_produtos_reserva_emergencia():
    produtos = carregar_produtos()

    resultado = buscar_produtos_compativeis(
        produtos=produtos,
        risco_maximo="baixo",
        aporte_disponivel=500,
        objetivo="reserva emergencia",
    )

    nomes = {produto["nome"] for produto in resultado}

    assert "Tesouro Selic" in nomes
    assert "CDB com Liquidez Diária" in nomes

def teste_aporte_insuficiente_filtra_produtos():
    produtos = carregar_produtos()

    resultado = buscar_produtos_compativeis(
        produtos=produtos,
        risco_maximo="baixo",
        aporte_disponivel=50,
    )

    assert all(
        produto["aporte_minimo"] <= 50
        for produto in resultado
    )

@pytest.mark.parametrize(
    "risco",
    ["muito_baixo", "", "extremo"],
)
def teste_risco_invalido_gera_erro(risco):
    produtos = carregar_produtos()

    with pytest.raises(
        ErroServicoProdutos,
        match="risco_maximo",
    ):
        buscar_produtos_compativeis(
            produtos=produtos,
            risco_maximo=risco,
            aporte_disponivel=500,
        )

def teste_aporte_negativo_gera_erro():
    produtos = carregar_produtos()

    with pytest.raises(
        ErroServicoProdutos,
        match="aporte_disponivel",
    ):
        buscar_produtos_compativeis(
            produtos=produtos,
            risco_maximo="baixo",
            aporte_disponivel=-100,
        )

def teste_filtro_nao_retorna_produto_acima_do_risco():
    produtos = carregar_produtos()

    resultado = buscar_produtos_compativeis(
        produtos=produtos,
        risco_maximo="medio",
        aporte_disponivel=10000,
    )

    assert all(
        produto["risco"] in {"baixo", "medio", "médio"}
        for produto in resultado
    )