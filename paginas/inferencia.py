"""Painel 3: inferência estatística (ICs e testes) e comparação com a população."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import inferencia as inf
import painel_comum as pc

pop = pc.dados_populacao()
amo = pc.dados_amostra()
sims = pc.simulacoes()
resultados = {h["codigo"]: inf.avaliar(h, amo, pop) for h in inf.HIPOTESES}
NOME_CURTO = {"P1": "Competição alta", "P2": "Intenção local", "M1": "Competição média", "M2": "Lance máximo"}


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------
def prop(h) -> bool:
    return h["tipo"] == "proporcao"


def fmt(h, v) -> str:
    if prop(h):
        return pc.pct(v, 2)
    if h["coluna"] == "lance_max":
        return pc.reais(v)
    return pc.br(v, 2)


def fmt_v0(h) -> str:
    return pc.pct(h["valor0"], 0) if prop(h) else fmt(h, h["valor0"])


def fmt_dif(h, v) -> str:
    """Diferença com sinal (p.p. para proporções)."""
    sinal = "+" if v > 0 else "−" if v < 0 else ""
    if prop(h):
        return f"{sinal}{pc.br(abs(v) * 100, 2)} p.p."
    if h["coluna"] == "lance_max":
        return f"{sinal}R$ {pc.br(abs(v), 2)}"
    return f"{sinal}{pc.br(abs(v), 2)}"


def fmt_p(p: float) -> str:
    return "< 0,0001" if p < 0.0001 else pc.br(p, 4)  # espaço inquebrável: não parte em duas linhas


def letra(h) -> str:
    return "p" if prop(h) else "μ"


def escala(h) -> int:
    return 100 if prop(h) else 1


def titulo_eixo(h) -> str:
    return {"competicao_alta": "% das buscas", "intencao_local": "% das buscas",
            "competicao": "competição média (0 a 100)", "lance_max": "R$ por clique"}[h["coluna"]]


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def linha_legenda(fig: go.Figure, nome: str, cor: str, tracejado: str = "solid") -> None:
    """Entrada de legenda para uma linha vertical de referência."""
    fig.add_scatter(x=[None], y=[None], mode="lines", name=nome, line=dict(color=cor, width=2, dash=tracejado))


def grafico_ic(h, r) -> go.Figure:
    """Uma linha para cada elemento: amostra (estimativa + IC), valor real e H₀. Sem rótulos sobrepostos."""
    e, (li, ls), real, v0, k = r["estimativa"], r["ic"], r["parametro"], h["valor0"], escala(h)
    linhas = ["H₀ (referência do teste)", "Valor real (população)", "Amostra: estimativa e IC 95%"]
    fig = go.Figure()
    fig.add_vline(x=real * k, line=dict(color=pc.AZUL, width=1), layer="below")
    fig.add_vline(x=v0 * k, line=dict(color=pc.CINZA, width=1, dash="dash"), layer="below")
    fig.add_scatter(
        x=[e * k], y=[linhas[2]], mode="markers", marker=dict(color=pc.LARANJA, size=13),
        error_x=dict(type="data", symmetric=False, array=[(ls - e) * k], arrayminus=[(e - li) * k],
                     color=pc.LARANJA, thickness=2.5, width=12),
        hovertemplate=f"IC 95%: {fmt(h, li)} a {fmt(h, ls)}<extra>Amostra</extra>",
    )
    fig.add_scatter(x=[real * k], y=[linhas[1]], mode="markers",
                    marker=dict(color=pc.AZUL, size=13, symbol="diamond"),
                    hovertemplate=f"{fmt(h, real)}<extra>Valor real</extra>")
    fig.add_scatter(x=[v0 * k], y=[linhas[0]], mode="markers",
                    marker=dict(color=pc.CINZA, size=12, symbol="square"),
                    hovertemplate=f"{fmt_v0(h)}<extra>H₀</extra>")
    # Rótulos com fundo opaco, acima de cada ponto: as linhas verticais passam por trás
    for y, x, texto in [(linhas[2], e * k, f"{fmt(h, e)}   (IC: {fmt(h, li)} a {fmt(h, ls)})"),
                        (linhas[1], real * k, fmt(h, real)), (linhas[0], v0 * k, fmt_v0(h))]:
        fig.add_annotation(x=x, y=y, text=texto, showarrow=False, yshift=19, bgcolor=pc.FUNDO, borderpad=2,
                           font=dict(color=pc.TINTA, size=13))
    pontos = [li * k, ls * k, real * k, v0 * k]
    folga = (max(pontos) - min(pontos)) * 0.12
    fig = pc.estilizar(fig, 290, titulo_eixo(h))
    fig.update_xaxes(range=[min(pontos) - folga, max(pontos) + folga])
    fig.update_yaxes(categoryorder="array", categoryarray=linhas, gridcolor=pc.FUNDO, range=[-0.5, 2.65])
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=20))
    return fig


def grafico_distribuicao(h, r, sim) -> go.Figure:
    """Histograma das 1.000 estimativas simuladas (distribuição amostral)."""
    k = escala(h)
    fig = go.Figure(go.Histogram(
        x=sim["estimativas"] * k, nbinsx=30, marker=dict(color=pc.LARANJA, line=dict(color=pc.FUNDO, width=1)),
        hovertemplate="%{x}<br><b>%{y} amostras</b><extra></extra>", name="Estimativas", showlegend=False,
    ))
    fig.add_vline(x=sim["parametro"] * k, line=dict(color=pc.AZUL, width=2))
    fig.add_vline(x=r["estimativa"] * k, line=dict(color=pc.TINTA, width=2, dash="dot"))
    linha_legenda(fig, "Valor real", pc.AZUL)
    linha_legenda(fig, "Nossa amostra", pc.TINTA, "dot")
    return pc.estilizar(fig, 340, titulo_eixo(h), "nº de amostras", legenda=True)


def grafico_ics(h, r, sim, quantos: int = 100) -> go.Figure:
    """Os primeiros 100 ICs simulados: cinza acertou, vermelho errou."""
    k = escala(h)
    li, ls, e = sim["li"][:quantos] * k, sim["ls"][:quantos] * k, sim["estimativas"][:quantos] * k
    real = sim["parametro"] * k
    contem = (li <= real) & (real <= ls)
    fig = go.Figure()
    fig.add_vline(x=real, line=dict(color=pc.AZUL, width=2))
    for acertou, cor in [(True, pc.CINZA), (False, pc.VERMELHO)]:
        idx = np.where(contem == acertou)[0]
        nome = f"{len(idx)} contêm o valor real" if acertou else f"{len(idx)} não contêm"
        xs, ys = [], []
        for i in idx:
            xs += [li[i], ls[i], None]
            ys += [i + 1, i + 1, None]
        fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=cor, width=1.5), name=nome, hoverinfo="skip")
        fig.add_scatter(x=e[idx], y=idx + 1, mode="markers", marker=dict(color=cor, size=4), showlegend=False,
                        customdata=np.c_[li[idx], ls[idx]],
                        hovertemplate="Amostra %{y}: %{x:.2f}<br>IC: %{customdata[0]:.2f} a %{customdata[1]:.2f}<extra></extra>")
    linha_legenda(fig, "Valor real", pc.AZUL)
    return pc.estilizar(fig, 340, titulo_eixo(h), "amostra simulada nº", legenda=True)


# ---------------------------------------------------------------------------
# Textos de interpretação (gerados a partir dos números)
# ---------------------------------------------------------------------------
def interpretacao(h, r) -> str:
    li, ls = r["ic"]
    linhas = [
        f"- A amostra estimou **{fmt(h, r['estimativa'])}**; o valor real é **{fmt(h, r['parametro'])}** "
        f"(erro de {fmt_dif(h, r['erro_estimativa'])}).",
        f"- O IC de 95% vai de **{fmt(h, li)} a {fmt(h, ls)}** e **{'contém' if r['ic_contem_parametro'] else 'NÃO contém'}** "
        "o valor real.",
    ]
    lugar = "dentro" if r["ic_contem_valor0"] else "fora"
    if h["alternativa"] == "bilateral":
        linhas.append(
            f"- O valor de H₀ ({fmt_v0(h)}) está **{lugar}** do IC, coerente com **{'rejeitar' if r['rejeita'] else 'não rejeitar'} H₀**: "
            "em teste bilateral, rejeitar a 5% equivale a H₀ ficar fora do IC de 95%."
        )
    else:
        linhas.append(
            f"- O valor de H₀ ({fmt_v0(h)}) está **{lugar}** do IC de 95%. Como o teste é unilateral, a correspondência "
            "exata seria com um intervalo unilateral, mas a leitura é a mesma."
        )
    return "\n".join(linhas)


def texto_simulacao(h, r, sim) -> str:
    cob, rej = sim["cobertura"], sim["taxa_rejeicao"]
    linhas = [
        f"- **Cobertura:** {pc.pct(cob)} dos 1.000 intervalos de 95% contêm o valor real, praticamente os 95% "
        "prometidos pelo nível de confiança. No gráfico da direita, os vermelhos são os intervalos que erraram.",
    ]
    if not r["h1_verdadeira"]:
        linhas.append(f"- **Erro tipo I:** H₀ foi rejeitada em {pc.pct(rej)} das amostras. Como H₀ é verdadeira na "
                      "população, essa é a taxa de erro tipo I, próxima de α = 5%.")
    elif abs(r["diferenca_real"]) < r["erro_padrao"]:
        linhas.append(
            f"- **Poder quase nulo:** H₀ foi rejeitada em só {pc.pct(rej)} das amostras, quase igual a α. A diferença "
            f"real ({fmt_dif(h, r['diferenca_real'])}) é pequena demais para uma amostra de {r['n']} buscas detectar: "
            "estatisticamente H₀ é falsa, mas **na prática é quase verdadeira**. Significância estatística não é o mesmo "
            "que relevância prática."
        )
    elif rej >= 0.995:
        linhas.append(
            f"- **Poder do teste:** H₀ foi rejeitada em {pc.pct(rej)} das amostras. Como H₁ é verdadeira na população, "
            "esse é o poder do teste: a diferença é grande o bastante para ser detectada em praticamente qualquer "
            "amostra, e o risco de erro tipo II é quase nulo."
        )
    else:
        linhas.append(
            f"- **Poder do teste:** H₀ foi rejeitada em {pc.pct(rej)} das amostras. Como H₁ é verdadeira na população, "
            f"esse é o poder do teste; nas outras {pc.pct(1 - rej)} ocorreria **erro tipo II** (não detectar a "
            "diferença). A conclusão da nossa amostra dependeu, em parte, da sorte do sorteio."
        )
    linhas.append(
        f"- **Distribuição amostral:** as 1.000 estimativas formam um sino em torno do valor real, como prevê o "
        f"Teorema Central do Limite. A nossa amostra ({fmt(h, r['estimativa'])}) é só uma dessas possibilidades."
    )
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.title(":violet[Painel 3 · Inferência estatística e comparação dos resultados]")  # mesmo roxo da página Início
st.markdown(
    "Os intervalos de confiança e os testes usam **somente a amostra** (n = 358). Os valores reais vêm da população e "
    "entram **só na comparação**. Nível de confiança **95%**, nível de significância **α = 5%**. "
    "<span style='color:#2a78d6'>**■ População**</span> = valor real · "
    "<span style='color:#eb6834'>**■ Amostra**</span> = estimativa.",
    unsafe_allow_html=True,
)

# Resumo
st.header("Resumo das quatro hipóteses")
resumo = []
for h in inf.HIPOTESES:
    r = resultados[h["codigo"]]
    li, ls = r["ic"]
    resumo.append({
        "Hipótese": f"{h['codigo']} · {NOME_CURTO[h['codigo']]}",
        "H₀ × H₁": f"{letra(h)} = {fmt_v0(h)} × {letra(h)} {inf.SIMBOLO_H1[h['alternativa']]} {fmt_v0(h)}",
        "Estimativa (amostra)": fmt(h, r["estimativa"]),
        "IC 95%": f"{fmt(h, li)} a {fmt(h, ls)}",
        "Estatística": f"{r['nome_estatistica']} = {pc.br(r['estatistica'], 2)}",
        "Valor-p": fmt_p(r["valor_p"]),
        "Decisão": "Rejeita H₀" if r["rejeita"] else "Não rejeita H₀",
        "Valor real (população)": fmt(h, r["parametro"]),
        "IC contém o real?": "Sim" if r["ic_contem_parametro"] else "Não",
    })
pc.tabela(pd.DataFrame(resumo), indice=False)

# Detalhe de cada hipótese, em abas com cara de botão (estilo vale só para a chave "abas_hipoteses")
ROXO, ROXO_CLARO, ROXO_FUNDO, ROXO_ESCURO = "#9b5de5", "#ece0ff", "#f8f2ff", "#6f33b8"  # roxo da página Início
st.html(f"""
<style>
.st-key-abas_hipoteses [role="tablist"] {{ gap: 0.6rem; flex-wrap: wrap; padding-bottom: 0.4rem; }}
.st-key-abas_hipoteses [role="tab"] {{
    background-color: {ROXO_FUNDO};
    border: 2px solid {ROXO};
    border-radius: 0.6rem;
    padding: 0.55rem 1.2rem;
    box-shadow: 0 1px 3px rgba(111, 51, 184, 0.18);
    transition: background-color 0.15s, transform 0.15s;
}}
.st-key-abas_hipoteses [role="tab"], .st-key-abas_hipoteses [role="tab"] * {{
    color: {ROXO_ESCURO} !important; font-weight: 700 !important; font-size: 1.02rem !important;
}}
.st-key-abas_hipoteses [role="tab"]:hover {{ background-color: {ROXO_CLARO}; transform: translateY(-1px); }}
.st-key-abas_hipoteses [role="tab"][aria-selected="true"] {{ background-color: {ROXO_ESCURO}; border-color: {ROXO_ESCURO}; }}
.st-key-abas_hipoteses [role="tab"][aria-selected="true"],
.st-key-abas_hipoteses [role="tab"][aria-selected="true"] * {{ color: #ffffff !important; }}
</style>
""")
st.header("Detalhe de cada hipótese")
st.markdown(":material/touch_app: **Clique nas abas abaixo** para ver cada hipótese em detalhe: pergunta, teste, "
            "intervalo de confiança, comparação com a população e simulação.")
abas = st.tabs([f"{h['codigo']} · {NOME_CURTO[h['codigo']]}" for h in inf.HIPOTESES], key="abas_hipoteses")
for h, aba in zip(inf.HIPOTESES, abas):
    r, sim = resultados[h["codigo"]], sims[h["codigo"]]
    li, ls = r["ic"]
    with aba:
        st.subheader(f"{h['codigo']} · {h['titulo']}")
        st.markdown(pc.md(f"**Pergunta:** {h['pergunta']}  \n**Por que esta hipótese:** {h['justificativa']}  \n"
                          f"**Parâmetro:** {h['parametro']}"))
        c = st.columns(3)
        c[0].markdown(pc.md(f"#### H₀: {letra(h)} = {fmt_v0(h)}"))
        c[1].markdown(pc.md(f"#### H₁: {letra(h)} {inf.SIMBOLO_H1[h['alternativa']]} {fmt_v0(h)}"))
        if h.get("h0_texto"):  # explicação em palavras, quando a hipótese tem uma
            c[0].caption(h["h0_texto"])
            c[1].caption(h["h1_texto"])
        c[2].markdown(f"Teste **{inf.NOME_ALTERNATIVA[h['alternativa']]}**, α = 5%  \n"
                      f"{'Teste z para proporção' if prop(h) else 'Teste t de uma amostra'}")

        with st.expander("Condições de aplicação e fórmulas"):
            for texto, ok in r["condicoes"]:
                st.markdown(f"{'✅' if ok else '❌'} {texto}")
            if prop(h):
                st.markdown("**IC:** p̂ ± z · √(p̂(1 − p̂)/n), com z = 1,96  \n"
                            "**Estatística:** z = (p̂ − p₀) / √(p₀(1 − p₀)/n), comparada com a curva normal padrão")
            else:
                st.markdown("**IC:** x̄ ± t · s/√n, com t da distribuição t de Student (n − 1 graus de liberdade)  \n"
                            "**Estatística:** t = (x̄ − μ₀) / (s/√n), comparada com a distribuição t (n − 1 g.l.)")

        st.markdown("#### Resultado com a amostra")
        detalhe = f"{r['sucessos']} de {r['n']} buscas" if prop(h) else f"n = {r['n']}, s = {fmt(h, r['desvio'])}"
        k = st.columns(4)
        k[0].metric("Estimativa", fmt(h, r["estimativa"]), help=detalhe)
        k[1].metric(f"Estatística {r['nome_estatistica']}", pc.br(r["estatistica"], 3),
                    help=f"{r['gl']} graus de liberdade" if r["gl"] else "Distribuição normal padrão")
        k[2].metric("Valor-p", fmt_p(r["valor_p"]))
        k[3].metric("Decisão (α = 5%)", "Rejeita H₀" if r["rejeita"] else "Não rejeita H₀")
        st.markdown(pc.md(f"**IC de 95%:** {fmt(h, li)} a {fmt(h, ls)}  ·  erro-padrão {fmt(h, r['erro_padrao'])}  ·  "
                          f"{detalhe}" + (f" ({r['vazios']} vazios descartados)" if r["vazios"] else "")))
        st.info(pc.md(r["conclusao"]), title="Conclusão")
        pc.titulo_grafico("Intervalo de confiança da amostra × valor real × H₀")
        pc.mostrar(grafico_ic(h, r))

        st.markdown("#### Comparação com a população")
        k = st.columns(3)
        k[0].metric("Valor real (população)", fmt(h, r["parametro"]), help=f"Calculado com as {pc.br(r['N'], 0)} buscas válidas")
        k[1].metric("Erro da estimativa", fmt_dif(h, r["erro_estimativa"]), help="Estimativa da amostra − valor real")
        k[2].metric("O IC contém o valor real?", "Sim" if r["ic_contem_parametro"] else "Não")
        st.markdown(pc.md(interpretacao(h, r)))
        st.markdown(pc.md(f"**A decisão do teste estava certa?** {r['avaliacao']}"))

        st.markdown("#### Variabilidade amostral: e se tivéssemos sorteado outra amostra?")
        g1, g2 = st.columns(2)
        with g1:
            pc.titulo_grafico("Distribuição das 1.000 estimativas simuladas")
            pc.mostrar(grafico_distribuicao(h, r, sim))
        with g2:
            pc.titulo_grafico("100 intervalos de 95% simulados")
            pc.mostrar(grafico_ics(h, r, sim))
        st.markdown(pc.md(texto_simulacao(h, r, sim)))

# Síntese
st.header("Síntese: população × amostra")
contem = sum(r["ic_contem_parametro"] for r in resultados.values())
rejeitadas = [c for c, r in resultados.items() if r["rejeita"]]
st.markdown(
    f"""
- **Estimativas pontuais:** todas ficaram próximas dos valores reais. Proporções erraram menos de 1 ponto percentual;
  a média do lance errou mais ({fmt_dif(inf.HIPOTESES[3], resultados['M2']['erro_estimativa'])}) por causa da assimetria
  (poucos lances muito caros).
- **Intervalos de confiança:** **{contem} de 4** contêm o valor real. A estimativa pontual quase nunca acerta em cheio,
  mas o intervalo, que considera a variabilidade amostral, captura o valor real na grande maioria das amostras
  (cerca de 95% nas simulações).
- **Testes:** H₀ foi rejeitada em {', '.join(rejeitadas)}, decisões que conferem com a população. Em P1 não se rejeitou
  H₀: a proporção real ({fmt(inf.HIPOTESES[0], resultados['P1']['parametro'])}) difere de 50% por apenas
  {pc.br(abs(resultados['P1']['diferenca_real']) * 100, 2)} ponto, uma diferença sem relevância prática e impossível de
  detectar com n = {resultados['P1']['n']}.
- **Variabilidade:** a conclusão de P2 depende do sorteio (só {pc.pct(sims['P2']['taxa_rejeicao'], 0)} das amostras
  rejeitariam H₀), enquanto M1 e M2 são robustas ({pc.pct(sims['M1']['taxa_rejeicao'], 0)} e
  {pc.pct(sims['M2']['taxa_rejeicao'], 0)}). Quanto mais perto o valor real estiver de H₀, mais a conclusão depende da
  amostra sorteada.
""".replace("$", "\\$")
)

# Nova amostra
st.header("Experimente: sorteie outra amostra")
st.markdown("Nossa amostra é uma entre muitas possíveis. Sorteie outra AAS de 358 buscas e compare os resultados. "
            "A amostra oficial do trabalho continua a mesma.")
if st.button("Sortear nova amostra", icon=":material/casino:"):
    st.session_state["semente_nova"] = int(np.random.default_rng().integers(1, 2**31 - 1))
semente = st.session_state.get("semente_nova")
if semente:
    nova = pop.sample(n=len(amo), random_state=semente)
    linhas = []
    for h in inf.HIPOTESES:
        r_o, r_n = resultados[h["codigo"]], inf.avaliar(h, nova, pop)
        linhas.append({
            "Hipótese": f"{h['codigo']} · {NOME_CURTO[h['codigo']]}", "Valor real": fmt(h, r_o["parametro"]),
            "Amostra oficial": f"{fmt(h, r_o['estimativa'])}  ({'rejeita' if r_o['rejeita'] else 'não rejeita'})",
            "Nova amostra": f"{fmt(h, r_n['estimativa'])}  ({'rejeita' if r_n['rejeita'] else 'não rejeita'})",
            "IC da nova amostra": f"{fmt(h, r_n['ic'][0])} a {fmt(h, r_n['ic'][1])}",
            "IC novo contém o real?": "Sim" if r_n["ic_contem_parametro"] else "Não",
            "Valor-p novo": fmt_p(r_n["valor_p"]),
        })
    pc.tabela(pd.DataFrame(linhas), indice=False)
    st.caption(f"Semente desta nova amostra: {semente}. Entre parênteses, a decisão sobre H₀ a 5%.")

# Limitações
st.header("Limitações da análise")
st.markdown(
    """
- **Assimetria:** volume e lance têm cauda longa de valores altos. O volume não foi usado em teste de média (a média é
  pouco representativa) e a média do lance oscila conforme a amostra pega ou não lances extremos. A validade do teste t
  com n ≈ 350 foi confirmada pela simulação (cobertura dos ICs ≈ 95%).
- **Valores ausentes:** 6 buscas da amostra sem lance (n = 352 em M2); o Google não informou o valor.
- **População finita:** a amostra é 7% da população e as fórmulas não usam a correção para população finita. Os ICs ficam
  um pouco mais largos que o necessário, o que tende a puxar a cobertura simulada um pouco para cima.
- **Independência e generalização:** como a amostra é uma AAS desta população, as conclusões valem para as 5.124
  buscas (a simulação confirma a cobertura de ~95%). Mas buscas do mesmo nicho se parecem entre si (ex.: "carrinho de
  bebê" e "carrinhos de bebe"), então generalizar para outros nichos ou outras épocas exigiria mais cuidado.
- **Quatro testes ao mesmo tempo:** cada teste tem 5% de risco de erro tipo I; com quatro testes, a chance de pelo
  menos um falso positivo (se todas as H₀ fossem verdadeiras) chegaria a 1 − 0,95⁴ ≈ 18,5%.
- **Dados do Google:** volumes são estimativas arredondadas em faixas (320, 1.300, 5.400…) e o dataset é um retrato de
  uma única data.
- **Escolhas do analista:** o corte de competição alta (≥ 67), as palavras da intenção local e os valores de referência
  (50%, 25%, 50 e R$ 5,00) são convenções; outros valores mudariam as perguntas, não a técnica.
- **Significância × relevância:** com amostras grandes, diferenças mínimas podem ser significativas; com amostras
  moderadas, diferenças pequenas (como em P1) passam despercebidas. O IC ajuda a julgar o tamanho da diferença.
"""
)
