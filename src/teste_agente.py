from agent import (
    ErroAgenteFinanceiro,
    executar_pergunta,
)
from seguranca import ErroSeguranca

def main() -> None:
    cliente_id = "CLI-0001"

    perguntas = [
        "O que é uma reserva de emergência?",
        "Qual foi o meu saldo no período?",
        "Quanto gastei com alimentação?",
        "Quais são minhas metas financeiras?",
    ]

    for pergunta in perguntas:
        print("=" * 70)
        print(f"Pergunta: {pergunta}")

        try:
            resposta = executar_pergunta(
                cliente_id=cliente_id,
                pergunta=pergunta,
            )

            print(f"Resposta: {resposta}")

        except ErroSeguranca as erro:
            print(
                "Resposta bloqueada por segurança:",
                erro,
            )

        except ErroAgenteFinanceiro as erro:
            print(
                "Não foi possível concluir a consulta:",
                erro,
            )

if __name__ == "__main__":
    main()