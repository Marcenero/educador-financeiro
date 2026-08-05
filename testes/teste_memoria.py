import pytest

from memoria import (
    construir_thread_id,
    criar_configuracao,
    criar_id_sessao,
    limpar_memoria,
)

def teste_cria_id_sessao():
    assert criar_id_sessao()

def teste_thread_separa_perfis():
    sessao = "sessao-123"

    joao = construir_thread_id(
        sessao,
        "CLI-0001",
    )
    visitante = construir_thread_id(
        sessao,
        "VISITANTE",
    )

    assert joao != visitante
    assert joao.endswith("CLI-0001")
    assert visitante.endswith("VISITANTE")

def teste_configuracao_possui_thread_id():
    config = criar_configuracao(
        "sessao:CLI-0001"
    )

    assert (
        config["configurable"]["thread_id"]
        == "sessao:CLI-0001"
    )

def teste_thread_exige_sessao():
    with pytest.raises(ValueError):
        construir_thread_id(
            "",
            "CLI-0001",
        )

def teste_limpar_thread_inexistente_nao_falha():
    limpar_memoria(
        "thread-que-nao-existe"
    )