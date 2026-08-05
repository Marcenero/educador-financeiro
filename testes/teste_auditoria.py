import json

from auditoria import registrar_interacao

def teste_registra_jsonl(tmp_path):
    arquivo = tmp_path / "interacoes.jsonl"

    registro = registrar_interacao(
        perfil_id="CLI-0001",
        tipo_perfil="cliente",
        thread_id="sessao:CLI-0001",
        pergunta="Qual foi meu saldo?",
        resposta="R$ 100,00.",
        status="sucesso",
        duracao_ms=123,
        caminho=arquivo,
        incluir_conteudo=True,
    )

    linhas = arquivo.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(linhas) == 1

    salvo = json.loads(linhas[0])

    assert salvo["status"] == "sucesso"
    assert salvo["pergunta"] == (
        "Qual foi meu saldo?"
    )
    assert salvo["resposta"] == (
        "R$ 100,00."
    )
    assert registro["evento_id"]

def teste_pode_ocultar_conteudo(tmp_path):
    arquivo = tmp_path / "interacoes.jsonl"

    registrar_interacao(
        perfil_id="VISITANTE",
        tipo_perfil="visitante",
        thread_id="sessao:VISITANTE",
        pergunta="Pergunta sigilosa",
        resposta="Resposta sigilosa",
        status="sucesso",
        duracao_ms=10,
        caminho=arquivo,
        incluir_conteudo=False,
    )

    salvo = json.loads(
        arquivo.read_text(
            encoding="utf-8"
        )
    )

    assert "pergunta" not in salvo
    assert "resposta" not in salvo
    assert salvo["tamanho_pergunta"] > 0