from __future__ import annotations

from typing import TypedDict

import streamlit as st

from agent import (
    ErroAgenteFinanceiro, 
    executar_pergunta, 
    executar_pergunta_visitante,
)
from memoria import (
    construir_thread_id,
    criar_id_sessao,
    limpar_memoria,
)
from seguranca import ErroSeguranca

class MensagemChat(TypedDict):
    role: str
    content: str

PERFIL_VISITANTE = "VISITANTE"

PERFIS = {
    "CLI-0001": {
        "nome": "João Silva",
        "tipo": "cliente",
    },
    "CLI-0002": {
        "nome": "Mariana Costa",
        "tipo": "cliente",
    },
    "CLI-0003": {
        "nome": "Carlos Mendes",
        "tipo": "cliente",
    },
    PERFIL_VISITANTE: {
        "nome": "Não cliente",
        "tipo": "visitante",
    },
}

MENSAGEM_INICIAL = (
    "Olá! Sou o FinGuia. Como posso ajudar?"
)

def configurar_pagina() -> None:
    st.set_page_config(
        page_title="FinGuia",
        page_icon="",
        layout="centered",
        initial_sidebar_state="expanded",
    )

def inicializar_estado() -> None:
    """Inicializa os dados da sessão do navegador"""
    if "sessao_id" not in st.session_state:
        st.session_state["sessao_id"] = (
            criar_id_sessao()
        )

    if "historicos" not in st.session_state:
        st.session_state["historicos"] = {
            perfil_id: [
                {
                    "role": "assistant",
                    "content": MENSAGEM_INICIAL,
                }
            ]
            for perfil_id in PERFIS
        }

def obter_thread_id(perfil_id: str) -> str:
    return construir_thread_id(
        sessao_id=st.session_state.sessao_id,
        perfil_id=perfil_id,
    )

def obter_historico(
    perfil_id: str,
) -> list[MensagemChat]:
    return st.session_state.historicos[perfil_id]

def limpar_conversa(
    perfil_id: str,
) -> None:
    st.session_state.historicos[perfil_id] = [
        {
            "role": "assistant",
            "content": MENSAGEM_INICIAL,
        }
    ]

    limpar_memoria(obter_thread_id(perfil_id))

def exibir_barra_lateral() -> str:
    with st.sidebar:
        st.title("FinGuia")
        st.caption("Agente de educação financeira")

        perfil_id = st.selectbox(
            "Escolha um perfil",
            options=list(PERFIS),
            format_func=lambda item: (
                "Visitante - sem dados cadastrados"
                if item == PERFIL_VISITANTE
                else (
                    f"{PERFIS[item]['nome']} - {item}"
                )
            ),
            key="perfil_selecionado",
            help=(
                "Clientes cadastrados possuem acesso aos seus dados. O visitante recebe apenas orientações educativas."
            ),
        )

        if perfil_id == PERFIL_VISITANTE:
            st.warning("Modo visitante: apenas dúvidas educativas gerais.")
        else:
            st.success("Dados do cliente selecionado disponíveis.")

        st.divider()

        if st.button(
            "Limpar conversa",
            use_container_width=True,
        ):
            limpar_conversa(perfil_id)
            st.rerun()

        st.divider()

        st.info(
            "Este MVP oferece informações educativas. "
            "Ele não substitui orientação financeira profissional e não garante rentabilidade."
        )

        st.caption("Os dados utilizados neste projeto são fictícios.")

    return perfil_id

def exibir_historico(
    historico: list[MensagemChat],
) -> None:
    for mensagem in historico:
        with st.chat_message(mensagem["role"]):
            exibir_resposta_markdown(mensagem["content"])

def processar_pergunta(
    perfil_id: str,
    pergunta: str,
    historico: list[MensagemChat],
) -> None:
    historico.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )

    with st.chat_message("user"):
        st.markdown(pergunta)

    thread_id = obter_thread_id(perfil_id)

    with st.chat_message("assistant"):
        with st.spinner(
            "Analisando sua pergunta..."
        ):
            try:
                if perfil_id == PERFIL_VISITANTE:
                    resposta = executar_pergunta_visitante(
                        pergunta=pergunta,
                        thread_id=thread_id,
                    )
                else:
                    resposta = executar_pergunta(
                        cliente_id=perfil_id,
                        pergunta=pergunta,
                        thread_id=thread_id,
                    )

            except ErroSeguranca as erro:
                resposta = (
                    "Não foi possível atender a "
                    f"essa solicitação: {erro}"
                )
                st.warning(resposta)

            except ErroAgenteFinanceiro:
                resposta = (
                    "Não foi possível concluir a consulta. "
                    "Verifique se o Ollama está em execução."
                )
                st.error(resposta)

            except Exception:
                resposta = (
                    "Ocorreu um erro inesperado ao processar a solicitação."
                )
                st.error(resposta)

        exibir_resposta_markdown(resposta)

    historico.append(
        {
            "role": "assistant",
            "content": resposta,
        }
    )

def main() -> None:
    configurar_pagina()
    inicializar_estado()

    perfil_id = exibir_barra_lateral()
    historico = obter_historico(perfil_id)

    st.title("FinGuia")

    if perfil_id == PERFIL_VISITANTE:
        st.caption("Modo visitante: sem acesso a dados financeiros pessoais.")
    else:
        st.caption(f"Sessão vinculada a {PERFIS[perfil_id]['nome']} - {perfil_id}")

    exibir_historico(historico)

    pergunta = st.chat_input(
        "Digite sua pergunta...",
        max_chars=2000,
    )

    if pergunta:
        processar_pergunta(
            perfil_id=perfil_id,
            pergunta=pergunta,
            historico=historico,
        )

def exibir_resposta_markdown(
    texto: str,
) -> None:
    """Exibe texto preservando símbolos monetários."""
    texto_formatado = texto.replace(
        "$",
        r"\$",
    )

    st.markdown(texto_formatado)

if __name__ == "__main__":
    main()