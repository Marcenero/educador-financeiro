from __future__ import annotations

import unicodedata
from typing import Any

import pandas as pd

COLUNAS_OBRIGATORIAS = {
    "data",
    "descricao",
    "categoria",
    "subcategoria",
    "valor",
    "tipo",
    "recorrente",
    "essencial",
    "forma_pagamento",
}

class ErroServicoTransacoes(ValueError):
    """Erro de validação ou cálculo relacionado às transações."""

def _validar_dataframe(transacoes: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(transacoes, pd.DataFrame):
        raise ErroServicoTransacoes("transacoes deve ser um DataFrame do Pandas.")

    ausentes = COLUNAS_OBRIGATORIAS - set(transacoes.columns)
    if ausentes:
        raise ErroServicoTransacoes(
            "Colunas ausentes no DataFrame: "
            + ", ".join(sorted(ausentes))
        )

    dados = transacoes.copy()
    dados["data"] = pd.to_datetime(dados["data"], errors="coerce")
    dados["valor"] = pd.to_numeric(dados["valor"], errors="coerce")

    if dados["data"].isna().any():
        raise ErroServicoTransacoes("Existem datas inválidas nas transações.")

    if dados["valor"].isna().any():
        raise ErroServicoTransacoes("Existem valores inválidos nas transações.")

    if (dados["valor"] <= 0).any():
        raise ErroServicoTransacoes("Todos os valores de transação devem ser positivos.")

    dados["tipo"] = (
        dados["tipo"]
        .astype(str)
        .map(_normalizar_texto)
    )

    tipos_invalidos = set(dados["tipo"].unique()) - {"entrada", "saida"}

    if tipos_invalidos:
        raise ErroServicoTransacoes(
            "Tipos de movimentação inválidos: "
            + ", ".join(sorted(tipos_invalidos))
        )

    dados["categoria"] = (
    dados["categoria"]
        .astype(str)
        .map(_normalizar_texto)
    )

    dados["subcategoria"] = (
        dados["subcategoria"]
        .astype(str)
        .map(_normalizar_texto)
    )

    dados["recorrente"] = (
        dados["recorrente"]
        .map(_normalizar_booleano)
    )

    dados["essencial"] = (
        dados["essencial"]
        .map(_normalizar_booleano)
    )

    return dados

def filtrar_periodo(
    transacoes: pd.DataFrame,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> pd.DataFrame:
    dados = _validar_dataframe(transacoes)

    data_inicial = (
        data_inicial.strip()
        if data_inicial and data_inicial.strip()
        else None
    )

    data_final = (
        data_final.strip()
        if data_final and data_final.strip()
        else None
    )

    try:
        inicio = (
            pd.Timestamp(data_inicial)
            if data_inicial
            else None
        )

        fim = (
            pd.Timestamp(data_final)
            if data_final
            else None
        )

    except (ValueError, TypeError) as erro:
        raise ErroServicoTransacoes(
            "As datas devem estar no formato AAAA-MM-DD."
        ) from erro

    if (
        inicio is not None
        and fim is not None
        and inicio > fim
    ):
        raise ErroServicoTransacoes(
            "data_inicial não pode ser posterior "
            "a data_final."
        )

    if inicio is not None:
        dados = dados[
            dados["data"] >= inicio
        ]

    if fim is not None:
        dados = dados[
            dados["data"] <= fim
        ]

    return dados.copy()

def calcular_resumo_financeiro(
    transacoes: pd.DataFrame,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    dados = filtrar_periodo(
        transacoes,
        data_inicial,
        data_final,
    )

    entradas = float(
        dados.loc[dados["tipo"] == "entrada", "valor"].sum()
    )
    saidas = float(
        dados.loc[dados["tipo"] == "saida", "valor"].sum()
    )
    saldo = entradas - saidas

    taxa_poupanca = (
        saldo / entradas * 100
        if entradas > 0
        else None
    )

    return {
        "periodo_inicial": (
            dados["data"].min().strftime("%d/%m/%Y")
            if not dados.empty
            else None
        ),
        "periodo_final": (
            dados["data"].max().strftime("%d/%m/%Y")
            if not dados.empty
            else None
        ),
        "entradas": round(entradas, 2),
        "saidas": round(saidas, 2),
        "saldo": round(saldo, 2),
        "taxa_poupanca_percentual": (
            round(taxa_poupanca, 2)
            if taxa_poupanca is not None
            else None
        ),
        "quantidade_transacoes": int(len(dados)),
    }

def calcular_gastos_por_categoria(
    transacoes: pd.DataFrame,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, float]:
    dados = filtrar_periodo(
        transacoes,
        data_inicial,
        data_final,
    )

    resultado = (
        dados[dados["tipo"] == "saida"]
        .groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
        .to_dict()
    )

    return {
        str(categoria): float(valor)
        for categoria, valor in resultado.items()
    }

def consultar_gastos_categoria(
    transacoes: pd.DataFrame,
    categoria: str,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    """
    Consulta os gastos de uma categoria específica.

    A comparação ignora diferenças de maiúsculas, espaços e acentos.
    """
    if not categoria or not categoria.strip():
        raise ErroServicoTransacoes(
            "A categoria deve ser informada."
        )

    categoria_normalizada = _normalizar_texto(
        categoria
    )

    dados = filtrar_periodo(
        transacoes,
        data_inicial,
        data_final,
    )

    if dados.empty:
        periodo_inicial = None
        periodo_final = None
        periodo_formatado = None
    else:
        periodo_inicial = (
            dados["data"]
            .min()
            .strftime("%d/%m/%Y")
        )

        periodo_final = (
            dados["data"]
            .max()
            .strftime("%d/%m/%Y")
        )

    periodo_formatado = (
        f"{periodo_inicial} a {periodo_final}"
    )

    saidas = dados[
        dados["tipo"] == "saida"
    ].copy()

    categorias_disponiveis = sorted(
        saidas["categoria"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    categoria_encontrada = (
        categoria_normalizada
        in categorias_disponiveis
    )

    registros = saidas[
        saidas["categoria"]
        == categoria_normalizada
    ].copy()

    return {
        "categoria_consultada": categoria,
        "categoria_normalizada": categoria_normalizada,
        "categoria_encontrada": categoria_encontrada,
        "valor_total": round(
            float(registros["valor"].sum()),
            2,
        ),
        "quantidade_transacoes": int(
            len(registros)
        ),
        "categorias_disponiveis": categorias_disponiveis,
        "transacoes": [
            {
                "data": linha.data.date().isoformat(),
                "descricao": linha.descricao,
                "subcategoria": linha.subcategoria,
                "valor": round(
                    float(linha.valor),
                    2,
                ),
                "forma_pagamento": (
                    linha.forma_pagamento
                ),
            }
            for linha in (
                registros
                .sort_values("data")
                .itertuples()
            )
        ],
    }

def listar_maiores_gastos(
    transacoes: pd.DataFrame,
    quantidade: int = 5,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> list[dict[str, Any]]:
    if quantidade < 1:
        raise ErroServicoTransacoes("quantidade deve ser maior que zero.")

    quantidade = min(quantidade, 20)

    dados = filtrar_periodo(
        transacoes,
        data_inicial,
        data_final,
    )

    maiores = (
        dados[dados["tipo"] == "saida"]
        .nlargest(quantidade, "valor")
    )

    return [
        {
            "data": linha.data.date().isoformat(),
            "descricao": linha.descricao,
            "categoria": linha.categoria,
            "subcategoria": linha.subcategoria,
            "valor": round(float(linha.valor), 2),
        }
        for linha in maiores.itertuples()
    ]

def listar_gastos_recorrentes(
    transacoes: pd.DataFrame,
) -> list[dict[str, Any]]:
    dados = _validar_dataframe(transacoes)

    recorrentes = dados[
        (dados["tipo"] == "saida")
        & (dados["recorrente"])
    ].copy()

    agrupado = (
        recorrentes.groupby(
            ["descricao", "categoria"],
            as_index=False,
        )
        .agg(
            valor_total=("valor", "sum"),
            valor_medio=("valor", "mean"),
            ocorrencias=("valor", "count"),
        )
        .sort_values("valor_total", ascending=False)
    )

    return [
        {
            "descricao": linha.descricao,
            "categoria": linha.categoria,
            "valor_total": round(float(linha.valor_total), 2),
            "valor_medio": round(float(linha.valor_medio), 2),
            "ocorrencias": int(linha.ocorrencias),
        }
        for linha in agrupado.itertuples()
    ]

def calcular_percentual_despesas_essenciais(
    transacoes: pd.DataFrame,
) -> dict[str, float | None]:
    dados = _validar_dataframe(transacoes)
    saidas = dados[dados["tipo"] == "saida"]

    total_saidas = float(saidas["valor"].sum())
    total_essenciais = float(
        saidas.loc[
            saidas["essencial"],
            "valor",
        ].sum()
    )

    percentual = (
        total_essenciais / total_saidas * 100
        if total_saidas > 0
        else None
    )

    return {
        "despesas_totais": round(total_saidas, 2),
        "despesas_essenciais": round(total_essenciais, 2),
        "percentual_essenciais": (
            round(percentual, 2)
            if percentual is not None
            else None
        ),
    }

def comparar_meses(
    transacoes: pd.DataFrame,
) -> list[dict[str, Any]]:
    dados = _validar_dataframe(transacoes)
    dados["mes"] = dados["data"].dt.to_period("M").astype(str)

    entradas = (
        dados[dados["tipo"] == "entrada"]
        .groupby("mes")["valor"]
        .sum()
    )

    saidas = (
        dados[dados["tipo"] == "saida"]
        .groupby("mes")["valor"]
        .sum()
    )

    meses = sorted(set(entradas.index) | set(saidas.index))
    resultado = []

    for mes in meses:
        valor_entrada = float(entradas.get(mes, 0))
        valor_saida = float(saidas.get(mes, 0))

        resultado.append(
            {
                "mes": mes,
                "entradas": round(valor_entrada, 2),
                "saidas": round(valor_saida, 2),
                "saldo": round(
                    valor_entrada - valor_saida,
                    2,
                ),
            }
        )

    return resultado

def _normalizar_texto(valor: Any) -> str:
    """
    Normaliza textos para comparação.

    Remove espaços, converte para minúsculas e retira acentos.
    """
    texto = str(valor).strip().lower()

    texto_sem_acentos = unicodedata.normalize(
        "NFKD",
        texto,
    )

    return "".join(
        caractere
        for caractere in texto_sem_acentos
        if not unicodedata.combining(caractere)
    )

def _normalizar_booleano(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor

    texto = _normalizar_texto(valor)

    if texto in {"true", "1", "sim", "s"}:
        return True

    if texto in {"false", "0", "nao", "n"}:
        return False

    raise ErroServicoTransacoes(
        f"Valor booleano inválido: {valor!r}"
    )