"""
Página extra: "Onde vale a pena anunciar no Google?"

Adaptação do dashboard da pasta EDA (EDA/atividade02_dashboard/app.py) para rodar dentro do app do trabalho final.
Diferenças em relação ao original:
- lê o mesmo dataset.txt da raiz do IAA003 (via estatistica.ARQUIVO_POPULACAO), como as demais páginas;
- não chama st.set_page_config (quem configura a página é o app.py);
- as chaves dos widgets têm o prefixo "eda_", para não colidir com as das outras páginas.
Lê SOMENTE o arquivo .txt, nunca o banco de dados.
"""

import altair as alt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import estatistica as est

ARQUIVO = est.ARQUIVO_POPULACAO  # o mesmo dataset.txt usado pelos painéis 1, 2 e 3
AZUL, LARANJA, CINZA = "#2a78d6", "#eb6834", "#898781"
NOME_PUBLICO = {"SERVICOS": "Serviços", "ECOMMERCE": "E-commerce"}
COR_PUBLICO = {"Serviços": AZUL, "E-commerce": LARANJA}
ESCALA_COR = alt.Scale(domain=list(COR_PUBLICO), range=list(COR_PUBLICO.values()))
VIRGULA = "replace(datum.label, '.', ',')"  # rótulos de eixo com vírgula decimal (Altair/Vega)


def br(v, casas=0):
    """Formata número no padrão brasileiro: 1234.5 -> '1.234,5'."""
    t = f"{v:,.{casas}f}"
    return t.replace(",", "§").replace(".", ",").replace("§", ".")


def reais(v):
    return "R\\$ " + br(v, 2)  # "\$" evita que o Markdown do Streamlit trate o cifrão como fórmula


@st.cache_data
def carregar_eda() -> pd.DataFrame:
    df = pd.read_csv(ARQUIVO, sep="\t", encoding="utf-8")
    df["publico_nome"] = df["publico"].map(NOME_PUBLICO)
    df["intencao_local"] = df["texto"].str.contains(est.PADRAO_INTENCAO_LOCAL, regex=True)
    return df


def sem_dados(mensagem: str) -> None:
    st.warning(f"{mensagem} Ajuste os filtros na barra lateral.", icon=":material/filter_alt_off:")


df_total = carregar_eda()

# ---------------------------------------------------------------------------
# Filtros globais (barra lateral)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    publicos = st.pills("Público", ["Serviços", "E-commerce"], selection_mode="multi",
                        default=["Serviços", "E-commerce"], key="eda_publico",
                        help="Serviços atendem clientes (ex.: clínica); e-commerce vende produtos online.")
    tipo = st.segmented_control("Tipo de busca", ["Todas", "Com \"perto/próximo\"", "Sem \"perto/próximo\""],
                                default="Todas", key="eda_tipo",
                                help="Intenção local: a busca contém \"perto\" ou \"próximo/próxima\".")
    volume_min = st.select_slider("Volume mínimo da busca (pesquisas/mês)", options=[0, 50, 100, 500, 1000, 5000, 10000],
                                  value=0, format_func=lambda v: br(v), key="eda_volume_min")
    st.divider()
    st.caption("**Fonte:** Google Ads Keyword Planner, via Observatório Lucro Digital. Extração de 11/11/2026; "
               "volume = média mensal dos últimos 12 meses no Brasil.")

df = df_total[df_total["publico_nome"].isin(publicos or [])]
if tipo == "Com \"perto/próximo\"":
    df = df[df["intencao_local"]]
elif tipo == "Sem \"perto/próximo\"":
    df = df[~df["intencao_local"]]
df = df[df["volume_brasil"] >= volume_min]

# ---------------------------------------------------------------------------
# Cabeçalho e indicadores
# ---------------------------------------------------------------------------
st.title("Onde vale a pena anunciar no Google?")
st.markdown(
    "Análise exploratória para **gestores de tráfego e donos de pequenos negócios** compararem a procura e o custo de "
    f"anunciar em {df_total['nicho'].nunique()} ramos de negócio (*nichos*), usando a mesma base do trabalho. Cada busca "
    "é uma frase digitada no Google, como \"dentista perto de mim\". Use os filtros da barra lateral; todas as abas "
    "respondem a eles."
)

if df.empty:
    sem_dados("Nenhuma busca atende a essa combinação de filtros.")
    st.stop()

k = st.columns(5)
k[0].metric("Buscas", br(len(df)), help="Buscas que atendem aos filtros")
k[1].metric("Nichos", br(df["nicho"].nunique()))
k[2].metric("Volume mediano", br(df["volume_brasil"].median()), help="Pesquisas por mês no Brasil (mediana por busca)")
lance_med = df["lance_max"].median()
k[3].metric("Lance máx. mediano", "—" if np.isnan(lance_med) else "R$ " + br(lance_med, 2),
            help="Lance para aparecer no topo da página, em R$ por clique")
k[4].metric("Competição média", br(df["competicao"].mean(), 1), help="Índice do Google de 0 a 100")

aba1, aba2, aba3, aba4 = st.tabs(["1 · Oportunidades por nicho", "2 · Custo do clique", "3 · Buscas \"perto de mim\"",
                                  "4 · Competição × custo"])

# ---------------------------------------------------------------------------
# Pergunta 1: oportunidades (Plotly)
# ---------------------------------------------------------------------------
with aba1:
    st.subheader("Quais nichos combinam alta demanda com baixa competição?")
    limite = st.slider("Considerar \"baixa competição\" abaixo de (índice 0 a 100)", 10, 90, 50, step=5, key="eda_limite")
    nichos = (df.groupby(["nicho", "publico_nome"])
                .agg(volume=("volume_brasil", "sum"), competicao=("competicao", "mean"),
                     lance=("lance_max", "median"), buscas=("id", "size"))
                .reset_index().dropna(subset=["competicao"]))
    nichos = nichos[nichos["volume"] > 0]
    if nichos.empty:
        sem_dados("Não há nichos com competição informada para esses filtros.")
    else:
        corte_volume = nichos["volume"].median()
        nichos["oportunidade"] = (nichos["volume"] > corte_volume) & (nichos["competicao"] < limite)
        fig = go.Figure()
        for publico, cor in COR_PUBLICO.items():
            parte = nichos[nichos["publico_nome"] == publico]
            if parte.empty:
                continue
            fig.add_scatter(
                x=parte["volume"], y=parte["competicao"], mode="markers", name=publico,
                marker=dict(color=cor, size=np.clip(np.sqrt(parte["lance"].fillna(1)) * 7, 6, 40), opacity=0.7,
                            line=dict(color="white", width=1)),
                customdata=np.c_[parte["nicho"], parte["lance"].fillna(np.nan), parte["buscas"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Volume total: %{x:,.0f} pesquisas/mês<br>"
                              "Competição média: %{y:.1f}<br>Lance mediano: R$ %{customdata[1]:.2f}<br>"
                              "Buscas no filtro: %{customdata[2]}<extra></extra>",
            )
        fig.add_shape(type="rect", x0=corte_volume, x1=nichos["volume"].max() * 1.5, y0=0, y1=limite,
                      fillcolor="rgba(42,120,214,0.07)", line=dict(width=0), layer="below")
        fig.add_hline(y=limite, line=dict(color=CINZA, dash="dash", width=1))
        fig.add_vline(x=corte_volume, line=dict(color=CINZA, dash="dash", width=1))
        fig.add_annotation(x=np.log10(nichos["volume"].max()), y=3, text="zona de oportunidade", showarrow=False,
                           xanchor="right", yanchor="bottom", font=dict(color=AZUL))
        fig.update_layout(height=460, separators=",.", margin=dict(l=10, r=10, t=30, b=10),
                          legend=dict(orientation="h", y=1.05, x=0), template="plotly_white")
        fig.update_xaxes(type="log", title="Volume total do nicho (pesquisas/mês), escala log",
                         tickvals=[10**k for k in range(2, 8)],
                         ticktext=["100", "1 mil", "10 mil", "100 mil", "1 milhão", "10 milhões"])
        fig.update_yaxes(title="Competição média (0 a 100)", range=[0, 105])
        st.plotly_chart(fig, theme=None, config={"displaylogo": False})
        st.caption("Cada ponto é um nicho; o tamanho do ponto cresce com o lance mediano. Linhas tracejadas: mediana "
                   "do volume entre os nichos filtrados e o limite de competição escolhido.")

        oport = nichos[nichos["oportunidade"]].sort_values("volume", ascending=False)
        if oport.empty:
            st.info(f"Nenhum nicho tem volume acima da mediana e competição abaixo de {limite}. Tente aumentar o limite.")
        else:
            st.markdown(f"**{len(oport)} nicho(s) na zona de oportunidade** (volume acima de "
                        f"{br(corte_volume)} pesquisas/mês e competição abaixo de {limite}):")
            st.dataframe(
                oport[["nicho", "publico_nome", "volume", "competicao", "lance", "buscas"]],
                hide_index=True,
                column_config={
                    "nicho": "Nicho", "publico_nome": "Público",
                    "volume": st.column_config.NumberColumn("Volume total (pesquisas/mês)", format="localized"),
                    "competicao": st.column_config.ProgressColumn("Competição média", min_value=0, max_value=100,
                                                                  format="%.0f"),
                    "lance": st.column_config.NumberColumn("Lance mediano (R$/clique)", format="localized"),
                    "buscas": st.column_config.NumberColumn("Buscas"),
                },
            )

# ---------------------------------------------------------------------------
# Pergunta 2: custo do clique por nicho (Altair)
# ---------------------------------------------------------------------------
with aba2:
    st.subheader("Quanto custa o clique em cada nicho?")
    com_lance = df.dropna(subset=["lance_max"])
    if com_lance.empty:
        sem_dados("Não há buscas com lance informado para esses filtros.")
    else:
        mediana_nicho = com_lance.groupby("nicho")["lance_max"].median().sort_values(ascending=False)
        escolha = st.multiselect("Nichos para comparar", mediana_nicho.index.tolist(),
                                 default=mediana_nicho.index[:12].tolist(),
                                 # a chave muda com os filtros: ao mudar o recorte, a sugestão é refeita
                                 key=f"eda_nichos_{'-'.join(publicos or [])}_{tipo}_{volume_min}",
                                 help="Por padrão, os 12 nichos com o clique mais caro dentro dos filtros.")
        if not escolha:
            st.info("Selecione pelo menos um nicho para ver a distribuição do lance.")
        else:
            dados = com_lance[com_lance["nicho"].isin(escolha)]
            ordem = mediana_nicho[mediana_nicho.index.isin(escolha)].index.tolist()
            grafico = (alt.Chart(dados).mark_boxplot(extent=1.5, size=14, median={"color": "black"})
                       .encode(x=alt.X("lance_max:Q", scale=alt.Scale(type="log", nice=False),
                                       title="Lance máximo para o topo da página (R$ por clique), escala log",
                                       axis=alt.Axis(format="~g", labelExpr=VIRGULA)),
                               y=alt.Y("nicho:N", sort=ordem, title=None,
                                       axis=alt.Axis(labelLimit=320, labelOverlap=False)),
                               color=alt.Color("publico_nome:N", scale=ESCALA_COR, title="Público"))
                       .properties(height=max(220, 28 * len(ordem))))
            st.altair_chart(grafico, width="stretch")
            caro, barato = ordem[0], ordem[-1]
            st.markdown(
                f"Ordenado do clique mais caro para o mais barato (mediana). Entre os selecionados, **{caro}** tem o "
                f"clique mediano mais caro ({reais(mediana_nicho[caro])}) e **{barato}** o mais barato "
                f"({reais(mediana_nicho[barato])}). Caixas largas indicam nichos em que o preço varia muito de uma "
                "busca para outra: vale escolher as buscas com cuidado."
            )

# ---------------------------------------------------------------------------
# Pergunta 3: intenção local (Altair)
# ---------------------------------------------------------------------------
with aba3:
    st.subheader("Buscas \"perto de mim\" são diferentes das demais do mesmo nicho?")
    if tipo != "Todas":
        st.info("Esta comparação precisa das buscas locais **e** das demais. Volte o filtro *Tipo de busca* para "
                "\"Todas\".")
    else:
        metrica = st.segmented_control("Comparar", ["Competição", "Volume", "Lance"], default="Competição",
                                       key="eda_metrica_local") or "Competição"
        coluna = {"Competição": "competicao", "Volume": "volume_brasil", "Lance": "lance_max"}[metrica]
        titulo = {"Competição": "Competição mediana (0 a 100)", "Volume": "Volume mediano (pesquisas/mês), escala log",
                  "Lance": "Lance máximo mediano (R$ por clique)"}[metrica]
        med = (df.groupby(["nicho", "intencao_local"])[coluna].median().unstack()
                 .rename(columns={True: "Com perto/próximo", False: "Demais buscas"}))
        n_local = df[df["intencao_local"]].groupby("nicho").size()
        med = med.dropna()  # só nichos com os dois tipos de busca
        med = med[med.index.isin(n_local[n_local >= 3].index)]  # mediana local com pelo menos 3 buscas
        if med.empty:
            sem_dados("Nenhum nicho tem, ao mesmo tempo, buscas locais e não locais nesses filtros.")
        else:
            med["diferenca"] = med["Com perto/próximo"] - med["Demais buscas"]
            longo = med.reset_index().melt(id_vars=["nicho", "diferenca"], value_vars=["Com perto/próximo", "Demais buscas"],
                                           var_name="tipo", value_name="valor")
            ordem = med.sort_values("diferenca").index.tolist()
            escala_x = alt.Scale(type="log") if coluna == "volume_brasil" else alt.Scale(zero=False)
            base = alt.Chart(longo).encode(y=alt.Y("nicho:N", sort=ordem, title=None,
                                                   axis=alt.Axis(labelLimit=320, labelOverlap=False)))
            linhas = base.mark_rule(color="#c3c2b7", strokeWidth=2).encode(x="min(valor):Q", x2="max(valor):Q")
            pontos = base.mark_circle(size=90, opacity=1).encode(
                x=alt.X("valor:Q", scale=escala_x, title=titulo),
                color=alt.Color("tipo:N", scale=alt.Scale(domain=["Com perto/próximo", "Demais buscas"],
                                                          range=[AZUL, CINZA]), title=None),
                tooltip=[alt.Tooltip("nicho:N", title="Nicho"), alt.Tooltip("tipo:N", title="Tipo"),
                         alt.Tooltip("valor:Q", title=metrica, format=",.2f")])
            st.altair_chart((linhas + pontos).properties(height=max(240, 24 * len(ordem))), width="stretch")
            menor = (med["diferenca"] < 0).sum()
            st.markdown(
                f"Cada linha liga, num mesmo nicho, a mediana das buscas com \"perto/próximo\" (azul) e das demais "
                f"(cinza). Em **{menor} de {len(med)} nichos** a {metrica.lower()} das buscas locais é **menor**. "
                + ("Buscas locais tendem a ter menos disputa: uma oportunidade para negócios de bairro."
                   if metrica == "Competição" and menor > len(med) / 2 else
                   "Compare as métricas para ver se as buscas locais compensam em procura e custo.")
            )
            st.caption("Só aparecem nichos com pelo menos 3 buscas com \"perto/próximo\" e alguma busca sem; "
                       "na prática, quase todos são de serviços.")

# ---------------------------------------------------------------------------
# Pergunta 4: competição × custo (Altair)
# ---------------------------------------------------------------------------
with aba4:
    st.subheader("O índice de competição ajuda a prever o custo do clique?")
    separar = st.toggle("Separar por público", value=False, key="eda_separar",
                        help="Mostra serviços e e-commerce em gráficos lado a lado.")
    d = df.dropna(subset=["competicao", "lance_max"])
    if len(d) < 3:
        sem_dados("Há poucas buscas com competição e lance informados para esses filtros.")
    else:
        grafico = (alt.Chart(d).mark_circle(size=22, opacity=0.45)
                   .encode(x=alt.X("competicao:Q", title="Competição (índice de 0 a 100)"),
                           y=alt.Y("lance_max:Q", scale=alt.Scale(type="log", nice=False),
                                   title="Lance máximo (R$ por clique), escala log",
                                   axis=alt.Axis(format="~g", labelExpr=VIRGULA)),
                           color=alt.Color("publico_nome:N", scale=ESCALA_COR, title="Público"),
                           tooltip=[alt.Tooltip("texto:N", title="Busca"), alt.Tooltip("nicho:N", title="Nicho"),
                                    alt.Tooltip("competicao:Q", title="Competição"),
                                    alt.Tooltip("lance_max:Q", title="Lance (R$)", format=".2f")]))
        if separar:
            grafico = grafico.properties(width=320, height=320).facet(
                column=alt.Column("publico_nome:N", title=None, sort=list(COR_PUBLICO)))
            st.altair_chart(grafico)
        else:
            st.altair_chart(grafico.properties(height=400), width="stretch")
        rho_total = d["competicao"].corr(d["lance_max"], method="spearman")
        c = st.columns(3)
        c[0].metric("Correlação (todas as buscas)", br(rho_total, 2), help="Correlação de Spearman entre competição e lance")
        for i, publico in enumerate(COR_PUBLICO, start=1):
            parte = d[d["publico_nome"] == publico]
            c[i].metric(f"Só {publico.lower()}",
                        br(parte["competicao"].corr(parte["lance_max"], method="spearman"), 2) if len(parte) > 2 else "—")
        st.markdown(
            "Correlações perto de 0 indicam que a competição **não** prevê o custo. Quando os dois públicos aparecem "
            "juntos, a correlação pode ficar negativa só por causa da mistura: o e-commerce reúne competição alta e "
            "clique barato. Separe por público para ver a relação dentro de cada grupo. O índice do Google mede "
            "**quantos** anunciantes disputam a busca, não **quanto** eles pagam."
        )

st.divider()
st.caption(f"Dados: {br(len(df_total))} buscas do catálogo do Observatório Lucro Digital (Google Ads Keyword Planner), "
           "extração de 11/11/2026 (o mesmo dataset.txt dos painéis do trabalho). Volumes são estimativas arredondadas "
           "do Google; o lance é a faixa sugerida para o topo da página, não o custo efetivamente pago.")
