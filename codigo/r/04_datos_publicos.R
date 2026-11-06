# =============================================================================
# Caso con datos públicos: KC1 (NASA) — defectos por módulo y complejidad.
#
# Alternativa a los datos simulados: el archivo lo publica el repositorio PROMISE
# y se descarga directo. Mismo atributo que U-09, pero sobre código real.
#
# Fuente:  https://www.openml.org/d/1067  (PROMISE / NASA KC1, clase)
# Cita:    Koru, A. G. y Liu, H. (2005). An investigation of the effect of module
#          size on defect prediction using static measures. PROMISE Workshop, ICSE.
#
# Uso, desde la raíz del proyecto:
#   Rscript 06_Codigo/02_Analisis/R/04_datos_publicos.R
#
# Salidas: 06_Codigo/02_Analisis/R/resultados/publico_KC1.csv
#          06_Codigo/02_Analisis/R/resultados/publico_KC1.md
# =============================================================================

# La raíz del proyecto se busca hacia arriba: funciona igual desde RStudio (que abre
# la carpeta del script) que desde la consola con el directorio del proyecto.
raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "05_Datos")) && dir.exists(file.path(raiz, "03_Manuscritos"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro 05_Datos.")
  raiz <- padre
}
cat("raíz del proyecto:", raiz, "\n")

out <- file.path(raiz, "06_Codigo", "02_Analisis", "R", "resultados")
dir.create(out, showWarnings = FALSE, recursive = TRUE)

url <- "https://www.openml.org/data/download/53953/kc1-numeric.arff"

# 1) copia local, si existe; 2) descarga directa
local   <- file.path(raiz, "05_Datos", "05_Publicos", "kc1-numeric.arff")
destino <- if (file.exists(local)) local else file.path(tempdir(), "kc1.arff")

if (!file.exists(destino)) {
  cat("Descargando KC1 de OpenML...\n")
  dir.create(dirname(local), showWarnings = FALSE, recursive = TRUE)
  try(download.file(url, local, mode = "wb", quiet = TRUE), silent = TRUE)
  destino <- local
}

if (!file.exists(destino) || file.size(destino) < 10000) {
  stop("No se pudo obtener el conjunto. Comprueba la conexión y vuelve a intentarlo.\n",
       "Descarga manual: ", url, "\n",
       "y guarda el archivo como ", local, sep = "")
}

if (!requireNamespace("foreign", quietly = TRUE)) {
  stop("Falta el paquete foreign, que viene con R. Reinstala R si no está disponible.")
}
datos <- foreign::read.arff(destino)
cat("módulos:", nrow(datos), "| columnas:", ncol(datos), "\n")

# --- utilidades: los nombres de KC1 llevan prefijo (sum, avg, min, max) --------
buscar <- function(patrones) {
  nombres <- names(datos)
  for (p in patrones) {
    encontrado <- nombres[toupper(nombres) == toupper(p)]
    if (length(encontrado) == 1) return(encontrado)
  }
  for (p in patrones) {
    encontrado <- grep(p, nombres, ignore.case = TRUE, value = TRUE)
    if (length(encontrado) >= 1) return(encontrado[1])
  }
  NA_character_
}

col_tamano <- buscar(c("sumLOC_TOTAL", "LOC_TOTAL", "loc_total"))
col_cplx   <- buscar(c("sumCYCLOMATIC_COMPLEXITY", "CYCLOMATIC_COMPLEXITY", "cyclomatic"))
col_def    <- buscar(c("NUMDEFECTS", "NUM_DEFECTS", "defects"))

if (any(is.na(c(col_tamano, col_cplx, col_def)))) {
  cat("No se encontraron las columnas esperadas.\n")
  cat("Columnas del archivo:\n")
  print(names(datos))
  stop("Ajusta los nombres en el bloque 'buscar' del script.")
}

cat("columnas usadas:", col_tamano, "|", col_cplx, "|", col_def, "\n")

datos$tamano <- datos[[col_tamano]]
datos$cplx   <- datos[[col_cplx]]
datos$def    <- datos[[col_def]]

# --- el caso: densidad de defectos por mil líneas -----------------------------
datos <- subset(datos, tamano > 0 & !is.na(tamano))
datos$kloc     <- datos$tamano / 1000
datos$densidad <- datos$def / datos$kloc

cat("\nResumen de la muestra real\n")
cat("  módulos analizados:", nrow(datos), "\n")
cat("  módulos con al menos un defecto:", sum(datos$def > 0),
    "(", round(100 * mean(datos$def > 0), 1), "% )\n")
cat("  mediana de tamaño (KLOC):", round(median(datos$kloc), 2), "\n")
cat("  mediana de densidad (defectos/KLOC):", round(median(datos$densidad), 2), "\n")
cat("  mediana de complejidad ciclomática:", round(median(datos$cplx), 2), "\n")

rho <- suppressWarnings(cor(datos$densidad, datos$cplx, method = "spearman"))
cat("  Spearman densidad-complejidad:", round(rho, 3), "\n")

# --- comparación de módulos grandes frente a pequeños -------------------------
corte   <- median(datos$kloc)
grande  <- subset(datos, kloc >= corte)
pequeno <- subset(datos, kloc <  corte)
w <- wilcox.test(grande$densidad, pequeno$densidad, exact = FALSE)
a12 <- as.numeric(w$statistic) / (nrow(grande) * nrow(pequeno))

cat("  densidad en módulos grandes:", round(median(grande$densidad), 2),
    "| en pequeños:", round(median(pequeno$densidad), 2), "\n")
cat("  Mann-Whitney p =", format.pval(w$p.value, digits = 4), "| A12 =", round(a12, 3), "\n")

# --- salidas -----------------------------------------------------------------
write.csv(datos[, c("kloc", "cplx", "def", "densidad")],
          file.path(out, "publico_KC1.csv"), row.names = FALSE)

resumen <- c(
  "# KC1 · resultados de la corrida",
  "",
  paste0("- módulos analizados: ", nrow(datos)),
  paste0("- módulos con al menos un defecto: ", sum(datos$def > 0),
         " (", round(100 * mean(datos$def > 0), 1), " %)"),
  paste0("- mediana de tamaño: ", round(median(datos$kloc), 2), " KLOC"),
  paste0("- mediana de densidad: ", round(median(datos$densidad), 2), " defectos/KLOC"),
  paste0("- mediana de complejidad ciclomática: ", round(median(datos$cplx), 2)),
  paste0("- Spearman densidad-complejidad: ", round(rho, 3)),
  paste0("- densidad en módulos grandes: ", round(median(grande$densidad), 2),
         " | en pequeños: ", round(median(pequeno$densidad), 2)),
  paste0("- Mann-Whitney p = ", format.pval(w$p.value, digits = 4), " | A12 = ", round(a12, 3))
)
writeLines(resumen, file.path(out, "publico_KC1.md"))

cat("\nGuardado en", file.path(out, "publico_KC1.csv"), "\n")
cat(paste(resumen, collapse = "\n"), "\n")
