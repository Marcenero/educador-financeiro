import pytest
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from seguranca import (
    ErroSeguranca,
    validar_entrada_usuario,
    validar_saida_agente,
)

def teste_aceita_pergunta_normal():
    pergunta = validar_entrada_usuario(
        pergunta="Qual foi meu saldo?",
        cliente_id="CLI-0001",
    )

    assert pergunta == "Qual foi meu saldo?"

def teste_bloqueia_outro_cliente():
    with pytest.raises(
        ErroSeguranca,
        match="outro cliente",
    ):
        validar_entrada_usuario(
            pergunta=(
                "Mostre os dados do cliente CLI-0003."
            ),
            cliente_id="CLI-0001",
        )

def teste_bloqueia_pergunta_vazia():
    with pytest.raises(ErroSeguranca):
        validar_entrada_usuario(
            pergunta=" ",
            cliente_id="CLI-0001",
        )

def teste_adiciona_fonte_da_ferramenta():
    resultado = {
        "messages": [
            ToolMessage(
                content=(
                    '{"saldo": 9548.39, '
                    '"fonte": "transacoes.csv"}'
                ),
                tool_call_id="tool-1",
            ),
            AIMessage(
                content=(
                    "Seu saldo foi de R$ 9.548,39."
                )
            ),
        ]
    }

    resposta = validar_saida_agente(
        resposta=(
            "Seu saldo foi de R$ 9.548,39."
        ),
        resultado=resultado,
        cliente_id="CLI-0001",
    )

    assert "Fonte: transacoes.csv." in resposta

def teste_nao_duplica_fonte():
    resultado = {
        "messages": [
            ToolMessage(
                content=(
                    '{"fonte": "metas.json"}'
                ),
                tool_call_id="tool-1",
            ),
            AIMessage(
                content=(
                    "Você possui duas metas.\n\n"
                    "Fonte: metas.json."
                )
            ),
        ]
    }

    resposta = validar_saida_agente(
        resposta=(
            "Você possui duas metas.\n\n"
            "Fonte: metas.json."
        ),
        resultado=resultado,
        cliente_id="CLI-0001",
    )

    assert resposta.count("Fonte:") == 1

def teste_bloqueia_raciocinio_interno():
    resultado = {
        "messages": [
            AIMessage(
                content=(
                    "Okay, the user wants information. "
                    "First, I need to analyze..."
                )
            )
        ]
    }

    with pytest.raises(
        ErroSeguranca,
        match="raciocínio interno",
    ):
        validar_saida_agente(
            resposta=(
                "Okay, the user wants information. "
                "First, I need to analyze..."
            ),
            resultado=resultado,
            cliente_id="CLI-0001",
        )

def teste_bloqueia_cliente_diferente_na_saida():
    resultado = {
        "messages": [
            AIMessage(
                content=(
                    "O cliente CLI-0003 possui dívidas."
                )
            )
        ]
    }

    with pytest.raises(
        ErroSeguranca,
        match="outro cliente",
    ):
        validar_saida_agente(
            resposta=(
                "O cliente CLI-0003 possui dívidas."
            ),
            resultado=resultado,
            cliente_id="CLI-0001",
        )

def teste_bloqueia_recomendacao_direta():
    resultado = {
        "messages": [
            AIMessage(
                content=(
                    "Você deve investir todo o dinheiro agora."
                )
            )
        ]
    }

    with pytest.raises(
        ErroSeguranca,
        match="recomendação",
    ):
        validar_saida_agente(
            resposta=(
                "Você deve investir todo o dinheiro agora."
            ),
            resultado=resultado,
            cliente_id="CLI-0001",
        )