# Buscas do Google por ramo de negócio — Observatório Lucro Digital

Trabalho final da disciplina **Probabilidade e Estatística para IA (IAA003)**, pós-graduação em IA Avançada:
amostragem, intervalos de confiança e testes de hipóteses, comparando população e amostra.

Aluna: Ana Paula Rigon

> **Painéis (Streamlit Cloud):** https://iaa003-buscas.streamlit.app
> 1. Análise descritiva da população: https://iaa003-buscas.streamlit.app/populacao
> 2. Análise descritiva da amostra: https://iaa003-buscas.streamlit.app/amostra
> 3. Inferência estatística e comparação dos resultados: https://iaa003-buscas.streamlit.app/inferencia
>
> **Extra (análise exploratória):** "Onde vale a pena anunciar?", com oportunidades por nicho, custo do clique, buscas
> "perto de mim" e competição × custo. Usa o mesmo `dataset.txt`: https://iaa003-buscas.streamlit.app/onde-anunciar
>
> **Base de dados:** [`dataset.txt`](https://github.com/aprigon-br/IAA003/blob/main/dataset.txt)

---

## 1. Fonte e acesso aos dados

| | |
|---|---|
| **Fonte primária** | Google Ads API, ferramenta *Planejador de palavras-chave* (Keyword Planner). Base oficial do Google sobre volume de pesquisas e custo de anúncios. |
| **Coleta e organização** | Observatório Lucro Digital |
| **Arquivo publicado** | [`dataset.txt`](dataset.txt), extraído do banco em **11/11/2026** |
| **Formato** | Texto UTF-8 separado por TAB, primeira linha com os nomes das colunas, decimais com ponto, campos vazios = valor ausente |

O banco original é privado. O `dataset.txt` é a cópia integral da tabela no dia da extração e é a população
usada no trabalho. Os volumes e lances vêm da coleta semanal do Google; as buscas foram cadastradas entre 08 e
25/10/2026.

### 1.1 O arquivo dataset.txt

O arquivo `dataset.txt` contém dados de buscas/pesquisas no Google, e foi criado por mim especialmente para este
trabalho.

### 1.2 Origem dos dados do dataset

Os dados vêm de duas origens: **a) Observatório Lucro Digital** e **b) Google Ads API / Google Keyword Planner**.

#### a) Observatório Lucro Digital

A empresa Lucro Digital, que atua no ramo de consultoria em Marketing Digital, possui um sistema chamado "Observatorio Lucro Digital", que possui um banco de dados privado utilizado em seus analytics.
A empresa autorizou realizar consulta somente leitura em seu banco de dados, para extração de um dataset, com foco principal na tabela que possui dados públicos coletados diretamente do Google sobre "buscas". 

Sendo assim, o `dataset.txt` utilizado no trabalho foi criado a partir do banco de dados do "Observatório Lucro Digital", que é o
centro de pesquisa de mercado da empresa. Toda semana um job executa a extração de dados do Google e grava os
resultados num banco de dados PostgreSQL, na tabela "buscas". Para cada "busca" ficam registrados o volume mensal de
pesquisas no Brasil, o id do nicho, a faixa de lance e o índice de concorrência.

Como o banco de dados do Observatório é privado e não tem acesso público, além de ser atualizado toda semana, no dia
11/11/2026 foi extraída a tabela "buscas" completa (5.124 buscas e 12 colunas), sem filtros e sem alterar nenhum valor. No
SQL foi cruzado o id do nicho da tabela "buscas" com outra tabela, "nichos", para introduzir duas novas colunas no dataset, com o nome do nicho e o "publico"
(tipo de público), as duas únicas colunas de categorização acrescentadas. Com elas, o dataset ficou com 14
variáveis. O resultado foi publicado no GitHub para que a base pudesse ser "congelada" e consultada, e foi este dataset
utilizado no trabalho.

- Base: https://github.com/aprigon-br/IAA003/blob/main/dataset.txt
- Manual do dataset (formato do arquivo, descrição das colunas, resumo e exemplos de linhas):
  https://github.com/aprigon-br/IAA003/blob/main/dataset_manual.docx
- Dicionário de dados das tabelas "buscas" e "nichos" que foram consultadas para criar o dataset:
  https://github.com/aprigon-br/IAA003/blob/main/dataset_dicionario_observatorio_tabelas_buscas_nichos.docx

#### b) Google Ads API do Planejador de palavras-chave do Google (Google Keyword Planner)

Os dados da tabela "buscas" do Observatório vêm da Google Ads API, da ferramenta Planejador de palavras-chave do
Google (Google Keyword Planner). É a base oficial do Google sobre o volume de pesquisas, o custo por clique (lance) e
a concorrência entre anunciantes.

- Link para a ferramenta do Google: https://ads.google.com/home/tools/keyword-planner/
- API: https://developers.google.com/google-ads/api/docs/keyword-planning/overview

A tabela "nichos" é criada pelo Observatório com categorizações de nichos de negócios, baseadas em dados da Receita
Federal, inferências do Gemini e dados de clientes para agrupamento de atividades de negócios similares em um mesmo
nicho dentro do contexto da empresa. Esta classificação é específica da empresa Lucro Digital, e é baseada em padrões
de mercado e critérios próprios da empresa.

## 2. Contexto e objetivo da base

O **Observatório** é o centro de pesquisa de mercado da Lucro Digital, uma agência de marketing digital. Toda
semana ele consulta o Google para saber **quantas pessoas pesquisaram por cada ramo de negócio** (*nicho*: dentista,
padaria, pet shop, loja de roupas online…) e **quanto custa anunciar** para aparecer nessas pesquisas. Esses números
alimentam o *Mapa do Dinheiro*, ferramenta que mostra a empresários a demanda e o custo de anúncio do seu ramo.

Cada nicho é representado por um conjunto de **buscas**: as frases que as pessoas digitam no Google, como
"dentista perto de mim". 

A tabela guarda, para cada busca, o volume mensal de pesquisas no Brasil, a faixa de lance para aparecer
no topo da página e o índice de concorrência entre anunciantes.

**Objetivo da base:** medir a demanda e o custo de anunciar em cada ramo de negócio no Google, no Brasil.

## 3. Tamanho

- **5.124 observações** (linhas)
- **14 variáveis** (colunas)
- **137 nichos** (ramos de negócio), com média de 37 buscas por nicho

## 4. População e unidade amostral

- **População de interesse:** todas as 5.124 buscas monitoradas pelo Observatório na extração de 11/11/2026.
  É uma população finita e conhecida, o que permite calcular os parâmetros reais e compará-los
  com as estimativas da amostra.
- **Unidade amostral:** uma busca de um nicho, que corresponde a uma linha do arquivo. O mesmo texto pode aparecer
  em dois nichos (45 casos, por exemplo "conserto de pc perto de mim"), e cada ocorrência conta como uma unidade.

## 5. Variáveis selecionadas para a análise

### Quantitativas (parâmetro de interesse: média)

| Variável | Tipo | O que significa | Unidade |
|---|---|---|---|
| `volume_brasil` | discreta | Média de pesquisas por mês no Brasil nos últimos 12 meses | pesquisas/mês |
| `lance_min` | contínua | Ponta de baixo da faixa de lance para o anúncio aparecer no topo da página | R$ por clique |
| `lance_max` | contínua | Ponta de cima da mesma faixa | R$ por clique |
| `competicao` | discreta (0 a 100) | Índice de concorrência do Google: quanto maior, mais anunciantes disputam a busca | índice |

### Qualitativas (parâmetro de interesse: proporção)

| Variável | Tipo | Categorias |
|---|---|---|
| `nicho` | nominal | 137 ramos de negócio (Dentista, Padaria, Pet shop…). **Usada só na análise descritiva** (ver nota abaixo) |
| `publico` | nominal | `SERVICOS` (atende clientes, como uma clínica) ou `ECOMMERCE` (vende produtos online) |
| `origem` | nominal | `SEMENTE` (escrita pela IA), `EXPANSAO` (sugerida pelo Google), `MANUAL` (incluída à mão) |
| `competicao_alta` *(derivada)* | binária | **Sim** se `competicao` ≥ 67 (terço superior da escala 0–100) |
| `intencao_local` *(derivada)* | binária | **Sim** se o texto da busca contém "perto" ou "próximo/próxima" (com ou sem acento), como em "dentista perto de mim" |

As duas variáveis derivadas não estão no arquivo. Elas são calculadas na análise a partir de `competicao` e `texto`,
com as regras acima.

**Sobre `nicho`:** é qualitativa nominal, mas não entra na inferência, por três motivos:
- **Muitas categorias:** são 137, o que torna inviável mostrar a frequência de todas.
- **A frequência reflete o catálogo, não o mercado:** cada nicho tem de 30 a 40 buscas por construção do catálogo.
- **Falta de casos na amostra:** cada nicho representa cerca de 0,7% das buscas, o que dá 2 a 3 casos esperados
  numa amostra de 358. Isso fica abaixo do mínimo de 10 exigido pelo teste de proporção.

Nos painéis descritivos ela aparece cruzada com variáveis quantitativas, por exemplo nos nichos com maior volume
de pesquisas e nos nichos com lance mais caro.

### Variáveis não usadas nas análises

| Variável | Motivo |
|---|---|
| `id`, `nicho_id` | Identificadores internos, sem significado estatístico |
| `texto` | A busca em si. Usado só para derivar `intencao_local` |
| `grupo` | Texto livre (grupo de anúncios sugerido pela IA), com 600 categorias diferentes |
| `ativa` | Quase constante: 5.117 de 5.124 são "sim" |
| `criado_em`, `atualizado_em` | Datas de controle do sistema |

## 6. Valores ausentes

| Variável | Vazios | Motivo |
|---|---|---|
| `lance_min`, `lance_max` | 128 (2,5%) | O Google não informou o lance para a busca |
| `competicao` | 31 (0,6%) | O Google não informou o índice |
| `grupo` | 7 | Grupo de anúncios não atribuído |

Nas análises, os vazios de cada variável são descartados, e o número de observações efetivamente usadas é
informado em cada resultado.

## 7. Dimensionamento da amostra

A amostra foi dimensionada para **estimar uma proporção**, com os parâmetros abaixo.

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Tamanho da população (N) | 5.124 | Total de buscas no `dataset.txt` |
| Nível de confiança | 95% (z = 1,96) | Padrão em pesquisas: 95% dos intervalos construídos dessa forma contêm o valor real |
| Margem de erro (E) | 5 pontos percentuais | Precisão suficiente para as perguntas do trabalho, com amostra de tamanho viável |
| Proporção esperada (p) | 50% | Escolha conservadora: p·(1−p) é máximo em 0,5, então n atende qualquer proporção estimada |

**Fórmula**, com correção para população finita:

- População infinita: n₀ = z² · p · (1 − p) / E² = 1,96² × 0,5 × 0,5 / 0,05² = **384,15**
- População finita: n = n₀ / (1 + (n₀ − 1) / N) = **357,42**, arredondado para cima: **n = 358**
- Fração amostral: n/N = 358 / 5.124 = **7,0%**

**Conferência:**
- Calculadora on-line [Comentto — Calculadora Amostral](https://comentto.com/calculadora-amostral/). A
  calculadora da USP/Bauru sugerida no enunciado estava fora do ar em 11/11/2026.
- A mesma fórmula, calculada em Python no script [`calcular_tamanho_amostra.py`](calcular_tamanho_amostra.py), que
  também gera a tabela de sensibilidade abaixo. Os dois deram n = 358.

**Sensibilidade:** como n muda com os parâmetros (p = 50%, N = 5.124).

| Confiança | E = 3% | E = 5% | E = 7% |
|---|---|---|---|
| 90% | 656 | 258 | 135 |
| **95%** | 884 | **358** | 189 |
| 99% | 1.356 | 588 | 318 |

A mesma amostra é usada nos testes de média. A precisão alcançada para cada média aparece no painel de inferência.

## 8. Seleção da amostra aleatória simples (AAS)

| | |
|---|---|
| **Método** | Amostra aleatória simples **sem reposição**: cada busca pode ser sorteada no máximo uma vez |
| **Probabilidade de seleção** | Igual para todas: 358 / 5.124 = **6,99%** |
| **Ferramenta** | Python, função `DataFrame.sample(n=358, replace=False, random_state=20261111)` do pandas, que usa o gerador de números aleatórios do NumPy |
| **Semente aleatória** | **20261111**, a data do sorteio (11/11/2026), escolhida antes de ver o resultado e não alterada depois |
| **Script** | [`sortear_amostra.py`](sortear_amostra.py) |
| **Resultado** | [`amostra.txt`](amostra.txt): 358 buscas no mesmo formato do `dataset.txt` |

### 8.1 O que é a semente aleatória

O computador não sorteia "de verdade". Ele usa uma **fórmula matemática** (um gerador de números pseudoaleatórios)
que, a partir de um número inicial, produz uma sequência longa de números que *parecem* aleatórios. Esse número
inicial é a **semente**.

**A mesma semente produz sempre a mesma sequência,** e portanto o mesmo sorteio. Uma analogia: imagine as 5.124
buscas como cartas de um baralho e a semente como o número de uma "receita de embaralhar".
- A receita nº 20261111 sempre deixa as cartas na mesma ordem.
- Outra receita (outra semente) produz uma ordem completamente diferente.
- As 358 cartas de cima, depois de embaralhar com a receita 20261111, são sempre as mesmas.

Os números gerados passam nos testes estatísticos de aleatoriedade, e cada busca continua com a mesma chance de ser
escolhida. Por isso o resultado é uma amostra aleatória simples válida. A semente fixa só acrescenta uma propriedade:
o sorteio pode ser **repetido e conferido** por qualquer pessoa.

### 8.2 Onde a semente está guardada e como o sorteio está codificado

A semente não fica guardada em nenhum lugar escondido, e o computador não "lembra" dela. Ela está **escrita no
código** do script [`sortear_amostra.py`](sortear_amostra.py):

```python
TAMANHO_AMOSTRA = 358   # linha 23: calculado em calcular_tamanho_amostra.py
SEMENTE = 20261111      # linha 24: data do sorteio; fixa para o sorteio ser reproduzível

# linha 38: o sorteio
amostra = populacao.sample(n=TAMANHO_AMOSTRA, replace=False, random_state=SEMENTE)
```

Nessa linha 38, o pandas faz três coisas:
1. **Cria o gerador** de números pseudoaleatórios a partir da semente 20261111 (o gerador do NumPy).
2. **Sorteia 358 posições diferentes** entre as 5.124 linhas do `dataset.txt`. `replace=False` impede que a mesma
   busca saia duas vezes, e cada busca tem a mesma chance: 358/5.124 = 6,99%.
3. **Copia as linhas** dessas posições para a amostra, na ordem em que foram sorteadas, e o script grava o
   resultado em `amostra.txt`.

A semente também está documentada nesta seção e na página inicial dos painéis.

### 8.3 Onde fica a relação das buscas que caíram na amostra

Fica no próprio [`amostra.txt`](amostra.txt), que tem as 358 linhas sorteadas, **completas e idênticas** às do
`dataset.txt` (mesmas 14 colunas), na ordem do sorteio.

A ligação entre os dois arquivos é a coluna **`id`**, um código único para cada busca. O mesmo `id` aparece nos dois
arquivos, então para saber de onde veio uma linha da amostra basta procurar o `id` dela no `dataset.txt`. As três
primeiras buscas sorteadas:

| Ordem do sorteio | Registro da população | Linha no `dataset.txt` | `id` | Nicho | Busca |
|---|---|---|---|---|---|
| 1º | nº 4.611 | 4.612 | `cmuz3j61900540xqt1474bfm7` | Roupas femininas | conjuntos femininos alfaiataria |
| 2º | nº 4.920 | 4.921 | `cmuz3ldry00mb0xqtflfwzets` | Suplementos alimentares | creatina monohidratada micronizada |
| 3º | nº 582 | 583 | `cmuz4125t03220xqt1chzbv45` | Autoelétrica | consertar motor de arranque |

A linha no arquivo é o número do registro + 1, porque a primeira linha do `dataset.txt` é o cabeçalho.

Não existe um arquivo separado com a lista das posições sorteadas, e ele não é necessário: a relação já está no
`amostra.txt` (pela coluna `id`), e a lista pode ser recriada a qualquer momento com a semente.

### 8.4 Como reproduzir e conferir a amostra

**Opção 1, rodar o script.** O script lê o `dataset.txt`, refaz o sorteio e regrava o `amostra.txt`, que sai idêntico
ao publicado:

```bash
python sortear_amostra.py
```

**Opção 2, conferir sem regravar nada.** O código abaixo refaz o sorteio e compara com o `amostra.txt` publicado:

```python
import pandas as pd

pop = pd.read_csv("dataset.txt", sep="\t", dtype=str, keep_default_na=False)
amo = pd.read_csv("amostra.txt", sep="\t", dtype=str, keep_default_na=False)

nova = pop.sample(n=358, replace=False, random_state=20261111)
print(nova["id"].tolist() == amo["id"].tolist())   # True: mesmas 358 buscas, na mesma ordem
print(nova.index[:3] + 1)                           # registros sorteados: 4611, 4920, 582
```

**Para o sorteio sair igual, três coisas precisam ser mantidas:**
1. **A mesma semente** (20261111).
2. **O mesmo `dataset.txt`, com as linhas na mesma ordem.** A população foi congelada em 11/11/2026 por isso:
   mudar a ordem das linhas muda quais buscas ocupam cada posição.
3. **O mesmo método** (`DataFrame.sample` do pandas com `random_state` inteiro). O gerador usado por ele produz
   sempre a mesma sequência para a mesma semente, mesmo em versões diferentes.

**O que muda com outra semente:** com a semente 20261112, por exemplo, a amostra seria outra. Só 26 das 358 buscas
coincidiriam, o que é o esperado por puro acaso (358 × 358 / 5.124 ≈ 25). A semente é o que identifica **qual** das
muitas amostras possíveis foi a usada no trabalho.

**Honestidade do sorteio:** a semente foi escolhida antes de ver o resultado e nunca foi trocada. Testar várias
sementes até aparecer uma amostra "bonita" seria manipular o sorteio, e a amostra deixaria de ser aleatória.

### 8.5 Conferências feitas

- 358 linhas, nenhuma busca repetida.
- Todas as linhas são idênticas a linhas do `dataset.txt`.
- A amostra contém buscas de 125 dos 137 nichos.
- Rodando o sorteio duas vezes, os dois arquivos gerados ficaram idênticos.

### 8.6 Outras sementes que aparecem no trabalho

Elas não têm relação com a amostra oficial:
- **Semente 2026,** em `inferencia.py`: usada só na **simulação das 1.000 amostras** do painel de inferência, que
  mostra a variabilidade amostral.
- **Botão "Sortear nova amostra",** no painel de inferência: usa uma semente nova a cada clique e mostra essa semente
  na tela. É só para experimentar; a amostra oficial continua sendo a do `amostra.txt`.

## 9. Dicionário completo do arquivo

| # | Coluna | Descrição |
|---|---|---|
| 1 | `id` | Identificador da busca |
| 2 | `nicho_id` | Identificador do nicho |
| 3 | `nicho` | Nome do nicho (ramo de negócio) |
| 4 | `publico` | SERVICOS ou ECOMMERCE |
| 5 | `texto` | A busca, em minúsculas, como o Google devolve |
| 6 | `origem` | SEMENTE, EXPANSAO ou MANUAL |
| 7 | `ativa` | Se a busca entra na soma do nicho (True/False) |
| 8 | `volume_brasil` | Pesquisas por mês no Brasil (média de 12 meses) |
| 9 | `lance_min` | Lance mínimo do topo da página (R$) |
| 10 | `lance_max` | Lance máximo do topo da página (R$) |
| 11 | `competicao` | Índice de concorrência (0 a 100) |
| 12 | `grupo` | Grupo de anúncios sugerido |
| 13 | `criado_em` | Quando a busca entrou no sistema (UTC) |
| 14 | `atualizado_em` | Última alteração da linha (UTC) |

## 10. Como ler o arquivo em Python

```python
import pandas as pd
df = pd.read_csv("dataset.txt", sep="\t")
```
