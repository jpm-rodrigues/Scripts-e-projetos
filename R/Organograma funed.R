# Chamando as librarys que precisam
library(dplyr)
library(readxl)

# Colocando o work directory pro desktop que é onde está a tabela no momento em que vos escrevo
setwd("/home/jpmr/Desktop")
# Importando a tabela do excel
dados_brutos <- read_excel("como saber qual serviço é de qual lugar versão 2.xlsx",sheet = "Base de Dados")

# Removendo as colunas desnecessárias
df <- dados_brutos |> 
  select(3:5)

# Renomeando as colunas
colnames(df) <- c("Diretoria","Divisão", "Serviço")
  
# Separando as diretorias em data.frames individuais
## Desnecessário, posso fazer tudo isso aqui com a função abaixo
presidência <- df |> # O pipe, pega o que ta na esquerda e aplica como o primeiro argumento do entre parênteses da direita
  filter(Diretoria == "PRE - Presidência") # Filter usa 
di <- df |> 
  filter(Diretoria == "DI - Diretoria Industrial")
dpgf <- df |> 
  filter(Diretoria == "DPGF - Diretoria de Planejamento Gestão e Finanças")
diom <- df |> 
  filter(Diretoria == "DIOM - Diretoria do Instituto Otávio Magalhães")
dpd <- df |>
  filter(Diretoria == "DPD - Diretoria de Pesquisa e Desenvolvimento")

# Exemplo de pegando as divisões utilizando os data.frames unicos de diretoria
# Mantendo só por manter, não vou usar mais isso já que a função é mais prático
divisões_presidência <- presidência |>
  distinct(Divisão, .keep_all = TRUE) # Distinct pega todas as linhas únicas, o .keep_all = TRUE faz com que todas as colunas, mesmo as não procuradas, permaneçam.

# Função para extrair divisões
divisões <- function(diretoria) { df |> 
    filter(Diretoria == diretoria) |>
    distinct(Divisão)
}
  
# Função para extrair serviços
serviços <- function(divisões) { df |>
    filter(Divisão == divisões) |> 
    distinct(Serviço)
}

# Juntando os dois
# Ta rolando, mas tem que achar um jeito de deixar separado por cada um dos tipos.
busca <- function(x) {
print("Divisões")
divisões(x)
divisão_procurada <- divisões(x)
print("Serviços")
serviços(divisão_procurada[1,1])
}

