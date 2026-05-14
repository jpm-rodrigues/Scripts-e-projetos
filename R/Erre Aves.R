library(wikiaves)
library(dplyr)
library(readxl)


############ Se eu fosse fazer um script para sempre com isso, colocaria aqui: #############
# [FEITO]     A fórmula de importar, ao invés de importar pela GUI

dados_município <- read_excel("Brasilância de Minas.xlsx")

# [NÃO FEITO] Um jeito de automaticamente preencher as famílias (não repetem no site do Wiki Aves)


#### Agrupando por famílias
Famílias <- distinct(dados_município, Família)

# Loop para agrupar as espécies por família
lista_por_familias <- list()

for (familia in Famílias) {
  filter(dados_município, Família == familia) # Filtra as espécies da família atual
  lista_por_familias[[familia]]
}


print(lista_por_familias)
  
'
resultado[[familia]] <- paste(unique(especies), collapse = ", ") # Concatena os nomes das espécies
  individuos_por_familia <- data.frame(Família = names(resultado), Espécies = unlist(resultado), stringsAsFactors = FALSE)
  print(individuos_por_familia)
    }
  
    