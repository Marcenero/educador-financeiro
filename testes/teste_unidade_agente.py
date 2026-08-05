from unittest.mock import Mock, patch

import pytest
from langchain.messages import AIMessage

from agent import (
    ErroAgenteFinanceiro,
    criar_agente_financeiro,
    executar_pergunta,
    extrair_resposta_final,
)

def teste_extrair_resposta_final():
    resultado = {
        "messages": [AIMessage(content="Resposta final.")]
    }

    assert extrair_resposta_final(resultado) == "Resposta final."

def teste_sem_mensagens_gera_erro():
    with pytest.raises(ErroAgenteFinanceiro):
        extrair_resposta_final({})

def teste_cliente_vazio_gera_erro():
    with pytest.raises(ValueError):
        criar_agente_financeiro("")

@patch("agent.criar_agente_financeiro")
def teste_executar_pergunta(mock_criar):
    agente = Mock()
    agente.invoke.return_value = {
        "messages": [AIMessage(content="Saldo positivo.")]
    }
    mock_criar.return_value = agente

    assert executar_pergunta(
        "CLI-0001",
        "Qual foi meu saldo?",
    ) == "Saldo positivo."