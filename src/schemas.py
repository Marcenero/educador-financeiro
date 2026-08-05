from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ENUMS
class TipoRenda(str, Enum):
    FIXA = "fixa"
    VARIAVEL = "variavel"
    MISTA = "mista"

class PerfilInvestidor(str, Enum):
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    ARROJADO = "arrojado"

class NivelConhecimento(str, Enum):
    INICIANTE = "iniciante"
    BASICO = "basico"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"

class HorizonteInvestimento(str, Enum):
    CURTO_PRAZO = "curto_prazo"
    MEDIO_PRAZO = "medio_prazo"
    LONGO_PRAZO = "longo_prazo"

class PrioridadeMeta(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

class StatusMeta(str, Enum):
    PLANEJADA = "planejada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    PAUSADA = "pausada"
    CANCELADA = "cancelada"

class StatusDivida(str, Enum):
    ATIVA = "ativa"
    QUITADA = "quitada"
    RENEGOCIADA = "renegociada"
    ATRASADA = "atrasada"

class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"

# MODELO BASE
class ModeloBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

# CLIENTES
class RendaCliente(ModeloBase):
    tipo: TipoRenda
    renda_mensal_media: float = Field(ge=0)
    renda_extra_media: float = Field(default=0, ge=0)

class PerfilFinanceiro(ModeloBase):
    perfil_investidor: PerfilInvestidor
    conhecimento_financeiro: NivelConhecimento
    tolerancia_risco: int = Field(ge=1, le=3)
    aceita_perda_temporaria: bool
    horizonte_investimento: HorizonteInvestimento

class SituacaoFinanceira(ModeloBase):
    patrimonio_total: float = Field(ge=0)
    reserva_emergencia_atual: float = Field(ge=0)
    divida_total: float = Field(ge=0)
    limite_cartao: float = Field(ge=0)

class PreferenciasCliente(ModeloBase):
    tom: Literal["didatico", "acolhedor", "direto", "formal", "informal"]
    canal_preferido: Literal["chat", "aplicativo", "whatsapp", "email", "telefone"]
    frequencia_alertas: Literal["diaria", "semanal", "quinzenal", "mensal", "nenhuma"]

class Cliente(ModeloBase):
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    nome_ficticio: str = Field(min_length=3, max_length=100)
    idade: int = Field(ge=18, le=120)
    profissao: str = Field(min_length=2, max_length=100)
    estado_civil: Literal["solteiro", "solteira", "casado", "casada", "divorciado", "divorciada", "viuvo", "viuva", "uniao_estavel"]
    dependentes: int = Field(ge=0, le=20)
    cidade: str = Field(min_length=2, max_length=100)
    uf: str = Field(min_length=2, max_length=2)
    renda: RendaCliente
    perfil_financeiro: PerfilFinanceiro
    situacao_financeira: SituacaoFinanceira
    objetivo_principal: str = Field(min_length=5, max_length=300)
    preferencias: PreferenciasCliente

    @field_validator("uf")
    @classmethod
    def normalizar_uf(cls, valor: str) -> str:
        return valor.upper()

# CONTAS
class Conta(ModeloBase):
    conta_id: str = Field(pattern=r"^(CONTA|CARTAO)-\d{4}$")
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    tipo: Literal["conta_corrente", "conta_digital", "cartao_credito", "conta_poupanca", "carteira_digital"]
    instituicao_ficticia: str = Field(min_length=2, max_length=100)
    status: Literal["ativa", "ativo", "inativa", "inativo", "bloqueada", "bloqueado"]

# METAS
class MetaFinanceira(ModeloBase):
    meta_id: str = Field(pattern=r"^META-\d{4}$")
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    nome: str = Field(min_length=3, max_length=150)
    categoria: Literal["reserva_emergencia", "moradia", "trabalho", "quitacao_divida", "educacao", "viagem", "aposentadoria", "outros"]
    valor_alvo: float = Field(gt=0)
    valor_atual: float = Field(ge=0)
    prazo: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    prioridade: PrioridadeMeta
    status: StatusMeta

    @model_validator(mode="after")
    def validar_progresso(self):
        if self.valor_atual > self.valor_alvo and self.status != StatusMeta.CONCLUIDA:
            raise ValueError("valor_atual não pode superar valor_alvo sem status 'concluida'.")
        if self.status == StatusMeta.CONCLUIDA and self.valor_atual < self.valor_alvo:
             raise ValueError("Meta concluída deve possuir valor_atual maior ou igual ao valor_alvo.")

        return self

# DÍVIDAS
class Divida(ModeloBase):
    divida_id: str = Field(pattern=r"^DIV-\d{4}$")
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    tipo: Literal["parcelamento_eletronico", "cartao_rotativo_parcelado", "emprestimo_pessoal", "financiamento", "cheque_especial", "outros"]
    saldo_devedor: float = Field(ge=0)
    taxa_mensal: float | None = Field(default=None, ge=0, le=1)
    parcelas_restantes: int = Field(ge=0)
    parcela_mensal: float = Field(ge=0)
    status: StatusDivida

    @model_validator(mode="after")
    def validar_divida_quitada(self):
        if self.status == StatusDivida.QUITADA:
            if self.saldo_devedor != 0:
                raise ValueError("Dívida quitada deve ter saldo_devedor igual a zero.")
            if self.parcelas_restantes != 0:
                raise ValueError("Dívida quitada deve ter parcelas_restantes igual a zero.")

        return self

# TRANSAÇÕES
class Transacao(ModeloBase):
    transacao_id: str = Field(pattern=r"^TRX-\d{5}$")
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    conta_id: str = Field(pattern=r"^(CONTA|CARTAO)-\d{4}$")
    data: date
    descricao: str = Field(min_length=2, max_length=150)
    categoria: str = Field(min_length=2, max_length=50)
    subcategoria: str = Field(min_length=2, max_length=80)
    valor: float = Field(gt=0)
    tipo: TipoMovimentacao
    forma_pagamento: str = Field(min_length=2, max_length=50)
    parcelado: bool
    parcela_atual: int | None = Field(default=None, ge=1)
    total_parcelas: int | None = Field(default=None, ge=1)
    recorrente: bool
    essencial: bool
    origem_dado: Literal["sintetico", "manual", "hugging_face", "importado"]

    @model_validator(mode="after")
    def validar_parcelamento(self):
        if not self.parcelado:
            if self.parcela_atual is not None or self.total_parcelas is not None:
                raise ValueError("Transação não parcelada não pode ter parcela_atual ou total_parcelas.")

            return self

        if self.parcela_atual is None or self.total_parcelas is None:
            raise ValueError("Transação parcelada deve informar parcela_atual e total_parcelas.")

        if self.parcela_atual > self.total_parcelas:
            raise ValueError("parcela_atual não pode ser maior que total_parcelas.")

        return self

# HISTÓRICO DE ATENDIMENTO
class Atendimento(ModeloBase):
    atendimento_id: str = Field(pattern=r"^ATD-\d{4}$")
    cliente_id: str = Field(pattern=r"^CLI-\d{4}$")
    data: date
    canal: Literal["chat", "email", "telefone", "aplicativo", "whatsapp"]
    tema: str = Field(min_length=2, max_length=150)
    resumo: str = Field(min_length=5, max_length=500)
    resolvido: Literal["sim", "nao"]
    intencao: Literal["orientacao", "analise_gastos", "metas", "orcamento", "emergencia", "dividas", "produtos", "educacao_financeira"]

# CONTEXTO COMPLETO DO CLIENTE
class ContextoCliente(ModeloBase):
    cliente: Cliente
    contas: list[Conta] = Field(default_factory=list)
    metas: list[MetaFinanceira] = Field(default_factory=list)
    dividas: list[Divida] = Field(default_factory=list)
    transacoes: list[Transacao] = Field(default_factory=list)
    historico_atendimento: list[Atendimento] = Field(default_factory=list)