from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DATOS = RAIZ / "05_Datos" / "01_Simulados" / "U-07" / "datos.csv"
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
    n = len(d)
    antes = int(d["implementado_antes"].sum())
    despues = int(d["implementado_despues"].sum())
    lo_a, hi_a = wilson(antes, n)
    lo_d, hi_d = wilson(despues, n)

    tabla = pd.crosstab(d["implementado_antes"], d["implementado_despues"])
    b = int(tabla.loc[0, 1])   # no implementado antes, si despues
    c = int(tabla.loc[1, 0])   # si antes, no despues
    mcnemar = stats.binomtest(b, b + c, 0.5) if (b + c) else None
    # razon de momios del cambio apareado
    odds = b / c if c else float("inf")

    lineas = [
        f"# U-07 · cobertura del anexo A · {DATOS.name}",
        "",
        f"- controles = {n} (organizacional, personas, fisico, tecnologico)",
        f"- antes: {antes} implementados = {coma(100 * antes / n, 1)} % · IC 95 % Wilson "
        f"[{coma(100 * lo_a, 1)}; {coma(100 * hi_a, 1)}]",
        f"- despues: {despues} implementados = {coma(100 * despues / n, 1)} % · IC 95 % Wilson "
        f"[{coma(100 * lo_d, 1)}; {coma(100 * hi_d, 1)}]",
        f"- diferencia de proporciones = {coma(100 * (despues - antes) / n, 1)} puntos porcentuales",
        "",
        "## Tabla de concordancia (McNemar)",
        f"- sin implementar y luego implementado: {b}",
        f"- implementado y luego abandonado: {c}",
        f"- McNemar exacto: p = {coma(mcnemar.pvalue, 8) if mcnemar else 'no aplica'}",
        f"- razon de momios del cambio: {coma(odds, 2)}",
        "",
        "## Por tema",
    ]
    por_tema = d.groupby("tema").agg(
        controles=("control_id", "size"),
        antes=("implementado_antes", "sum"),
        despues=("implementado_despues", "sum"),
    )
    for tema, fila in por_tema.iterrows():
        lineas.append(
            f"- {tema}: {int(fila.antes)}/{int(fila.controles)} antes · "
            f"{int(fila.despues)}/{int(fila.controles)} despues")

    lineas += [
        "",
        "Interpretacion: la unidad es el control y la comparacion es pareada; por eso McNemar y no",
        "una prueba de dos proporciones independientes. L_M = 4, L_D = 3 (mismos controles antes y",
        "despues, sin asignacion aleatoria), L_A = 3 (proporcion con intervalo) => L* = 3.",
    ]
    guardar("U-07_cobertura_controles.md", lineas)


if __name__ == "__main__":
    main()
