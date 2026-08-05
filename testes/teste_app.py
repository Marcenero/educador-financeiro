from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "app.py"
)

def teste_app_carrega_sem_excecao():
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=20)

    assert not app.exception
    assert any("FinGuia" in item.value for item in app.title)

def teste_app_possui_seletor_de_cliente():
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=20)

    assert len(app.selectbox) == 1
    assert app.selectbox[0].value == "CLI-0001"

def teste_app_possui_entrada_de_chat():
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=20)

    assert len(app.chat_input) == 1