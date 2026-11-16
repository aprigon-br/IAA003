"""
Peças comuns aos painéis: carga dos dados, cores, formatação brasileira e gráficos.
Os painéis leem SOMENTE dataset.txt e amostra.txt, nunca o banco de dados.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import estatistica as est
import inferencia as inf

# ---------------------------------------------------------------------------
# Cores: população sempre azul, amostra sempre laranja (paleta validada, slots 1 e 2)
# ---------------------------------------------------------------------------
AZUL = "#2a78d6"  # População (valores reais)
LARANJA = "#eb6834"  # Amostra (estimativas)
CINZA = "#898781"  # referências neutras (H₀, ICs que acertaram)
VERMELHO = "#d03b3b"  # status crítico: IC que NÃO contém o valor real
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
FUNDO = "#fcfcfb"
COR = {"População": AZUL, "Amostra": LARANJA}

ROTULOS = {
    "publico": {"SERVICOS": "Serviços", "ECOMMERCE": "E-commerce"},
    "origem": {"EXPANSAO": "Expansão (Google)", "SEMENTE": "Semente (IA)", "MANUAL": "Manual"},
    "competicao_alta": {"Sim": "Sim (≥ 67)", "Não": "Não (< 67)"},
    "intencao_local": {"Sim": "Sim", "Não": "Não"},
}
ORDEM = {
    "publico": ["SERVICOS", "ECOMMERCE"],
    "origem": ["EXPANSAO", "SEMENTE", "MANUAL"],
    "competicao_alta": ["Sim", "Não"],
    "intencao_local": ["Sim", "Não"],
}
CASAS = {"volume_brasil": 0, "lance_min": 2, "lance_max": 2, "competicao": 0}
FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'
NOMES_POTENCIA = {0: "1", 1: "10", 2: "100", 3: "1 mil", 4: "10 mil", 5: "100 mil", 6: "1 milhão"}


# ---------------------------------------------------------------------------
# Formatação no padrão brasileiro
# ---------------------------------------------------------------------------
def br(valor, casas: int = 2) -> str:
    """1234.5 -> '1.234,50' (negativos com o sinal de menos tipográfico)."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return "—"
    texto = f"{abs(valor):,.{casas}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return ("−" if valor < 0 and texto.strip("0,.") else "") + texto


def pct(fracao, casas: int = 1) -> str:
    """0.4948 -> '49,5%'"""
    return br(fracao * 100, casas) + "%"


def reais(valor, casas: int = 2) -> str:
    return "R$ " + br(valor, casas)  # espaço inquebrável: "R$" não se separa do número


def valor_var(coluna: str, valor) -> str:
    """Formata um valor de acordo com a variável."""
    if coluna in ("lance_min", "lance_max"):
        return reais(valor)
    return br(valor, CASAS.get(coluna, 2))


def md(texto: str) -> str:
    """Protege o cifrão: no Markdown do Streamlit, dois '$' viram fórmula matemática."""
    return texto.replace("$", "\\$")


def tabela(df: pd.DataFrame, indice: bool = True) -> None:
    """Tabela estática, sem rolagem interna (mostra todas as linhas)."""
    df = df.map(lambda v: md(v) if isinstance(v, str) else v)
    df.index = [md(str(i)) for i in df.index]
    st.table(df, hide_index=not indice, border="horizontal")


def titulo_colorido(texto: str, cor: str, chave: str) -> None:
    """Título da página numa cor exata. As cores do tema do Streamlit não batem com as dos gráficos, então o estilo é
    aplicado só ao container com esta chave."""
    st.html(f"<style>.st-key-{chave} h1, .st-key-{chave} h1 * {{ color: {cor} !important; }}</style>")
    with st.container(key=chave):
        st.title(texto)


def titulo_grafico(texto: str) -> None:
    st.markdown(f"**{md(texto)}**")


def marcas_log(minimo: float, maximo: float) -> tuple[list[int], list[str]]:
    """Expoentes e rótulos em português para eixos em escala logarítmica."""
    ks = list(range(int(np.floor(np.log10(minimo))), int(np.ceil(np.log10(maximo))) + 1))
    nomes = [NOMES_POTENCIA.get(k, br(10.0**k, max(-k, 0))) for k in ks]
    return ks, nomes


# ---------------------------------------------------------------------------
# Dados (lidos dos .txt e guardados em cache)
# ---------------------------------------------------------------------------
@st.cache_data
def dados_populacao() -> pd.DataFrame:
    return est.carregar_populacao()


@st.cache_data
def dados_amostra() -> pd.DataFrame:
    return est.carregar_amostra()


@st.cache_data
def simulacoes() -> dict:
    """As 1.000 amostras simuladas, aplicadas a cada hipótese."""
    pop = dados_populacao()
    indices = inf.sortear_indices(len(pop))
    return {h["codigo"]: inf.simular(h, pop, indices) for h in inf.HIPOTESES}


def filtro_publico(chave: str) -> str:
    escolha = st.segmented_control(
        "Filtrar por público", ["Todos", "Serviços", "E-commerce"], default="Todos", key=chave,
    )
    return escolha or "Todos"


def aplicar_filtro(df: pd.DataFrame, escolha: str) -> pd.DataFrame:
    if escolha == "Serviços":
        return df[df["publico"] == "SERVICOS"]
    if escolha == "E-commerce":
        return df[df["publico"] == "ECOMMERCE"]
    return df


# ---------------------------------------------------------------------------
# Estilo e gráficos (títulos ficam FORA do gráfico, para não colidir com a legenda)
# ---------------------------------------------------------------------------
def estilizar(fig: go.Figure, altura: int = 320, titulo_x: str | None = None,
              titulo_y: str | None = None, legenda: bool = False) -> go.Figure:
    fig.update_layout(
        height=altura, template="plotly_white", paper_bgcolor=FUNDO, plot_bgcolor=FUNDO,
        font=dict(family=FONTE, color=TINTA_2, size=13), separators=",.",
        margin=dict(l=10, r=20, t=40 if legenda else 10, b=10),
        hoverlabel=dict(bgcolor="white", font=dict(family=FONTE, size=13, color=TINTA)),
        showlegend=legenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None),
    )
    fig.update_xaxes(gridcolor=GRADE, linecolor=EIXO, zeroline=False, title=titulo_x)
    fig.update_yaxes(gridcolor=GRADE, linecolor=EIXO, zeroline=False, title=titulo_y)
    return fig


def mostrar(fig: go.Figure) -> None:
    st.plotly_chart(fig, theme=None, config={"displaylogo": False})


def histograma(x: pd.Series, coluna: str, cor: str, log: bool = False, nbins: int = 30) -> go.Figure:
    """Histograma com faixas calculadas aqui, para o tooltip mostrar 'de X a Y'."""
    x = x.dropna()
    if log:
        x = x[x > 0]
    valores = np.log10(x) if log else x
    contagem, bordas = np.histogram(valores, bins=nbins)
    inicio, fim = bordas[:-1], bordas[1:]
    if log:
        inicio, fim = 10**inicio, 10**fim
    faixa = [f"{valor_var(coluna, a)} a {valor_var(coluna, b)}" for a, b in zip(inicio, fim)]
    fig = go.Figure(go.Bar(
        x=(bordas[:-1] + bordas[1:]) / 2, y=contagem, width=bordas[1] - bordas[0],
        marker=dict(color=cor, line=dict(color=FUNDO, width=1)),
        customdata=faixa, hovertemplate="%{customdata}<br><b>%{y} buscas</b><extra></extra>",
    ))
    titulo = est.QUANTITATIVAS[coluna] + (" · escala logarítmica" if log else "")
    fig = estilizar(fig, 340, titulo, "nº de buscas")
    if log:
        ks, nomes = marcas_log(x.min(), x.max())
        fig.update_xaxes(tickvals=ks, ticktext=nomes)
    return fig


def boxplot(series: dict, coluna: str, log: bool = False, altura: int = 340) -> go.Figure:
    """Boxplot horizontal; series = {"População": x, "Amostra": x}, o primeiro fica em cima."""
    fig = go.Figure()
    minimo, maximo = np.inf, -np.inf
    for nome, x in series.items():
        x = x.dropna()
        if log:
            x = x[x > 0]
        minimo, maximo = min(minimo, x.min()), max(maximo, x.max())
        fig.add_box(x=x, name=nome, orientation="h", marker=dict(color=COR[nome], size=4),
                    line=dict(width=1.5), boxpoints="outliers")
    titulo = est.QUANTITATIVAS[coluna] + (" · escala logarítmica" if log else "")
    fig = estilizar(fig, altura, titulo)
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(list(series))))
    if log:
        ks, nomes = marcas_log(minimo, maximo)
        fig.update_xaxes(type="log", tickvals=[10.0**k for k in ks], ticktext=nomes)
    elif coluna in ("lance_min", "lance_max"):
        fig.update_xaxes(tickprefix="R$ ")
    else:
        fig.update_xaxes(tickformat=",.0f")
    return fig


def tabela_frequencias(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Frequências na ordem fixa das categorias, incluindo as que têm zero."""
    t = est.frequencias(df, coluna).reindex(ORDEM[coluna]).fillna(0)
    t.index = [ROTULOS[coluna][c] for c in t.index]
    return t


def barras_proporcao(tabelas: dict, altura: int = 250) -> go.Figure:
    """Barras horizontais de proporção; tabelas = {"População": freq, "Amostra": freq}."""
    fig = go.Figure()
    for nome, t in tabelas.items():
        fig.add_bar(
            y=t.index, x=t["proporção (%)"], name=nome, orientation="h",
            marker=dict(color=COR[nome], line=dict(color=FUNDO, width=2)),
            text=[br(v, 1) + "%" for v in t["proporção (%)"]], textposition="outside",
            textfont=dict(color=TINTA_2), cliponaxis=False,
            customdata=t["frequência"].astype(int),
            hovertemplate="%{y}: <b>%{x:.1f}%</b> (%{customdata} buscas)<extra>" + nome + "</extra>",
        )
    fig = estilizar(fig, altura, "% das buscas", legenda=len(tabelas) > 1)
    fig.update_layout(barmode="group")
    fig.update_yaxes(autorange="reversed", gridcolor=FUNDO)
    fig.update_xaxes(range=[0, 112])
    return fig


def barras_nichos(serie: pd.Series, coluna: str, cor: str, titulo_x: str) -> go.Figure:
    fig = go.Figure(go.Bar(
        y=serie.index, x=serie.values, orientation="h", marker=dict(color=cor, line=dict(color=FUNDO, width=2)),
        customdata=[valor_var(coluna, v) for v in serie.values],
        hovertemplate="%{y}: <b>%{customdata}</b><extra></extra>",
    ))
    fig = estilizar(fig, 380, titulo_x)
    fig.update_yaxes(autorange="reversed", gridcolor=FUNDO)
    if coluna in ("lance_min", "lance_max"):
        fig.update_xaxes(tickprefix="R$ ")
    else:
        fig.update_xaxes(tickformat=",.0f")
    return fig


def tabela_medidas(df: pd.DataFrame, populacao: bool) -> pd.DataFrame:
    """Medidas descritivas formatadas em português, prontas para exibir."""
    m = est.medidas(df, populacao=populacao)
    saida = pd.DataFrame(index=m.index)
    for rotulo, coluna in zip(m.columns, est.QUANTITATIVAS):
        valores = []
        for medida, v in m[rotulo].items():
            if medida in ("n (válidos)", "vazios", "atípicos (outliers)"):
                valores.append(br(v, 0))
            elif medida == "coef. de variação (%)":
                valores.append(br(v, 1) + "%")
            elif medida == "assimetria":
                valores.append(br(v, 2))
            else:
                valores.append(br(v, max(CASAS[coluna], 2) if medida in ("média", "desvio-padrão") else CASAS[coluna]))
        saida[rotulo] = valores
    saida = saida.rename(index={"desvio-padrão": "desvio-padrão (σ)" if populacao else "desvio-padrão (s)"})
    return saida


def nota_distribuicao(x: pd.Series, coluna: str) -> str:
    """Frase curta que interpreta a forma da distribuição."""
    x = x.dropna()
    media, mediana, assim = x.mean(), x.median(), x.skew()
    base = f"Média **{valor_var(coluna, media)}** × mediana **{valor_var(coluna, mediana)}**, assimetria **{br(assim, 2)}**. "
    if assim > 1:
        texto = base + ("Distribuição concentrada em valores baixos, com uma cauda longa de valores muito altos que "
                        "puxa a média para cima: a **mediana** representa melhor o valor típico.")
    elif assim < -1:
        texto = base + "Distribuição com cauda à esquerda: a média fica abaixo da mediana."
    else:
        texto = base + "Distribuição aproximadamente simétrica: média e mediana próximas."
    return md(texto)


# ---------------------------------------------------------------------------
# Página descritiva (usada pelos painéis 1 e 2, para serem idênticos)
# ---------------------------------------------------------------------------
def secoes_descritivas(df: pd.DataFrame, tipo: str) -> None:
    """Indicadores, quantitativas, qualitativas e nichos de um conjunto de buscas."""
    eh_pop = tipo == "População"
    cor = COR[tipo]

    # Indicadores
    comp_alta = df["competicao_alta"].dropna()
    c = st.columns(6)
    c[0].metric("Buscas", br(len(df), 0))
    c[1].metric("Nichos", br(df["nicho"].nunique(), 0))
    c[2].metric("Volume mediano", br(df["volume_brasil"].median(), 0), help="Pesquisas por mês no Brasil")
    c[3].metric("Lance máx. mediano", reais(df["lance_max"].median()), help="Por clique, topo da página")
    c[4].metric("Competição média", br(df["competicao"].mean(), 1), help="Índice de 0 a 100")
    c[5].metric("Competição alta", pct((comp_alta == "Sim").mean()), help="Buscas com competição ≥ 67")

    # Quantitativas
    st.header("Variáveis quantitativas")
    a, b = st.columns([3, 1], vertical_alignment="bottom")
    coluna = a.segmented_control(
        "Variável", list(est.QUANTITATIVAS), default="volume_brasil",
        format_func=lambda c: est.QUANTITATIVAS[c], key=f"var_{tipo}",
    ) or "volume_brasil"
    log = b.toggle("Escala logarítmica", value=coluna == "volume_brasil", key=f"log_{tipo}_{coluna}",
                   help="Útil para variáveis muito assimétricas, como o volume")
    g1, g2 = st.columns([3, 2])
    with g1:
        titulo_grafico("Distribuição (histograma)")
        mostrar(histograma(df[coluna], coluna, cor, log))
    with g2:
        titulo_grafico("Resumo em 5 números (boxplot)")
        mostrar(boxplot({tipo: df[coluna]}, coluna, log))
    st.markdown(nota_distribuicao(df[coluna], coluna))
    if log and (df[coluna] <= 0).any():
        st.caption(f"Na escala logarítmica, {int((df[coluna] <= 0).sum())} buscas com valor 0 ficam fora do gráfico "
                   "(mas entram nas medidas).")

    st.subheader("Medidas descritivas")
    tabela(tabela_medidas(df, eh_pop))
    st.caption(
        ("Desvio-padrão populacional σ (divide por N). " if eh_pop else "Desvio-padrão amostral s (divide por n − 1). ")
        + "Atípicos: valores além de 1,5 × a amplitude interquartil a partir dos quartis (pontos soltos do boxplot). "
        "Vazios ficam fora do cálculo."
    )

    # Qualitativas: duas por linha, para os gráficos ficarem alinhados
    st.header("Variáveis qualitativas")
    itens = list(est.QUALITATIVAS.items())
    for par in (itens[:2], itens[2:]):
        colunas = st.columns(2)
        for (coluna, rotulo), lugar in zip(par, colunas):
            with lugar:
                t = tabela_frequencias(df, coluna)
                titulo_grafico(rotulo)
                mostrar(barras_proporcao({tipo: t}))
                with st.expander(f"Tabela de frequências: {rotulo}"):
                    vista = pd.DataFrame({
                        "frequência": [br(v, 0) for v in t["frequência"]],
                        "proporção": [br(v, 1) + "%" for v in t["proporção (%)"]],
                    }, index=t.index)
                    tabela(vista)
                    vazios = int(df[coluna].isna().sum())
                    if vazios:
                        st.caption(f"{vazios} buscas sem valor (competição não informada) ficam fora.")

    # Nichos
    st.header("Nichos")
    st.caption("A variável nicho é qualitativa nominal com 137 categorias: aparece aqui cruzada com variáveis quantitativas.")
    n1, n2 = st.columns(2)
    with n1:
        titulo_grafico("10 nichos com mais pesquisas")
        mostrar(barras_nichos(est.top_nichos(df, "volume_brasil", "sum", 10), "volume_brasil", cor,
                              "soma do volume (pesquisas/mês)"))
    with n2:
        titulo_grafico("10 nichos com lance máximo médio mais caro")
        mostrar(barras_nichos(est.top_nichos(df, "lance_max", "mean", 10), "lance_max", cor,
                              "lance máximo médio (R$ por clique)"))
    if not eh_pop:
        st.caption("Na amostra, cada nicho tem poucas buscas (1 a 7), então esses rankings são instáveis.")
