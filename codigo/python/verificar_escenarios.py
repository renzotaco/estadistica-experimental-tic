"""Verifica que cada escenario simulado produzca el fenomeno que el caso ensena.

No es un analisis del libro: es el control de calidad de los datos. Si un escenario
deja de reproducir su propiedad (por ejemplo, el retest con sesgo deja de dar r alta
y CCI baja), el caso pierde su valor didactico y hay que revisar el generador.

Salida: dataset/05_Manifiestos/verificacion_escenarios.csv
Uso: python verificar_escenarios.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "dataset" / "01_Simulados"
OUT = ROOT / "dataset" / "05_Manifiestos"


def leer(caso: str, archivo: str = "datos.csv") -> pd.DataFrame:
    return pd.read_csv(SIM / caso / archivo)


def icc_a1(x: np.ndarray, y: np.ndarray) -> float:
    """CCI(2,1) de acuerdo absoluto para dos mediciones por sujeto."""
    m = np.column_stack([x, y]).astype(float)
    n, k = m.shape
    grand = m.mean()
    msr = k * ((m.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    msc = n * ((m.mean(axis=0) - grand) ** 2).sum() / (k - 1)
    resid = m - m.mean(axis=1, keepdims=True) - m.mean(axis=0, keepdims=True) + grand
    mse = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def alpha(items: pd.DataFrame) -> float:
    k = items.shape[1]
    return float(k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def kr20(items: pd.DataFrame) -> float:
    k = items.shape[1]
    p = items.mean(axis=0)
    return float(k / (k - 1) * (1 - (p * (1 - p)).sum() / items.sum(axis=1).var(ddof=1)))


def a12(x: np.ndarray, y: np.ndarray) -> float:
    u = stats.mannwhitneyu(x, y, alternative="two-sided").statistic
    return float(u / (len(x) * len(y)))


def fila(caso: str, metrica: str, valor, nota: str) -> dict:
    return {"caso": caso, "metrica": metrica,
            "valor": round(valor, 4) if isinstance(valor, (int, float, np.floating)) else valor,
            "nota": nota}


def main() -> None:
    filas: list[dict] = []

    # U-01 dos instrumentos
    d = leer("U-01")
    x, y = d["latencia_log_ms"].to_numpy(), d["latencia_apm_ms"].to_numpy()
    dif = y - x
    filas += [
        fila("U-01", "r_pearson", stats.pearsonr(x, y)[0], "correlacion alta pese al sesgo"),
        fila("U-01", "cci_a1", icc_a1(x, y), "acuerdo absoluto: descuenta el sesgo"),
        fila("U-01", "sesgo_medio_ms", dif.mean(), "diferencia media entre instrumentos"),
        fila("U-01", "loa_inferior", dif.mean() - 1.96 * dif.std(ddof=1), "Bland-Altman"),
        fila("U-01", "loa_superior", dif.mean() + 1.96 * dif.std(ddof=1), "Bland-Altman"),
    ]

    # U-02 A/B con basal
    d = leer("U-02")
    t_post = stats.ttest_ind(d.loc[d.grupo == "B", "post_ms"], d.loc[d.grupo == "A", "post_ms"])
    anc = smf.ols("post_ms ~ C(grupo) + pre_ms", data=d).fit()
    filas += [
        fila("U-02", "t_postest_p", t_post.pvalue, "contraste sin ajuste"),
        fila("U-02", "ancova_p", anc.pvalues["C(grupo)[T.B]"], "ANCOVA"),
        fila("U-02", "ancova_efecto_ms", anc.params["C(grupo)[T.B]"], "efecto ajustado"),
        fila("U-02", "diferencia_bruta_ms",
             d.loc[d.grupo == "B", "post_ms"].mean() - d.loc[d.grupo == "A", "post_ms"].mean(),
             "diferencia de medias postest"),
    ]

    # U-03 prueba de conocimiento
    d = leer("U-03")
    items = d[[c for c in d.columns if c.startswith("i")]]
    dif3 = d["post_total"] - d["pre_total"]
    t3 = stats.ttest_rel(d["post_total"], d["pre_total"])
    filas += [
        fila("U-03", "kr20_post", kr20(items), "consistencia de una prueba dicotomica"),
        fila("U-03", "t_pareada_p", t3.pvalue, "diferencia pre-post"),
        fila("U-03", "dz", dif3.mean() / dif3.std(ddof=1), "tamano del efecto pareado"),
    ]

    # U-04 usabilidad
    d = leer("U-04")
    its = d[[c for c in d.columns if c.startswith("sus_") and len(c) == 6]]
    mw = stats.mannwhitneyu(d.loc[d.grupo == "Interfaz_B", "tiempo_tarea_s"],
                            d.loc[d.grupo == "Interfaz_A", "tiempo_tarea_s"])
    filas += [
        fila("U-04", "alfa_sus", alpha(its), "consistencia del SUS (10 items)"),
        fila("U-04", "mw_tiempo_p", mw.pvalue, "Mann-Whitney sobre el tiempo de tarea"),
        fila("U-04", "a12_tiempo", a12(d.loc[d.grupo == "Interfaz_B", "tiempo_tarea_s"].to_numpy(),
                                       d.loc[d.grupo == "Interfaz_A", "tiempo_tarea_s"].to_numpy()),
             "probabilidad de superioridad"),
        fila("U-04", "sus_mediana_A", d.loc[d.grupo == "Interfaz_A", "sus_puntaje"].median(), ""),
        fila("U-04", "sus_mediana_B", d.loc[d.grupo == "Interfaz_B", "sus_puntaje"].median(), ""),
    ]

    # U-05 conteos
    d = leer("U-05")
    tasas = d.groupby("periodo")["incidentes"].agg(["sum", "count"])
    razon = (tasas.loc["despues", "sum"] / tasas.loc["despues", "count"]) / \
            (tasas.loc["antes", "sum"] / tasas.loc["antes", "count"])
    t5 = stats.ttest_ind(d.loc[d.periodo == "despues", "incidentes"],
                         d.loc[d.periodo == "antes", "incidentes"])
    se = np.sqrt(1 / tasas.loc["despues", "sum"] + 1 / tasas.loc["antes", "sum"])
    filas += [
        fila("U-05", "razon_tasas", razon, "incidentes por dia, despues/antes"),
        fila("U-05", "rr_ic_inferior", np.exp(np.log(razon) - 1.96 * se), "IC 95 % de la razon"),
        fila("U-05", "rr_ic_superior", np.exp(np.log(razon) + 1.96 * se), "IC 95 % de la razon"),
        fila("U-05", "t_conteos_p", t5.pvalue, "prueba inadecuada, para contraste docente"),
    ]

    # U-06 benchmark
    d = leer("U-06")
    d = d[d.warmup == 0]
    b = d.loc[d.variante == "v2_optimizada", "latencia_ms"].to_numpy()
    a = d.loc[d.variante == "v1_legacy", "latencia_ms"].to_numpy()
    rng = np.random.default_rng(20261103)
    boots = [np.median(rng.choice(b, b.size)) - np.median(rng.choice(a, a.size))
             for _ in range(2000)]
    filas += [
        fila("U-06", "mediana_v1_ms", np.median(a), "sin calentamiento"),
        fila("U-06", "mediana_v2_ms", np.median(b), "sin calentamiento"),
        fila("U-06", "p95_v1_ms", np.percentile(a, 95), "cola"),
        fila("U-06", "p95_v2_ms", np.percentile(b, 95), "cola"),
        fila("U-06", "dif_medianas_ic_inf", np.percentile(boots, 2.5), "bootstrap 2000"),
        fila("U-06", "dif_medianas_ic_sup", np.percentile(boots, 97.5), "bootstrap 2000"),
    ]

    # M-01 retest con sesgo
    d = leer("M-01")
    x, y = d["t1_min"].to_numpy(), d["t2_min"].to_numpy()
    dif = y - x
    filas += [
        fila("M-01", "r_retest", stats.pearsonr(x, y)[0], "el certificado que engania"),
        fila("M-01", "alfa_dos_columnas", alpha(d[["t1_min", "t2_min"]]), "alfa sobre dos mediciones"),
        fila("M-01", "cci_a1", icc_a1(x, y), "acuerdo absoluto"),
        fila("M-01", "sesgo_medio_min", dif.mean(), "sesgo sistematico no detectado por r"),
        fila("M-01", "sesgo_pct", 100 * dif.mean() / x.mean(), "porcentaje sobre la medicion basal"),
    ]

    # M-02 tendencia
    d = leer("M-02")
    t2 = stats.ttest_ind(d.loc[d.fase == "post", "indicador_horas"],
                         d.loc[d.fase == "pre", "indicador_horas"])
    filas += [
        fila("M-02", "t_p", t2.pvalue, "un solo grupo, efecto verdadero nulo"),
        fila("M-02", "diferencia_medias_h", d.loc[d.fase == "post", "indicador_horas"].mean()
             - d.loc[d.fase == "pre", "indicador_horas"].mean(), "lo que la tesis llamaria mejora"),
        fila("M-02", "efecto_verdadero", 0.0, "declarado en parametros.json"),
    ]

    # M-03 p sin magnitud
    d = leer("M-03")
    x = d.loc[d.grupo == "tratamiento", "latencia_ms"].to_numpy()
    y = d.loc[d.grupo == "control", "latencia_ms"].to_numpy()
    t3 = stats.ttest_ind(x, y)
    sp = np.sqrt(((x.size - 1) * x.var(ddof=1) + (y.size - 1) * y.var(ddof=1)) / (x.size + y.size - 2))
    filas += [
        fila("M-03", "n_total", len(d), "muestra grande"),
        fila("M-03", "t_p", t3.pvalue, "p minusculo"),
        fila("M-03", "d_cohen", (x.mean() - y.mean()) / sp, "efecto trivial"),
        fila("M-03", "diferencia_ms", x.mean() - y.mean(), "magnitud en unidades originales"),
    ]

    # M-04 desbalance basal
    d = leer("M-04")
    sp_pre = np.sqrt(((d.loc[d.grupo == "piloto", "pre_puntaje"].var(ddof=1) * 49)
                      + (d.loc[d.grupo == "control", "pre_puntaje"].var(ddof=1) * 49)) / 98)
    desbalance = (d.loc[d.grupo == "piloto", "pre_puntaje"].mean()
                  - d.loc[d.grupo == "control", "pre_puntaje"].mean()) / sp_pre
    t4 = stats.ttest_ind(d.loc[d.grupo == "piloto", "post_puntaje"],
                         d.loc[d.grupo == "control", "post_puntaje"])
    anc = smf.ols("post_puntaje ~ C(grupo) + pre_puntaje", data=d).fit()
    filas += [
        fila("M-04", "desbalance_basal_de", desbalance, "diferencia inicial en desviaciones"),
        fila("M-04", "t_postest_p", t4.pvalue, "sin ajuste"),
        fila("M-04", "t_postest_efecto", d.loc[d.grupo == "piloto", "post_puntaje"].mean()
             - d.loc[d.grupo == "control", "post_puntaje"].mean(), "sesgado por la linea basal"),
        fila("M-04", "ancova_efecto", anc.params["C(grupo)[T.piloto]"], "efecto ajustado"),
        fila("M-04", "ancova_p", anc.pvalues["C(grupo)[T.piloto]"], ""),
    ]

    # M-05 pseudorreplicacion
    d = leer("M-05")
    t5 = stats.ttest_ind(d.loc[d.grupo == "tratamiento", "tiempo_carga_min"],
                         d.loc[d.grupo == "control", "tiempo_carga_min"])
    agg = d.groupby(["camion", "grupo"])["tiempo_carga_min"].mean().reset_index()
    t5b = stats.ttest_ind(agg.loc[agg.grupo == "tratamiento", "tiempo_carga_min"],
                          agg.loc[agg.grupo == "control", "tiempo_carga_min"])
    filas += [
        fila("M-05", "n_observaciones", len(d), "despachos"),
        fila("M-05", "n_unidades", agg.shape[0], "camiones"),
        fila("M-05", "t_ingenuo_p", t5.pvalue, "n = 5250"),
        fila("M-05", "t_agregado_p", t5b.pvalue, "n = 10"),
        fila("M-05", "d_ingenuo", (d.loc[d.grupo == "tratamiento", "tiempo_carga_min"].mean()
                                   - d.loc[d.grupo == "control", "tiempo_carga_min"].mean())
             / d["tiempo_carga_min"].std(ddof=1), "tamano inflado por pseudorreplicacion"),
    ]

    # M-06 constructo desplazado
    d = leer("M-06")
    mod = leer("M-06", "datos_modulos.csv")
    its = d[[c for c in d.columns if c.startswith("cal")]]
    per_mod = d.groupby("modulo")["cal01"].mean().rename("likert_medio")
    j = mod.set_index("modulo").join(per_mod)
    filas += [
        fila("M-06", "alfa_likert", alpha(its), "consistencia del cuestionario"),
        fila("M-06", "r_likert_defectos", stats.pearsonr(j["likert_medio"], j["defectos_por_kloc"])[0],
             "asociacion entre percepcion y atributo tecnico"),
        fila("M-06", "n_modulos", len(j), "unidades del atributo tecnico"),
    ]

    # M-07 el mismo coeficiente en tres naturalezas de dato
    lik = leer("M-07", "datos_likert.csv")
    tst = leer("M-07", "datos_test.csv")
    fic = leer("M-07", "datos_ficha.csv")
    items_lik = lik[[c for c in lik.columns if c.startswith("item_")]]
    items_tst = tst[[c for c in tst.columns if c.startswith("reactivo_")]]
    x, y = fic["t1_min"].to_numpy(), fic["t2_min"].to_numpy()
    filas += [
        fila("M-07", "alfa_likert", alpha(items_lik), "escala multi-item: uso legitimo del coeficiente"),
        fila("M-07", "kr20_prueba", kr20(items_tst), "prueba dicotomica: el numero correcto con otro nombre"),
        fila("M-07", "alfa_ficha", alpha(fic[["t1_min", "t2_min"]]),
             "dos columnas de una ficha: el coeficiente no significa nada"),
        fila("M-07", "r_ficha", stats.pearsonr(x, y)[0], "con dos columnas el alfa es igual a r"),
        fila("M-07", "cci_ficha", icc_a1(x, y), "lo que corresponde a la ficha: acuerdo absoluto"),
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "verificacion_escenarios.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 120)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
