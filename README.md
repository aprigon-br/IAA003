# Buscas do Google por ramo de negócio — Observatório Lucro Digital

Trabalho final da disciplina **Probabilidade e Estatística para IA (IAA003)**, pós-graduação em IA Avançada:
amostragem, intervalos de confiança e testes de hipóteses, comparando população e amostra.

> **Links dos painéis:** *(serão incluídos após a publicação)*
> 1. Análise descritiva da população
> 2. Análise descritiva da amostra
> 3. Inferência estatística e comparação dos resultados
>
> **Extra (análise exploratória):** "Onde vale a pena anunciar?", com oportunidades por nicho, custo do clique, buscas
> "perto de mim" e competição × custo. Usa o mesmo `dataset.txt`.

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
- A mesma fórmula, calculada em Python. Os dois deram n = 358.

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
| **Como reproduzir** | `pd.read_csv("dataset.txt", sep="\t").sample(n=358, replace=False, random_state=20261111)` |
| **Resultado** | [`amostra.txt`](amostra.txt): 358 buscas no mesmo formato do `dataset.txt` |

**Reprodutibilidade:** a semente fixa faz o gerador produzir sempre a mesma sequência de sorteios, então quem aplicar
o comando acima ao `dataset.txt` obtém exatamente as mesmas 358 buscas do `amostra.txt`. Isso foi conferido rodando o sorteio duas vezes: os dois arquivos ficaram idênticos.

**Conferências:**
- 358 linhas, nenhuma busca repetida.
- Todas as linhas são idênticas a linhas do `dataset.txt`.
- A amostra contém buscas de 125 dos 137 nichos.

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
