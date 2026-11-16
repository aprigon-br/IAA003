"""
Etapa 2: cálculo do tamanho da amostra para estimar uma proporção.

Confere o resultado da calculadora on-line usando a fórmula clássica,
com correção para população finita. Lê o tamanho da população (N)
direto do dataset.txt.

Uso:
    .venv\\Scripts\\python.exe calcular_tamanho_amostra.py
"""

import math
from pathlib import Path
from statistics import NormalDist

import pandas as pd

ARQUIVO_DATASET = Path(__file__).resolve().parent / "dataset.txt"

# Parâmetros escolhidos (justificativa no README)
CONFIANCA = 0.95  # nível de confiança
MARGEM_ERRO = 0.05  # erro máximo aceito: 5 pontos percentuais
PROPORCAO = 0.50  # proporção esperada; 0,5 é o caso mais conservador


def tamanho_amostra(N: int, confianca: float, margem: float, p: float) -> tuple[float, float, int]:
    """Devolve (z, n0 para população infinita, n final com correção para população finita)."""
    # z: quantos desvios-padrão da curva normal cobrem a confiança desejada (95% -> 1,96)
    z = NormalDist().inv_cdf(1 - (1 - confianca) / 2)
    # Passo 1: amostra para uma população infinita
    n0 = z**2 * p * (1 - p) / margem**2
    # Passo 2: correção para população finita (nossa população tem tamanho conhecido)
    n = n0 / (1 + (n0 - 1) / N)
    # Arredonda sempre para cima, para garantir pelo menos a precisão pedida
    return z, n0, math.ceil(n)


def main() -> None:
    N = len(pd.read_csv(ARQUIVO_DATASET, sep="\t"))
    z, n0, n = tamanho_amostra(N, CONFIANCA, MARGEM_ERRO, PROPORCAO)

    print("=== Tamanho da amostra (estimação de proporção) ===")
    print(f"População (N) ................. {N}")
    print(f"Nível de confiança ............ {CONFIANCA:.0%}  ->  z = {z:.4f}")
    print(f"Margem de erro (E) ............ {MARGEM_ERRO:.0%}")
    print(f"Proporção esperada (p) ........ {PROPORCAO:.0%}")
    print()
    print(f"Passo 1, população infinita:  n0 = z² · p · (1-p) / E² = {n0:.2f}")
    print(f"Passo 2, população finita:    n  = n0 / (1 + (n0 - 1) / N) = {n0 / (1 + (n0 - 1) / N):.2f}")
    print(f"Arredondando para cima:       n  = {n}")
    print(f"Fração amostral:              n/N = {n / N:.1%}")
    print()

    print("=== Como n muda com os parâmetros (p = 50%, N =", N, ") ===")
    margens = (0.03, 0.05, 0.07)
    print("Confiança  " + "".join(f"  E = {m:.0%}" for m in margens))
    for conf in (0.90, 0.95, 0.99):
        linha = "".join(f"{tamanho_amostra(N, conf, m, PROPORCAO)[2]:>9}" for m in margens)
        print(f"   {conf:.0%}    {linha}")


if __name__ == "__main__":
    main()
