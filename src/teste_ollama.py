from __future__ import annotations

from model_config import criar_modelo_ollama

def main() -> None:
    modelo = criar_modelo_ollama()

    resposta = modelo.invoke(
        "Responda em português, em uma frase: "
        "o que é uma reserva de emergência?"
    )

    print("Objeto completo:")
    print(resposta)

    print("\nContent com repr:")
    print(repr(resposta.content))

    print("\nMetadados:")
    print(resposta.response_metadata)

    print("\nAdditional kwargs:")
    print(resposta.additional_kwargs)

    print("\nResposta final:")
    print(resposta.content or "Conteúdo vazio retornado pelo modelo.")

if __name__ == "__main__":
    main()