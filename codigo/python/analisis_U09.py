from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DATOS = RAIZ / "05_Datos" / "01_Simulados" / "U-09" / "datos.csv"
SALIDA = pathlib.Path(__file__).resolve().parent / "resultados"
SALIDA.mkdir(exist_ok=True)
rng = np.random.default_rng(20261103)


def coma(x, dec=2):
    return f"{x:.{dec}f}".replace(".", ",")


def wilson(exitos, total):
    lo, hi = proportion_confint(exitos, total, method="wilson")
    return lo, hi


def guardar(nombre, lineas):
    texto = "\n".join(lineas) + "\n"
    (SALIDA / nombre).write_text(texto, encoding="utf-8")
    print(texto)


def main() -> None:
    d = pd.read_csv(DATOS)
    v1 = d[d.version == "v1"]
    v2 = d[d.version == "v2"]

    u = stats.mannwhitneyu(v1.densidad_defectos_kloc, v2.densidad_defectos_kloc, alternative="two-sided")
    a12 = u.statistic / (len(v1) * len(v2))  # probabilidad de superioridad
    dif = v2.densidad_defectos_kloc.median() - v1.densidad_defectos_kloc.median()

    ic = []
    for _ in range(2000):
        m1 = rng.choice(v1.densidad_defectos_kloc.to_numpy(), len(v1), replace=True)
        m2 = rng.choice(v2.densidad_defectos_kloc.to_numpy(), len(v2), replace=True)
        ic.append(np.median(m2) - np.median(m1))
    lo, hi = np.percentile(ic, [2.5, 97.5])

    r = stats.spearmanr(d.complejidad_ciclomatica, d.densidad_defectos_kloc)

    lineas = [
        f"# U-09 · mantenibilidad · {DATOS.name}",
        "",
        f"- modulos = {len(v1)} por version",
        f"- densidad media: {coma(v1.densidad_defectos_kloc.mean(), 2)} v1 · "
        f"{coma(v2.densidad_defectos_kloc.mean(), 2)} v2 (defectos por KLOC)",
        f"- complejidad media: {coma(v1.complejidad_ciclomatica.mean(), 1)} v1 · "
        f"{coma(v2.complejidad_ciclomatica.mean(), 1)} v2",
        "",
        "## Contraste",
        f"- Mann-Whitney U = {coma(u.statistic, 1)} · p = {coma(u.pvalue, 8)}",
        f"- A12 (probabilidad de superioridad) = {coma(a12, 3)}",
        f"- diferencia de medianas = {coma(dif, 2)} defectos por KLOC · IC 95 % bootstrap "
        f"[{coma(lo, 2)}; {coma(hi, 2)}]",
        f"- Spearman complejidad-densidad: rho = {coma(r.statistic, 3)} · p = {coma(r.pvalue, 8)}",
        "",
        "Interpretacion: la densidad tiene cola larga, de modo que la comparacion va por rangos y la",
        "magnitud se informa como diferencia de medianas con intervalo. L_M = 4 (medida estandarizada",
        "del producto), L_D = 3 (dos versiones del mismo producto, sin aleatorizacion de modulos),",
        "L_A = 3 => L* = 3.",
    ]
    guardar("U-09_mantenibilidad.md", lineas)


if __name__ == "__main__":
    main()
