from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from model_config import criar_modelo_ollama

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct")

def verificar_servidor() -> dict:
    url = f"{BASE_URL}/api/tags"

    try:
        with urllib.request.urlopen(url, timeout=5) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.URLError as erro:
        raise RuntimeError(
            f"Não foi possível acessar o Ollama em {BASE_URL}. "
            "Confirme se o aplicativo está aberto."
        ) from erro

def main() -> None:
    dados = verificar_servidor()
    modelos = [
        item.get("name", "")
        for item in dados.get("models", [])
    ]

    print("Servidor Ollama acessível.")
    print("Módulos instalados:")

    if modelos:
        for nome in modelos:
            print(f"- {nome}")
    else:
        print("- nenhum")

    if not any (nome.startswith(MODEL) for nome in modelos):
        print(f"\nModelo {MODEL!r} não encontrado.")
        print(f"Execute: ollama pull {MODEL}")
        return

    modelo = criar_modelo_ollama()
    resposta = modelo.invoke("Responda apenas com OK.")

    print("\nTeste LangChain:")
    print(resposta.content)

if __name__ == "__main__":
    main()