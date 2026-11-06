from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DATOS = RAIZ / "05_Datos" / "01_Simulados" / "U-08" / "datos.csv"
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
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    d = pd.read_csv(DATOS)
    d["despues"] = (d["periodo"] == "despues").astype(int)
    d["semana_desde_cambio"] = np.where(d["despues"] == 1, d["semana"] - 12, 0)

    antes = d[d.despues == 0]
    despues = d[d.despues == 1]

    fcr_a, fcr_d = antes.resueltos_primer_contacto.sum() / antes.tickets_abiertos.sum(), \
        despues.resueltos_primer_contacto.sum() / despues.tickets_abiertos.sum()
    lo_a, hi_a = wilson(int(antes.resueltos_primer_contacto.sum()), int(antes.tickets_abiertos.sum()))
    lo_d, hi_d = wilson(int(despues.resueltos_primer_contacto.sum()), int(despues.tickets_abiertos.sum()))

    # regresion segmentada sobre el logaritmo del tiempo mediano
    d["log_t"] = np.log(d["tiempo_mediano_h"])
    modelo = smf.ols("log_t ~ despues + semana_desde_cambio", data=d).fit()

    # conteos: binomial negativa
    try:
        nb = smf.negativebinomial("tickets_abiertos ~ despues", data=d).fit(disp=0)
        p_nb = f"{nb.pvalues['despues']:.4f}"
    except Exception as error:  # pragma: no cover
        p_nb = f"no estimable ({error})"

    lineas = [
        f"# U-08 · mesa de ayuda · {DATOS.name}",
        "",
        f"- semanas = {len(d)} (12 antes, 12 despues)",
        f"- mediana del tiempo de resolucion: {coma(antes.tiempo_mediano_h.median(), 1)} h antes · "
        f"{coma(despues.tiempo_mediano_h.median(), 1)} h despues",
        f"- resolucion al primer contacto: {coma(100 * fcr_a, 1)} % "
        f"[{coma(100 * lo_a, 1)}; {coma(100 * hi_a, 1)}] antes · {coma(100 * fcr_d, 1)} % "
        f"[{coma(100 * lo_d, 1)}; {coma(100 * hi_d, 1)}] despues",
        "",
        "## Serie temporal interrumpida (log del tiempo mediano)",
        f"- cambio de nivel al intervenir: {coma(100 * (np.exp(modelo.params['despues']) - 1), 1)} %",
        f"- cambio de pendiente por semana: {coma(100 * (np.exp(modelo.params['semana_desde_cambio']) - 1), 2)} %",
        f"- p del cambio de nivel = {modelo.pvalues['despues']:.6f}",
        "",
        "## Conteo de tickets",
        f"- media semanal: {coma(antes.tickets_abiertos.mean(), 1)} antes · "
        f"{coma(despues.tickets_abiertos.mean(), 1)} despues",
        f"- binomial negativa, p del periodo = {p_nb}",
        "",
        "Interpretacion: con serie temporal el contraste correcto no es una t de dos grupos sino el",
        "cambio de nivel y de pendiente. L_M = 4 (registro del sistema), L_D = 3 (serie interrumpida",
        "sin aleatorizacion), L_A = 3 => L* = 3.",
    ]
    guardar("U-08_mesa_de_ayuda.md", lineas)


if __name__ == "__main__":
    main()
