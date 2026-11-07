# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Sin publicar]

### Añadido
- `PROJECT_CONTEXT.md` con el propósito, la estructura, las convenciones y las cifras de control.
- `CHANGELOG.md` con el historial del proyecto.

## 2026-11-06

### `be53a63` — docs: autor con foto y correo; enlaces externos en nueva pestaña
- Bloque del autor bajo el título de la portada: foto redonda (`docs/assets/autor.jpg`, 160×160),
  nombre, Universidad Privada de Tacna, correo y ORCID.
- Correo del autor en el pie de `index.html` y `caso.html`.
- Los enlaces externos (repositorio, ORCID, Ver y Descargar archivos) abren en pestaña nueva
  con `target="_blank" rel="noopener"`.
- Estilos `.autor` en `estilos.css`.

### `6329599` — fix: rutas de los scripts al repositorio (dataset/ y codigo/)
- Los 17 scripts de Python y R usan `dataset/` y `codigo/` en lugar de `05_Datos/` y `06_Codigo/`.
- Se eliminan las rutas absolutas (`C:\...\Libro_Tesis_TIC`) de `acuerdo_U01_M01.py` e
  `indicadores_U03_U04_U05.py`; la raíz se calcula desde la ubicación del script.
- Las salidas de M-01 y M-07 van a `codigo/python/resultados/` y `codigo/r/resultados/`
  (ignoradas en `.gitignore`).
- `04_datos_publicos.R` ya no exige la carpeta `03_Manuscritos`; `run_all.R` con rutas nuevas.
- `indicadores_U03_U04_U05.py`:
  - salida forzada a UTF-8 (fallaba con `UnicodeEncodeError` en la consola de Windows);
  - U-04 usa `sus_puntaje` (ya en escala 0–100) y la columna `tiempo_tarea_s`.
    Antes daba SUS 146.4 vs 169.1; ahora reproduce el libro (50.0 vs 62.5).
- Verificado: los 10 scripts de Python, `run_all.R` y `04_datos_publicos.R` reproducen las cifras del libro.

### `27af839` — docs: sitio por casos y unidades con enlaces a datos y código
- Nuevo sitio para el revisor en `docs/`:
  - portada con ruta M–D–A–I, calculadora del techo `L*`, cuadrícula de casos con filtro y búsqueda,
    tabla de unidades del cuaderno, volúmenes e instrucciones para reproducir;
  - `caso.html?id=…`: escena, cifras, frase de conclusión permitida y no permitida, archivos de datos
    y código (Python, R, generador), techo por dimensión, capítulos y fuentes, navegación anterior/siguiente.
- `assets/casos.js` concentra los 17 casos y las 16 unidades; se comprobaron los 50 enlaces a archivos.
- Se retiran del sitio las referencias a `05_Datos/` y `06_Codigo/`.

### `f339d97` — feat: código y datasets
- Se suben los scripts de Python y R y los datos (simulados, docentes, públicos y manifiestos).

### `a7076e7` — feat: estructura inicial de datos, código y sitio web docs
- Estructura de carpetas y `.gitignore` (`__pycache__/`, `*.pyc`, `.venv/`, `.Rhistory`, `.RData`, `.DS_Store`).

### `f0e97a2` — Initial commit
- Creación del repositorio.
