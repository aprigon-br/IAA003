"""Painel 2: análise descritiva da amostra (358 buscas) e comparação com a população."""

import pandas as pd
import streamlit as st

import estatistica as est
import painel_comum as pc

pc.titulo_colorido("Painel 2 · Análise descritiva da amostra", pc.LARANJA, "titulo_painel2")  # laranja da amostra
st.markdown(
    "A **amostra aleatória simples de 358 buscas** (7,0% da população, semente 20261111). Esta página repete as "
    "análises do Painel 1 usando **somente a amostra**: os números aqui são **estimativas**. No final, a seção "
    "*Comparação com a população* mostra o quanto a amostra se parece com a população."
)

escolha = pc.filtro_publico("filtro_amostra")
amo = pc.aplicar_filtro(pc.dados_amostra(), escolha)
pop = pc.aplicar_filtro(pc.dados_populacao(), escolha)
if escolha != "Todos":
    st.caption(f"Mostrando só **{escolha}**: {pc.br(len(amo), 0)} buscas da amostra.")

pc.secoes_descritivas(amo, "Amostra")

# ---------------------------------------------------------------------------
st.header("Comparação com a população")
st.markdown(
    "Cores fixas em todos os painéis: <span style='color:#2a78d6'>**■ População**</span> (valor real) e "
    "<span style='color:#eb6834'>**■ Amostra**</span> (estimativa).",
    unsafe_allow_html=True,
)

# Medidas lado a lado
m_pop, m_amo = est.medidas(pop, populacao=True), est.medidas(amo, populacao=False)
linhas = []
for rotulo, coluna in zip(m_pop.columns, est.QUANTITATIVAS):
    for medida in ("média", "mediana", "desvio-padrão"):
        vp, va = m_pop.loc[medida, rotulo], m_amo.loc[medida, rotulo]
        casas = 2 if coluna == "competicao" else None
        linhas.append({
            "Variável": rotulo, "Medida": medida,
            "População": pc.br(vp, casas) if casas else pc.valor_var(coluna, vp),
            "Amostra": pc.br(va, casas) if casas else pc.valor_var(coluna, va),
            "Diferença": pc.br((va - vp) / vp * 100, 1) + "%",
        })
st.subheader("Medidas descritivas: população × amostra")
pc.tabela(pd.DataFrame(linhas), indice=False)
st.caption("Diferença = (amostra − população) / população. Desvio-padrão: σ na população, s na amostra.")

st.subheader("Distribuições: população × amostra")
a, b = st.columns([3, 1], vertical_alignment="bottom")
coluna = a.segmented_control(
    "Variável", list(est.QUANTITATIVAS), default="lance_max",
    format_func=lambda c: est.QUANTITATIVAS[c], key="var_comparacao",
) or "lance_max"
log = b.toggle("Escala logarítmica", value=coluna == "volume_brasil", key=f"log_comparacao_{coluna}")
pc.mostrar(pc.boxplot({"População": pop[coluna], "Amostra": amo[coluna]}, coluna, log, altura=300))

st.subheader("Proporções: população × amostra")
tabela_dif = []
itens = list(est.QUALITATIVAS.items())
for par in (itens[:2], itens[2:]):
    colunas = st.columns(2)
    for (coluna, rotulo), lugar in zip(par, colunas):
        t_pop, t_amo = pc.tabela_frequencias(pop, coluna), pc.tabela_frequencias(amo, coluna)
        with lugar:
            pc.titulo_grafico(rotulo)
            pc.mostrar(pc.barras_proporcao({"População": t_pop, "Amostra": t_amo}, altura=300))
        for categoria in t_pop.index:
            p, q = t_pop.loc[categoria, "proporção (%)"], t_amo.loc[categoria, "proporção (%)"]
            tabela_dif.append({"Variável": rotulo, "Categoria": categoria, "População": pc.br(p, 1) + "%",
                               "Amostra": pc.br(q, 1) + "%", "Diferença (p.p.)": pc.br(q - p, 1), "_abs": abs(q - p)})
dif = pd.DataFrame(tabela_dif)
with st.expander("Tabela: proporções da população × amostra"):
    pc.tabela(dif.drop(columns="_abs"), indice=False)

# Leitura dos resultados
maior = dif.loc[dif["_abs"].idxmax()]
med_dif = {
    rotulo: abs(m_amo.loc["mediana", rotulo] - m_pop.loc["mediana", rotulo]) / m_pop.loc["mediana", rotulo] * 100
    for rotulo in m_pop.columns
}
media_dif = {
    rotulo: (m_amo.loc["média", rotulo] - m_pop.loc["média", rotulo]) / m_pop.loc["média", rotulo] * 100
    for rotulo in m_pop.columns
}
def com_sinal(v: float) -> str:
    return ("+" if v > 0 else "") + pc.br(v, 1) + "%"


st.subheader("O que a comparação mostra")
st.markdown(
    f"""
- **Proporções:** todas ficaram perto da população. A maior diferença foi de **{pc.br(maior['_abs'], 1)} ponto
  percentual** ({maior['Variável']}, categoria "{maior['Categoria']}"), bem dentro da margem de erro de 5 pontos usada
  no dimensionamento. Categorias raras (como *Manual*, com poucas buscas) oscilam mais em termos relativos.
- **Medianas:** estáveis, com diferença máxima de {pc.br(max(med_dif.values()), 1)}% entre população e amostra.
- **Médias:** variam mais nas variáveis assimétricas: volume {com_sinal(media_dif['Volume (pesquisas/mês)'])},
  lance máximo {com_sinal(media_dif['Lance máximo (R$)'])}, contra {com_sinal(media_dif['Competição (0-100)'])} na
  competição (quase simétrica). A média depende de a amostra "pegar" ou não alguns valores extremos; a mediana não.
- **Extremos:** os maiores valores da população raramente entram numa amostra de 7%. Por isso o máximo e o
  desvio-padrão da amostra são menos confiáveis do que a mediana e os quartis.
""".replace("$", "\\$")
)
