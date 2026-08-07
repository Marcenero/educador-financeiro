# Documentação do Agente FinGuia

## 1. Visão geral

O FinGuia é um agente local de educação financeira desenvolvido em Python. Seu objetivo é ajudar usuários a compreender informações financeiras pessoais de forma clara, educativa e segura.

O projeto combina:
* Modelo de linguagem executado localmente com Ollama
* Agente e ferramentas com LangChain
* Memória conversacional com LangGraph
* Serviços determinísticos em Python
* Interface em Streamlit
* Validações de segurança
* Auditoria das interações
* Base de dados fictícia para testes

O FinGuia não realiza operações financeiras, não substitui orientação profissional e não promete rentabilidade.

## 2. Objetivo do projeto

O agente foi projetado para responder perguntas como:
* Qual foi meu saldo no período?
* Quanto gastei com alimentação?
* Quais são minhas metas financeiras?
* Tenho dívidas cadastradas?
* O que é uma reserva de emergência?
* Como posso organizar melhor meu orçamento?
* Quais opções educativas podem ser consideradas para uma meta?

O sistema diferencia dois tipos de uso:
1. Cliente cadastrado: pode consultar os próprios dados
2. Visitante: pode fazer perguntas educativas gerais, mas não possui acesso a dados pessoais

## 3. Escopo do MVP

O MVP contempla:
* 3 perfis de clientes fictícios
* 1 perfil visitante
* Consulta de transações
* Cálculo de entradas, saídas e saldo
* Consulta de gastos por categoria
* Consulta de metas financeiras
* Consulta de dívidas
* Consulta educativa de produtos financeiros
* Memória conversacional por perfil
* Isolamento entre clientes
* Auditoria de perguntas, respostas, fontes e ferramentas
* Interface conversacional em navegador

Não fazem parte do MVP:
* Autenticação real
* Conexão com banco de dados
* Integração bancária
* Transferências
* Compra ou venda de ativos
* Aconselhamento financeiro personalizado regulado
* Persistência de memória após reiniciar aplicação
* Uso de dados financeiros reais

## 4. Arquitetura

Usuário

&darr;

Interface Streamlit

&darr;

Validação de entrada

&darr;

Agente LangChain

&darr;

Memória LangGraph

&darr;

Ferramentas do cliente

&darr;

Serviços determinísticos

&darr;

Arquivos com dados inventados

&darr;

Validação de saída

&darr;

Auditoria

&darr;

Resposta ao usuário

### 4.1 Camadas

| **Camada**  | **Responsabilidade** |
| ----------- | :-----------: |
| Interface | Receber perguntas e exibir respostas |
| Agente | Decidir quando responder diretamente ou usar ferramentas |
| Prompt | Definir comportamento, limites e linguagem |
| Ferramentas | Disponibilizar operações estruturadas para o agente |
| Serviços | Executar cálculos determinísticos |
| Dados | Armazenar informações |
| Segurança | Validar entrada, saída e isolamento |
| Memória | Preservar contexto por sessão e perfil |
| Auditoria | Registrar execução, ferramentas, fontes e status |

## 5. Estrutura sugerida
## Estrutura do projeto

```
educador-financeiro/
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
├── dados/
│   ├── clientes.json
│   ├── contas.json
│   ├── metas.json
│   ├── dividas.json
│   ├── transacoes.csv
│   ├── historico_atendimento.csv
│   ├── produtos_financeiros.json
│   └── resumo_validacao.json
├── docs/
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
├── src/
│   ├── app.py
│   ├── agent.py
│   ├── auditoria.py
│   ├── data_loader.py
│   ├── diagnostico_ollama.py
│   ├── memoria.py
│   ├── model_config.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── seguranca.py
│   ├── teste_agente.py
│   ├── teste_ollama.py
│   ├── ferramentas/
│   │   ├── ferramenta_dividas.py
│   │   ├── ferramenta_metas.py
│   │   ├── ferramenta_produtos.py
│   │   ├── ferramenta_transacoes.py
│   │   └── toolkit.py
│   └── servicos/
│       ├── servico_dividas.py
│       ├── servico_metas.py
│       ├── servico_produtos.py
│       └── servico_transacoes.py
└── testes/
    ├── conftest.py
    ├── teste_app.py
    ├── teste_auditoria.py
    ├── teste_data_loader.py
    ├── teste_ferramentas.py
    ├── teste_fluxos_e2e.py
    ├── teste_integracao_agente.py
    ├── teste_memoria.py
    ├── teste_prompts.py
    ├── teste_seguranca.py
    ├── teste_servico_dividas.py
    ├── teste_servico_metas.py
    ├── teste_servico_produtos.py
    ├── teste_servico_transacoes.py
    └── teste_unidade_agente.py
```

## 6. Tecnologias

| **Tecnologia**  | **Uso** |
| ----------- | :-----------: |
| Python | Linguagem principal |
| LangChain | Criação do agente e das ferramentas |
| LangGraph | Memória de curto prazo |
| Ollama | Execução local do modelo |
| Qwen 3:4b Instruct | Modelo de linguagem do MVP |
| Streamlit | Criação de interface |
| Pydantic | Validação de estruturas de dados |
| Pandas | Leitura e análise de transações |
| Pytest | Testes automatizados |
| JSON/CSV | Persistência dos dados |

## 7. Configuração do ambiente

### 7.1 Criar ambiente virtual

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 7.2 Instalar dependências

```
python -m pip install -r requirements.txt
```

Exemplo de dependências:
```
langchain
langchain-core
langchain-ollama
langgraph
pandas
pydantic
python-dotenv
streamlit
pytest
```

### 7.3 Configurar o .env

```
OLLAMA_MODEL=qwen3:4b-instruct
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEMPERATURE=0
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_PREDICT=500

AUDITORIA_INCLUIR_CONTEUDO_TRUE=true

# Para evitar salvar perguntas e respostas completas:
AUDITORIA_INCLUIR_CONTEUDO_TRUE=false

```

### 7.4 Preparar o Ollama

```
ollama pull qwen3:4b-instruct
ollama serve
```

## 8. Execução

### 8.1 Teste em terminal

```
python src/teste_agente.py
```

### 8.2 Interface Streamlit

```
python -m streamlit run src/app.py
```

## 9. Perfis disponíveis

| **Perfil**  | **Tipo** | **Acesso** |
| ----------- | :-----------: | :-----------: |
| CLI-0001 |  Cliente fictício | Próprios dados |
| CLI-0002 |  Cliente fictício | Próprios dados |
| CLI-0003 |  Cliente fictício | Próprios dados |
| VISITANTE | Não cliente | Apenas conteúdo educativo |

##### O seletor de perfis é adequado apenas para demonstração com dados inventados; Em produção, o identificador do cliente deve vir de autenticação e autorização reais.

## 10. Ferramentas do agente

### 10.1 Transações

Possíveis operações:
* Resumo financeiro
* Gastos por categoria
* Consulta por período
* Identificação de categorias disponíveis

### 10.2 Metas

Possíveis operações:
* Listar metas
* Calcular percentual concluído
* Calcular valor faltante
* Simular contribuição mensal educativa

### 10.3 Dívidas

Possíveis operações:
* Listar dívidas
* Identificar saldo devedor
* Comparar taxas
* Organizar prioridades educativas

### 10.4 Produtos

Possíveis operações:
* Listar produtos cadastrados
* Filtrar opções por objetivo
* Apresentar características e riscos
* Evitar recomendação direta de compra

## 11. Memória conversacional

A memória usa um identificador composto por:

```
sessão do navegador + perfil
```

Exemplo:

```
9c0f7d...:CLI-0001
9c0f7d...:VISITANTE
```

Isso impede que o contexto de um perfil seja usado para outros perfis cadastrados ou visitante

A implementação atual usa `InMemorySaver`. Portanto, a memória é perdida quando o processo da aplicação é encerrado.

## 12. Segurança

O projeto aplica validações em três momentos.

### 12.1 Entrada

* Bloqueio de perguntas vazias
* Limite de tamanho
* Bloqueio de identificadores de outro cliente
* Restrição de consultas pessoais no modo visitante

### 12.2 Ferramentas

* Ferramentas criadas para um cliente específico
* `cliente_id` não é escolhido pelo modelo
* Acesso somente aos dados vinculados ao perfil da sessão

### 12.3 Saída

* Remoção de blocos `<think>`
* Bloqueio de raciocínio interno
* Bloqueio de identificadores de outros clientes
* Bloqueio de recomendações financeiras adequadas
* Inclusão de fonte quando uma ferramenta foi utilizada

## 13. Auditoria

As interações são registradas em:

`logs/interacoes.jsonl`

Campos esperados:

```
{
    "evento_id": "identificador",
    "timestamp_utc": "data e hora",
    "perfil_id": "CLI-0001",
    "tipo_perfil": "cliente",
    "thread_id": "sessao:CLI-0001",
    "status": "sucesso",
    "duracao_ms": 1200,
    "ferramentas": ["consultar_resumo_financeiro"],
    "fontes": ["transacoes.csv"]
}
```

Status possíveis:
* `sucesso`
* `bloqueado`
* `erro`

## 14. Testes

### 14.1 Testes unitários

```
python -m pytest testes/teste_memoria.py
python -m pytest testes/teste_auditoria.py
python -m pytest testes/teste_seguranca.py
```

### 14.2 Interface

```
python -m pytest testes/teste_app.py
```

### 14.3 Integração com Ollama

```
python -m pytest -m integration testes/teste_fluxos_e2e.py
```

### 14.4 Todos os testes

```
python -m pytest
```

## 15. Limitações conhecidas

* Resultados dependem da qualidade do modelo local
* O modelo pequeno pode omitir detalhes
* A memória atual não persiste após reinicialização
* Não existe autenticação
* Os dados são inventados
* Não existe conexão com instituições financeiras
* Recomendações são apenas educativas
* Testes de linguagem natural podem variar entre execuções
* Auditoria em arquivo não substitui monitoramento de produção

## 16. Melhorias futuras

* Autenticação por usuário
* Banco de dados relacional
* Checkpointer SQLite ou PostgreSQL
* Painel de métricas
* Avaliação automática de respostas
* Testes contra vazamento entre clientes
* Integração com Open Finance mediante consentimento
* Classificação de intenção
* Explicações personalizadas
* Anonimização dos registros
* Política de retenção de logs
* Deploy em ambiente controlado