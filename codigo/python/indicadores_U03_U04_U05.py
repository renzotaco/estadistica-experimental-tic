"""Calcula los indicadores de U-03, U-04 y U-05 para sus fichas."""

import pathlib

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = pathlib.Path(r"C:\Download\downpdfs\ARTICLES\Libro_Tesis_TIC")
BASE = RAIZ / "05_Datos" / "01_Simulados"
rng = np.random.default_rng(20261103)


def u03() -> None:
    d = pd.read_csv(BASE / "U-03" / "datos.csv")
    items = [c for c in d.columns if c.startswith("i")]
    k = len(items)
    p = d[items].mean()
    vt = d[items].sum(axis=1).var(ddof=1)
    kr20 = k / (k - 1) * (1 - (p * (1 - p)).sum() / vt)
    dif = d.post_total - d.pre_total
    t = stats.ttest_rel(d.post_total, d.pre_total)
    dz = dif.mean() / dif.std(ddof=1)
    boot = [np.mean(rng.choice(dif, len(dif))) for _ in range(5000)]
    ic = np.percentile(boot, [2.5, 97.5])
    print("=== U-03")
    print(f"  n = {len(d)} · ítems dicotómicos = {k}")
    print(f"  pre {d.pre_total.mean():.2f} · post {d.post_total.mean():.2f} (sobre {k})")
    print(f"  KR-20 = {kr20:.3f}")
    print(f"  diferencia = {dif.mean():.2f} [{ic[0]:.2f}; {ic[1]:.2f}] · t({len(d)-1}) = {t.statistic:.2f} · p = {t.pvalue:.2e}")
    print(f"  d_z = {dz:.2f}")


def u04() -> None:
    d = pd.read_csv(BASE / "U-04" / "datos.csv")
    sus = [c for c in d.columns if c.startswith("sus")]
    puntaje = d[sus].mean(axis=1) * 20  # escala SUS 0-100
    d = d.assign(sus_total=puntaje)
    a, b = sorted(d.grupo.unique())
    x = d.loc[d.grupo == a, "sus_total"].to_numpy()
    y = d.loc[d.grupo == b, "sus_total"].to_numpy()
    u = stats.mannwhitneyu(x, y, alternative="two-sided")
    a12 = u.statistic / (len(x) * len(y))
    print("=== U-04")
    print(f"  n = {len(d)} ({a}: {len(x)} · {b}: {len(y)})")
    print(f"  SUS mediana {a} = {np.median(x):.1f} · {b} = {np.median(y):.1f}")
    print(f"  Mann-Whitney p = {u.pvalue:.4f} · A12 = {a12:.3f}")
    if "tiempo_tarea_seg" in d.columns:
        t1 = d.loc[d.grupo == a, "tiempo_tarea_seg"].to_numpy()
        t2 = d.loc[d.grupo == b, "tiempo_tarea_seg"].to_numpy()
        u2 = stats.mannwhitneyu(t1, t2, alternative="two-sided")
        print(f"  tiempo de tarea: mediana {np.median(t1):.0f} vs {np.median(t2):.0f} s · "
              f"A12 = {u2.statistic/(len(t1)*len(t2)):.3f} · p = {u2.pvalue:.2e}")
    else:
        print("  columnas:", [c for c in d.columns if not c.startswith("sus")])


def u05() -> None:
    d = pd.read_csv(BASE / "U-05" / "datos.csv")
    print("=== U-05")
    res = d.groupby("periodo").agg(dias=("incidentes", "size"), incidentes=("incidentes", "sum"),
                                   horas=("exposicion_horas", "sum"))
    print(res.to_string())
    a = d[d.periodo == sorted(d.periodo.unique())[0]]
    b = d[d.periodo == sorted(d.periodo.unique())[1]]
    tasa_a = a.incidentes.sum() / a.exposicion_horas.sum()
    tasa_b = b.incidentes.sum() / b.exposicion_horas.sum()
    rr = tasa_b / tasa_a
    se = np.sqrt(1 / a.incidentes.sum() + 1 / b.incidentes.sum())
    ic = (np.exp(np.log(rr) - 1.96 * se), np.exp(np.log(rr) + 1.96 * se))
    print(f"  tasas por 100 h: {100*tasa_a:.2f} → {100*tasa_b:.2f}")
    print(f"  RR = {rr:.3f} · IC 95 % [{ic[0]:.3f}; {ic[1]:.3f}]")


if __name__ == "__main__":
    u03()
    u04()
    u05()
