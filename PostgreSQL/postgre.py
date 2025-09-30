import pandas as pd
import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "agromercantil_db"
DB_USER = "postgres"
DB_PASS = "0000"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cursor = conn.cursor()

df = pd.read_csv(r"RAW/cepea_dados_2.csv")
commodities = df['commodity'].unique()

for nome in commodities:
    cursor.execute("""
        INSERT INTO commodities (nome)
        VALUES (%s)
        ON CONFLICT (nome) DO NOTHING;
    """, (nome,))
conn.commit()

cursor.execute("SELECT id, nome FROM commodities;")
rows = cursor.fetchall()
commodity_map = {nome: id for id, nome in rows}

for _, row in df.iterrows():
    commodity_id = commodity_map.get(row['commodity'])
    data = row['data']
    preco = row['preco']
    regiao = row['regiao']
    quantidade = row['quantidade'] if not pd.isna(row['quantidade']) else 0


    cursor.execute("""
        INSERT INTO registros (commodity_id, data, preco, regiao, quantidade)
        VALUES (%s, %s, %s, %s, %s);
    """, (commodity_id, data, preco, regiao, quantidade))

conn.commit()
cursor.close()
conn.close()

print("Dados inseridos")
