# Contexto del proyecto

Repositorio complementario del libro **Estadística experimental para TIC**, del **Cuaderno de ejercicios** y del
**Solucionario para el docente**.

- **Autor:** Dr. Renzo Alberto Taco Coayla — Universidad Privada de Tacna · rentaco@upt.pe ·
  [ORCID 0000-0003-0014-7216](https://orcid.org/0000-0003-0014-7216)
- **Repositorio:** https://github.com/renzotaco/estadistica-experimental-tic
- **Sitio (GitHub Pages, rama `main`, carpeta `/docs`):** https://renzotaco.github.io/estadistica-experimental-tic/
- **Licencia:** CC BY-NC-SA 4.0

## Propósito

Permitir que cualquier lector o revisor reproduzca cada cifra del libro. Toda cifra tiene tres referencias:
el **caso**, el **script** y el **archivo de datos**.

## Estructura

```
codigo/
  python/            análisis de los casos y generadores de datos (10 scripts)
  python/resultados/ salidas de M-01 y M-07 (ignorada por git)
  r/                 los mismos análisis en R (run_all.R los ejecuta en orden)
  r/resultados/      salidas en R (ignorada por git)
dataset/
  01_Simulados/      16 escenarios (U-01…U-09, M-01…M-07): datos.csv + parametros.json
  04_Docentes/       cinco conjuntos para enseñar (xlsx)
  05_Publicos/       KC1 (NASA), el caso U-10 con datos reales
  05_Manifiestos/    SHA-256 de cada archivo simulado y verificación de escenarios
docs/
  index.html         portada del sitio
  caso.html          plantilla única de caso (caso.html?id=U-01)
  assets/casos.js    datos de los 17 casos y 16 unidades; genera ambas páginas
  assets/estilos.css diseño (tokens, modo oscuro, responsive)
  assets/autor.jpg   foto del autor (160×160)
```

## Conceptos del libro reflejados en el sitio

- **Ruta M–D–A–I:** medición, diseño, análisis, interpretación.
- **Techo de la conclusión:** `L* = min(LM, LD, LA)`; cinco niveles, cada uno con su verbo permitido.
  En la calculadora, un análisis de nivel 4 se limita a 3 si el diseño es menor que 4.
- **Familias de casos:** **U** (uso correcto) y **M** (oportunidad de mejora); U-10 usa datos públicos.

## Convenciones técnicas

- Los scripts localizan la raíz con `pathlib.Path(__file__).resolve().parents[2]` (Python) y rutas relativas
  a `dataset/` y `codigo/` (R). No hay rutas absolutas.
- Datos simulados con semilla **20261103**; los generadores son deterministas.
  Al regenerar, solo cambian BOM, fin de línea y `fecha_utc`; no se suben esos cambios.
- Enlaces del sitio a archivos: `github.com/<repo>/blob/main/<ruta>` para ver y
  `raw.githubusercontent.com/<repo>/main/<ruta>` para descargar. Los enlaces externos abren en pestaña nueva.
- Sitio estático sin framework ni compilación; fuentes de Google (Inter, Source Serif 4, JetBrains Mono).
- Entorno probado: Python 3.12.10 y R 4.6.0 en Windows 11.

## Cifras de control (deben reproducirse)

| Caso | Script | Resultado |
|---|---|---|
| M-01 | `acuerdo_U01_M01.py` / `analisis_M01.*` | CCI 0.742 |
| M-07 | `analisis_M07.*` | 0.914 / 0.715 / 0.900 |
| U-04 | `indicadores_U03_U04_U05.py` | SUS 50.0 vs 62.5, A12 0.013; tiempo A12 0.892, p 1.6e-9 |
| U-10 | `04_datos_publicos.R` | KC1 A12 0.668 |

## Reparto de responsabilidades

- El texto del libro, el cuaderno y el solucionario los corrige el autor.
- Este repositorio mantiene código, datos y sitio coherentes con esos textos.

## Pendientes conocidos

- Algunos scripts muestran tildes mal codificadas en la consola de Windows (cp1252); es solo visual.
