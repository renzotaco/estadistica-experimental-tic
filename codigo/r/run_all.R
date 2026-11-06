# =============================================================================
# Ejecuta todos los análisis de R del libro, en orden.
#
# Uso, desde la raíz del proyecto:
#   Rscript 06_Codigo/02_Analisis/R/run_all.R
#
# Si un script falla, se detiene y dice cuál: es preferible a seguir con un
# resultado incompleto.
# =============================================================================

raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "05_Datos"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro 05_Datos.")
  raiz <- padre
}
if (!dir.exists(file.path(raiz, "05_Datos", "01_Simulados"))) {
  stop("Ejecuta este script desde la raíz del proyecto: no encuentro 05_Datos/01_Simulados.")
}

scripts <- c(
  "06_Codigo/02_Analisis/analisis_M01.R",
  "06_Codigo/02_Analisis/analisis_M07.R",
  "06_Codigo/02_Analisis/R/03_casos_tecnicos.R",
  "06_Codigo/07_Datasets_Docentes/equivalente_R.R"
)

for (s in scripts) {
  ruta <- file.path(raiz, s)
  if (!file.exists(ruta)) {
    cat("AVISO: no existe", s, "\n")
    next
  }
  cat("\n==========", s, "==========\n")
  resultado <- try(source(ruta, echo = FALSE), silent = TRUE)
  if (inherits(resultado, "try-error")) {
    cat("FALLÓ:", s, "\n")
    cat(as.character(resultado), "\n")
    stop("Se detiene aquí para no dejar resultados a medias.")
  }
}

cat("\nTodos los análisis de R terminaron.\n")
cat("Compara las cifras con la tabla del README de esta carpeta.\n")
