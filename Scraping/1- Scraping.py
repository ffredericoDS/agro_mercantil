import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
import json


def limpar_preco(preco_texto):
    preco_texto = re.sub(r'[^\d,]', '', preco_texto)
    return float(preco_texto.replace(',', '.')) if preco_texto else None

def extrair_regiao(tabela, indice):
    try:
        prev = tabela.find_previous_sibling("div", class_=re.compile(r"table-titulo"))
        if prev:
            t = prev.get_text(strip=True).upper()
            if "PARANAGUÁ" in t: return "Paranaguá/PR"
            if "PARANÁ" in t: return "Paraná"
            if "SÃO PAULO" in t or "SP" in t: return "São Paulo"
    except: pass
    return {0:"Paranaguá/PR", 1:"Paraná", 2:"São Paulo/SP"}.get(indice, "Brasil")

def coletar_dados(commodity, url):
    dados = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            print(f"Falha ao acessar {url} (status {r.status_code})")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        tabelas = soup.find_all("table", {"class": "imagenet-table"})
        if not tabelas:
            return []
        for i, tabela in enumerate(tabelas):
            regiao = extrair_regiao(tabela, i)
            tid = tabela.get("id", f"imagenet-indicador{i+1}")
            for linha in tabela.find_all("tr")[1:]:
                colunas = linha.find_all("td")
                if len(colunas) >= 2:
                    data = colunas[0].get_text(strip=True)
                    preco = limpar_preco(colunas[1].get_text(strip=True))
                    if re.match(r"\d{2}/\d{2}/\d{4}", data) and preco:
                        dados.append({
                            "commodity": commodity,
                            "data": datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            "preco": preco,
                            "regiao": regiao,
                            "fonte": "CEPEA/ESALQ",
                            "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "tabela": tid
                        })
    except Exception as e:
        print(f"Erro em {commodity}: {e}")
    return dados

def main():
    commodities = {
        "ALGODÃO":"https://www.cepea.esalq.usp.br/br/indicador/algodao.aspx",
        "ARROZ":"https://www.cepea.esalq.usp.br/br/indicador/arroz.aspx",
        "CAFÉ":"https://www.cepea.esalq.usp.br/br/indicador/cafe.aspx",
        "MILHO":"https://www.cepea.esalq.usp.br/br/indicador/milho.aspx",
        "TRIGO":"https://www.cepea.esalq.usp.br/br/indicador/trigo.aspx",
        "SOJA":"https://www.cepea.esalq.usp.br/br/indicador/soja.aspx",
        "AÇUCAR":"https://www.cepea.org.br/br/indicador/acucar.aspx"
    }

    todos_dados = []
    for nome,url in commodities.items():
        print(f"Coletando {nome}")
        dados = coletar_dados(nome,url)
        todos_dados.extend(dados)
        print(f"{nome}: {len(dados)} registros coletados")
        time.sleep(2)

    if todos_dados:
        df = pd.DataFrame(todos_dados)
        nome_csv = f"cepea_dados_10.csv"
        df.to_csv(nome_csv, index=False, encoding="utf-8-sig")
        print(f"\nBase CEPEA baixada com sucesso!")
    else:
        print("Nenhum dado coletado.")

if __name__ == "__main__":
    main()