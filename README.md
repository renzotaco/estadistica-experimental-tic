# Estadística experimental para TIC — código y datos

Repositorio del libro **Estadística experimental para TIC**, del **Cuaderno de ejercicios** y del
**Solucionario para el docente**. Contiene lo mínimo para reproducir cada cifra: los análisis en Python y en
R, los generadores y los datos.

**Licencia:** CC BY-NC-SA 4.0 · **Autor:** [ORCID 0000-0003-0014-7216](https://orcid.org/0000-0003-0014-7216)

---

## Estructura

```
codigo/
  python/   análisis de los casos y generadores de datos
  r/        los mismos análisis en R
dataset/
  01_Simulados/   16 escenarios, con datos.csv y parametros.json
  04_Docentes/    cinco conjuntos para enseñar (xlsx)
  05_Publicos/    KC1 (NASA), el caso con datos reales
  05_Manifiestos/ SHA-256 de cada archivo simulado
```

## Cómo se reproduce una cifra

Toda cifra del libro tiene tres referencias: el caso, el script y el archivo de datos.

```bash
# la verificación maestra reproduce las cifras de los 13 escenarios simulados
python codigo/python/verificar_escenarios.py

# y los análisis específicos
python codigo/python/acuerdo_U01_M01.py          # U-01 y M-01
python codigo/python/indicadores_U03_U04_U05.py  # U-03, U-04 y U-05
python codigo/python/analisis_U07.py             # U-07, U-08, U-09
```

## Cómo se regeneran los datos

```bash
python codigo/python/generar_datos_casos.py
python codigo/python/generar_casos_tecnicos.py
python codigo/python/verificar_escenarios.py     # comprueba contra el manifiesto SHA-256
```

## R

```bash
Rscript codigo/r/analisis_M01.R
Rscript codigo/r/analisis_M07.R
Rscript codigo/r/03_casos_tecnicos.R
Rscript codigo/r/run_all.R
```

Solo dos guiones necesitan paquetes (`readxl`, `effectsize`, `rstatix`); los demás son R base. Para
instalarlos:

```r
source("codigo/r/00_instalar_paquetes.R")
```

El caso con datos reales se descarga solo:

```bash
Rscript codigo/r/04_datos_publicos.R
```

## Datos

**Los escenarios son sintéticos.** Se generan con la semilla 20261103 y reproducen patrones documentados en
un corpus de 124 tesis, no organizaciones reales. Cada carpeta de caso declara sus parámetros y su semilla.

**El caso con datos reales** usa KC1 del repositorio PROMISE: 145 clases de un producto de la NASA. Se cita
a Koru y Liu (2005).

No hay datos personales en este repositorio.

## Cómo se cita

> Taco Coayla, R. A. (2026). *Estadística experimental para TIC: código y datos* [software]. CC BY-NC-SA 4.0.


