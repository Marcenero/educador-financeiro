# Base de conhecimento

## 1. Objetivo

A base de conhecimento do FinGuia reúne os dados estruturados usados pelas ferramentas do agente.

Nesta versão, os dados são totalmente fictícios e servem para:
* Demonstrar o funcionamento do agente
* Testar consultas financeiras
* Validar isolamento entre clientes
* Avaliar cálculos
* Evitar o uso de informações bancárias reais

## 2. Fontes de dados

| **Arquivo**  | **Formato** | **Conteúdo** |
| ----------- | :-----------: | :-----------: |
| clientes.json | JSON | Cadastro fictício dos clientes |
| contas.json | JSON | Contas associadas aos clientes |
| metas.json | JSON | Metas financeiras |
| dividas.json | JSON | Dívidas cadastradas |
| transacoes.csv | CSV | Entradas e saídas financeiras |
| historico_atendimento.csv | CSV | Histórico de interações |
| produtos_financeiros.json | JSON | Produtos usados em explicações educativas |

## 3. Relacionamento entre os dados

O campo principal de relacionamento é:

`cliente_id`

Exemplo:

`CLI-0001`

O identificador permite filtrar:
* Contas
* Transações
* Metas
* Dívidas
* Histórico de atendimento

##### O agente não deve receber liberdade para substituir esse identificador durante uma consulta. O valor é definido pela sessão ou pelo perfil selecionado.

## 4. Clientes

O arquivo `clientes.json` representa perfis fictícios.

Estrutura esperada:

```
[
    {
        "cliente_id": "CLI-0001",
        "nome_ficticio": "João Silva",
        "faixa_etaria": "25-34",
        "perfil_financeiro": "moderado"
    }
]
```

Os campos podem variar conforme a evolução do projeto, mas o `cliente_id` deve ser único.

## 5. Contas

O arquivo `contas.json` pode armazenar informações como:

```
[
    {
        "conta_id": "CONTA-0001",
        "cliente_id": "CLI-0001",
        "tipo": "conta_corrente",
        "instituicao_ficticia": "Banco Exemplo",
        "ativa": "true"
    }
]
```

Regras:
* Uma conta pertence a somente um cliente
* Um cliente pode possuir várias contas
* Contas inativas podem ser mantidas para histórico
* Nomes de instituições devem ser fictícios no conjunto demonstrativo

## 6. Transações

O arquivo `transacoes.csv` contém lançamentos financeiros.

Colunas esperadas:

| **Coluna**  | **Descrição** |
| ----------- | :-----------: |
| transacao_id | Identificador da transação |
| cliente_id | Cliente associado |
| conta_id | Conta associada |
| data | Data da transação |
| descricao | Descrição inventada |
| tipo | Entrada ou saída |
| categoria | Categoria normalizada |
| subcategoria | Detalhamento |
| valor | Valor positivo da operação |
| forma_pagamento | Meio utilizado para pagamento |
| recorrente | Indicador booleano |

Exemplo:
```
transacao_id,cliente_id,data,descricao,tipo,categoria,valor
TRX-0001,CLI-0001,2026-01-07,Supermercado,saida,alimentacao,183.50
```

### 6.1 Categorias

As categorias são armazenadas preferencialmente sem acentos:
* `alimentacao`
* `compras`
* `investimento`
* `lazer`
* `moradia`
* `saude`
* `transporte`

A entrada do usuário é normalizada. Portanto:

`alimentação, ALIMENTACAO, Alimentacao`

devem ser interpretadas como:

`alimentacao`

### 6.2 Tipos

Valores esperados:
* `entrada`
* `saida`

### 6.3 Cálculo do saldo

`saldo = total de entradas- total de saídas`

O cálculo é realizado em Python, e não pelo modelo de linguagem.

### 6.4 Período

Quando o usuário não informa datas, o sistema considera todo o período disponível para o cliente.

As datas apresentadas ao usuário devem usar:

`DD/MM/AAAA`

## 7. Metas financeiras

O arquivo `metas.json` contém objetivos financeiros.

Exemplo:
```
[
    {
        "meta_id": "META-0001",
        "cliente_id": "CLI-0001",
        "nome": "Completar reserva de emergência",
        "categoria": "reserva_emergencia",
        "valor_alvo": 18000.0,
        "valor_atual": 10000.0,
        "prazo": "2027-06",
        "prioridade": "alta",
        "status": "em_andamento"
    }
]
```

### 7.1 Valor faltante

`valor_faltante = máximo(valor_alvo - valor_atual, 0)`

### 7.2 Percentual concluído

`percentual = valor_atual / valor_alvo * 100`

Quando `valor_alvo` for zero, o sistema deve evitar divisão por zero.

### 7.3 Simulação de contribuição

Uma simulação pode calcular quanto guardar mensalmente até o prazo.

A simulação deve ser identificada como:

`simulação educativa`

Ela não deve ser apresentada como garantia de resultado.

## 8. Dívidas

O arquivo `dividas.json` representa obrigações financeiras inventadas.

Exemplo:

```
[
    {
        "divida_id": "DIV-0001",
        "cliente_id": "CLI-0001",
        "tipo": "cartao_credito",
        "saldo_devedor": 2500.0,
        "taxa_mensal_percentual": 12.5,
        "parcela_atual": 3,
        "total_parcelas": 10,
        "status": "ativa"
    }
]
```

Informações úteis:
* Saldo devedor
* Taxa
* Parcela atual
* Quantidade total de parcelas
* Vencimento
* Status

O agente pode explicar prioridades educativas, mas não deve ordenar uma decisão sem contexto suficiente.

## 9. Produtos financeiros

O arquivo `produtos_financeiros.json` contém opções educativas.

Exemplo:

```
[
    {
        "produto_id": "PROD-0001",
        "nome": "Produto conservador fictício",
        "categoria": "renda_fixa",
        "liquidez": "diaria",
        "risco": "baixo",
        "garantia": "depende das regras do produto",
        "adequado_para": ["reserva_emergencia"]
    }
]
```

Regras:
* Apresentar produtos como possibilidades educativas
* Explicar riscos e limitações
* Não prometer retorno
* Não declarar que um produto é o melhor
* Não dar ordem direta de compra
* Não inventar taxas ausentes

## 10. Histórico de atendimento

O arquivo `historico_atendimento.csv` pode ser usado para:
* Registrar interações fictícias
* Avaliar perguntas frequentes
* Identificar padrões de dúvida
* Construir testes
* Melhorar prompts

Ele não substitui a auditoria atual em `logs/interacoes.jsonl`

## 11. Carregamento dos dados

O módulo `data_loader.py` centraliza a leitura.

Responsabilidades:
* Localizar os arquivos
* Interpretar JSON e CSV
* Validar existência
* Converter tipos
* Aplicar schemas
* Retornar estruturas consistentes
* Produzir erros claros

Exemplo conceitual:

```
def carregar_transacoes() -> pd.DataFrame:
    ...
```

## 12. Schemas

O arquivo `schemas.py` utiliza Pydantic para representar entidades;

Exemplos de modelos:
* `Cliente`
* `Conta`
* `MetaFinanceira`
* `Divida`
* `Produto financeiro`

Benefícios:

* Validação de campos obrigatórios
* Conversão de tipos
* Mensagens de erro
* Documentação de estruturas
* Redução de inconsistências

## 13. Serviços determinísticos

O serviços executam a lógica financeira.

Exemplos:
* `servico_transacoes.py`
* `servico_metas.py`
* `servico_dividas.py`
* `servico_produtos.py`

O modelo de linguagem não deve calcular diretamente valores que podem ser obtidos por código.

Fluxo:

pergunta

&darr;

ferramenta

&darr;

serviço Python

&darr;

resultado estruturado

&darr;

modelo explica o resultado

## 14. Fontes nas respostas

Cada ferramenta retorna um campo:

```
{
    "fonte": "transacoes.csv",
    "tipo_resultado": "calculo_deterministico"
}
```

A resposta final pode apresentar:

`Fontes: transacoes.csv`

Tipos de resultado sugeridos:
* `fato_registrado`
* `calculo_deterministico`
* `simulacao_educativa`
* `conteudo_educativo`

## 15. Isolamento

O isolamento depende de três medidas:

1. O perfil define o `cliente_id`
2. As ferramentas são criadas para esse cliente
3. A segurança bloqueia identificadores diferentes

O perfil visitante não recebe ferramentas pessoais.

## 16. Qualidade dos dados

Antes de executar o agente, devem ser verificados:
* Identificadores duplicados
* Valores negativos indevidos
* Datas inválidas
* Categorias vazias
* Relacionamento com cliente inexistente
* Relacionamento com conta inexistente
* Metas com alvo inválido
* Dívidas com parcelas inconsistentes
* Booleanos lidos incorretamente
* Campos obrigatórios ausentes

## 17. Limitações

* Os dados não representam pessoas reais
* A variedade de perfis é pequena
* Não existem atualizações automáticas
* Categorias dependem do conjunto definido
* Produtos não refletem necessariamente ofertas atuais
* Não existe histórico bancário em tempo real
* Os valores servem apenas para validação do MVP