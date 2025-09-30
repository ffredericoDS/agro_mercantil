import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

arquivo_entrada = "RAW/cepea_dados_1.csv"

arquivo_saida = "cepea_dados_20.csv"

commodities = {
    "ALGODÃO": {"preco": (300, 400), "quantidade": (500, 2000)},          
    "ARROZ": {"preco": (50, 80), "quantidade": (1000, 5000)},             
    "CAFÉ": {"preco": (2000, 3000), "quantidade": (100, 1000)},           
    "MILHO": {"preco": (60, 90), "quantidade": (2000, 10000)},            
    "TRIGO": {"preco": (900, 1500), "quantidade": (1000, 6000)},          
    "SOJA": {"preco": (120, 180), "quantidade": (3000, 12000)},           
    "CANA-DE-AÇÚCAR": {"preco": (0.5, 1.2), "quantidade": (10000, 50000)},
    "MILHO SILO": {"preco": (55, 85), "quantidade": (1500, 9000)},        # novo
    "FEIJÃO": {"preco": (300, 500), "quantidade": (200, 1500)},           # novo
    "LARANJA": {"preco": (70, 120), "quantidade": (800, 5000)}            # novo
}

regioes = [
    "Paranaguá/PR",    
    "campinas/sp",      
    "Santos/SP",        
    "ribeirão preto/SP",
    "Cuiabá/mt"         
]

fonte = "CEPEA/ESALQ"
tabela = "imagenet-indicador1"

def gerar_precos(dias, faixa):
    preco = random.uniform(*faixa)
    precos = []
    for _ in range(dias):
        preco *= (1 + np.random.normal(0, 0.01))  
        precos.append(round(preco, 2))
    return precos

def gerar_quantidades(dias, faixa):
    return [random.randint(*faixa) for _ in range(dias)]

def gerar_dados_sinteticos():
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=2*365)  # 2 anos
    dias = (data_fim - data_inicio).days + 1
    datas = [data_inicio + timedelta(days=i) for i in range(dias)]
    registros = []

    for commodity, faixas in commodities.items():
        precos = gerar_precos(dias, faixas["preco"])
        quantidades = gerar_quantidades(dias, faixas["quantidade"])

        for i, data in enumerate(datas):
            linha = {
                "commodity": commodity,
                "data": data.strftime("%Y-%m-%d"),
                "preco": precos[i],
                "quantidade": quantidades[i],
                "regiao": random.choice(regioes),
                "fonte": fonte,
                "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tabela": tabela
            }
            registros.append(linha)

        for _ in range(5):
            idx = random.randint(0, dias-1)
            registros[idx]["preco"] = random.choice([
                round(random.uniform(-100, -1), 2),      
                round(random.uniform(faixas["preco"][1]*3, faixas["preco"][1]*5), 2)
            ])
            registros[idx]["quantidade"] = random.choice([
                random.randint(-1000, -1),                 
                random.randint(faixas["quantidade"][1]*3, faixas["quantidade"][1]*5) 
            ])

    return pd.DataFrame(registros)

df_sintetico = gerar_dados_sinteticos()
df_original = pd.read_csv(arquivo_entrada)
df_final = pd.concat([df_original, df_sintetico], ignore_index=True)
df_final.to_csv(arquivo_saida, index=False, encoding="utf-8-sig")
