"""
Etapa 4: funções de estatística descritiva.

Usadas igualmente na população (dataset.txt) e na amostra (amostra.txt), para
os painéis 1 e 2 serem calculados exatamente do mesmo jeito.
Lê SOMENTE os arquivos .txt, nunca o banco de dados.

Rodar este arquivo direto mostra o resumo população × amostra no terminal:
    .venv\\Scripts\\python.exe estatistica.py
"""

from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
ARQUIVO_POPULACAO = PASTA / "dataset.txt"
ARQUIVO_AMOSTRA = PASTA / "amostra.txt"

# Regras das variáveis derivadas (documentadas no README)
LIMITE_COMPETICAO_ALTA = 67  # competição >= 67 = terço superior da escala 0-100
PADRAO_INTENCAO_LOCAL = r"perto|pr[oó]xim[oa]"  # "perto", "próximo", "proxima"...

# Variáveis analisadas: nome da coluna -> rótulo para mostrar
QUANTITATIVAS = {
    "volume_brasil": "Volume (pesquisas/mês)",
    "lance_min": "Lance mínimo (R$)",
    "lance_max": "Lance máximo (R$)",
    "competicao": "Competição (0-100)",
}
QUALITATIVAS = {
    "publico": "Público",
    "origem": "Origem da busca",
    "competicao_alta": "Competição alta (≥ 67)",
    "intencao_local": "Intenção local",
}


def carregar(caminho: Path) -> pd.DataFrame:
    """Lê o arquivo .txt e acrescenta as duas variáveis derivadas."""
    df = pd.read_csv(caminho, sep="\t")

    # Competição alta: "Sim"/"Não"; fica vazia quando a competição não foi informada
    alta = (df["competicao"] >= LIMITE_COMPETICAO_ALTA).map({True: "Sim", False: "Não"})
    df["competicao_alta"] = alta.where(df["competicao"].notna())

    # Intenção local: o texto da busca fala em "perto" ou "próximo"?
    local = df["texto"].str.contains(PADRAO_INTENCAO_LOCAL, regex=True)
    df["intencao_local"] = local.map({True: "Sim", False: "Não"})
    return df


def carregar_populacao() -> pd.DataFrame:
    return carregar(ARQUIVO_POPULACAO)


def carregar_amostra() -> pd.DataFrame:
    return carregar(ARQUIVO_AMOSTRA)


def medidas(df: pd.DataFrame, populacao: bool) -> pd.DataFrame:
    """
    Medidas descritivas das variáveis quantitativas (uma coluna por variável).

    populacao=True  -> desvio-padrão populacional (σ, divide por N)
    populacao=False -> desvio-padrão amostral     (s, divide por n-1)
    """
    ddof = 0 if populacao else 1
    resultado = {}
    for coluna, rotulo in QUANTITATIVAS.items():
        x = df[coluna].dropna()  # vazios ficam de fora do cálculo
        q1, q3 = x.quantile(0.25), x.quantile(0.75)
        aiq = q3 - q1  # amplitude interquartil: onde estão os 50% do meio
        media = x.mean()
        dp = x.std(ddof=ddof)
        resultado[rotulo] = {
            "n (válidos)": len(x),
            "vazios": int(df[coluna].isna().sum()),
            "média": media,
            "mediana": x.median(),
            "desvio-padrão": dp,
            "coef. de variação (%)": dp / media * 100,
            "mínimo": x.min(),
            "1º quartil (Q1)": q1,
            "3º quartil (Q3)": q3,
            "máximo": x.max(),
            "amplitude interquartil": aiq,
            "assimetria": x.skew(),
            # valores atípicos pela regra do boxplot: além de 1,5 x AIQ dos quartis
            "atípicos (outliers)": int(((x < q1 - 1.5 * aiq) | (x > q3 + 1.5 * aiq)).sum()),
        }
    return pd.DataFrame(resultado)


def frequencias(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Tabela de frequências (contagem e %) de uma variável qualitativa, sem os vazios."""
    contagem = df[coluna].value_counts()
    return pd.DataFrame({
        "frequência": contagem,
        "proporção (%)": contagem / contagem.sum() * 100,
    })


def top_nichos(df: pd.DataFrame, coluna: str, agregacao: str = "sum", k: int = 10) -> pd.Series:
    """Os k nichos com maior valor de uma variável (soma ou média por nicho)."""
    return df.groupby("nicho")[coluna].agg(agregacao).nlargest(k)


# ---------------------------------------------------------------------------
# Resumo no terminal (só quando o arquivo é rodado direto)
# ---------------------------------------------------------------------------
def main() -> None:
    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

    pop, amo = carregar_populacao(), carregar_amostra()
    med_pop, med_amo = medidas(pop, populacao=True), medidas(amo, populacao=False)

    print(f"POPULAÇÃO: {len(pop)} buscas  |  AMOSTRA: {len(amo)} buscas\n")
    print("=== Medidas descritivas: POPULAÇÃO ===")
    print(med_pop.to_string(), "\n")
    print("=== Medidas descritivas: AMOSTRA ===")
    print(med_amo.to_string(), "\n")

    print("=== Variáveis qualitativas: proporção (%) ===")
    for coluna, rotulo in QUALITATIVAS.items():
        tabela = pd.DataFrame({
            "população": frequencias(pop, coluna)["proporção (%)"],
            "amostra": frequencias(amo, coluna)["proporção (%)"],
        }).fillna(0)
        tabela["diferença (p.p.)"] = tabela["amostra"] - tabela["população"]
        print(f"-- {rotulo} --")
        print(tabela.to_string(), "\n")

    print("=== Por que a média do volume engana ===")
    v = pop["volume_brasil"]
    print(f"Média: {v.mean():,.0f}  |  Mediana: {v.median():,.0f}")
    print(f"Buscas com volume ABAIXO da média: {(v < v.mean()).mean():.1%}")
    top1 = v.nlargest(int(len(v) * 0.01)).sum() / v.sum()
    print(f"O 1% de buscas mais pesquisadas concentra {top1:.1%} de todo o volume\n")

    print("=== Top 5 nichos por volume total (população) ===")
    print(top_nichos(pop, "volume_brasil", "sum", 5).to_string())


if __name__ == "__main__":
    main()
