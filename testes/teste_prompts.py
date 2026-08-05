from prompts import SYSTEM_PROMPT


def teste_system_prompt_nao_esta_vazio():
    assert SYSTEM_PROMPT.strip()


def teste_system_prompt_define_portugues():
    assert "português" in SYSTEM_PROMPT.lower()


def teste_system_prompt_exige_ferramentas():
    assert "use ferramentas" in SYSTEM_PROMPT.lower()


def teste_system_prompt_proibe_inventar():
    assert "nunca invente" in SYSTEM_PROMPT.lower()


def teste_system_prompt_protege_clientes():
    assert "outro cliente" in SYSTEM_PROMPT.lower()