# Equivalentes en R de los cuatro analisis docentes.
# Ejecutado con R 4.6.0 (readxl, effectsize, rstatix): reproduce las cifras del libro.
# Uso: Rscript equivalente_R.R

library(readxl)
library(effectsize)

raiz <- normalizePath(".")
repeat {
  if (dir.exists(file.path(raiz, "dataset"))) break
  padre <- dirname(raiz)
  if (padre == raiz) stop("Ejecuta el script dentro del proyecto del libro: no encuentro la carpeta dataset.")
  raiz <- padre
}
datos_docentes <- file.path(raiz, "dataset", "04_Docentes")

# 1) Mann-Whitney
mw <- read_excel(file.path(datos_docentes, "dataset_MannWhitney_100_casos.xlsx"))
wilcox.test(Tiempo_Ciclo_Horas ~ Grupo, data = mw, exact = FALSE)
rstatix::wilcox_effsize(mw, Tiempo_Ciclo_Horas ~ Grupo)

# 2) t pareada
tp <- read_excel(file.path(datos_docentes, "dataset_t_emparejada_Sistemas.xlsx"))
t.test(tp$Tiempo_Antes_ms, tp$Tiempo_Despues_ms, paired = TRUE)
cohens_d(tp$Tiempo_Antes_ms, tp$Tiempo_Despues_ms, paired = TRUE)

# 3) t independiente
ti <- read_excel(file.path(datos_docentes, "dataset_t_independiente_Sistemas.xlsx"))
t.test(Tiempo_Respuesta_ms ~ Arquitectura, data = ti, var.equal = TRUE)
cohens_d(Tiempo_Respuesta_ms ~ Arquitectura, data = ti)

# 4) Wilcoxon con varios pares
wx <- read_excel(file.path(datos_docentes, "datos_wilcoxon_SPSS-JAMOVI.xlsx"), sheet = "Wilcoxon_SPSS")
pares <- grep("_pretest$", names(wx), value = TRUE)
for (p in pares) {
  base <- sub("_pretest$", "", p)
  pre <- wx[[paste0(base, "_pretest")]]
  post <- wx[[paste0(base, "_postest")]]
  if (sum(!is.na(pre)) < 5) next
  prueba <- wilcox.test(pre, post, paired = TRUE, exact = FALSE)
  cat(base, "\tW =", prueba$statistic, "\tp =", prueba$p.value, "\n")
}
