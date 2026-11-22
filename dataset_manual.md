# Manual do dataset

**`dataset.txt` · buscas do Google por ramo de negócio**

## 1. O que é este dataset

O [`dataset.txt`](dataset.txt) reúne as buscas do Google que representam cada ramo de negócio (nicho) acompanhado pelo
Observatório Lucro Digital, o centro de pesquisa de mercado de uma agência de marketing digital. Para cada busca (por
exemplo, "dentista perto de mim"), o arquivo traz quantas pessoas a pesquisam por mês no Brasil, quanto custa anunciar
para aparecer no topo da página do Google e quão disputada ela é entre anunciantes.

- **Fonte primária:** Google Ads API, ferramenta Planejador de palavras-chave (Keyword Planner).
- **Origem no banco:** PostgreSQL do Observatório, tabela `observatorio.buscas` unida à tabela `observatorio.nichos`
  (de onde vêm o nome do nicho e o público).
- **Extração:** 11/11/2026, pelo script `gerar_dataset.py`. O arquivo está congelado: é a população do trabalho.
- **Tamanho:** 5.124 linhas (buscas) × 14 colunas, de 137 nichos; 1,1 MB.
- Cada linha é uma busca de um nicho. O mesmo texto pode aparecer em dois nichos (45 casos).

## 2. Formato do arquivo

| Característica | Como é no arquivo |
|---|---|
| Tipo de arquivo | texto puro (.txt) |
| Codificação | UTF-8 (acentos preservados) |
| Separador de colunas | TAB (tabulação), não vírgula nem ponto e vírgula |
| Primeira linha | cabeçalho com os nomes das 14 colunas |
| Números decimais | com ponto (ex.: 1.21 = R$ 1,21) |
| Valores verdadeiro/falso | `True` ou `False` |
| Datas e horas | `AAAA-MM-DD HH:MM:SS.mmm`, no fuso UTC (Brasília = UTC − 3h) |
| Valores ausentes | campo em branco (nada entre dois TABs) |
| Ordem das linhas | por nome do nicho e, dentro do nicho, da busca mais pesquisada para a menos |

**Para abrir em Python:**

```python
import pandas as pd
df = pd.read_csv("dataset.txt", sep="\t")
```

**Para abrir no Excel:** Dados → Obter dados → De Texto/CSV → escolha o arquivo, defina o delimitador como Tabulação e,
em configurações regionais, use o ponto como separador decimal (senão 1.21 pode virar data).

## 3. As colunas

| # | Coluna | Tipo | Exemplo / valores | O que significa | Vazios |
|---|---|---|---|---|---|
| 1 | `id` | texto (25 caracteres) | `cmuz3udlr025m0xqtz25zzi58` | Identificador único da busca (formato cuid). | 0 |
| 2 | `nicho_id` | texto (25 ou 36 caracteres) | `cmuz3hysl001f0xqtyps0nu7d` | Identificador do nicho. Quase sempre cuid (25); 2 nichos criados depois usam UUID (36, ex.: `5b3626f3-999e-…`). | 0 |
| 3 | `nicho` | texto | Academia de ginástica | Nome do ramo de negócio (137 nichos). | 0 |
| 4 | `publico` | categoria | `SERVICOS` / `ECOMMERCE` | Tipo de negócio: atende clientes (serviços) ou vende online. | 0 |
| 5 | `texto` | texto (minúsculas) | academia perto de mim | A busca, como o Google a devolve. | 0 |
| 6 | `origem` | categoria | `SEMENTE` / `EXPANSAO` / `MANUAL` | Escrita pela IA, sugerida pelo Google ou incluída à mão. | 0 |
| 7 | `ativa` | verdadeiro/falso | `True` / `False` | Se a busca entra na soma do nicho (quase todas True). | 0 |
| 8 | `volume_brasil` | número inteiro | 301000 | Média de pesquisas por mês no Brasil, últimos 12 meses. | 0 |
| 9 | `lance_min` | decimal (2 casas) | 1.21 | Ponta de baixo da faixa de lance para o topo da página, em R$ por clique. | 128 |
| 10 | `lance_max` | decimal (2 casas) | 5.52 | Ponta de cima da mesma faixa, em R$ por clique. | 128 |
| 11 | `competicao` | número inteiro (0 a 100) | 37 | Índice de concorrência do Google entre anunciantes. | 31 |
| 12 | `grupo` | texto | Academia perto de mim | Grupo de anúncios sugerido pela IA (600 grupos diferentes). | 7 |
| 13 | `criado_em` | data e hora (UTC) | 2026-10-08 05:37:32.511 | Quando a busca entrou no sistema. | 0 |
| 14 | `atualizado_em` | data e hora (UTC) | 2026-10-08 05:37:32.511 | Última alteração da linha. | 0 |

As análises do trabalho também usam duas variáveis derivadas, que não estão no arquivo e são calculadas a partir dele:
`competicao_alta` (Sim se `competicao` ≥ 67) e `intencao_local` (Sim se `texto` contém "perto" ou "próximo/próxima").

## 4. Resumo rápido das colunas numéricas

| Coluna | Mínimo | Mediana | Média | Máximo | Vazios |
|---|---:|---:|---:|---:|---:|
| `volume_brasil` (pesquisas/mês) | 0 | 1.300 | 7.924,03 | 1.000.000 | 0 |
| `lance_min` (R$) | 0,02 | 0,90 | 1,52 | 19,04 | 128 |
| `lance_max` (R$) | 0,33 | 3,99 | 7,49 | 107,80 | 128 |
| `competicao` (0 a 100) | 0 | 66 | 64,82 | 100 | 31 |

**Público:** 4.197 buscas de serviços (81,9%) e 927 de e-commerce (18,1%). **Origem:** 4.845 EXPANSAO, 258 SEMENTE e
21 MANUAL.

## 5. Exemplo: 15 linhas do arquivo

Quinze linhas escolhidas ao acaso (nichos diferentes, serviços e e-commerce, incluindo uma linha com valores vazios),
mostradas exatamente como estão no arquivo. Como as 14 colunas não cabem lado a lado, a tabela está dividida em duas
partes; a coluna **Linha** (posição no arquivo, sem contar o cabeçalho) liga as duas.

### Parte A: identificação da busca

| Linha | id | nicho_id | nicho | publico | texto |
|---:|---|---|---|---|---|
| 195 | `cmuz3ra2u01jj0xqtju0w4f7s` | `cmuz3hys900180xqtfwaeisz6` | Agência de viagens e turismo | SERVICOS | pesquisar passagens aereas baratas |
| 616 | `cmuz433nn03jc0xqtainqg02c` | `cmuz3hyut002q0xqtd48p1eon` | Autoescola | SERVICOS | carteira de habilitação preço |
| 1261 | `cmv11g2ir00150ys9xyd3974f` | `5b3626f3-999e-4df3-a929-80a50939e34d` | Consórcio | SERVICOS | consorcio carro |
| 1375 | `cmuz3o43w015q0xqtmi6825di` | `cmuz3hyrb000o0xqtrvbdu9ch` | Consultoria empresarial | SERVICOS | empresa de consultoria financeira empresarial |
| 2002 | `cmuz3yrjj02s80xqtp3hdc6vw` | `cmuz3hytx00280xqtj2f7fdoe` | Encanador | SERVICOS | preço de caça vazamento |
| 2361 | `cmuz3vl8602bu0xqt24vk5ppp` | `cmuz3hywk003n0xqt9qfmi93d` | Ferramentas | ECOMMERCE | parafusadeira da makita |
| 2572 | `cmuz3o43d012c0xqtm8790krq` | `cmuz3hyr5000l0xqtc56746bz` | Home care e enfermagem domiciliar | SERVICOS | cuidadora home care |
| 2957 | `cmuz3wu2q02fo0xqtbu23j3nf` | `cmuz3hyuc002g0xqt9zyx630y` | Locação de máquinas para construção | SERVICOS | aluguel betoneira 400 litros |
| 3781 | `cmuz3yrj702pp0xqtoq5f1oda` | `cmuz3hytd001x0xqtz64qcfkv` | Oficina de motos | SERVICOS | oficina de moto perto |
| 3958 | `cmuz3vl7o028r0xqtxo2psykn` | `cmuz3hysp001i0xqtcv3y65mo` | Ótica | SERVICOS | armação oculos grau masculino |
| 4056 | `cmuz3xrju02nu0xqt8we6idw7` | `cmuz3hyt6001t0xqtybpvto7v` | Papelaria | SERVICOS | estojo quadrado barato |
| 4243 | `cmuz3o43p013x0xqttdw8nfqu` | `cmuz3hyro000w0xqt0tuq8jxv` | Pet shop e banho e tosa | SERVICOS | pet shop perto de mim banho e tosa |
| 4414 | `cmvlggerb00870zr3tgv6i5eh` | `cmvlf5if800070wqlnxiyf0zu` | Pneus para caminhão | ECOMMERCE | pneus michelin 215 75r17 5 |
| 4612 | `cmuz3j61900570xqti3enbjgw` | `cmuz3hyvo00370xqty5zkzfww` | Roupas femininas | ECOMMERCE | conjunto feminino calça e blusa |
| 5084 | `cmuz3mees00ud0xqtv29kdfkn` | `cmuz3hywc003i0xqtvfge6ey0` | Videogames e consoles | ECOMMERCE | nintendo switch 64gb |

### Parte B: medidas e controle

| Linha | origem | ativa | volume_brasil | lance_min | lance_max | competicao | grupo | criado_em | atualizado_em |
|---:|---|---|---:|---:|---:|---:|---|---|---|
| 195 | EXPANSAO | True | 390 | 0.93 | 3.81 | 82 | Passagens aéreas e hospedagem | 2026-10-08 05:35:07.974 | 2026-10-08 05:35:07.974 |
| 616 | EXPANSAO | True | 880 | 0.81 | 2.88 | 13 | Preço carteira de motorista | 2026-10-08 05:44:19.523 | 2026-10-08 05:44:19.523 |
| 1261 | EXPANSAO | True | 40500 | 3.16 | 10.22 | 80 | Consórcio de carros e veículos | 2026-10-09 14:05:58.083 | 2026-10-09 14:05:58.083 |
| 1375 | EXPANSAO | True | 20 | 5.00 | 43.55 | 73 | Consultoria financeira e administrativa | 2026-10-08 05:32:40.267 | 2026-10-08 05:32:40.267 |
| 2002 | EXPANSAO | True | 30 | 3.34 | 8.88 | 63 | Preço de caça vazamento | 2026-10-08 05:40:57.198 | 2026-10-08 05:40:57.198 |
| 2361 | EXPANSAO | True | 33100 | 0.26 | 1.08 | 100 | Parafusadeiras em geral | 2026-10-08 05:38:29.046 | 2026-10-08 05:38:29.046 |
| 2572 | EXPANSAO | True | 70 | 2.25 | 8.65 | 57 | Cuidador e home care | 2026-10-08 05:32:40.249 | 2026-10-08 05:32:40.249 |
| 2957 | EXPANSAO | True | 320 | 1.93 | 9.91 | 63 | Aluguel de betoneiras | 2026-10-08 05:39:27.170 | 2026-10-08 05:39:27.170 |
| 3781 | EXPANSAO | True | 480 | 0.49 | 2.27 | 25 | Oficina perto de mim | 2026-10-08 05:40:57.187 | 2026-10-08 05:40:57.187 |
| 3958 | EXPANSAO | True | 2900 | 0.63 | 2.69 | 100 | Armações de óculos masculinas | 2026-10-08 05:38:29.028 | 2026-10-08 05:38:29.028 |
| 4056 | EXPANSAO | True | 390 | *(vazio)* | *(vazio)* | 66 | Cadernos e itens de escrita | 2026-10-08 05:40:10.554 | 2026-10-08 05:40:10.554 |
| 4243 | EXPANSAO | True | 1300 | 1.07 | 3.84 | 58 | Banho e tosa | 2026-10-08 05:32:40.261 | 2026-10-08 05:32:40.261 |
| 4414 | EXPANSAO | True | 590 | 0.65 | 5.18 | 100 | Pneus de medida 215 | 2026-10-23 21:01:31.703 | 2026-10-23 21:01:31.703 |
| 4612 | EXPANSAO | True | 8100 | 0.26 | 1.89 | 100 | Conjuntos e peças sociais | 2026-10-08 05:28:49.485 | 2026-10-08 05:28:49.485 |
| 5084 | EXPANSAO | True | 480 | 0.22 | 0.96 | 99 | Nintendo Switch OLED consoles | 2026-10-08 05:31:20.308 | 2026-10-08 05:31:20.308 |
