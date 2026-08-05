from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TypeVar

import pandas as pd
from pydantic import BaseModel, ValidationError

from schemas import (
    Atendimento,
    Cliente,
    Conta,
    ContextoCliente,
    Divida,
    MetaFinanceira,
    Transacao,
)

# CONFIGURAÇÃO
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "dados"

ModeloT = TypeVar("ModeloT", bound=BaseModel)

class ErroCarregamentoDados(RuntimeError):
    """Erro geral ao localizar, ler ou validar os arquivos da base."""

class ErroIntegridadeDados(ErroCarregamentoDados):
    """Erro de relacionamento entre clientes, contas e demais registros."""

# FUNÇÕES GENÉRICAS
def _resolver_caminho(nome_arquivo: str) -> Path:
    """
    Resolve e valida o caminho de um arquivo dentro da pasta data
    """
    caminho = DATA_DIR / nome_arquivo

    if not caminho.exists():
        raise ErroCarregamentoDados(f"Arquivo não encontrado: {caminho}")

    if not caminho.is_file():
        raise ErroCarregamentoDados(f"O caminho não representa um arquivo: {caminho}")

    return caminho

def _carregar_json_bruto(nome_arquivo: str) -> Any:
    """
    Lê um arquivo JSON e devolve seu conteúdo sem validar o modelo
    """
    caminho = _resolver_caminho(nome_arquivo)

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ErroCarregamentoDados(
            f"JSON inválido em {nome_arquivo}: "
            f"linha {erro.lineno}, coluna {erro.colno}."
        ) from erro
    except OSError as erro:
        raise ErroCarregamentoDados(
            f"Não foi possível ler {nome_arquivo}: {erro}"
        ) from erro

def _validar_lista_modelos(
    registros: Iterable[dict[str, Any]],
    modelo: type[ModeloT],
    nome_fonte: str,
) -> list[ModeloT]:
    """
    Valida todos os registros de uma fonte com um schema Pydantic
    """
    validados: list[ModeloT] = []
    erros: list[str] = []

    for indice, registro in enumerate(registros, start=1):
        try:
            validados.append(modelo.model_validate(registro))
        except ValidationError as erro:
            erros.append(f"Registro {indice} de {nome_fonte}:\n{erro}")

    if erros:
        detalhes = "\n\n".join(erros[:10])

        if len(erros) > 10:
            detalhes += (f"\n\n... em mais {len(erros) - 10} erro(s).")

        raise ErroCarregamentoDados(
            f"Foram encontrados {len(erros)} registro(s) inválido(s)"
            f"em {nome_fonte}:\n\n{detalhes}"
        )

    return validados

def _carregar_lista_json(
    nome_arquivo: str,
    modelo: type[ModeloT],
) -> list[ModeloT]:
    """
    Carrega um JSON cuja raiz deve ser uma lista de objetos
    """
    dados = _carregar_json_bruto(nome_arquivo)

    if not isinstance(dados, list):
        raise ErroCarregamentoDados(f"A raiz de {nome_arquivo} deve ser uma lista.")

    if not all(isinstance(item, dict) for item in dados):
        raise ErroCarregamentoDados(f"Todos os itens de {nome_arquivo} devem ser objetos JSON.")

    return _validar_lista_modelos(
        registros=dados,
        modelo=modelo,
        nome_fonte=nome_arquivo,
    )

def _normalizar_booleano(valor: Any) -> bool:
    """
    Converte booleanos reais 0/1 e textos comuns em bool
    """
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, (int, float)) and not pd.isna(valor):
        if valor in (0, 1):
            return bool(valor)

    if isinstance(valor, str):
        normalizado = valor.strip().lower()

        if normalizado in {"true", "1", "sim", "s", "yes"}:
            return True

        if normalizado in {"false", "0", "nao", "não", "n", "no"}:
            return False

    raise ValueError(f"Valor booleano inválido: {valor!r}")

def _inteiro_ou_none(valor: Any) -> int | None:
    """
    Converte números do Pandas em inteiro e NaN/vazio em None
    """
    if valor is None or pd.isna(valor):
        return None

    if isinstance(valor, str) and not valor.strip():
        return None

    numero = float(valor)

    if not numero.is_integer():
        raise ValueError(f"Era esperado um inteiro, mas foi recebido {valor!r}.")

    return int(numero)

# CARREGADORES JSON
def carregar_clientes() -> list[Cliente]:
    return _carregar_lista_json("clientes.json", Cliente)

def carregar_contas() -> list[Conta]:
    return _carregar_lista_json("contas.json", Conta)

def carregar_metas() -> list[MetaFinanceira]:
    return _carregar_lista_json("metas.json", MetaFinanceira)

def carregar_dividas() -> list[Divida]:
    return _carregar_lista_json("dividas.json", Divida)


def carregar_produtos() -> list[dict[str, Any]]:
    """
    Carrega e valida o catálogo de produtos financeiros.

    Os produtos são globais: não pertencem a um cliente específico.
    O cruzamento com o perfil do cliente é feito posteriormente pelo
    products_service.py.
    """
    dados = _carregar_json_bruto("produtos_financeiros.json")

    if not isinstance(dados, list):
        raise ErroCarregamentoDados(
            "A raiz de produtos_financeiros.json deve ser uma lista."
        )

    campos_obrigatorios = {
        "produto_id",
        "nome",
        "categoria",
        "risco",
        "aporte_minimo",
        "indicado_para",
    }

    riscos_validos = {"baixo", "medio", "alto"}
    produtos_validados: list[dict[str, Any]] = []
    ids_encontrados: set[str] = set()
    erros: list[str] = []

    for indice, produto in enumerate(dados, start=1):
        if not isinstance(produto, dict):
            erros.append(f"Produto {indice}: deve ser um objeto JSON.")
            continue

        ausentes = campos_obrigatorios - set(produto)
        if ausentes:
            erros.append(
                f"Produto {indice}: campos ausentes: "
                + ", ".join(sorted(ausentes))
            )
            continue

        produto_id = str(produto["produto_id"]).strip()
        nome = str(produto["nome"]).strip()
        categoria = str(produto["categoria"]).strip().lower()
        risco = str(produto["risco"]).strip().lower()
        indicado_para = str(produto["indicado_para"]).strip()

        try:
            aporte_minimo = float(produto["aporte_minimo"])
        except (TypeError, ValueError):
            erros.append(
                f"Produto {indice}: aporte_minimo deve ser numérico."
            )
            continue

        if not produto_id:
            erros.append(f"Produto {indice}: produto_id não pode ser vazio.")
            continue

        if produto_id in ids_encontrados:
            erros.append(
                f"Produto {indice}: produto_id duplicado: {produto_id}."
            )
            continue

        if not nome:
            erros.append(f"Produto {indice}: nome não pode ser vazio.")
            continue

        if risco not in riscos_validos:
            erros.append(
                f"Produto {indice}: risco deve ser baixo, medio ou alto."
            )
            continue

        if aporte_minimo < 0:
            erros.append(
                f"Produto {indice}: aporte_minimo não pode ser negativo."
            )
            continue

        if not indicado_para:
            erros.append(
                f"Produto {indice}: indicado_para não pode ser vazio."
            )
            continue

        normalizado = dict(produto)
        normalizado["produto_id"] = produto_id
        normalizado["nome"] = nome
        normalizado["categoria"] = categoria
        normalizado["risco"] = risco
        normalizado["aporte_minimo"] = aporte_minimo
        normalizado["indicado_para"] = indicado_para

        ids_encontrados.add(produto_id)
        produtos_validados.append(normalizado)

    if erros:
        detalhes = "\n- ".join(erros[:10])
        if len(erros) > 10:
            detalhes += f"\n... e mais {len(erros) - 10} erro(s)."

        raise ErroCarregamentoDados(
            "Foram encontrados erros em produtos_financeiros.json:\n- "
            + detalhes
        )

    return produtos_validados

def carregar_cliente(cliente_id: str) -> Cliente:
    """
    Busca um cliente único pelo identificador
    """
    correspondencias = [
        cliente
        for cliente in carregar_clientes()
        if cliente.cliente_id == cliente_id
    ]

    if not correspondencias:
        raise ErroCarregamentoDados(f"Cliente não encontrado: {cliente_id}")

    if len(correspondencias) > 1:
        raise ErroIntegridadeDados(f"cliente_id duplicado em clientes.json: {cliente_id}.")

    return correspondencias[0]

def carregar_contas_cliente(cliente_id: str) -> list[Conta]:
    return [
        conta
        for conta in carregar_contas()
        if conta.cliente_id == cliente_id
    ]

def carregar_metas_cliente(
    cliente_id: str,
) -> list[MetaFinanceira]:
    return [
        meta
        for meta in carregar_metas()
        if meta.cliente_id == cliente_id
    ]

def carregar_dividas_cliente(
    cliente_id: str,
) -> list[Divida]:
    return [
        divida
        for divida in carregar_dividas()
        if divida.cliente_id == cliente_id
    ]

# TRANSAÇÕES
def _normalizar_registro_transacao(
    registro: dict[str, Any],
    corrigir_inconsistencias: bool,
) -> dict[str, Any]:
    """
    Converter os tipos de CSV e, opcionalmente, limpa campos de parcelamento e transações marcadas como não parceladas
    """
    normalizado = dict(registro)

    try:
        normalizado["parcelado"] = _normalizar_booleano(
            normalizado.get("parcelado")
        )

        normalizado["recorrente"] = _normalizar_booleano(
            normalizado.get("recorrente")
        )

        normalizado["essencial"] = _normalizar_booleano(
            normalizado.get("essencial")
        )

        normalizado["parcela_atual"] = _inteiro_ou_none(
            normalizado.get("parcela_atual")
        )

        normalizado["total_parcelas"] = _inteiro_ou_none(
            normalizado.get("total_parcelas")
        )
    except ValueError as erro:
        raise ErroCarregamentoDados(
            f"Erro ao normalizar a transação "
            f"{normalizado.get('transacao_id', '<sem id>')}: {erro}."
        ) from erro

    if corrigir_inconsistencias and not normalizado["parcelado"]:
        normalizado["parcela_atual"] = None
        normalizado["total_parcelas"] = None

    return normalizado

def carregar_transacoes(
    corrigir_inconsistencias: bool = True,
) -> list[Transacao]:
    """
    Carrega e valida todas as transações
    """
    caminho = _resolver_caminho("transacoes.csv")

    try:
        df = pd.read_csv(caminho)
    except Exception as erro:
        raise ErroCarregamentoDados(
            f"Não foi possível ler transacoes.csv: {erro}."
        ) from erro

    colunas_obrigatorias = {
        "transacao_id",
        "cliente_id",
        "conta_id",
        "data",
        "descricao",
        "categoria",
        "subcategoria",
        "valor",
        "tipo",
        "forma_pagamento",
        "parcelado",
        "parcela_atual",
        "total_parcelas",
        "recorrente",
        "essencial",
        "origem_dado",
    }

    ausentes = colunas_obrigatorias - set(df.columns)

    if ausentes:
        raise ErroCarregamentoDados(
            "Colunas ausentes em transacoes.csv: "
            + ", ".join(sorted(ausentes))
        )

    registros = [
        _normalizar_registro_transacao(
            registro=registro,
            corrigir_inconsistencias=corrigir_inconsistencias,
        )
        for registro in df.to_dict(orient="records")
    ]

    return _validar_lista_modelos(
        registros=registros,
        modelo=Transacao,
        nome_fonte="transacoes.csv",
    )

def carregar_transacoes_cliente(
    cliente_id: str,
    corrigir_inconsistencias: bool= True,
) -> list[Transacao]:
    return [
        transacao
        for transacao in carregar_transacoes(corrigir_inconsistencias=corrigir_inconsistencias)
        if transacao.cliente_id == cliente_id
    ]

def transacoes_para_dataframe(
    transacoes: Iterable[Transacao],
) -> pd.DataFrame:
    """
    Converte objetos Transacao validados em DataFrame para cálculos
    """
    registros = [
        transacao.model_dump(mode="json")
        for transacao in transacoes
    ]

    df = pd.DataFrame(registros)

    if df.empty:
        return df

    df["data"] = pd.to_datetime(df["data"])
    df["valor"] = pd.to_numeric(df["valor"])

    return df

def carregar_transacoes_dataframe(
        cliente_id: str | None = None,
        corrigir_inconsistencias: bool = True
) -> pd.DataFrame:
    """
    Atalho para obter as transações já validadas em formatos DataFrame
    """
    if cliente_id is None:
        transacoes = carregar_transacoes(corrigir_inconsistencias=corrigir_inconsistencias)
    else:
        transacoes = carregar_transacoes_cliente(
            cliente_id=cliente_id,
            corrigir_inconsistencias=corrigir_inconsistencias,
        )

    return transacoes_para_dataframe(transacoes)

# HISTÓRICO DE ATENDIMENTO
def carregar_historico_atendimento() -> list[Atendimento]:
    caminho = _resolver_caminho("historico_atendimento.csv")

    try:
        df = pd.read_csv(caminho)
    except Exception as erro:
        raise ErroCarregamentoDados(
            f"Não foi possível ler historico_atendimento.csv: {erro}"
        ) from erro

    colunas_obrigatorias = {
        "atendimento_id",
        "cliente_id",
        "data",
        "canal",
        "tema",
        "resumo",
        "resolvido",
        "intencao",
    }

    ausentes = colunas_obrigatorias - set(df.columns)

    if ausentes:
        raise ErroCarregamentoDados(
            "Colunas ausentes em historico_atendimento.csv: "
            + ", ".join(sorted(ausentes))
        )

    return _validar_lista_modelos(
        registros=df.to_dict(orient="records"),
        modelo=Atendimento,
        nome_fonte="historico_atendimento.csv",
    )

def carregar_historico_cliente(
    cliente_id: str,
) -> list[Atendimento]:
    return [
        atendimento
        for atendimento in carregar_historico_atendimento()
        if atendimento.cliente_id == cliente_id
    ]

# INTEGRIDADE REFERENCIAL
def validar_integridade_referencial(
    corrigir_inconsistencias: bool = True,
) -> list[str]:
    """
    Valida relacionamentos entre arquivos
    """
    clientes = carregar_clientes()
    contas = carregar_contas()
    metas = carregar_metas()
    dividas = carregar_dividas()
    carregar_produtos()
    transacoes = carregar_transacoes(
        corrigir_inconsistencias=corrigir_inconsistencias
    )
    atendimentos = carregar_historico_atendimento()

    cliente_ids = [cliente.cliente_id for cliente in clientes]
    conta_ids = [conta.conta_id for conta in contas]

    cliente_ids_validos = set(cliente_ids)
    conta_ids_validos = set(conta_ids)

    if len(cliente_ids) != len(cliente_ids_validos):
        raise ErroIntegridadeDados(
            "Existem cliente_id duplicados em clientes.json."
        )

    if len(conta_ids) != len(conta_ids_validos):
        raise ErroIntegridadeDados(
            "Existem conta_id duplicados em contas.json."
        )

    erros: list[str] = []
    avisos: list[str] = []

    for conta in contas:
        if conta.cliente_id not in cliente_ids_validos:
            erros.append(
                f"A conta {conta.conta_id} referencia cliente inexistente "
                f"{conta.cliente_id}."
            )

    for meta in metas:
        if meta.cliente_id not in cliente_ids_validos:
            erros.append(
                f"A meta {meta.meta_id} referencia cliente inexistente "
                f"{meta.cliente_id}."
            )

    for divida in dividas:
        if divida.cliente_id not in cliente_ids_validos:
            erros.append(
                f"A dívida {divida.divida_id} referencia cliente inexistente "
                f"{divida.cliente_id}."
            )

    contas_por_id = {
        conta.conta_id: conta
        for conta in contas
    }

    for transacao in transacoes:
        if transacao.cliente_id not in cliente_ids_validos:
            erros.append(
                f"A transação {transacao.transacao_id} referencia cliente "
                f"inexistente {transacao.cliente_id}."
            )

        if transacao.conta_id not in conta_ids_validos:
            erros.append(
                f"A transação {transacao.transacao_id} referencia conta "
                f"inexistente {transacao.conta_id}."
            )
            continue

        conta = contas_por_id[transacao.conta_id]

        if conta.cliente_id != transacao.cliente_id:
            erros.append(
                f"A transação {transacao.transacao_id} pertence ao cliente "
                f"{transacao.cliente_id}, mas usa a conta {transacao.conta_id} "
                f"do cliente {conta.cliente_id}."
            )

    for atendimento in atendimentos:
        if atendimento.cliente_id not in cliente_ids_validos:
            erros.append(
                f"O atendimento {atendimento.atendimento_id} referencia "
                f"cliente inexistente {atendimento.cliente_id}."
            )

    for cliente in clientes:
        metas_cliente = [
            meta
            for meta in metas
            if meta.cliente_id == cliente.cliente_id
        ]

        if not metas_cliente:
            avisos.append(
                f"O cliente {cliente.cliente_id} não possui metas cadastradas."
            )

    if erros:
        raise ErroIntegridadeDados(
            "Foram encontrados erros de integridade:\n- "
            + "\n- ".join(erros)
        )

    return avisos

# CONTEXTO COMPLETO
def carregar_contexto_cliente(
    cliente_id: str,
    corrigir_inconsistencias: bool = True,
    validar_integridade: bool = True,
) -> ContextoCliente:
    """
    Carrega todos os dados relacionados a um cliente
    """
    if validar_integridade:
        validar_integridade_referencial(corrigir_inconsistencias=corrigir_inconsistencias)

    cliente = carregar_cliente(cliente_id)

    return ContextoCliente(
        cliente=cliente,
        contas=carregar_contas_cliente(cliente_id),
        metas=carregar_metas_cliente(cliente_id),
        dividas=carregar_dividas_cliente(cliente_id),
        transacoes=carregar_transacoes_cliente(
            cliente_id=cliente_id,
            corrigir_inconsistencias=corrigir_inconsistencias,
        ),
        historico_atendimento=carregar_historico_cliente(cliente_id),
    )

def listar_clientes_para_interface() -> list[dict[str, str]]:
    """
    Retorna somente os campos necessários para um seletor de interface
    """
    return [
        {
            "cliente_id": cliente.cliente_id,
            "nome": cliente.nome_ficticio,
        }
        for cliente in carregar_clientes()
    ]

# EXECUTAR DIAGNÓSTICO
def main() -> None:
    """
    Diagnóstico simples
    """
    avisos = validar_integridade_referencial(corrigir_inconsistencias=True)

    clientes = listar_clientes_para_interface()
    produtos = carregar_produtos()

    print("Base carregada e validada com sucesso.")
    print(f"Clientes encontrados: {len(clientes)}")
    print(f"Produtos financeiros encontrados: {len(produtos)}")

    for item in clientes:
        contexto = carregar_contexto_cliente(
            cliente_id=item["cliente_id"],
            validar_integridade=False,
        )

        print(
            f"- {item['cliente_id']} | {item['nome']} | "
            f"{len(contexto.transacoes)} transações | "
            f"{len(contexto.metas)} metas | "
            f"{len(contexto.dividas)} dívidas"
        )

    if avisos:
        print("\nAvisos:")
        for aviso in avisos:
            print(f"- {aviso}")

if __name__ == "__main__":
    main()