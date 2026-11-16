"""Página inicial: a base de dados, a população, o dimensionamento e o sorteio da amostra."""

import pandas as pd
import streamlit as st

import painel_comum as pc

pop = pc.dados_populacao()
amo = pc.dados_amostra()

# Paleta roxa: a mesma "violet" do tema claro do Streamlit (usada no título com :violet[...])
ROXO, ROXO_FUNDO, ROXO_TEXTO = "#9b5de5", "#f8f2ff", "#6f33b8"

# Títulos juntos e nome da aluna com metade do tamanho do título (estilo vale só para estes containers)
TAMANHO_TITULO = 2.75  # rem: tamanho padrão do st.title (h1) no tema do Streamlit
st.html(f"""
<style>
.st-key-titulos_inicio h1 {{ padding-top: 0.25rem; padding-bottom: 0.25rem; }}
.st-key-aluna p {{ font-size: {TAMANHO_TITULO / 2}rem; line-height: 1.3; }}
</style>
""")
with st.container(key="titulos_inicio", gap=None):
    st.title("IAA003 - Estatística e Probabilidade para IA")
    st.title(":violet[Buscas do Google por ramo de negócio]")
with st.container(key="aluna"):
    st.markdown("**Aluna:** Ana Paula Rigon")
st.markdown(
    "Quantas buscas são executadas por ramo de negócio no Google, e quanto custa anunciar?  \n"
    "Este trabalho compara a população de buscas com uma amostra aleatória simples, estimando proporções e médias "
    "com intervalos de confiança e testes de hipóteses."
)

# Botões dos painéis em roxo: o estilo vale só dentro do container "botoes_paineis"
st.html(f"""
<style>
.st-key-botoes_paineis a {{
    background-color: {ROXO_FUNDO};
    border: 1px solid {ROXO};
    border-radius: 0.5rem;
}}
.st-key-botoes_paineis a, .st-key-botoes_paineis a * {{ color: {ROXO_TEXTO} !important; }}
.st-key-botoes_paineis a:hover {{ background-color: {ROXO}; }}
.st-key-botoes_paineis a:hover, .st-key-botoes_paineis a:hover * {{ color: #ffffff !important; }}
</style>
""")
with st.container(key="botoes_paineis"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("paginas/populacao.py", label="**Painel 1:** análise descritiva da população",
                     icon=":material/groups:", width="stretch")
    with c2:
        st.page_link("paginas/amostra.py", label="**Painel 2:** análise descritiva da amostra",
                     icon=":material/filter_alt:", width="stretch")
    with c3:
        st.page_link("paginas/inferencia.py", label="**Painel 3:** inferência e comparação",
                     icon=":material/functions:", width="stretch")

k = st.columns(4)
k[0].metric("Observações (buscas)", pc.br(len(pop), 0))
k[1].metric("Variáveis no arquivo", "14")
k[2].metric("Nichos (ramos de negócio)", pc.br(pop["nicho"].nunique(), 0))
k[3].metric("Tamanho da amostra", pc.br(len(amo), 0), help="7,0% da população")

st.header("A base de dados")
st.markdown(
    """
**Fonte:** Google Ads API, ferramenta *Planejador de palavras-chave* (Keyword Planner), a base oficial do Google
sobre volume de pesquisas e custo de anúncios. Os dados foram coletados e organizados pelo **Observatório Lucro Digital**
e extraídos em **11/11/2026**.

**Arquivo publicado:** `dataset.txt` no repositório do trabalho (texto separado por TAB, 5.124 linhas, 14 colunas).

**Contexto:** o Observatório é o centro de pesquisa de mercado da Lucro Digital, uma agência de marketing digital.
Toda semana ele consulta o Google para saber quantas pessoas pesquisaram por cada ramo de negócio (*nicho*:
dentista, padaria, pet shop, loja de roupas online…) e quanto custa anunciar para aparecer nessas pesquisas.
Cada nicho é representado por um conjunto de **buscas**, as frases que as pessoas digitam no Google, como
"dentista perto de mim".

**Objetivo da base:** medir a demanda e o custo de anunciar em cada ramo de negócio no Google, no Brasil.
"""
)

p1, p2 = st.columns(2)
with p1:
    st.markdown(
        """
**População de interesse:** cada instância é uma "Busca/Texto pesquisado" no Google, sendo a população composta por
5.124 buscas monitoradas pelo Observatório na extração de 11/11/2026. É uma população finita e totalmente conhecida: seus parâmetros podem ser calculados diretamente
e comparados com as estimativas da amostra.
"""
    )
with p2:
    st.markdown(
        """
**Unidade amostral:** uma busca de um nicho (uma linha do arquivo). O mesmo texto pode aparecer
em dois nichos (45 casos), e cada ocorrência é uma unidade.
"""
    )

st.subheader("Variáveis selecionadas")
variaveis = pd.DataFrame(
    [
        ("volume_brasil", "Quantitativa discreta", "Média de pesquisas por mês no Brasil (últimos 12 meses)"),
        ("lance_min", "Quantitativa contínua", "Ponta de baixo da faixa de lance para o topo da página (R$/clique)"),
        ("lance_max", "Quantitativa contínua", "Ponta de cima da faixa de lance para o topo da página (R$/clique)"),
        ("competicao", "Quantitativa discreta", "Índice de concorrência entre anunciantes, de 0 a 100"),
        ("publico", "Qualitativa nominal", "SERVICOS (atende clientes) ou ECOMMERCE (vende online)"),
        ("origem", "Qualitativa nominal", "SEMENTE (escrita pela IA), EXPANSAO (sugerida pelo Google), MANUAL"),
        ("competicao_alta", "Qualitativa binária (derivada)", "Sim se competicao ≥ 67 (terço superior da escala)"),
        ("intencao_local", "Qualitativa binária (derivada)", "Sim se o texto contém \"perto\" ou \"próximo/próxima\""),
        ("nicho", "Qualitativa nominal", "137 ramos de negócio. Só na análise descritiva (poucos casos por nicho na amostra)"),
    ],
    columns=["Variável", "Tipo", "Descrição"],
)
pc.tabela(variaveis, indice=False)
st.caption(
    "Não usadas: id e nicho_id (identificadores), texto (só para derivar a intenção local), grupo (600 categorias "
    "de texto livre), ativa (5.117 de 5.124 são \"sim\") e as datas de controle. Valores ausentes: lance_min e "
    "lance_max 128 (2,5%), competicao 31 (0,6%), descartados em cada cálculo."
)

st.header("Dimensionamento da amostra")
d1, d2 = st.columns([3, 2])
with d1:
    st.markdown(
        """
A amostra foi dimensionada para **estimar uma proporção**:

| Parâmetro | Valor | Justificativa |
|---|---|---|
| População (N) | 5.124 | total de buscas |
| Nível de confiança | 95% (z = 1,96) | padrão em pesquisas |
| Margem de erro (E) | 5 pontos percentuais | precisão suficiente com amostra viável |
| Proporção esperada (p) | 50% | conservadora: p·(1−p) é máximo em 0,5 |

- n₀ = z² · p · (1 − p) / E² = 1,96² × 0,5 × 0,5 / 0,05² = **384,15** (população infinita)
- n = n₀ / (1 + (n₀ − 1)/N) = **357,42**, arredondado para cima: **n = 358** (correção para população finita)

Calculado na [Calculadora Amostral da Comentto](https://comentto.com/calculadora-amostral/) (a da USP/Bauru
estava fora do ar) e conferido pela mesma fórmula em Python.
"""
    )
with d2:
    st.markdown("**Sensibilidade:** como n muda com os parâmetros")
    pc.tabela(pd.DataFrame({"Confiança": ["90%", "95%", "99%"], "E = 3%": ["656", "884", "1.356"],
                            "E = 5%": ["258", "**358** ◀ usado", "588"], "E = 7%": ["135", "189", "318"]}),
              indice=False)

st.header("Seleção da amostra aleatória simples (AAS)")
st.markdown(
    """
- **Método:** sorteio **sem reposição**, em que todas as buscas têm a mesma chance: 358 / 5.124 = **6,99%**.
- **Ferramenta:** Python, `DataFrame.sample(n=358, replace=False, random_state=20261111)` (pandas/NumPy).
- **Semente aleatória 20261111** (a data do sorteio), escolhida antes de ver o resultado e nunca alterada. Com ela,
  o sorteio é reproduzível: quem aplicar esse comando ao `dataset.txt` obtém exatamente as mesmas 358 buscas.
- **Conferências:** 358 buscas distintas, todas idênticas a linhas da população, de 125 dos 137 nichos.
"""
)
