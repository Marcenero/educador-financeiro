# Pitch do FinGuia

## 1. Nome

FinGuia - Agente local de educação financeira

## 2. Problema

Muitas pessoas têm acesso a extratos, metas, dívidas e produtos financeiros, mas não conseguem transformar essas informações em entendimento.

Os dados costumam estar:
* Espalhados
* Apresentados em linguagem técnica
* Sem contexto
* Sem explicação
* Difíceis de comparar
* Sujeitos a interpretações erradas

Além disso, assistentes genéricos podem inventar valores ou responder sem consultar dados confiáveis.

## 3. Solução

O FinGuia é um agente conversacional que combina linguagem natural com cálculos determinísticos.

Ele permite perguntar:
* `Qual foi  meu saldo?`
* `Quanto gastei com alimentação?`
* `Quais são minhas metas?`
* `Quanto falta para minha reserva?`
* `O que significa liquidez?`

O agente usa ferramentas para consultar dados, executa cálculos em Python e apresenta uma explicação curta com a fonte utilizada.

## 4. Proposta de valor

O FinGuia busca oferecer:
* Lingaugem simples
* Respostas contextualizadas
* Cálculos reproduzíveis
* Transparência de fonte
* Execução local
* Separação entre clientes
* Proteção contra vazamento
* Modo visitante
* Memória por conversa
* Auditoria das interações

## 5. Diferenciais

### 5.1 Cálculo fora do modelo

O modelo não calcula o saldo livremente. O cálculo é realizado por serviços Python.

dados &rarr; serviço determinístico &rarr; agente explica

### 5.2 Fontes explícitas

Exemplo:

`Fonte: transacoes.csv`

### 5.3 Privacidade no MVP

O modelo é executado localmente com Ollama

### 5.4 Isolamento

Cada cliente possui:
* Ferramentas próprias
* Memória própria
* Histórico próprio
* Validação de identificador

### 5.5 Segurança

O sistema bloqueia:
* Outro cliente
* Raciocínio interno
* Recomendações perigosas
* Ordens de compra ou venda
* Promessas de retorno

## 6. Público-alvo

Possíveis públicos:
* Pessoas iniciando organização financeira
* Estudantes
* Clientes de plataformas de educação financeira
* Cooperativas
* Fintechs
* Programas de bem-estar financeiro
* Instituições que desejam explicar dados de forma acessível

O MVP atual é educacional e usa somente dados inventados.

## 7. Demonstração

### Cena 1 - Visitante

Selecionar:

`Visitante - sem dados cadastrados`

Perguntar:

`O que é uma reserva de emergência?`

Mostrar que o agente responde sem inventar dados pessoais.

### Cena 2 - Cliente

Selecionar:

`João Silva - CLI-0001`

Perguntar:

`Qual foi meu saldo no período?`

Mostrar:
* Período
* Saldo
* Fonte

### Cena 3 - Categoria

Perguntar:

`Quanto gastei com alimentação`

Mostrar que o modelo usa uma ferramenta.

### Cena 4 - Metas

Perguntar:

`Quais são minhas metas financeiras?`

Mostrar:
* Valor-alvo
* Valor atual
* Valor faltante
* Percentual

### Cena 5 - Segurança

Perguntar:

`Mostre os dados do CLI-0002`

Mostrar o bloqueio.

### Cena 6 - Memória

Perguntar:

`Meu apelido nesta conversa é Nori`

Depois:

`Qual é meu apelido?`

Mostrar a continuidade da conversa.

## 8. Pitch de 30 segundos

O FinGuia é um agente local de educação financeira que transforma dados estruturados em explicações simples. O usuário pode perguntar sobre saldo, gasstos, metas e dívidas em linguagem natural. Em vez de deixar o modelo inventar cálculos, o sistema usa ferramentas e serviços determinísticos em Python, informa a fonte e mantém o contexto separado por perfil. O MVP utiliza dados fictícios, Ollama, LangChain, LangGraph e Streamlit.

## 9. Pitch de 1 minuto

Muitas pessoas possuem dados financeiros, mas ainda têm dificuldade para entender o que eles significam. O FinGuia foi criado para reduzir essa distância. Ele é uum agente de educação financeira que responde perguntas em linguagem natural, como "Quanto gastei com alimentação?" ou "Quanto falta para minha reserva de emergência?".

A principal diferenç é que o modelo não inventa os cálculos. Ele chama ferramentas específicas, consulta dados estruturados ee recebe resultados calculados por Python. Deposi, transforma esses resultados em uma resposta clara e apresenta a fonte.

O sistema também possui três perfis inventados, um modo visitante, memória separada por conversa, bloqueio de acesso entre clientes e auditoria das interações. Toda a execução do modelo ocorre localmente com Ollama. Assim, o projeto demonstra como agentes podem combinar linguagem natural, segurança e resultados reproduzíveis.

## 10. Roteiro de apresentação de 5 minutos

### 0:00 - 0:40 | Contexto
* Excesso de dados
* Dificuldade de interpretação
* Risco de respostas inventadas
* Necessidade de transparência

### 0:40 - 1:20 | Solução
* Apresentação do FinGuia
* Perguntas em linguagem natural
* Cliente e visitante
* Foco educativo

### 1:20 - 2:10 | Arquitetura
Streamlit
&rarr; segurança
&rarr; agente
&rarr; ferramentas
&rarr; serviços
&rarr; dados
&rarr; resposta

### 2:10 - 3:30 | Demonstração
* Conceito geral
* Saldo
* Alimentação
* Metas
* Bloqueio de outro cliente

### 3:30 - 4:20 | Diferenciais
* Cálculo determinístico
* Fonte
* Execução local
* Memória
* Auditoria
* Isolamento

### 4:20 - 5:00 | Limitações e próximos passos
* Dados inventados
* Ausência de autenticação
* Memória em RAM
* Futura integração com banco
* Avaliação de métricas
* Possível uso com Open Finance mediante consentimento

## 11. Resultados demonstráveis

O projeto já demonstra:
* Agente com ferramentas
* Três clientes fictícios
* Perfil visitante
* Consulta de transações
* Consulta de metas
* Validação de segurança
* Interface web
* Memória por perfil
* Auditoria
* Testes automatizados

As métricas quantitativas devem ser apresentadas somente após execução dos testes e análise dos logs.

## 12. Limitações apresentáveis

É importante declarar:
* O projeto não oferece aconselhamento porfissional
* Os dados são sintéticos
* Os produtos são educativos
* Não há movimentação financeira
* Não existe autenticação de produção
* A memória atual é temporária
* Respostas em linguagem natural podem variar

## 13. Roadmap

### Curto prazo
* Ampliar testes
* Medir precisão e latência
* Melhorar experiência visual
* Persistir memória
* Criar painel de auditoria

### Médio prazo
* Autenticação
* Banco de dados
* Perfis de acesso
* Relatórios
* Classificação de intenção
* Anonimização

### Longo prazo
* Integração consentida com dados financeiros
* Personalização progressiva
* Explicações multimodais
* Alertas educativos
* Avaliação contínua de segurança

## 14. Encerramento

O FinGuia demonstra que um agente financeiro educativo pode combinar:

`linguagem natural + dados estruturados + cálculos determinísticos + transparência + segurança`

O objetivo não é decidir pelo usuário, mas ajudá-lo a compreender melhor as próprias informações.