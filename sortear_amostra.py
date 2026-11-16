"""
Etapa 3: sorteio da amostra aleatória simples (AAS).

Lê a população (dataset.txt), sorteia n = 358 buscas sem reposição, com a mesma
chance para todas, e grava amostra.txt no mesmo formato do dataset.

A semente aleatória é fixa e foi escolhida ANTES de olhar o resultado (a data do
sorteio, 11/11/2026). Com ela, quem rodar este script de novo obtém exatamente a
mesma amostra. A semente não deve ser trocada depois, para não "escolher" a amostra.

Uso:
    .venv\\Scripts\\python.exe sortear_amostra.py
"""

from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
ARQUIVO_POPULACAO = PASTA / "dataset.txt"
ARQUIVO_AMOSTRA = PASTA / "amostra.txt"

TAMANHO_AMOSTRA = 358  # calculado na Etapa 2 (calcular_tamanho_amostra.py)
SEMENTE = 20261111  # data do sorteio; fixa para o sorteio ser reproduzível


def ler_texto(caminho: Path) -> pd.DataFrame:
    # dtype=str e keep_default_na=False: lê cada campo como texto, exatamente como
    # está no arquivo, para a amostra sair idêntica às linhas da população.
    return pd.read_csv(caminho, sep="\t", dtype=str, keep_default_na=False)


def main() -> None:
    populacao = ler_texto(ARQUIVO_POPULACAO)
    N = len(populacao)

    # Sorteio: sem reposição (cada busca no máximo uma vez), todas com a mesma chance.
    amostra = populacao.sample(n=TAMANHO_AMOSTRA, replace=False, random_state=SEMENTE)

    amostra.to_csv(ARQUIVO_AMOSTRA, sep="\t", index=False, encoding="utf-8")

    print(f"População: {N} buscas  |  Amostra: {len(amostra)} buscas  |  Semente: {SEMENTE}")
    print(f"Probabilidade de cada busca ser sorteada: {TAMANHO_AMOSTRA}/{N} = {TAMANHO_AMOSTRA / N:.2%}")
    print(f"Amostra gravada em {ARQUIVO_AMOSTRA}\n")
    print("As 10 primeiras buscas sorteadas (posição na população entre parênteses):")
    for posicao, linha in amostra.head(10).iterrows():
        print(f"  ({posicao + 1:>4})  {linha['nicho']:<40} {linha['texto']}")


if __name__ == "__main__":
    main()
