# FinGuia

Agente local de educação financeira desenvolvido em Python para ajudar usuários a compreender saldo, gastos, metas, dívidas e conceitos financeiros por meio de uma interface conversacional.

O projeto combina **LangChain**, **LangGraph**, **Ollama** e **Streamlit**, utilizando ferramentas determinísticas, memória por perfil, validações de segurança e auditoria das interações.

> O FinGuia utiliza dados sintéticos e possui finalidade educacional. Ele não substitui orientação financeira profissional e não realiza operações financeiras.

---

## Funcionalidades

* Consulta de saldo, entradas e saídas;
* Análise de gastos por categoria;
* Consulta de metas financeiras;
* Consulta de dívidas;
* Apresentação educativa de produtos financeiros;
* Três perfis de clientes sintéticos;
* Modo visitante sem acesso a dados pessoais;
* Memória conversacional separada por perfil;
* Isolamento entre clientes;
* Validação de entrada e saída;
* Inclusão de fontes nas respostas;
* Auditoria das interações;
* Interface de chat com Streamlit;
* Testes unitários e de integração.

---

## Tecnologias

* Python
* LangChain
* LangGraph
* Ollama
* Qwen 3 4B Instruct
* Streamlit
* Pandas
* Pydantic
* Pytest

---

## Arquitetura

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

Ferramentas

&darr;

Serviços determinísticos

&darr;

Arquivos JSON e CSV

&darr;

Validação de saída

&darr;

Auditoria

&darr;

Resposta ao usuário

Os cálculos financeiros são realizados por serviços em Python. O modelo de linguagem interpreta a pergunta, seleciona ferramentas e apresenta o resultado de forma clara.

---

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

---

## Perfis disponíveis

| Perfil    | Tipo              | Acesso                    |
| --------- | ----------------- | ------------------------- |
| CLI-0001  | Cliente sintético | Próprios dados            |
| CLI-0002  | Cliente sintético | Próprios dados            |
| CLI-0003  | Cliente sintético | Próprios dados            |
| VISITANTE | Não cliente       | Apenas conteúdo educativo |

O seletor de perfis existe para demonstração. Em produção, o identificador do cliente deve ser obtido por autenticação.

---

## Pré-requisitos

* Python 3.12 ou superior;
* Ollama instalado;
* Modelo configurado disponível localmente.

---

## Instalação

Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
cd educador-financeiro
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Baixe o modelo:

```powershell
ollama pull qwen3:4b-instruct
```

---

## Configuração

Crie um arquivo `.env` na raiz:

```env
OLLAMA_MODEL=qwen3:4b-instruct
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEMPERATURE=0
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_PREDICT=500

AUDITORIA_INCLUIR_CONTEUDO=true
```

Para não registrar perguntas e respostas completas:

```env
AUDITORIA_INCLUIR_CONTEUDO=false
```

---

## Execução

Inicie o Ollama:

```powershell
ollama serve
```

Em outro terminal, execute:

```powershell
python -m streamlit run src/app.py
```

---

## Exemplos de perguntas

Para clientes:

```text
Qual foi meu saldo no período?
Quanto gastei com alimentação?
Quais são minhas metas financeiras?
Qual dívida possui a maior taxa?
Quanto falta para concluir minha reserva?
```

Para visitante:

```text
O que é uma reserva de emergência?
O que significa liquidez?
Como organizar um orçamento mensal?
Qual a diferença entre receita e despesa?
```

---

## Segurança

O projeto possui validações para:

* impedir consultas a outro cliente;
* bloquear identificadores não autorizados;
* evitar exposição de raciocínio interno;
* impedir recomendações financeiras inadequadas;
* evitar promessas de lucro ou ausência de risco;
* restringir o visitante a conteúdo educativo;
* incluir fontes em respostas baseadas em dados.

As ferramentas são criadas para um cliente específico, e o `cliente_id` não é escolhido pelo modelo.

---

## Memória conversacional

A memória é separada por sessão e perfil:

```text
sessao:CLI-0001
sessao:CLI-0002
sessao:VISITANTE
```

A versão atual utiliza memória em processo. O histórico é perdido quando a aplicação é reiniciada.

---

## Auditoria

As interações são registradas em:

```text
logs/interacoes.jsonl
```

Os registros podem incluir horário, perfil, status, duração, ferramentas, fontes, pergunta e resposta.

Status possíveis:

```text
sucesso
bloqueado
erro
```

---

## Testes

Execute todos os testes:

```powershell
python -m pytest
```

Para uma saída detalhada:

```powershell
python -m pytest -v
```

Testes de integração com Ollama:

```powershell
python -m pytest -m integration
```

Cobertura de testes:

```powershell
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

O relatório será gerado em:

```text
htmlcov/index.html
```

---

## Métricas avaliadas

* testes aprovados;
* taxa de sucesso;
* latência média;
* P95 de latência;
* exatidão numérica;
* cobertura de fonte;
* vazamentos detectados;
* cobertura de testes.

Os resultados devem ser preenchidos após a execução dos testes e análise dos logs.

---

## Documentação

* `docs/01-documentacao-agente.md`
* `docs/02-base-conhecimento.md`
* `docs/03-prompts.md`
* `docs/04-metricas.md`
* `docs/05-pitch.md`

---

## Limitações

* utiliza dados sintéticos;
* não possui autenticação real;
* não se conecta a instituições financeiras;
* não realiza transferências ou investimentos;
* não substitui orientação profissional;
* a memória não persiste após reinicialização;
* respostas em linguagem natural podem variar.

---

## Próximos passos

* autenticação de usuários;
* banco de dados;
* persistência de memória;
* painel de métricas;
* melhoria da interface;
* ampliação da bateria de testes;
* anonimização de auditoria;
* integração consentida com dados financeiros.

---

## Finalidade

O FinGuia demonstra como agentes de IA podem combinar:

```text
linguagem natural
+ dados estruturados
+ cálculos determinísticos
+ memória
+ transparência
+ segurança
```

O objetivo é ajudar o usuário a compreender melhor suas informações financeiras, sem decidir por ele.