from __future__ import annotations

from ferramentas.toolkit import criar_ferramentas_cliente


def _por_nome(cliente_id: str):
    ferramentas = criar_ferramentas_cliente(cliente_id)
    return {ferramenta.nome: ferramenta for ferramenta in ferramentas}


def teste_toolkit_possui_ferramentas():
    ferramentas = criar_ferramentas_cliente("CLI-0001")
    assert len(ferramentas) == 15
    assert len({ferramenta.nome for ferramenta in ferramentas}) == 15


def teste_cliente_id_nao_e_argumento_das_ferramentas():
    ferramentas = criar_ferramentas_cliente("CLI-0001")
    for ferramenta in ferramentas:
        assert "cliente_id" not in ferramenta.args_schema.model_fields


def teste_resumo_financeiro_joao():
    ferramentas = _por_nome("CLI-0001")
    resultado = ferramentas["consultar_resumo_financeiro"].invoke({})
    assert resultado["cliente_id"] == "CLI-0001"
    assert resultado["entradas"] == 30900.0
    assert resultado["saidas"] == 21351.61
    assert resultado["saldo"] == 9548.39


def teste_toolkits_nao_misturam_clientes():
    joao = _por_nome("CLI-0001")["consultar_resumo_financeiro"].invoke({})
    carlos = _por_nome("CLI-0003")["consultar_resumo_financeiro"].invoke({})
    assert joao["cliente_id"] == "CLI-0001"
    assert joao["saldo"] == 9548.39
    assert carlos["cliente_id"] == "CLI-0003"
    assert carlos["saldo"] == -5403.57


def teste_consultar_categoria():
    resultado = _por_nome("CLI-0002")["consultar_gasto_de_categoria"].invoke(
        {"categoria": "alimentacao"}
    )
    assert resultado["cliente_id"] == "CLI-0002"
    assert resultado["valor_total"] > 0


def teste_consultar_metas():
    resultado = _por_nome("CLI-0001")["consultar_metas_financeiras"].invoke({})
    assert len(resultado["metas"]) == 2


def teste_resumo_dividas_carlos():
    resultado = _por_nome("CLI-0003")["consultar_resumo_dividas"].invoke({})
    assert resultado["saldo_devedor_total"] == 14800.0
    assert resultado["parcelas_mensais_total"] == 1260.0


def teste_produtos_educativos():
    resultado = _por_nome("CLI-0001")["consultar_produtos_educativos"].invoke(
        {"aporte_disponivel": 500, "objetivo": "reserva emergencia"}
    )
    assert resultado["tipo_resultado"] == "filtro_educativo"
    assert "recomendação" in resultado["aviso"]