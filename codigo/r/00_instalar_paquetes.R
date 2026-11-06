# =============================================================================
# Instalador de paquetes de R para los análisis del libro.
#
# Uso, desde la raíz del proyecto:
#   source("06_Codigo/02_Analisis/R/00_instalar_paquetes.R")
#
# Solo instala lo que falta. Los casos centrales del libro (M-01, M-07, U-07,
# U-08, U-09) funcionan con R base; los paquetes de esta lista son para los
# datasets docentes y para quien quiera los mismos resultados con paquetes
# especializados.
# =============================================================================

necesarios <- c(
  "readxl",      # leer .xlsx
  "effectsize",  # d, d_z y sus intervalos
  "rstatix"      # A12 y pruebas con salida ordenada
)

cat("R", as.character(getRversion()), "en", R.version$platform, "\n\n")

faltan <- necesarios[!vapply(necesarios, requireNamespace, logical(1), quietly = TRUE)]

if (length(faltan) == 0) {
  cat("Todo instalado. No hay nada que hacer.\n")
} else {
  cat("Faltan:", paste(faltan, collapse = ", "), "\n")
  instalar <- readline("¿Los instalo ahora? (s/n): ")
  if (tolower(substr(instalar, 1, 1)) == "s") {
    install.packages(faltan, repos = "https://cloud.r-project.org")
  } else {
    cat("No se instaló nada. Los scripts de M-01, M-07 y de los casos técnicos\n",
        "funcionan igual, porque solo usan R base.\n", sep = "")
  }
}

cat("\nComprobación final:\n")
for (p in necesarios) {
  estado <- if (requireNamespace(p, quietly = TRUE)) "ok" else "FALTA"
  cat(sprintf("  %-12s %s\n", p, estado))
}

cat("\nMASS (binomial negativa) viene con R:",
    if (requireNamespace("MASS", quietly = TRUE)) "ok" else "FALTA", "\n")
