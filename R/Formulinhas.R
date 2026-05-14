#Ajuda
## Colocar ? na frente de um comando para abrir o help
#Vignette
vignette(package = "package_name") #Para ver as vignettes do pacote
vignette("vignette_name", "package_name")

#Visualização
##Ver um objeto (tipo clicar no enviroment)
View(df)

#Visão estruturada:
Str(df)

#Ver um sumário:
summary(df)

#Ver a classe:
Class(df)

#Ver as n(opcional) primeiras e últimas linhas de um df:
head(x, n)

tail(x , n)


#Ler arquivo e insirir os valores à um objeto:
dat <- read.csv("femaleMiceWeights.csv")

#Chamar colunas:
colnames(df)

#Procurar linhas (x) e colunas (y) dentro de um objeto:
df(x,y)

#Procurar em uma coluna (variável) específica:
df$coluna[x]

# Função length retorna número de elementos em um vetor
length(x)

# Find Elements in a Vector:
#'The which() function in R returns the position of elements in a logical vector that are TRUE.



### Coerção
#logical → integer → numeric → character
#Logical vectors can only take on two values: TRUE or FALSE. Integer vectors can only contain integers, so TRUE and FALSE can be coerced to 1 and 0. Numeric vectors can contain numbers with decimals, so integers can be coerced from, say, 6 to 6.0 (though R will still display a numeric 6 as 6.). Finally, any string of characters can be represented as a character vector, so any of the other types can be coerced to a character vector.
