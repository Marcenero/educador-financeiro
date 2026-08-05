import pytest

from agent import (
    executar_pergunta,
    executar_pergunta_visitante,
)
from memoria import (
    construir_thread_id,
    limpar_memoria,
)

@pytest.mark.integration
def teste_memoria_visitante():
    thread_id = construir_thread_id(
        "teste-memoria",
        "VISITANTE",
    )

    limpar_memoria(thread_id)

    executar_pergunta_visitante(
        pergunta=(
            "Meu apelido nesta conversa é Nori. "
            "Responda apenas OK."
        ),
        thread_id=thread_id,
    )

    resposta = executar_pergunta_visitante(
        pergunta="Qual é meu apelido?",
        thread_id=thread_id,
    )

    assert "Nori" in resposta

    limpar_memoria(thread_id)

@pytest.mark.integration
@pytest.mark.parametrize(
    ("pergunta", "termos"),
    [
        (
            "Qual foi meu saldo no período?",
            ["9.548", "transacoes.csv"],
        ),
        (
            "Quais são minhas metas financeiras?",
            ["reserva", "metas.json"],
        ),
    ],
)
def teste_fluxos_cliente(pergunta, termos):
    thread_id = construir_thread_id(
        "teste-fluxos",
        "CLI-0001",
    )

    limpar_memoria(thread_id)

    resposta = executar_pergunta(
        cliente_id="CLI-0001",
        pergunta=pergunta,
        thread_id=thread_id,
    ).lower()

    for termo in termos:
        assert termo.lower() in resposta

    limpar_memoria(thread_id)