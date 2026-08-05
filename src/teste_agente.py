from agent import executar_pergunta

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
        print(
            "Resposta:",
            executar_pergunta(cliente_id, pergunta)
        )

if __name__ == "__main__":
    main()