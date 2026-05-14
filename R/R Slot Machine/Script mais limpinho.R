
## Passo 1: Gerar os símbolos
get_symbols <- function() {
  wheel <- c("DD", "7", "BBB", "BB", "B","C", "0")
  sample(wheel, size = 3, replace = TRUE,
         prob = c(0.03, 0.03, 0.06, 0.1, 0.25, 0.1, 0.52))
}
# Scorar os symbols
all_same <- symbols[1] == symbols[2] && symbols[2] == symbols[3]
all_bars <- symbols %in% c("B", "BB", "BBB")

score <- function(symbols){
if (all_same) { # Case 1: all the same <1>
  payouts <- c("DD" = 100, "7" = 80, "BBB" = 40, "BB" = 25, "B" = 10, "C" = 10, "0" = 0) # Criando uma tabela com "nomes" e valores.
  prize <- unname(payouts[symbols[1]]) # look up the prize <3>
  } else if (all(all_bars)) {# Case 2: all bars <2> 
    prize <- 5 # assign $5 <4>
    } else {
      cherries <- sum(symbols == "C") # count cherries <5>
      prize <- c(0,2,5)[cherries + 1]# calculate a prize <7>
    }
diamonds <- sum(symbols == "DD") # count diamonds <6>
prize*2^diamonds # double the prize if necessary <8>
}



play <- function() {
  symbols <- get_symbols()
  print(symbols)
  score(symbols)
}
  