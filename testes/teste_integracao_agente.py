import pytest

from agent import executar_pergunta

@pytest.mark.integration
def teste_agente_responde():
    resposta = executar_pergunta(
        "CLI-0001",
        "Explique em uma frase o que é reserva de emergência.",
    )

    assert resposta

@pytest.mark.integration
def teste_agente_consulta_saldo():
    resposta = executar_pergunta(
        "CLI-0001",
        "Qual foi meu saldo no período?",
    )

    assert "9.548" in resposta or "9548" in resposta