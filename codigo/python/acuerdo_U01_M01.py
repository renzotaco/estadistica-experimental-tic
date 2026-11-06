"""Calcula los indicadores de acuerdo de U-01 y M-01 con intervalo bootstrap del CCI."""

import pathlib

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(r"C:\Download\downpdfs\ARTICLES\Libro_Tesis_TIC")
BASE = RAIZ / "05_Datos" / "01_Simulados"
rng = np.random.default_rng(20261103)


def icc_a1(a, b):
    """CCI(A,1): modelo de dos vías, efectos aleatorios, acuerdo absoluto."""
    datos = np.column_stack([a, b])
    n, k = datos.shape
    total = datos.mean()
    media_fila = datos.mean(axis=1)
    media_col = datos.mean(axis=0)
    sc = ((datos - total) ** 2).sum()
    sf = k * ((media_fila - total) ** 2).sum()
    scc = n * ((media_col - total) ** 2).sum()
    se = sc - sf - scc
    cmf = sf / (n - 1)
    cmc = scc / (k - 1)
    cme = se / ((n - 1) * (k - 1))
    return (cmf - cme) / (cmf + (k - 1) * cme + k * (cmc - cme) / n)


def acuerdo(nombre, a, b, unidad):
    # sesgo = segunda medicion menos primera (positivo: la segunda mide mas)
    dif = b - a
    sesgo = dif.mean()
    de = dif.std(ddof=1)
    loa = (sesgo - 1.96 * de, sesgo + 1.96 * de)
    boot = []
    for _ in range(5000):
        idx = rng.integers(0, len(a), len(a))
        boot.append(icc_a1(a[idx], b[idx]))
    ic = np.percentile(boot, [2.5, 97.5])
    print(f"=== {nombre} (n = {len(a)})")
    print(f"  r         = {np.corrcoef(a, b)[0,1]:.4f}")
    print(f"  CCI(A,1)  = {icc_a1(a, b):.3f}  IC 95 % [{ic[0]:.3f}; {ic[1]:.3f}]")
    print(f"  sesgo     = {sesgo:.2f} {unidad} ({100*sesgo/a.mean():.1f} % del valor medio)")
    print(f"  LoA 95 %  = [{loa[0]:.2f}; {loa[1]:.2f}]")


def main() -> None:
    u = pd.read_csv(BASE / "U-01" / "datos.csv")
    acuerdo("U-01 log vs APM", u["latencia_log_ms"].to_numpy(), u["latencia_apm_ms"].to_numpy(), "ms")

    m = pd.read_csv(BASE / "M-01" / "datos.csv")
    acuerdo("M-01 ficha t1 vs t2", m["t1_min"].to_numpy(), m["t2_min"].to_numpy(), "min")


if __name__ == "__main__":
    main()
