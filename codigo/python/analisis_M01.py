"""Caso M-01: el alfa sobre la ficha de registro (retest con sesgo sistematico).

Muestra el contraste que sostiene la seccion 2.4 del capitulo 2:
  - lo que la tesis informa (r de retest y alfa sobre dos columnas)
  - lo que corresponde (CCI(A,1) y limites de acuerdo de Bland-Altman)

Salida: codigo/python/resultados/T-M01-01_acuerdo.csv

Uso: python analisis_M01.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "dataset" / "01_Simulados" / "M-01"
OUT = Path(__file__).resolve().parent / "resultados"
SEMILLA = 20261103
REPLICAS = 2000


def alpha(m: np.ndarray) -> float:
    k = m.shape[1]
    return k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1))


def icc_a1(m: np.ndarray) -> float:
    n, k = m.shape
    g = m.mean()
    msr = k * ((m.mean(axis=1) - g) ** 2).sum() / (n - 1)
    msc = n * ((m.mean(axis=0) - g) ** 2).sum() / (k - 1)
    resid = m - m.mean(axis=1, keepdims=True) - m.mean(axis=0, keepdims=True) + g
    mse = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def ic_boot(f, m: np.ndarray, rng) -> tuple[float, float]:
    vals = [f(m[rng.integers(0, m.shape[0], m.shape[0])]) for _ in range(REPLICAS)]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    d = pd.read_csv(SIM / "datos.csv")
    m = d[["t1_min", "t2_min"]].to_numpy(float)
    dif = m[:, 1] - m[:, 0]

    r = float(np.corrcoef(m[:, 0], m[:, 1])[0, 1])
    a = alpha(m)
    icc = icc_a1(m)
    lo_a, hi_a = ic_boot(alpha, m, rng)
    lo_i, hi_i = ic_boot(icc_a1, m, rng)

    sesgo = float(dif.mean())
    loa = (sesgo - 1.96 * dif.std(ddof=1), sesgo + 1.96 * dif.std(ddof=1))
    sesgo_pct = 100 * sesgo / float(m[:, 0].mean())

    filas = [
        {"indicador": "r de Pearson entre ocasiones", "valor": round(r, 3),
         "ic_inf": "", "ic_sup": "",
         "que_dice": "altisima: es lo que la tesis presenta como confiabilidad",
         "veredicto": "no evalua acuerdo: un sesgo constante no la baja"},
        {"indicador": "alfa sobre las dos columnas", "valor": round(a, 3),
         "ic_inf": round(lo_a, 3), "ic_sup": round(hi_a, 3),
         "que_dice": "practicamente igual a r (con dos columnas, alfa = r)",
         "veredicto": "no corresponde: no hay itemes ni constructo"},
        {"indicador": "CCI(A,1) de acuerdo absoluto", "valor": round(icc, 3),
         "ic_inf": round(lo_i, 3), "ic_sup": round(hi_i, 3),
         "que_dice": "buena pero menor: descuenta el sesgo",
         "veredicto": "corresponde: es la evidencia de calidad del registro"},
        {"indicador": "sesgo medio (min)", "valor": round(sesgo, 3),
         "ic_inf": "", "ic_sup": "",
         "que_dice": f"{sesgo_pct:.1f} % de la medicion basal",
         "veredicto": "invisible para r y para el alfa"},
        {"indicador": "limite inferior de acuerdo (min)", "valor": round(loa[0], 3),
         "ic_inf": "", "ic_sup": "", "que_dice": "Bland-Altman",
         "veredicto": "el registro no es intercambiable entre ocasiones"},
        {"indicador": "limite superior de acuerdo (min)", "valor": round(loa[1], 3),
         "ic_inf": "", "ic_sup": "", "que_dice": "Bland-Altman",
         "veredicto": "amplitud que el tesista debe declarar"},
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(OUT / "T-M01-01_acuerdo.csv", index=False, encoding="utf-8")
    pd.DataFrame({"ficha": d["ficha"], "promedio": m.mean(axis=1), "diferencia": dif}).to_csv(
        OUT / "T-M01-02_bland_altman.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 150)
    print(tabla.to_string(index=False))
    print(f"\nSesgo: {sesgo:.2f} min ({sesgo_pct:.1f} %) | LoA: {loa[0]:.2f} a {loa[1]:.2f} min")


if __name__ == "__main__":
    main()
