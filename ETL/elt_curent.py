import pandas as pd

df = pd.read_csv("PROCESSED/cepea_dados_3.csv")


df_curated = df.groupby(['commodity', 'estado', 'mes', 'ano']).agg({
    'preco': 'mean',
    'quantidade': 'sum'
}).reset_index()

df_curated.rename(columns={
    'preco': 'preco_medio',
    'quantidade': 'quantidade_total'
}, inplace=True)

df_curated['variacao_preco'] = df_curated.groupby(['commodity', 'estado'])['preco_medio'].pct_change()
df_curated.to_csv("CURATED/cepea_dados_40.csv", index=False)
