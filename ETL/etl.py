import pandas as pd
from sqlalchemy import create_engine

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "agromercantil_db"
DB_USER = "postgres"
DB_PASS = "0000"

df = pd.read_csv("RAW/cepea_dados_2.csv")

df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['preco'] = pd.to_numeric(df['preco'], errors='coerce')
df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
df = df.dropna(subset=['preco', 'quantidade'])
df['commodity'] = df['commodity'].str.strip().str.upper()
df['regiao'] = df['regiao'].str.strip().str.upper()
df[['cidade', 'estado']] = df['regiao'].str.split("/", expand=True)
df['cidade'] = df['cidade'].str.strip().str.upper()
df['estado'] = df['estado'].str.strip().str.upper()
df['dia'] = df['data'].dt.day
df['mes'] = df['data'].dt.month
df['ano'] = df['data'].dt.year
df = df.drop(columns=['fonte', 'data_coleta', 'tabela'])
df = df.drop_duplicates()

commodities_df = pd.DataFrame(df['commodity'].unique(), columns=['nome'])
commodities_df['nome'] = commodities_df['nome'].str.upper()
commodities_df['id'] = range(1, len(commodities_df) + 1)
commodity_map = dict(zip(commodities_df['nome'], commodities_df['id']))
df['commodity_id'] = df['commodity'].map(commodity_map)

registros_df = df[['commodity_id', 'data', 'preco', 'regiao', 'quantidade', 'cidade', 'estado', 'dia', 'mes', 'ano']]

df.to_csv("RAW/cepea_dados_30.csv", index=False)

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

commodities_df[['id', 'nome']].to_sql("commodities_processados", engine, if_exists="replace", index=False)
registros_df.to_sql("registros_processados", engine, if_exists="replace", index=False)

