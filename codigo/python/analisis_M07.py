"""Caso M-07: el mismo coeficiente aplicado a tres naturalezas de dato.

Calcula, sobre los tres conjuntos del escenario:
  (a) escala multi-item  -> alfa de Cronbach (y su IC bootstrap)
  (b) prueba dicotomica  -> KR-20
  (c) ficha medida 2 veces -> "alfa" de dos columnas (que es r), CCI(A,1) y Bland-Altman

Salida:
  codigo/python/resultados/T-M07-01_coeficientes.csv
  codigo/python/resultados/T-M07-02_bland_altman.csv

Uso: python analisis_M07.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "dataset" / "01_Simulados" / "M-07"
OUT = Path(__file__).resolve().parent / "resultados"
SEMILLA = 20261103
REPLICAS = 2000


def alpha(items: np.ndarray) -> float:
    k = items.shape[1]
    return k / (k - 1) * (1 - items.var(axis=0, ddof=1).sum() / items.sum(axis=1).var(ddof=1))


def kr20(items: np.ndarray) -> float:
    k = items.shape[1]
    p = items.mean(axis=0)
    return k / (k - 1) * (1 - (p * (1 - p)).sum() / items.sum(axis=1).var(ddof=1))


def icc_a1(m: np.ndarray) -> float:
    n, k = m.shape
    grand = m.mean()
    msr = k * ((m.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    msc = n * ((m.mean(axis=0) - grand) ** 2).sum() / (k - 1)
    resid = m - m.mean(axis=1, keepdims=True) - m.mean(axis=0, keepdims=True) + grand
    mse = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def ic_ic(estimador, datos: np.ndarray, rng, eje: int = 0):
    """IC percentil 95 % por bootstrap de filas."""
    vals = []
    for _ in range(REPLICAS):
        idx = rng.integers(0, datos.shape[eje], datos.shape[eje])
        vals.append(estimador(datos[idx]))
    return np.percentile(vals, [2.5, 97.5])


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    lik = pd.read_csv(SIM / "datos_likert.csv")
    tst = pd.read_csv(SIM / "datos_test.csv")
    fic = pd.read_csv(SIM / "datos_ficha.csv")

    x_lik = lik[[c for c in lik.columns if c.startswith("item_")]].to_numpy(float)
    x_tst = tst[[c for c in tst.columns if c.startswith("reactivo_")]].to_numpy(float)
    x_fic = fic[["t1_min", "t2_min"]].to_numpy(float)

    a_lik = alpha(x_lik)
    a_tst = kr20(x_tst)
    a_fic = alpha(x_fic)
    icc = icc_a1(x_fic)

    lo, hi = ic_ic(alpha, x_lik, rng)
    lo2, hi2 = ic_ic(kr20, x_tst, rng)
    lo3, hi3 = ic_ic(icc_a1, x_fic, rng)

    dif = x_fic[:, 1] - x_fic[:, 0]
    sesgo = dif.mean()
    loa = (sesgo - 1.96 * dif.std(ddof=1), sesgo + 1.96 * dif.std(ddof=1))

    filas = [
        {"bloque": "a) escala Likert", "coeficiente": "alfa de Cronbach",
         "valor": round(a_lik, 3), "ic_inf": round(lo, 3), "ic_sup": round(hi, 3),
         "veredicto": "corresponde, aunque omega seria preferible con evidencia de estructura"},
        {"bloque": "b) prueba de conocimiento", "coeficiente": "KR-20",
         "valor": round(a_tst, 3), "ic_inf": round(lo2, 3), "ic_sup": round(hi2, 3),
         "veredicto": "corresponde; el alfa daria el mismo numero con otro nombre y otro sentido"},
        {"bloque": "c) ficha de registro", "coeficiente": "alfa sobre dos columnas (= r)",
         "valor": round(a_fic, 3), "ic_inf": "", "ic_sup": "",
         "veredicto": "no corresponde: mide correlacion, no acuerdo"},
        {"bloque": "c) ficha de registro", "coeficiente": "CCI(A,1) acuerdo absoluto",
         "valor": round(icc, 3), "ic_inf": round(lo3, 3), "ic_sup": round(hi3, 3),
         "veredicto": "corresponde: descuenta el sesgo sistematico"},
        {"bloque": "c) ficha de registro", "coeficiente": "sesgo medio (min)",
         "valor": round(sesgo, 3), "ic_inf": "", "ic_sup": "",
         "veredicto": "diferencia sistematica entre ocasiones: la correlacion no la ve"},
        {"bloque": "c) ficha de registro", "coeficiente": "limite inferior de acuerdo (min)",
         "valor": round(loa[0], 3), "ic_inf": "", "ic_sup": "", "veredicto": "Bland-Altman"},
        {"bloque": "c) ficha de registro", "coeficiente": "limite superior de acuerdo (min)",
         "valor": round(loa[1], 3), "ic_inf": "", "ic_sup": "", "veredicto": "Bland-Altman"},
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(OUT / "T-M07-01_coeficientes.csv", index=False, encoding="utf-8")

    ba = pd.DataFrame({"ficha": fic["ficha"], "promedio": x_fic.mean(axis=1),
                       "diferencia": dif})
    ba.to_csv(OUT / "T-M07-02_bland_altman.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 140)
    print(tabla.to_string(index=False))
    print(f"\nSesgo sistematico: {sesgo:.2f} min | LoA: {loa[0]:.2f} a {loa[1]:.2f} min")
    print(f"Tablas en {OUT}")


if __name__ == "__main__":
    main()
