#!/usr/bin/env python3
#Purpose: Localizar no organograma os serviços da funed

import pandas as pd
organograma_di = [  #Criando uma lista([]) do organograma da DI
    ["DI", "UPF", None],
    ["DI", "UTT", None],
    ["DI", "DGQ", "SGeQ"],
    ["DI", "DGQ", "SAQ"],
    ["DI", "DGQ", "SVQ"],
    ["DI", "DPGP", "SAI"],
    ["DI", "DPGP", "SPCP"],
    ["DI", "DDM", "SDPB"],
    ["DI", "DDM", "SDAE"],
    ["DI", "DDM", "SPEM"],
    ["DI", "DDM", "SDPF"],
    ["DI", "DDM", "SRE"],
    ["DI", "DDM", "SFEC"],
    ["DI", "DCQ", "SCM"],
    ["DI", "DCQ", "SCBio"],
    ["DI", "DCQ", "SCFQ"],
    ["DI", "DCQ", "SCAD"],
    ["DI", "DPF", "SPUII"],
    ["DI", "DPF", "SPUIII"],
    ["DI", "DPF", "SL"],
    ["DI", "DPF", "SPS"],
    ["DI", "DPF", "SPF"],
    ["DI", "DPF", "SEAS"],
    ["DI", "DPF", "SPSF"],
    ["DI", "DPA", "SFE"],
    ["DI", "DPA", "SAP"],
    ["DI", "DPA", "SB"],
]

aliases = { # Criando um dicionário ({}, e colocando a sigla como chave, e o nome completo como valor)
    "DI": "Diretoria Industrial",
    "UPF": "Unidade de Projetos Fabris",
    "UTT": "Unidade de Transferência de Tecnologia",
    "DGQ": "Divisão de Garantia da Qualidade",
    "SGeQ": "Serviço de Gestão da Qualidade",
    "SAQ": "Serviço de Avaliação da Qualidade",
    "SVQ": "Serviço de Validação e Qualificação",
    "DPGP": "Divisão de Planejamento e Gestão da Produção",
    "SAI": "Serviço de Almoxarifado Industrial",
    "SPCP": "Serviço de Planejamento e Controle da Produção",
    "DDM": "Divisão de Desenvolvimento de Medicamentos",
    "SDPB": "Serviço de Desenvolvimento de Produtos Biológicos",
    "SDAE": "Serviço de Desenvolvimento Analítico e Estudo de Estabilidade",
    "SPEM": "Serviço de Pré-Formulação e Estudo de Matéria-Prima",
    "SDPF": "Serviço de Desenvolvimento de Produtos Farmoquímicos",
    "SRE": "Serviço de Registro",
    "SFEC": "Serviço de Farmacovigilância e Estudos Clínicos",
    "DCQ": "Divisão de Controle da Qualidade",
    "SCM": "Serviço de Controle Microbiológico",
    "SCBio": "Serviço de Controle Biológico",
    "SCFQ": "Serviço de Controle Físico-Químico",
    "SCAD": "Serviço de Controle de Amostras e Documentação",
    "DPF": "Divisão de Produção Farmacêutica",
    "SPUII": "Serviço de Produção Unidade II",
    "SPUIII": "Serviço de Produção Unidade III",
    "SL": "Serviço de Líquidos",
    "SPS": "Serviço de Produção de Soros",
    "SPF": "Serviço de Processamento Final",
    "SEAS": "Serviço de Envase Asséptico",
    "SPSF": "Serviço de Preparo de Soluções e Formulação",
    "DPA": "Divisão de Produção Animal",
    "SFE": "Serviço de Fazenda Experimental",
    "SAP": "Serviço de Animais Peçonhentos",
    "SB": "Serviço de Biotério"
}

df = pd.DataFrame(organograma_di, columns=["Diretoria", "Divisão", "Serviço"]) # Criando um data frame com o organograma de data, e colunas com nomes
def buscar_hierarquia(termo): # definindo a função buscar hierarquia
    resultado = df[           # define resultado como e abre o índice de busca []
        (df == termo)         # onde df é igual ao termo. O parênteses ta ai só para poder operar
        .any(axis=1)          # axis=1 corresponde as linhas, e axis=0 nas colunas
        ]

    if resultado.empty:        
        print("Item não encontrado.")
        return
    
    for _, row in resultado.iterrows():
        hierarquia = row.dropna().tolist()

        if termo in hierarquia:
            index = hierarquia.index(termo)     # a função de lista.index(termo) retorna o índice(posição) do termo na lista
            acima = hierarquia[:index]          #
            abaixo = hierarquia[index + 1:]
            print(f"Item encontrado: {termo}")
            print(f"Acima: {acima if acima else 'Nenhum'}")
            print(f"Abaixo: {abaixo if abaixo else 'Nenhum'}")
            print("-" * 30)
            print(hierarquia)


# Main
if __name__ == "__main__":
    while True:
        termo = input("Digite o termo que deseja buscar, ou exit para sair: ").strip()
        if termo.lower() == 'exit':
            print("Saindo..")
            break
        buscar_hierarquia(termo)
