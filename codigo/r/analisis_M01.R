# =============================================================================
# Caso M-01 · El alfa sobre la ficha de registro (retest con sesgo)
# Libro: Estadistica experimental para TIC
#
# ESTADO: ejecutado con R 4.6.0 el 2026-11-05. Coincide con analisis_M01.py:
# r = 0,997 · CCI(A,1) = 0,742 · sesgo +2,38 min · LoA [1,28; 3,49].
# Solo base R: no requiere paquetes.
#
# Uso, desde la raiz del proyecto:
#   Rscript 06_Codigo/02_Analisis/analisis_M01.R
#
# Salidas: 02_Tablas_y_Figuras/01_Fuentes/T-M01-01_acuerdo.csv
#          02_Tablas_y_Figuras/01_Fuentes/T-M01-02_bland_altman.csv
# =============================================================================

raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "05_Datos"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro 05_Datos.")
  raiz <- padre
}
sim  <- file.path(raiz, "05_Datos", "01_Simulados", "M-01")
out  <- file.path(raiz, "02_Tablas_y_Figuras", "01_Fuentes")
dir.create(out, showWarnings = FALSE, recursive = TRUE)

d <- read.csv(file.path(sim, "datos.csv"), check.names = FALSE)
m <- as.matrix(d[, c("t1_min", "t2_min")])
dif <- m[, 2] - m[, 1]

alfa <- function(x) {
  k <- ncol(x)
  k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
}

icc_a1 <- function(x) {
  n <- nrow(x); k <- ncol(x); g <- mean(x)
  msr <- k * sum((rowMeans(x) - g)^2) / (n - 1)
  msc <- n * sum((colMeans(x) - g)^2) / (k - 1)
  resid <- x - outer(rowMeans(x), rep(1, k)) - outer(rep(1, n), colMeans(x)) + g
  mse <- sum(resid^2) / ((n - 1) * (k - 1))
  (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)
}

ic_boot <- function(estimador, x, replicas = 2000, semilla = 20261103) {
  set.seed(semilla)
  n <- nrow(x)
  v <- replicate(replicas, estimador(x[sample.int(n, n, replace = TRUE), , drop = FALSE]))
  quantile(v, c(0.025, 0.975))
}

r    <- cor(m[, 1], m[, 2])
a    <- alfa(m);   ic_a <- ic_boot(alfa, m)
icc  <- icc_a1(m); ic_i <- ic_boot(icc_a1, m)

sesgo     <- mean(dif)
sesgo_pct <- 100 * sesgo / mean(m[, 1])
loa       <- sesgo + c(-1.96, 1.96) * sd(dif)

tabla <- data.frame(
  indicador = c("r de Pearson entre ocasiones", "alfa sobre las dos columnas",
                "CCI(A,1) de acuerdo absoluto", "sesgo medio (min)",
                "limite inferior de acuerdo (min)", "limite superior de acuerdo (min)"),
  valor = round(c(r, a, icc, sesgo, loa[1], loa[2]), 3),
  ic_inf = c(NA, round(ic_a[1], 3), round(ic_i[1], 3), NA, NA, NA),
  ic_sup = c(NA, round(ic_a[2], 3), round(ic_i[2], 3), NA, NA, NA),
  que_dice = c("altisima: es lo que la tesis presenta como confiabilidad",
               "practicamente igual a r (con dos columnas, alfa = r)",
               "buena pero menor: descuenta el sesgo",
               sprintf("%.1f %% de la medicion basal", sesgo_pct),
               "Bland-Altman", "Bland-Altman"),
  veredicto = c("no evalua acuerdo: un sesgo constante no la baja",
                "no corresponde: no hay itemes ni constructo",
                "corresponde: es la evidencia de calidad del registro",
                "invisible para r y para el alfa",
                "el registro no es intercambiable entre ocasiones",
                "amplitud que el tesista debe declarar"),
  stringsAsFactors = FALSE
)

write.csv(tabla, file.path(out, "T-M01-01_acuerdo.csv"), row.names = FALSE)
write.csv(data.frame(ficha = d$ficha, promedio = rowMeans(m), diferencia = dif),
          file.path(out, "T-M01-02_bland_altman.csv"), row.names = FALSE)

print(tabla, row.names = FALSE)
cat(sprintf("\nSesgo: %.2f min (%.1f %%) | LoA: %.2f a %.2f min\n",
            sesgo, sesgo_pct, loa[1], loa[2]))
