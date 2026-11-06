"""Genera los datos simulados de U-07, U-08 y U-09.

Los parámetros están calibrados para ser plausibles en una institución peruana de tamaño medio:
cobertura de controles propia de un SGSI en implantación, tiempos de mesa de ayuda de un servicio
con ITIL y densidad de defectos de un producto mantenido. No provienen de ninguna organización real.

Salidas: 05_Datos/01_Simulados/{U-07,U-08,U-09}/datos.csv y parametros.json
"""

from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BASE = RAIZ / "05_Datos" / "01_Simulados"
SEMILLA = 20261103


def guardar(escenario: str, datos: pd.DataFrame, parametros: dict) -> None:
    destino = BASE / escenario
    destino.mkdir(parents=True, exist_ok=True)
    datos.to_csv(destino / "datos.csv", index=False, encoding="utf-8")
    (destino / "parametros.json").write_text(
        json.dumps(parametros, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{escenario}: {len(datos)} filas · {datos.shape[1]} columnas")


def u07(rng: np.random.Generator) -> None:
    """Cobertura del anexo A de ISO/IEC 27001:2022 antes y después de implantar el SGSI."""
    temas = {"Organizacional": 37, "Personas": 8, "Físico": 14, "Tecnológico": 34}
    antes = {"Organizacional": 0.30, "Personas": 0.45, "Físico": 0.35, "Tecnológico": 0.40}
    despues = {"Organizacional": 0.76, "Personas": 0.82, "Físico": 0.71, "Tecnológico": 0.79}

    filas = []
    numero = 1
    for tema, cantidad in temas.items():
        for _ in range(cantidad):
            filas.append({
                "control_id": f"A.{numero:02d}",
                "tema": tema,
                "implementado_antes": int(rng.random() < antes[tema]),
                "implementado_despues": int(rng.random() < despues[tema]),
            })
            numero += 1
    datos = pd.DataFrame(filas)
    guardar("U-07", datos, {
        "instrumento": "ISO/IEC 27001:2022, anexo A (93 controles en cuatro temas)",
        "unidad_experimental": "control del anexo A",
        "diseno": "dos auditorías sobre los mismos controles",
        "prueba_correcta": "McNemar para controles pareados; proporción con intervalo de Wilson",
        "calibracion": "cobertura inicial baja y final alta, compatible con un SGSI en implantación",
        "semilla": SEMILLA,
        "nota": "datos simulados; no corresponden a una organización real",
    })


def u08(rng: np.random.Generator) -> None:
    """Mesa de ayuda: 24 semanas, cambio de plataforma en la semana 13."""
    semanas = np.arange(1, 25)
    antes = semanas <= 12
    hora_base = np.where(antes, 48.0, 29.0)
    # tendencia leve y ruido multiplicativo
    tendencia = 1 - 0.006 * (semanas - 1)
    mediana = hora_base * tendencia * rng.lognormal(0, 0.08, semanas.size)
    tickets = rng.poisson(np.where(antes, 182, 176)).astype(int)
    fcr = np.where(antes, 0.42, 0.58) + rng.normal(0, 0.035, semanas.size)
    fcr = np.clip(fcr, 0.2, 0.85)
    resueltos = np.round(tickets * fcr).astype(int)

    datos = pd.DataFrame({
        "semana": semanas,
        "periodo": np.where(antes, "antes", "despues"),
        "tickets_abiertos": tickets,
        "resueltos_primer_contacto": resueltos,
        "tiempo_mediano_h": np.round(mediana, 1),
    })
    guardar("U-08", datos, {
        "instrumento": "registros de la herramienta de tickets (ITIL 4, ISO/IEC 20000-1)",
        "unidad_experimental": "semana de servicio",
        "diseno": "serie temporal interrumpida con 12 semanas antes y 12 después",
        "prueba_correcta": "regresión segmentada para el nivel y la pendiente; binomial negativa para conteos",
        "calibracion": "mediana de 48 h antes y 29 h después; resolución al primer contacto de 0,42 a 0,58",
        "semilla": SEMILLA,
        "nota": "datos simulados; no corresponden a una organización real",
    })


def u09(rng: np.random.Generator) -> None:
    """Densidad de defectos por KLOC y complejidad en dos versiones del mismo producto."""
    modulos = [f"MOD-{i:03d}" for i in range(1, 61)]
    filas = []
    for version, media_def, media_cx in (("v1", 4.3, 12.4), ("v2", 2.9, 9.2)):
        for modulo in modulos:
            kloc = float(np.round(rng.uniform(0.8, 6.5), 2))
            complejidad = float(np.round(max(3, rng.normal(media_cx, 2.6)), 1))
            # mas complejidad, mas defectos; densidad con cola larga
            esperados = kloc * media_def * (complejidad / media_cx)
            defectos = int(rng.poisson(max(esperados, 0.05)))
            filas.append({
                "version": version,
                "modulo": modulo,
                "kloc": kloc,
                "complejidad_ciclomatica": complejidad,
                "defectos": defectos,
                "densidad_defectos_kloc": round(defectos / kloc, 2),
            })
    datos = pd.DataFrame(filas)
    guardar("U-09", datos, {
        "instrumento": "ISO/IEC 25010:2023 (mantenibilidad) e ISO/IEC 25023:2016 (medidas)",
        "unidad_experimental": "módulo de software",
        "diseno": "dos versiones del mismo producto, mismos módulos",
        "prueba_correcta": "Mann-Whitney para densidad (cola larga) con A12 e intervalo bootstrap",
        "calibracion": "densidad media de 4,3 a 2,9 defectos por KLOC y complejidad de 12,4 a 9,2",
        "semilla": SEMILLA,
        "nota": "datos simulados; no corresponden a un producto real",
    })


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    u07(rng)
    u08(rng)
    u09(rng)


if __name__ == "__main__":
    main()
