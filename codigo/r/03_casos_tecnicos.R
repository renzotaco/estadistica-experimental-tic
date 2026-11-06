# =============================================================================
# Casos técnicos del libro: U-07 (McNemar), U-08 (serie temporal) y U-09
# (Mann-Whitney con A12). Equivalente en R de los scripts de Python.
#
# Uso, desde la raíz del proyecto:
#   Rscript 06_Codigo/02_Analisis/R/03_casos_tecnicos.R
#
# Salidas: 06_Codigo/02_Analisis/R/resultados/*.md y *.csv
# Solo base R, salvo MASS::glm.nb para la binomial negativa (viene con R).
# =============================================================================

raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "05_Datos"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro 05_Datos.")
  raiz <- padre
}
sim  <- file.path(raiz, "05_Datos", "01_Simulados")
out  <- file.path(raiz, "06_Codigo", "02_Analisis", "R", "resultados")
dir.create(out, showWarnings = FALSE, recursive = TRUE)

set.seed(20261103)

# --- utilidades --------------------------------------------------------------

coma <- function(x, dec = 2) {
  formatC(x, format = "f", digits = dec, decimal.mark = ",")
}

p_txt <- function(p) {
  if (is.na(p)) return("p = NA")
  if (p < 0.001) "p < 0,001" else paste("p =", coma(p, 4))
}

# intervalo de Wilson para una proporcion
wilson <- function(exitos, total) {
  z <- qnorm(0.975)
  p <- exitos / total
  centro <- (p + z^2 / (2 * total)) / (1 + z^2 / total)
  mitad <- z * sqrt(p * (1 - p) / total + z^2 / (4 * total^2)) / (1 + z^2 / total)
  c(centro - mitad, centro + mitad)
}

escribir <- function(nombre, lineas) {
  ruta <- file.path(out, nombre)
  writeLines(lineas, ruta, useBytes = TRUE)
  cat(paste(lineas, collapse = "\n"), "\n\n")
}

# =============================================================================
# U-07 · Controles del anexo A antes y despues del SGSI
# =============================================================================
u07 <- read.csv(file.path(sim, "U-07", "datos.csv"), check.names = FALSE)

antes   <- sum(u07$implementado_antes)
despues <- sum(u07$implementado_despues)
n       <- nrow(u07)
ic_a    <- wilson(antes, n) * 100
ic_d    <- wilson(despues, n) * 100

tabla <- table(u07$implementado_antes, u07$implementado_despues)
mcn   <- mcnemar.test(tabla, correct = FALSE)

lineas_u07 <- c(
  "# U-07 · cobertura del anexo A",
  "",
  paste0("- controles = ", n),
  paste0("- antes: ", antes, " implementados = ", coma(100 * antes / n, 1), " % [",
         coma(ic_a[1], 1), "; ", coma(ic_a[2], 1), "]"),
  paste0("- despues: ", despues, " implementados = ", coma(100 * despues / n, 1), " % [",
         coma(ic_d[1], 1), "; ", coma(ic_d[2], 1), "]"),
  paste0("- diferencia = ", coma(100 * (despues - antes) / n, 1), " puntos porcentuales"),
  paste0("- McNemar chi2 = ", coma(mcn$statistic, 2), " · ", p_txt(mcn$p.value)),
  paste0("- controles ganados = ", tabla[1, 2], " · perdidos = ", tabla[2, 1])
)
escribir("U-07_cobertura.md", lineas_u07)

# =============================================================================
# U-08 · Mesa de ayuda: serie temporal interrumpida
# =============================================================================
u08 <- read.csv(file.path(sim, "U-08", "datos.csv"), check.names = FALSE)
u08$despues <- as.integer(u08$periodo == "despues")
u08$semana_desde_cambio <- ifelse(u08$despues == 1, u08$semana - 12, 0)
u08$log_t <- log(u08$tiempo_mediano_h)

modelo <- lm(log_t ~ despues + semana_desde_cambio, data = u08)
cambio_nivel <- 100 * (exp(coef(modelo)["despues"]) - 1)

previo  <- subset(u08, despues == 0)
posterior <- subset(u08, despues == 1)

fcr_a <- sum(previo$resueltos_primer_contacto) / sum(previo$tickets_abiertos)
fcr_d <- sum(posterior$resueltos_primer_contacto) / sum(posterior$tickets_abiertos)

lineas_u08 <- c(
  "# U-08 · mesa de ayuda",
  "",
  paste0("- semanas = ", nrow(u08), " (12 antes, 12 despues)"),
  paste0("- mediana del tiempo: ", coma(median(previo$tiempo_mediano_h), 1), " h -> ",
         coma(median(posterior$tiempo_mediano_h), 1), " h"),
  paste0("- resolucion al primer contacto: ", coma(100 * fcr_a, 1), " % -> ",
         coma(100 * fcr_d, 1), " %"),
  paste0("- cambio de nivel al intervenir: ", coma(cambio_nivel, 1), " %"),
  paste0("- p del cambio de nivel: ", p_txt(summary(modelo)$coefficients["despues", 4])),
  paste0("- R2 del modelo = ", coma(summary(modelo)$r.squared, 3))
)
escribir("U-08_mesa_de_ayuda.md", lineas_u08)

# =============================================================================
# U-09 · Mantenibilidad: densidad de defectos por version
# =============================================================================
u09 <- read.csv(file.path(sim, "U-09", "datos.csv"), check.names = FALSE)
v1 <- subset(u09, version == "v1")$densidad_defectos_kloc
v2 <- subset(u09, version == "v2")$densidad_defectos_kloc

prueba <- wilcox.test(v1, v2, exact = FALSE)
a12    <- as.numeric(prueba$statistic) / (length(v1) * length(v2))

# bootstrap de la diferencia de medianas
replicas <- replicate(2000, {
  m1 <- median(sample(v1, length(v1), replace = TRUE))
  m2 <- median(sample(v2, length(v2), replace = TRUE))
  m2 - m1
})
ic_dif <- quantile(replicas, c(0.025, 0.975))

lineas_u09 <- c(
  "# U-09 · mantenibilidad",
  "",
  paste0("- modulos = ", length(v1), " por version"),
  paste0("- densidad media: ", coma(mean(v1), 2), " v1 -> ", coma(mean(v2), 2), " v2"),
  paste0("- Mann-Whitney W = ", coma(as.numeric(prueba$statistic), 1), " · ", p_txt(prueba$p.value)),
  paste0("- A12 = ", coma(a12, 3)),
  paste0("- diferencia de medianas = ", coma(median(v2) - median(v1), 2),
         " [", coma(ic_dif[1], 2), "; ", coma(ic_dif[2], 2), "]")
)
escribir("U-09_mantenibilidad.md", lineas_u09)

cat("Listo. Resultados en", out, "\n")
