import pandas as pd

data = [
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

aliases = {
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

df = pd.DataFrame(data, columns=["Nível 1", "Nível 2", "Nível 3"])

def buscar_hierarquia(termo):
    resultado = df[(df == termo).any(axis=1)]
    
    if resultado.empty:
        print("Item não encontrado.")
        return
    
    for _, row in resultado.iterrows():
        hierarquia = row.dropna().tolist()
        
        if termo in hierarquia:
            index = hierarquia.index(termo)
            acima = [aliases.get(item, item) for item in hierarquia[:index]]
            abaixo = [aliases.get(item, item) for item in hierarquia[index + 1:]]
            termo_completo = aliases.get(termo, termo)
            print(f"{termo} - {termo_completo} ")
            print(f"Acima: {acima if acima else 'Nenhum'}")
            print(f"Abaixo: {abaixo if abaixo else 'Nenhum'}")
            print("-" * 30)

# Exemplo de uso
if __name__ == "__main__":
    termo = input("Insira o nome do serviço: ").strip()
    buscar_hierarquia(termo)

