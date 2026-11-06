# =============================================================================
# Caso M-07 · El mismo coeficiente aplicado a tres naturalezas de dato
# Libro: Estadistica experimental para TIC
#
# ESTADO: ejecutado con R 4.6.0 el 2026-11-05. Coincide con analisis_M07.py:
# alfa 0,914 · KR-20 0,715 · CCI(A,1) 0,900 · sesgo +1,73 min.
# Solo base R: no requiere paquetes, para que el lector pueda correrlo tal cual.
#
# Uso, desde la raiz del proyecto:
#   Rscript 06_Codigo/02_Analisis/analisis_M07.R
#
# Salidas: 02_Tablas_y_Figuras/01_Fuentes/T-M07-01_coeficientes.csv
#          02_Tablas_y_Figuras/01_Fuentes/T-M07-02_bland_altman.csv
# =============================================================================

raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "05_Datos"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro 05_Datos.")
  raiz <- padre
}
sim  <- file.path(raiz, "05_Datos", "01_Simulados", "M-07")
out  <- file.path(raiz, "02_Tablas_y_Figuras", "01_Fuentes")
dir.create(out, showWarnings = FALSE, recursive = TRUE)

lik <- read.csv(file.path(sim, "datos_likert.csv"), check.names = FALSE)
tst <- read.csv(file.path(sim, "datos_test.csv"),   check.names = FALSE)
fic <- read.csv(file.path(sim, "datos_ficha.csv"),  check.names = FALSE)

m_lik <- as.matrix(lik[, grepl("^item_",     names(lik))])
m_tst <- as.matrix(tst[, grepl("^reactivo_", names(tst))])
m_fic <- as.matrix(fic[, c("t1_min", "t2_min")])

# --- Coeficientes ------------------------------------------------------------
alfa <- function(m) {
  k <- ncol(m)
  k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}

kr20 <- function(m) {
  k <- ncol(m)
  p <- colMeans(m)
  k / (k - 1) * (1 - sum(p * (1 - p)) / var(rowSums(m)))
}

# CCI(2,1) de acuerdo absoluto: dos mediciones por sujeto
icc_a1 <- function(m) {
  n <- nrow(m); k <- ncol(m); g <- mean(m)
  msr <- k * sum((rowMeans(m) - g)^2) / (n - 1)
  msc <- n * sum((colMeans(m) - g)^2) / (k - 1)
  resid <- m - outer(rowMeans(m), rep(1, k)) - outer(rep(1, n), colMeans(m)) + g
  mse <- sum(resid^2) / ((n - 1) * (k - 1))
  (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)
}

ic_boot <- function(estimador, m, replicas = 2000, semilla = 20261103) {
  set.seed(semilla)
  n <- nrow(m)
  v <- replicate(replicas, estimador(m[sample.int(n, n, replace = TRUE), , drop = FALSE]))
  quantile(v, c(0.025, 0.975))
}

a_lik <- alfa(m_lik); ic_lik <- ic_boot(alfa, m_lik)
a_tst <- kr20(m_tst); ic_tst <- ic_boot(kr20, m_tst)
a_fic <- alfa(m_fic)
icc   <- icc_a1(m_fic); ic_icc <- ic_boot(icc_a1, m_fic)

dif    <- m_fic[, 2] - m_fic[, 1]
sesgo  <- mean(dif)
loa    <- sesgo + c(-1.96, 1.96) * sd(dif)

# --- Tabla -------------------------------------------------------------------
tabla <- data.frame(
  bloque = c("a) escala Likert", "b) prueba de conocimiento",
             "c) ficha de registro", "c) ficha de registro",
             "c) ficha de registro", "c) ficha de registro", "c) ficha de registro"),
  coeficiente = c("alfa de Cronbach", "KR-20",
                  "alfa sobre dos columnas (= r)", "CCI(A,1) acuerdo absoluto",
                  "sesgo medio (min)", "limite inferior de acuerdo (min)",
                  "limite superior de acuerdo (min)"),
  valor = round(c(a_lik, a_tst, a_fic, icc, sesgo, loa[1], loa[2]), 3),
  ic_inf = c(round(ic_lik[1], 3), round(ic_tst[1], 3), NA, round(ic_icc[1], 3), NA, NA, NA),
  ic_sup = c(round(ic_lik[2], 3), round(ic_tst[2], 3), NA, round(ic_icc[2], 3), NA, NA, NA),
  veredicto = c(
    "corresponde, aunque omega seria preferible con evidencia de estructura",
    "corresponde; el alfa daria el mismo numero con otro nombre y otro sentido",
    "no corresponde: mide correlacion, no acuerdo",
    "corresponde: descuenta el sesgo sistematico",
    "diferencia sistematica entre ocasiones: la correlacion no la ve",
    "Bland-Altman", "Bland-Altman"),
  stringsAsFactors = FALSE
)

write.csv(tabla, file.path(out, "T-M07-01_coeficientes.csv"), row.names = FALSE)
write.csv(data.frame(ficha = fic$ficha,
                     promedio = rowMeans(m_fic),
                     diferencia = dif),
          file.path(out, "T-M07-02_bland_altman.csv"), row.names = FALSE)

print(tabla, row.names = FALSE)
cat(sprintf("\nSesgo sistematico: %.2f min | LoA: %.2f a %.2f min\n", sesgo, loa[1], loa[2]))
cat(sprintf("Tablas en %s\n", out))
