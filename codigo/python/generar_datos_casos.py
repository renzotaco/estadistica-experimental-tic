"""Genera los datos simulados del banco de casos del libro.

Un escenario por caso (6 de uso correcto U-01..U-06, 6 con oportunidad de mejora
M-01..M-06). Todos los datos son sinteticos y reproducibles: semilla maestra
20261103 con un generador independiente por caso, de modo que agregar o quitar un
caso no altera los demas.

Salidas:
  05_Datos/01_Simulados/<CASO>/datos.csv
  05_Datos/01_Simulados/<CASO>/parametros.json
  05_Datos/05_Manifiestos/manifiesto_sha256.csv

Uso: python generar_datos_casos.py
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "05_Datos" / "01_Simulados"
MAN = ROOT / "05_Datos" / "05_Manifiestos"
MASTER_SEED = 20261103
SCENARIOS = ["U-01", "U-02", "U-03", "U-04", "U-05", "U-06",
             "M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]


# --------------------------------------------------------------------------- U
def u01(rng):
    """Dos instrumentos que registran la misma latencia (log del servidor vs APM)."""
    n = 60
    base = rng.lognormal(mean=6.2, sigma=0.55, size=n)          # ms, asimetrica
    log_srv = base * rng.normal(1.00, 0.02, n)
    apm = base * rng.normal(1.04, 0.03, n)                       # sesgo sistematico +4 %
    df = pd.DataFrame({
        "lote": [f"L-{i:03d}" for i in range(1, n + 1)],
        "latencia_log_ms": np.round(log_srv, 1),
        "latencia_apm_ms": np.round(apm, 1),
    })
    return df, {"escenario": "Dos instrumentos, misma magnitud; acuerdo absoluto",
                "n": n, "unidad": "lote de 100 peticiones HTTP",
                "analisis_correcto": "CCI(A,1) y limites de acuerdo de Bland-Altman",
                "error_que_previene": "usar r de Pearson o un alfa como prueba de acuerdo"}


def u02(rng):
    """A/B concurrente con linea basal; el analisis correcto es ANCOVA."""
    n = 120
    grupo = np.repeat(["A", "B"], n // 2)
    rng.shuffle(grupo)
    pre = rng.normal(520, 85, n)
    efecto = np.where(grupo == "B", -45.0, 0.0)
    tendencia = 12.0
    post = pre + efecto + tendencia + rng.normal(0, 40, n)
    df = pd.DataFrame({
        "sesion": [f"S-{i:04d}" for i in range(1, n + 1)],
        "grupo": grupo,
        "pre_ms": np.round(pre, 1),
        "post_ms": np.round(np.clip(post, 80, None), 1),
    })
    return df, {"escenario": "Asignacion aleatoria por sesion; dos grupos con pre y post",
                "n": n, "unidad": "sesion de compra",
                "efecto_verdadero_ms": -45.0, "tendencia_temporal_ms": 12.0,
                "analisis_correcto": "ANCOVA sobre el postest con la linea basal como covariable",
                "error_que_previene": "t sobre el postest o sobre la diferencia sin ajuste"}


def u03(rng):
    """Prueba de conocimiento con 20 items dicotomicos antes y despues."""
    n, k = 45, 20
    theta_pre = rng.normal(0, 1, n)
    theta_post = theta_pre + 0.9 + rng.normal(0, 0.35, n)
    dificultad = np.linspace(-1.6, 1.6, k)

    def items(theta):
        p = 1 / (1 + np.exp(-(theta[:, None] - dificultad[None, :])))
        return (rng.random((n, k)) < p).astype(int)

    pre_items, post_items = items(theta_pre), items(theta_post)
    df = pd.DataFrame({"participante": [f"P-{i:02d}" for i in range(1, n + 1)],
                       "pre_total": pre_items.sum(axis=1),
                       "post_total": post_items.sum(axis=1)})
    for j in range(k):
        df[f"i{j + 1:02d}"] = post_items[:, j]
    return df, {"escenario": "Pre-post de un solo grupo, puntaje 0-20, items dicotomicos",
                "n": n, "k_items": k, "unidad": "participante",
                "analisis_correcto": "KR-20 para el instrumento; d_z con IC; conclusion como diferencia observada",
                "error_que_previene": "alfa sobre items dicotomicos sin discutir KR-20; concluir causalidad"}


def u04(rng):
    """Usabilidad: SUS de 10 items mas eficiencia y eficacia por tarea."""
    n = 80
    grupo = np.repeat(["Interfaz_A", "Interfaz_B"], n // 2)
    rng.shuffle(grupo)
    mejora = np.where(grupo == "Interfaz_B", 0.55, 0.0)
    persona = rng.normal(0, 0.7, n)                    # variabilidad entre usuarios
    items = []
    for j in range(10):
        signo = 1.0 if j % 2 == 0 else -1.0            # polaridad alterna del SUS
        val = 3.2 + persona + signo * mejora + rng.normal(0, 0.45, n)
        items.append(np.clip(np.round(val), 1, 5).astype(int))
    items = np.column_stack(items)
    sus = (items[:, [0, 2, 4, 6, 8]] - 1).sum(axis=1) + (5 - items[:, [1, 3, 5, 7, 9]]).sum(axis=1)
    df = pd.DataFrame({"usuario": [f"U-{i:03d}" for i in range(1, n + 1)], "grupo": grupo})
    for j in range(10):
        df[f"sus_{j + 1:02d}"] = items[:, j]
    df["sus_puntaje"] = sus * 2.5
    df["tiempo_tarea_s"] = np.round(np.clip(
        np.where(grupo == "Interfaz_B", 42, 55) + rng.normal(0, 9, n), 12, None), 1)
    df["exito_tarea"] = (rng.random(n) < np.where(grupo == "Interfaz_B", 0.92, 0.78)).astype(int)
    return df, {"escenario": "Dos interfaces, grupos independientes; SUS y metricas de tarea",
                "n": n, "unidad": "participante",
                "analisis_correcto": "omega y estructura del SUS; Mann-Whitney con A12 e IC para tiempo",
                "error_que_previene": "presentar el alfa como prueba de validez del constructo"}


def u05(rng):
    """Incidentes por dia de servicio antes y despues de un cambio de plataforma."""
    dias = 90
    periodo = np.array(["antes"] * 45 + ["despues"] * 45)
    lam = np.where(periodo == "antes", 4.2, 2.6)
    incidentes = rng.poisson(lam)
    df = pd.DataFrame({"dia": np.arange(1, dias + 1), "periodo": periodo,
                       "incidentes": incidentes,
                       "exposicion_horas": np.round(rng.normal(24, 0.15, dias), 2)})
    return df, {"escenario": "Conteo de incidentes por dia-servicio; cambio de plataforma",
                "n": dias, "unidad": "dia de servicio",
                "analisis_correcto": "razon de tasas con IC (Poisson o binomial negativa)",
                "error_que_previene": "t de Student sobre conteos o sobre porcentajes"}


def u06(rng):
    """Benchmark con calentamiento y ejecuciones repetidas."""
    rep = 100
    variante = np.repeat(["v1_legacy", "v2_optimizada"], rep)
    ejecucion = np.tile(np.arange(1, rep + 1), 2)
    warmup = (ejecucion <= 20).astype(int)
    escala = np.where(variante == "v2_optimizada", 0.75, 1.0)
    base = rng.lognormal(mean=5.0, sigma=0.30, size=2 * rep) * escala
    penal = np.where(warmup == 1, 1.6, 1.0)
    df = pd.DataFrame({"variante": variante, "ejecucion": ejecucion, "warmup": warmup,
                       "latencia_ms": np.round(base * penal, 2)})
    return df, {"escenario": "Dos implementaciones, 100 ejecuciones alternadas por variante",
                "n": 2 * rep, "unidad": "ejecucion del metodo",
                "descartar": "primeras 20 ejecuciones (calentamiento)",
                "analisis_correcto": "mediana y p95 con IC bootstrap; A12 de Vargha-Delaney",
                "error_que_previene": "media de cinco corridas y t de Student sobre todas las ejecuciones"}


# --------------------------------------------------------------------------- M
def m01(rng):
    """Ficha de registro con retest que registra 20 % mas."""
    n = 30
    t1 = np.round(np.clip(rng.normal(12, 3.2, n), 2, None), 2)
    t2 = np.round(t1 * rng.normal(1.20, 0.02, n), 2)              # sesgo sistematico
    df = pd.DataFrame({"ficha": [f"F-{i:02d}" for i in range(1, n + 1)],
                       "t1_min": t1, "t2_min": t2})
    return df, {"escenario": "Retest con sesgo del 20 % sobre una ficha de registro",
                "n": n, "unidad": "expediente",
                "error": "r y alfa >= 0,95 presentados como confiabilidad",
                "correccion": "CCI(A,1) y limites de acuerdo de Bland-Altman"}


def m02(rng):
    """Pre-post de un solo grupo sobre una serie con tendencia y efecto nulo."""
    dias = 24
    fase = np.array(["pre"] * 12 + ["post"] * 12)
    tiempo = np.arange(1, dias + 1)
    indicador = 48 + 2.0 * tiempo + rng.normal(0, 3.0, dias)      # efecto del cambio = 0
    df = pd.DataFrame({"dia": tiempo, "fase": fase,
                       "indicador_horas": np.round(indicador, 2)})
    return df, {"escenario": "Pre-post de un solo grupo con tendencia temporal de 2 h/dia",
                "n": dias, "unidad": "dia",
                "efecto_verdadero": 0.0, "tendencia_por_dia": 2.0,
                "error": "t pareada que atribuye la tendencia al artefacto",
                "correccion": "comparador concurrente con ANCOVA o serie temporal interrumpida"}


def m03(rng):
    """Muestra enorme, efecto trivial, p minusculo."""
    n = 5000
    grupo = np.repeat(["control", "tratamiento"], n // 2)
    efecto = np.where(grupo == "tratamiento", -25.0, 0.0)         # 25 ms sobre DE 160
    lat = rng.normal(480, 160, n) + efecto
    df = pd.DataFrame({"solicitud": [f"R-{i:05d}" for i in range(1, n + 1)],
                       "grupo": grupo, "latencia_ms": np.round(np.clip(lat, 30, None), 1)})
    return df, {"escenario": "Dos grupos independientes, n grande, efecto de 25 ms",
                "n": n, "unidad": "solicitud",
                "error": "informar p < 0,001 como prueba de mejora relevante",
                "correccion": "diferencia en ms con IC y d de Cohen con IC"}


def m04(rng):
    """Dos grupos no aleatorizados con desbalance basal de 0,6 DE."""
    n = 100
    grupo = np.repeat(["control", "piloto"], n // 2)
    pre = rng.normal(50, 10, n) + np.where(grupo == "piloto", 7.2, 0.0)
    efecto = np.where(grupo == "piloto", 5.0, 0.0)
    post = pre + efecto + rng.normal(0, 4, n)
    df = pd.DataFrame({"empleado": [f"E-{i:03d}" for i in range(1, n + 1)],
                       "grupo": grupo, "pre_puntaje": np.round(pre, 1),
                       "post_puntaje": np.round(post, 1)})
    return df, {"escenario": "Grupos intactos con desbalance basal de 0,6 DE",
                "n": n, "unidad": "empleado",
                "efecto_verdadero": 5.0, "desbalance_de": 0.6,
                "error": "t sobre el postest que atribuye al piloto la diferencia inicial",
                "correccion": "ANCOVA con la linea basal como covariable"}


def m05(rng):
    """Pseudorreplicacion: 10 camiones, 525 despachos cada uno."""
    camiones = [f"C-{i:02d}" for i in range(1, 11)]
    grupo = {c: ("control" if i < 5 else "tratamiento") for i, c in enumerate(camiones)}
    efecto_camion = rng.normal(0, 4, 10)
    filas = []
    for i, c in enumerate(camiones):
        base = 62 + efecto_camion[i] + (-7 if grupo[c] == "tratamiento" else 0)
        tiempos = np.round(np.clip(rng.normal(base, 6, 525), 8, None), 1)
        filas.append(pd.DataFrame({"camion": c, "grupo": grupo[c],
                                   "despacho": np.arange(1, 526), "tiempo_carga_min": tiempos}))
    df = pd.concat(filas, ignore_index=True)
    return df, {"escenario": "10 camiones y 525 despachos por camion",
                "n": len(df), "unidad_experimental": "camion (10)",
                "unidad_observacion": "despacho (5250)",
                "error": "t con n = 5250: pseudorreplicacion",
                "correccion": "agregar por camion o modelo mixto con intercepto por camion"}


def m06(rng):
    """Cuestionario de 'calidad de software' frente a la medicion tecnica del mismo artefacto."""
    usuarios, modulos = 180, 12
    mod = np.array([f"MOD-{i:02d}" for i in range(1, modulos + 1)])
    calidad_tecnica = rng.normal(0, 1, modulos)                   # defectos, cobertura
    asignado = rng.integers(0, modulos, usuarios)
    persona = rng.normal(0, 0.8, usuarios)                        # sesgo de respuesta
    items = []
    for j in range(10):
        base = 3.1 + persona + 0.30 * calidad_tecnica[asignado] + rng.normal(0, 0.35, usuarios)
        items.append(np.clip(np.round(base), 1, 5).astype(int))
    items = np.column_stack(items)
    df = pd.DataFrame({"usuario": [f"US-{i:03d}" for i in range(1, usuarios + 1)],
                       "modulo": mod[asignado]})
    for j in range(10):
        df[f"cal{j + 1:02d}"] = items[:, j]
    tecnico = pd.DataFrame({"modulo": mod,
                            "defectos_por_kloc": np.round(8 * np.exp(-calidad_tecnica), 2),
                            "cobertura_pct": np.round(np.clip(70 + 8 * calidad_tecnica, 40, 98), 1)})
    return {"datos.csv": df, "datos_modulos.csv": tecnico}, {
        "escenario": "Percepcion de calidad (Likert) frente a medida tecnica del mismo modulo",
        "n_usuarios": usuarios, "n_modulos": modulos,
        "unidad": "usuario para la percepcion; modulo para el atributo tecnico",
        "error": "presentar el cuestionario como medida de la calidad tecnica del software",
        "correccion": "ISO/IEC 25023 para el atributo; el cuestionario mide percepcion",
        "archivos": ["datos.csv", "datos_modulos.csv"]}


def m07(rng):
    """El mismo coeficiente aplicado a tres datos distintos: escala, prueba y ficha."""
    # (a) escala multi-item de un constructo: 12 items Likert, 60 sujetos
    n_lik, k_lik = 60, 12
    theta = rng.normal(0, 1, n_lik)
    likert = np.column_stack([
        np.clip(np.round(3 + 0.75 * theta + rng.normal(0, 0.75, n_lik)), 1, 5)
        for _ in range(k_lik)])
    df_lik = pd.DataFrame({"sujeto": [f"S-{i:02d}" for i in range(1, n_lik + 1)]})
    for j in range(k_lik):
        df_lik[f"item_{j + 1:02d}"] = likert[:, j]

    # (b) prueba de conocimiento: 20 items dicotomicos, 45 estudiantes
    n_kt, k_kt = 45, 20
    theta_kt = rng.normal(0, 1, n_kt)
    dificultad = np.linspace(-1.5, 1.5, k_kt)
    p = 1 / (1 + np.exp(-(theta_kt[:, None] - dificultad[None, :])))
    test = (rng.random((n_kt, k_kt)) < p).astype(int)
    df_test = pd.DataFrame({"estudiante": [f"E-{i:02d}" for i in range(1, n_kt + 1)]})
    for j in range(k_kt):
        df_test[f"reactivo_{j + 1:02d}"] = test[:, j]

    # (c) ficha de registro medida dos veces: dos columnas, 30 fichas
    n_f, k_f = 30, 2

    def ficha():
        t1 = np.round(np.clip(rng.normal(12, 3.2, n_f), 2, None), 2)
        t2 = np.round(t1 * rng.normal(1.15, 0.02, n_f), 2)    # sesgo sistematico del 15 %
        return pd.DataFrame({"ficha": [f"F-{i:02d}" for i in range(1, n_f + 1)],
                             "t1_min": t1, "t2_min": t2})

    return {"datos_likert.csv": df_lik, "datos_test.csv": df_test,
            "datos_ficha.csv": ficha()}, {
        "escenario": "Tres naturalezas de dato con el mismo coeficiente aplicado",
        "n_likert": n_lik, "k_likert": k_lik,
        "n_prueba": n_kt, "k_prueba": k_kt, "n_ficha": n_f, "k_ficha": k_f,
        "unidad": "sujeto (a); estudiante (b); ficha (c)",
        "error": "informar alfa de Cronbach como certificado unico de los tres instrumentos",
        "correccion": "alfa u omega con estructura para (a); KR-20 para (b); CCI(A,1) y Bland-Altman para (c)",
        "archivos": ["datos_likert.csv", "datos_test.csv", "datos_ficha.csv"]}


GENERADORES = {"U-01": u01, "U-02": u02, "U-03": u03, "U-04": u04, "U-05": u05,
               "U-06": u06, "M-01": m01, "M-02": m02, "M-03": m03, "M-04": m04,
               "M-05": m05, "M-06": m06, "M-07": m07}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    seeds = np.random.SeedSequence(MASTER_SEED).spawn(len(SCENARIOS))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    filas = []
    for nombre, seq in zip(SCENARIOS, seeds):
        rng = np.random.default_rng(seq)
        salida, meta = GENERADORES[nombre](rng)
        tablas = {"datos.csv": salida} if isinstance(salida, pd.DataFrame) else salida
        principal = next(iter(tablas.values()))
        carpeta = OUT / nombre
        carpeta.mkdir(parents=True, exist_ok=True)
        for archivo, tabla in tablas.items():
            ruta = carpeta / archivo
            tabla.to_csv(ruta, index=False, encoding="utf-8")
            filas.append({"escenario": nombre, "archivo": f"01_Simulados/{nombre}/{archivo}",
                          "sha256": sha256(ruta), "bytes": ruta.stat().st_size,
                          "filas": len(tabla), "columnas": tabla.shape[1], "fecha_utc": stamp})
        meta.update({"caso": nombre, "semilla_maestra": MASTER_SEED,
                     "generador": "generar_datos_casos.py",
                     "archivos": list(tablas),
                     "filas": int(len(principal)), "columnas": int(principal.shape[1]),
                     "fecha_utc": stamp,
                     "declaracion": "Datos sinteticos; no reproducen ninguna tesis del corpus."})
        (carpeta / "parametros.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{nombre}: " + ", ".join(f"{a} {t.shape[0]}x{t.shape[1]}" for a, t in tablas.items()))

    MAN.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(MAN / "manifiesto_sha256.csv", index=False, encoding="utf-8")
    print(f"\nManifiesto: {MAN / 'manifiesto_sha256.csv'} ({len(filas)} archivos)")


if __name__ == "__main__":
    main()
