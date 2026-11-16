"""
Etapa 5: inferência estatística (intervalos de confiança e testes de hipóteses).

- Os intervalos e os testes usam SOMENTE a amostra (amostra.txt).
- Os parâmetros reais são calculados com a população (dataset.txt), só para comparar.
- A simulação repete o sorteio muitas vezes para mostrar a variabilidade amostral.
Lê SOMENTE os arquivos .txt, nunca o banco de dados.

Rodar este arquivo direto mostra todos os resultados no terminal:
    .venv\\Scripts\\python.exe inferencia.py
"""

import numpy as np
import pandas as pd
from scipy import stats

from estatistica import carregar_amostra, carregar_populacao

ALFA = 0.05  # nível de significância: risco aceito de rejeitar H0 sendo ela verdadeira
CONFIANCA = 0.95  # nível de confiança dos intervalos
TAMANHO_AMOSTRA = 358
SEMENTE_SIMULACAO = 2026
REPETICOES = 1000

SIMBOLO_H1 = {"bilateral": "≠", "menor": "<", "maior": ">"}
NOME_ALTERNATIVA = {
    "bilateral": "bilateral",
    "menor": "unilateral à esquerda",
    "maior": "unilateral à direita",
}

# ---------------------------------------------------------------------------
# As 4 hipóteses do trabalho (P1, P2 e M1 definidas antes do sorteio da amostra)
# ---------------------------------------------------------------------------
HIPOTESES = [
    {
        "codigo": "P1",
        "tipo": "proporcao",
        "coluna": "competicao_alta",
        "evento": "Sim",
        "valor0": 0.50,
        "alternativa": "bilateral",
        "titulo": "Proporção de buscas com competição alta (índice ≥ 67)",
        "parametro": "p = proporção de buscas com competição ≥ 67",
        "pergunta": "Metade das buscas é altamente disputada pelos anunciantes?",
        "justificativa": (
            "Se mais da metade das buscas for muito disputada, anunciar no Google tende a ser caro "
            "para a maioria dos nichos; se for menos, há mais espaço para buscas baratas. "
            "50% é o ponto de equilíbrio entre os dois cenários."
        ),
        "se_rejeita": "a proporção de buscas com competição alta é diferente de 50%",
        "se_nao_rejeita": "a proporção de buscas com competição alta seja diferente de 50%",
    },
    {
        "codigo": "P2",
        "tipo": "proporcao",
        "coluna": "intencao_local",
        "evento": "Sim",
        "valor0": 0.25,
        "alternativa": "menor",
        "titulo": "Proporção de buscas com intenção local (\"perto de mim\")",
        "parametro": "p = proporção de buscas com \"perto\" ou \"próximo\" no texto",
        "pergunta": "Pelo menos 1 em cada 4 buscas tem intenção local?",
        "justificativa": (
            "Buscas como \"dentista perto de mim\" pedem campanhas com segmentação geográfica. "
            "Adotamos 25% (1 em cada 4) como patamar a partir do qual valeria priorizar esse tipo "
            "de campanha; o teste verifica se a proporção real fica abaixo desse patamar."
        ),
        "se_rejeita": "menos de 25% das buscas têm intenção local",
        "se_nao_rejeita": "menos de 25% das buscas tenham intenção local",
    },
    {
        "codigo": "M1",
        "tipo": "media",
        "coluna": "competicao",
        "valor0": 50.0,
        "alternativa": "maior",
        "titulo": "Competição média das buscas (índice de 0 a 100)",
        "parametro": "μ = competição média",
        "pergunta": (
            "Anunciar nesses nichos costuma ser disputado? Ou seja: o índice médio de competição das buscas é "
            "maior que 50, o meio da escala de 0 a 100?"
        ),
        "justificativa": (
            "O Google dá a cada busca um índice de competição de 0 (nenhum anunciante disputa a busca) a 100 "
            "(disputa máxima). O valor 50 é o meio da escala. Se a média passar de 50, a busca típica destes "
            "nichos é mais disputada do que moderada, e anunciar tende a exigir mais orçamento e estratégia."
        ),
        "h0_texto": "disputa típica moderada (no meio da escala)",
        "h1_texto": "disputa típica acima do meio da escala",
        "se_rejeita": "a busca típica é mais disputada que o meio da escala (índice 50)",
        "se_nao_rejeita": "a busca típica seja mais disputada que o meio da escala (índice 50)",
    },
    {
        "codigo": "M2",
        "tipo": "media",
        "coluna": "lance_max",
        "valor0": 5.00,
        "alternativa": "bilateral",
        "titulo": "Lance máximo médio para o topo da página (R$ por clique)",
        "parametro": "μ = lance máximo médio (R$)",
        "pergunta": "O lance médio para aparecer no topo da página do Google é R$ 5,00 por clique?",
        "justificativa": (
            "R$ 5,00 é um valor redondo de referência para o custo por clique no topo da página, "
            "usado para orçar campanhas. O teste verifica se a média real difere dele."
        ),
        "se_rejeita": "o lance máximo médio é diferente de R$ 5,00",
        "se_nao_rejeita": "o lance máximo médio seja diferente de R$ 5,00",
    },
]


# ---------------------------------------------------------------------------
# Fórmulas
# ---------------------------------------------------------------------------
def p_valor_normal(z, alternativa: str):
    """Valor-p de uma estatística z (curva normal padrão)."""
    if alternativa == "bilateral":
        return 2 * stats.norm.sf(np.abs(z))
    if alternativa == "menor":
        return stats.norm.cdf(z)
    return stats.norm.sf(z)


def p_valor_t(t, gl, alternativa: str):
    """Valor-p de uma estatística t com gl graus de liberdade."""
    if alternativa == "bilateral":
        return 2 * stats.t.sf(np.abs(t), gl)
    if alternativa == "menor":
        return stats.t.cdf(t, gl)
    return stats.t.sf(t, gl)


def ic_proporcao(sucessos: int, n: int, confianca: float = CONFIANCA):
    """IC para proporção (aproximação normal): p̂ ± z · √(p̂(1−p̂)/n)."""
    p = sucessos / n
    z = stats.norm.ppf(1 - (1 - confianca) / 2)  # 1,96 para 95%
    ep = np.sqrt(p * (1 - p) / n)  # erro-padrão
    return p, ep, z, p - z * ep, p + z * ep


def teste_proporcao(sucessos: int, n: int, p0: float, alternativa: str):
    """Teste z para proporção: z = (p̂ − p₀) / √(p₀(1−p₀)/n)."""
    p = sucessos / n
    z = (p - p0) / np.sqrt(p0 * (1 - p0) / n)
    return z, p_valor_normal(z, alternativa)


def ic_media(x: pd.Series, confianca: float = CONFIANCA):
    """IC para média (t de Student): x̄ ± t · s/√n."""
    n = len(x)
    media, s = x.mean(), x.std(ddof=1)
    ep = s / np.sqrt(n)  # erro-padrão da média
    t = stats.t.ppf(1 - (1 - confianca) / 2, df=n - 1)
    return media, s, ep, t, media - t * ep, media + t * ep


def teste_media(x: pd.Series, mu0: float, alternativa: str):
    """Teste t de uma amostra: t = (x̄ − μ₀) / (s/√n), com n−1 graus de liberdade."""
    mapa = {"bilateral": "two-sided", "menor": "less", "maior": "greater"}
    r = stats.ttest_1samp(x, mu0, alternative=mapa[alternativa])
    return float(r.statistic), float(r.pvalue)


# ---------------------------------------------------------------------------
# Avaliação completa de uma hipótese
# ---------------------------------------------------------------------------
def avaliar(h: dict, amostra: pd.DataFrame, populacao: pd.DataFrame, alfa: float = ALFA) -> dict:
    coluna = h["coluna"]
    x = amostra[coluna].dropna()  # a inferência usa só a amostra
    x_pop = populacao[coluna].dropna()  # a população serve só para comparar
    n, N = len(x), len(x_pop)
    v0 = h["valor0"]

    r = {"h": h, "n": n, "N": N, "vazios": int(amostra[coluna].isna().sum())}
    condicoes = [("Amostra aleatória simples (sorteio da Etapa 3)", True)]
    condicoes.append((f"n ≤ 10% da população ({n}/{N} = {n / N:.1%}): observações praticamente independentes", n <= 0.10 * N))

    if h["tipo"] == "proporcao":
        sucessos = int((x == h["evento"]).sum())
        est, ep, critico, li, ls = ic_proporcao(sucessos, n)
        estatistica, valor_p = teste_proporcao(sucessos, n, v0, h["alternativa"])
        parametro = float((x_pop == h["evento"]).mean())
        condicoes += [
            (f"n·p₀ = {n * v0:.1f} ≥ 10 e n·(1−p₀) = {n * (1 - v0):.1f} ≥ 10 (para o teste)",
             n * v0 >= 10 and n * (1 - v0) >= 10),
            (f"n·p̂ = {sucessos} ≥ 10 e n·(1−p̂) = {n - sucessos} ≥ 10 (para o IC)",
             sucessos >= 10 and n - sucessos >= 10),
        ]
        r.update(sucessos=sucessos, nome_estatistica="z", desvio=None, gl=None)
    else:
        est, s, ep, critico, li, ls = ic_media(x)
        estatistica, valor_p = teste_media(x, v0, h["alternativa"])
        parametro = float(x_pop.mean())
        condicoes.append((
            f"n = {n} ≥ 30: pelo Teorema Central do Limite a média amostral é aproximadamente "
            f"normal, mesmo com assimetria de {x.skew():.2f} nos dados",
            n >= 30,
        ))
        r.update(sucessos=None, nome_estatistica="t", desvio=float(s), gl=n - 1)

    rejeita = bool(valor_p < alfa)

    # A verdade na população: H1 é verdadeira?
    diferenca = parametro - v0
    h1_verdadeira = {"bilateral": diferenca != 0, "menor": diferenca < 0, "maior": diferenca > 0}[h["alternativa"]]
    if rejeita and h1_verdadeira:
        avaliacao = "Decisão correta: rejeitou H₀, e H₁ é verdadeira na população."
    elif rejeita:
        avaliacao = "Erro tipo I: rejeitou H₀, mas H₀ é verdadeira na população."
    elif not h1_verdadeira:
        avaliacao = "Decisão correta: não rejeitou H₀, e H₁ é falsa na população."
    else:
        avaliacao = "Erro tipo II: não rejeitou H₀, mas H₁ é verdadeira na população."
        if abs(diferenca) < ep:
            avaliacao += (
                " Porém a diferença real é menor que o erro-padrão da estimativa: na prática H₀ é "
                "quase verdadeira, e uma amostra deste tamanho não consegue detectar uma diferença tão pequena."
            )

    if rejeita:
        conclusao = f"Rejeita H₀. Ao nível de {alfa:.0%}, há evidência de que {h['se_rejeita']}."
    else:
        conclusao = f"Não rejeita H₀. Ao nível de {alfa:.0%}, não há evidência suficiente de que {h['se_nao_rejeita']}."

    r.update(
        estimativa=float(est), erro_padrao=float(ep), critico=float(critico),
        ic=(float(li), float(ls)), estatistica=float(estatistica), valor_p=float(valor_p),
        rejeita=rejeita, conclusao=conclusao, condicoes=condicoes,
        parametro=parametro, diferenca_real=float(diferenca),
        erro_estimativa=float(est - parametro),
        ic_contem_parametro=bool(li <= parametro <= ls),
        ic_contem_valor0=bool(li <= v0 <= ls),
        h1_verdadeira=bool(h1_verdadeira), avaliacao=avaliacao,
    )
    return r


# ---------------------------------------------------------------------------
# Simulação da variabilidade amostral
# ---------------------------------------------------------------------------
def sortear_indices(N: int, n: int = TAMANHO_AMOSTRA, repeticoes: int = REPETICOES,
                    semente: int = SEMENTE_SIMULACAO) -> np.ndarray:
    """Matriz repeticoes × n: cada linha é uma AAS sem reposição de posições da população."""
    rng = np.random.default_rng(semente)
    return np.argsort(rng.random((repeticoes, N)), axis=1)[:, :n]


def simular(h: dict, populacao: pd.DataFrame, indices: np.ndarray, alfa: float = ALFA) -> dict:
    """Aplica o IC e o teste a cada uma das amostras simuladas."""
    coluna = h["coluna"]
    if h["tipo"] == "proporcao":
        valores = (populacao[coluna] == h["evento"]).astype(float).where(populacao[coluna].notna())
    else:
        valores = populacao[coluna].astype(float)
    valores = valores.to_numpy()
    amostras = valores[indices]  # repeticoes × n, com NaN onde há vazio
    n_val = (~np.isnan(amostras)).sum(axis=1)
    est = np.nanmean(amostras, axis=1)
    v0 = h["valor0"]

    if h["tipo"] == "proporcao":
        ep = np.sqrt(est * (1 - est) / n_val)
        critico = stats.norm.ppf(1 - (1 - CONFIANCA) / 2)
        estat = (est - v0) / np.sqrt(v0 * (1 - v0) / n_val)
        valor_p = p_valor_normal(estat, h["alternativa"])
    else:
        ep = np.nanstd(amostras, axis=1, ddof=1) / np.sqrt(n_val)
        critico = stats.t.ppf(1 - (1 - CONFIANCA) / 2, n_val - 1)
        estat = (est - v0) / ep
        valor_p = p_valor_t(estat, n_val - 1, h["alternativa"])

    li, ls = est - critico * ep, est + critico * ep
    parametro = float(np.nanmean(valores))
    return {
        "estimativas": est, "li": li, "ls": ls, "parametro": parametro,
        "cobertura": float(((li <= parametro) & (parametro <= ls)).mean()),
        "taxa_rejeicao": float((valor_p < alfa).mean()),
    }


# ---------------------------------------------------------------------------
# Resultados no terminal (só quando o arquivo é rodado direto)
# ---------------------------------------------------------------------------
def main() -> None:
    pop, amo = carregar_populacao(), carregar_amostra()
    indices = sortear_indices(len(pop))

    for h in HIPOTESES:
        r = avaliar(h, amo, pop)
        sim = simular(h, pop, indices)
        pct = h["tipo"] == "proporcao"
        f = (lambda v: f"{v:.2%}") if pct else (lambda v: f"{v:,.2f}")
        v0 = f"{h['valor0']:.0%}" if pct else f"{h['valor0']:,.2f}"

        print("=" * 78)
        print(f"{h['codigo']} | {h['titulo']}")
        print(f"Pergunta: {h['pergunta']}")
        print(f"H₀: {h['parametro'].split(' = ')[0]} = {v0}    H₁: {h['parametro'].split(' = ')[0]} "
              f"{SIMBOLO_H1[h['alternativa']]} {v0}    ({NOME_ALTERNATIVA[h['alternativa']]}, α = {ALFA:.0%})")
        print("Condições:")
        for texto, ok in r["condicoes"]:
            print(f"  [{'OK' if ok else 'FALHA'}] {texto}")
        extra = f"  ({r['sucessos']} de {r['n']})" if pct else f"  (s = {r['desvio']:,.2f})"
        print(f"Amostra: n = {r['n']} (vazios: {r['vazios']}) | estimativa = {f(r['estimativa'])}{extra}")
        print(f"IC {CONFIANCA:.0%}: [{f(r['ic'][0])} ; {f(r['ic'][1])}]  (erro-padrão {f(r['erro_padrao'])}, "
              f"valor crítico {r['critico']:.3f})")
        gl = f", gl = {r['gl']}" if r["gl"] else ""
        print(f"Estatística de teste: {r['nome_estatistica']} = {r['estatistica']:.3f}{gl} | "
              f"valor-p = {r['valor_p']:.4g}")
        print(f"Conclusão: {r['conclusao']}")
        print(f"População: parâmetro real = {f(r['parametro'])} | erro da estimativa = {f(r['erro_estimativa'])} | "
              f"IC contém o valor real? {'sim' if r['ic_contem_parametro'] else 'NÃO'}")
        print(f"Avaliação: {r['avaliacao']}")
        print(f"Simulação ({REPETICOES} amostras): {sim['cobertura']:.1%} dos ICs contêm o valor real | "
              f"H₀ rejeitada em {sim['taxa_rejeicao']:.1%} das amostras")

    # Conferência das fórmulas com métodos independentes
    print("=" * 78)
    print("CONFERÊNCIA")
    r = avaliar(HIPOTESES[0], amo, pop)
    exato = stats.binomtest(r["sucessos"], r["n"], 0.5).pvalue
    print(f"P1: valor-p do teste z = {r['valor_p']:.4f} | teste binomial exato = {exato:.4f}")
    x = amo["lance_max"].dropna()
    t_mao = (x.mean() - 5) / (x.std(ddof=1) / np.sqrt(len(x)))
    r = avaliar(HIPOTESES[3], amo, pop)
    print(f"M2: t pela fórmula = {t_mao:.4f} | t do scipy = {r['estatistica']:.4f}")


if __name__ == "__main__":
    main()
