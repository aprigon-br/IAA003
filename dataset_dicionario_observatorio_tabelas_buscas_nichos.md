**LUCRO DIGITAL · OBSERVATÓRIO**

# Dicionário de dados das tabelas consultadas: `observatorio.buscas` e `observatorio.nichos`

Extrato do Dicionário de dados do Observatório com as duas tabelas do banco que foram consultadas para gerar o
[`dataset.txt`](dataset.txt) do trabalho final de IAA003: `observatorio.buscas` e `observatorio.nichos`.

> Versão em Markdown do arquivo
> [`dataset_dicionario_observatorio_tabelas_buscas_nichos.docx`](dataset_dicionario_observatorio_tabelas_buscas_nichos.docx),
> para leitura direta no GitHub.

| | |
|---|---|
| **Banco** | Postgres de produção (Railway), schema `observatorio` |
| **Dicionário original** | Versão de 07/11/2026, gerada a partir do código do sistema |
| **Extração do dataset** | 11/11/2026: 5.124 linhas e 14 colunas |
| **Trabalho** | IAA003 · Probabilidade e Estatística para IA · Ana Paula Rigon |

## 1. Sobre o Observatório e a fonte dos dados

O Observatório é o centro de pesquisa de mercado da Lucro Digital. Toda semana, ele pergunta ao Google quantas pessoas
pesquisaram por cada ramo de negócio (no Brasil, em cada estado e nas cidades grandes) e quanto custa anunciar para
aparecer nessas pesquisas.

**Fonte primária dos números de busca:** Google Ads API, ferramenta Planejador de palavras-chave (Keyword Planner). É
dela que vêm o volume mensal de pesquisas, a faixa de lance e o índice de concorrência de cada busca.

As descrições das duas tabelas e de suas colunas reproduzem, sem alterações, o texto do dicionário original; as
marcações sobre o uso no dataset foram acrescentadas neste extrato. O dicionário completo descreve as 20 tabelas do
schema `observatorio`; as outras 18 não foram usadas no trabalho.

## 2. Como o dataset.txt foi gerado

Uma única consulta SQL, feita em 11/11/2026, leu todas as linhas da tabela `buscas` e juntou cada busca ao seu nicho
pela coluna `nicho_id`. Da tabela `nichos` vieram só duas colunas: `nome` (gravada no arquivo como `nicho`) e
`publico`. Como toda busca pertence a um nicho, nenhuma linha ficou de fora: o arquivo tem as 5.124 buscas da tabela.

```sql
SELECT b.id, b.nicho_id, n.nome AS nicho, n.publico, b.texto, b.origem, b.ativa,
       b.volume_brasil, b.lance_min, b.lance_max, b.competicao,
       b.grupo, b.criado_em, b.atualizado_em
FROM observatorio.buscas b
JOIN observatorio.nichos n ON n.id = b.nicho_id
ORDER BY n.nome, b.volume_brasil DESC NULLS LAST, b.id
```

### De onde vem cada coluna do dataset.txt

| # | No dataset.txt | No banco |
|---:|---|---|
| 1 | `id` | `buscas.id` |
| 2 | `nicho_id` | `buscas.nicho_id` |
| 3 | `nicho` | **`nichos.nome`** |
| 4 | `publico` | **`nichos.publico`** |
| 5 | `texto` | `buscas.texto` |
| 6 | `origem` | `buscas.origem` |
| 7 | `ativa` | `buscas.ativa` |
| 8 | `volume_brasil` | `buscas.volume_brasil` |
| 9 | `lance_min` | `buscas.lance_min` |
| 10 | `lance_max` | `buscas.lance_max` |
| 11 | `competicao` | `buscas.competicao` |
| 12 | `grupo` | `buscas.grupo` |
| 13 | `criado_em` | `buscas.criado_em` |
| 14 | `atualizado_em` | `buscas.atualizado_em` |

Em destaque, as duas colunas que vêm da tabela `nichos`. As outras 12 são todas as colunas da tabela `buscas`, sem
alteração nos valores.

## 3. Como ler as tabelas

- **Preenchimento:** "sempre preenchida" = a coluna nunca fica vazia. "Pode ficar vazia" = pode ter NULL (sem valor),
  por exemplo quando o Google não informou o lance.
- **Chave:** as colunas marcadas como CHAVE identificam a linha: a combinação delas não se repete na tabela. ÚNICA
  indica outra coluna que também não se repete.
- **Ligações:** colunas terminadas em `_id` apontam para outra tabela: `nicho_id → nichos.id`.
- **Datas e horas:** estão em UTC; o horário de Brasília é 3 horas a menos.
- **Listas fixas (enum):** só aceitam os valores listados na descrição, em maiúsculas, como `SERVICOS` e `ECOMMERCE`.
- **NO DATASET / USADA NA LIGAÇÃO:** marcam as colunas da tabela `nichos` que foram usadas para gerar o dataset.txt.

### Tipos de dado que aparecem nas duas tabelas

| Tipo no banco | Como ler | Exemplo |
|---|---|---|
| `text` | Texto | `dentista perto de mim` |
| `integer` | Número inteiro | `12100` |
| `numeric(10,2)` | Número decimal: até 10 dígitos, 2 depois da vírgula | `3.45` (R$ 3,45) |
| `timestamp(3)` | Data e hora em UTC, com milissegundos | `2026-11-02 12:30:00.000` (9h30 em Brasília) |
| `boolean` | Sim ou não | `true` / `false` |
| `text[]` | Lista de textos | `{5611201,5611203}` |
| Lista fixa (enum) | Só aceita os valores listados na descrição | `PROPOSTO`, `ATIVO`, `RECUSADO` |

## 4. Tabela de buscas

`observatorio.buscas`

### Buscas de cada nicho

As pesquisas que as pessoas digitam no Google e que representam o nicho, por exemplo "dentista perto de mim". Ficam
em minúsculas, como o Planejador de palavras-chave do Google devolve. A soma das buscas ativas forma a demanda do
nicho.

**De onde vêm os dados**

- **Gemini:** escreve as sementes (como o brasileiro digita), filtra as ideias sem intenção de compra e sugere o grupo
  de anúncios.
- **Google Ads API, Planejador de palavras-chave:** ideias de busca a partir das sementes, volume mensal, faixa de
  lance e concorrência.
- **Painel:** buscas acrescentadas ou desligadas à mão.

**Quando é atualizada**

- Domingo, etapa buscas, só para nichos novos: o Gemini escreve sementes, o Planejador sugere ideias, o Gemini filtra
  as que têm intenção de compra. Ficam até 40 buscas por nicho, com pelo menos 20 pesquisas por mês.
- Todo domingo, etapa coleta: atualiza volume e lance no Brasil.
- Domingo, etapa direcao: grava o grupo de anúncios e o lance de cada busca.
- No painel, quem revisa pode acrescentar ou desligar buscas.

| | |
|---|---|
| **Identifica cada linha** | `id`; um mesmo texto não se repete dentro do nicho (`nicho_id` + texto é único) |
| **Ligações** | `nicho_id → nichos.id`. Apagar um nicho apaga as buscas dele. |

*Todas as 12 colunas desta tabela foram usadas no dataset.txt.*

| Coluna | Tipo | Preenchimento | O que significa |
|---|---|---|---|
| `id` · CHAVE | `text` (texto) | sempre preenchida | Identificador interno (cuid). |
| `nicho_id` | `text` (texto) | sempre preenchida | Nicho ao qual a busca pertence (`nichos.id`). |
| `texto` | `text` (texto) | sempre preenchida | A busca, em minúsculas, como o Google devolve. |
| `origem` | `OrigemBusca` (lista fixa de valores) | sempre preenchida | SEMENTE: escrita pelo Gemini, como o brasileiro digita.<br>EXPANSAO: ideia do Planejador a partir das sementes.<br>MANUAL: acrescentada no painel. |
| `ativa` | `boolean` (sim / não) | sempre preenchida | Só as buscas ativas entram na coleta e na soma do nicho. Padrão: sim. |
| `volume_brasil` | `integer` (número inteiro) | pode ficar vazia | Média de pesquisas por mês no Brasil nos últimos 12 meses, na última consulta. É o que decide quem fica no nicho. |
| `lance_min` | `numeric(10,2)` (decimal, 2 casas) | pode ficar vazia | Ponta de baixo da faixa de lance para aparecer no topo da página, no Brasil, em reais (última coleta). |
| `lance_max` | `numeric(10,2)` (decimal, 2 casas) | pode ficar vazia | Ponta de cima da mesma faixa, em reais. |
| `competicao` | `integer` (número inteiro) | pode ficar vazia | Índice de concorrência do Google, de 0 a 100: quanto maior, mais anunciantes disputam essa busca. |
| `grupo` | `text` (texto) | pode ficar vazia | Grupo de anúncios sugerido pelo Gemini para esta busca (etapa direcao). |
| `criado_em` | `timestamp(3)` (data e hora, em UTC) | sempre preenchida | Quando a busca entrou. |
| `atualizado_em` | `timestamp(3)` (data e hora, em UTC) | sempre preenchida | Última alteração na linha. |

## 5. Tabela de nichos (de onde vem o nome do nicho)

`observatorio.nichos`

### Catálogo de nichos

Lista dos ramos de negócio, que é gerada pelo módulo Mapa do Dinheiro do sistema da Lucro Digital. Um nicho novo nasce
como proposta e só entra na coleta semanal e no Mapa depois de aprovado na revisão.

**De onde vêm os dados**

- **Receita Federal (CNPJ):** atividades CNAE com mais empresas ativas, ponto de partida dos nichos de serviços (etapa
  catálogo).
- **Google (taxonomia de produtos):** categorias de produtos, ponto de partida dos nichos de e-commerce.
- **Gemini:** agrupa as atividades em nichos, avalia se vale anunciar (anunciável, motivo) e sugere o nicho mais
  próximo nos pedidos de lead.
- **Mapa do Dinheiro:** pedidos de nicho novo feitos pelos leads (contagem pedidos).
- **Painel e API do analisadorLD:** nichos criados à mão, aprovações, junções e recusas.

**Quando é atualizada**

- Criada pela etapa catálogo, uma vez, na montagem do catálogo (cerca de 80 nichos de serviços e 20 de e-commerce).
- Nichos novos entram por pedido de lead no Mapa, pelo painel (Catálogo → Novo nicho) ou pela API do analisadorLD,
  sempre como PROPOSTO.
- Status, junções e aprovações mudam na revisão de segunda, no painel.
- Domingo: a etapa direcao atualiza `direcao_em`. A contagem pedidos sobe a cada lead que pede o nicho.

| | |
|---|---|
| **Identifica cada linha** | `id` (e `slug`, que também é único) |
| **Ligações** | É a tabela central: buscas, negativas, series, lances, previsoes, qualidades, alertas, pacotes e fichas apontam para `nichos.id` pela coluna `nicho_id`. |

*Desta tabela, só três colunas foram usadas no dataset.txt (em destaque): `id` (para ligar cada busca ao seu nicho),
`nome` (gravada como `nicho`) e `publico`. As demais aparecem para completar a descrição da tabela.*

| Coluna | Tipo | Preenchimento | O que significa |
|---|---|---|---|
| **`id`** · CHAVE · **USADA NA LIGAÇÃO** | `text` (texto) | sempre preenchida | Identificador interno, gerado automaticamente (formato cuid, como `cmvi2g2zp00010xkao0p7dxvg`). |
| `slug` · ÚNICA | `text` (texto) | sempre preenchida | Nome curto e único do nicho, usado nos endereços do Mapa. |
| **`nome`** · **NO DATASET** como `nicho` | `text` (texto) | sempre preenchida | Nome do nicho como aparece para as pessoas. |
| **`publico`** · **NO DATASET** | `PublicoNicho` (lista fixa de valores) | sempre preenchida | Tipo de negócio: SERVICOS (atende clientes, como uma clínica) ou ECOMMERCE (vende produtos online). |
| `status` | `StatusNicho` (lista fixa de valores) | sempre preenchida | PROPOSTO: sugerido, espera a revisão de segunda.<br>ATIVO: entra na coleta semanal e no Mapa.<br>RECUSADO: não entra. Padrão: PROPOSTO. |
| `origem` | `OrigemNicho` (lista fixa de valores) | sempre preenchida | De onde veio: CNAE (atividades com mais empresas na Receita Federal), TAXONOMIA (categoria de produtos do Google, para e-commerce), LEAD (pedido de um lead do Mapa) ou MANUAL. |
| `cnaes` | `text[]` (lista de textos) | pode ficar vazia | Códigos CNAE (7 dígitos) das atividades que representam a concorrência física do nicho. No e-commerce, as do varejo físico equivalente. Liga com `empresas.cnae`. Padrão: lista vazia. |
| `categoria_google` | `integer` (número inteiro) | pode ficar vazia | Só e-commerce: número da categoria na taxonomia de produtos do Google. |
| `sinonimos` | `text[]` (lista de textos) | pode ficar vazia | Outros nomes do nicho. Viram ponto de partida (sementes) para descobrir as buscas. Padrão: lista vazia. |
| `anunciavel` | `boolean` (sim / não) | pode ficar vazia | Avaliação do Gemini quando o nicho foi proposto: se faz sentido anunciar no Google para esse ramo. |
| `motivo` | `text` (texto) | pode ficar vazia | O porquê da avaliação acima. |
| `empresas` | `integer` (número inteiro) | pode ficar vazia | Empresas ativas no Brasil somando as atividades CNAE do nicho, calculado quando o nicho entrou no catálogo (etapa catalogo). O número atualizado todo mês, por região, fica na tabela empresas. |
| `juntado_a` | `text` (texto) | pode ficar vazia | Se este nicho foi juntado a outro na revisão, o slug do nicho que ficou. |
| `proximo_slug` | `text` (texto) | pode ficar vazia | Em pedidos de lead: o nicho do catálogo mais parecido, sugerido pelo Gemini para a revisão de segunda. |
| `pedidos` | `integer` (número inteiro) | sempre preenchida | Quantos leads do Mapa pediram este nicho. Eles são avisados quando o nicho entra. Padrão: 0. |
| `criado_em` | `timestamp(3)` (data e hora, em UTC) | sempre preenchida | Quando o nicho foi criado. |
| `atualizado_em` | `timestamp(3)` (data e hora, em UTC) | sempre preenchida | Última alteração na linha (preenchido automaticamente). |
| `aprovado_em` | `timestamp(3)` (data e hora, em UTC) | pode ficar vazia | Quando o nicho foi aprovado (virou ATIVO). |
| `direcao_em` | `timestamp(3)` (data e hora, em UTC) | pode ficar vazia | Quando a direção para o Google Ads (grupos de anúncios e negativas) foi montada. É refeita quando as buscas do nicho mudam. |

## 6. Glossário

| Termo | Significado |
|---|---|
| **Nicho** | Um ramo de negócio (ex.: odontologia, pet shop, loja de roupas online). É a unidade de tudo no Observatório. |
| **Busca** | Uma pesquisa digitada no Google (ex.: "dentista perto de mim"). Cada nicho tem até 40. |
| **Planejador de palavras-chave (Planner)** | Ferramenta do Google Ads que informa quantas vezes uma busca foi feita por mês e quanto custa anunciar nela. |
| **Volume** | Quantidade de pesquisas no mês. |
| **Lance do topo da página** | Faixa de valor por clique que os anunciantes costumam pagar para o anúncio aparecer no alto da página do Google. |
| **Concorrência (0 a 100)** | Índice do Google que mostra quantos anunciantes disputam a busca, comparado com as demais. |
| **CNAE** | Código oficial da atividade econômica de uma empresa (7 dígitos). Ex.: 5611201 = restaurantes. |
| **Negativa** | Palavra que se exclui de uma campanha de Google Ads para não pagar por cliques de quem não vai comprar. |
| **Etapa** | Uma tarefa do Observatório (coleta, modelo, pacotes...). |
| **cuid** | Formato dos identificadores internos: um texto de 25 caracteres que começa com c, gerado automaticamente. |
| **UTC** | Horário universal. As colunas de data e hora estão em UTC; o horário de Brasília é 3 horas a menos. |

---

Fonte: Dicionário de dados do Observatório, Lucro Digital, versão de 07/11/2026 (seções 05, 06 e 11).
