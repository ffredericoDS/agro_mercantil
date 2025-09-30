# Projeto: Análise de Commodities Agrícolas

## Visão Geral
- Objetivo: coletar, tratar, armazenar e visualizar dados de commodities agrícolas.
- Simulação de pipeline real de dados em cenário de análise de mercado.
- Tecnologias: **Python**, **SQL (PostgreSQL)** e **Streamlit**.
---
## Coleta de Dados Externos

- **Fonte:** site **CEPEA** — referência em preços e informações sobre commodities agrícolas (soja, milho, trigo, café, arroz, algodão, entre outros).
- **Tipo de dados:** preços, datas e regiões.
- **Formato final:** CSV.
  <img width="1158" height="772" alt="image" src="https://github.com/user-attachments/assets/64421c13-e30d-495d-b134-0963741d1dad" />


#### Processo
- Ferramentas: **Python** (`requests` + `BeautifulSoup`).
- Script principal: **Scraping/`1 - Scraping.py`**.
- Função: extrair tabelas, tratar preços e datas, salvar dados.
- Desafios enfrentados: tabelas fragmentadas , necessidade de padronização , inconsistências nos dados. 

#### Dificuldades e Soluções
- O site exibia apenas dados recentes (últimos 13 a 30 dias).
- Não havia histórico completo disponível.
- **Solução:** criei o script **Scraping/`2 - Scraping_add_dados.py`**, que preencheu a tabela com dados dos últimos 2 anos.
- **Resultado:** expansão da base de **172 linhas** com os dados reais do site para **7.482 registros**.
- Arquivo Inicial(com dados reais do site): **RAW/`cepea_dados_1.csv`**.
- Arquivo final: **RAW/`cepea_dados_2.csv`**.

---

## Estruturação da Camada RAW

### Organização atual
- Estrutura local do projeto atual (não final):
<img width="292" height="238" alt="image" src="https://github.com/user-attachments/assets/d0c2684c-d6ab-4217-a629-a1eba24201d0" />

- Objetivo da pasta RAW: armazenar os dados brutos exatamente como coletados, garantindo rastreabilidade e permitindo reprocessamento se necessário. Funciona como "matéria-prima" para camadas posteriores.

### Formatos de arquivo
- **CSV:** simples, compatível com diversas ferramentas; fácil leitura, mas pode ser menos eficiente em volume grande.
- **JSON:** flexível, bom para dados semi-estruturados; arquivos maiores e leitura mais lenta.
- **Parquet:** formato colunar, ideal para grandes volumes; mais eficiente em armazenamento e performance, mas exige compatibilidade.

**Escolha:** usei **CSV** por simplicidade, compatibilidade e facilidade de uso em Python e PostgreSQL.  
Para projetos em escala, Parquet seria mais indicado por reduzir espaço e aumentar performance.

### Organização em AWS S3
local:
RAW/
      cepea_dados_1.csv
      cepea_dados_2.csv
PROCESSED/
      cepea_dados_3.csv
CURATED/
      cepea_dados_4.csv
      
- Estrutura S3:
s3://meu-datalake/raw/cepea_dados_1.csv
s3://meu-datalake/raw/cepea_dados_2.csv
s3://meu-datalake/processed/cepea_dados_3.csv
s3://meu-datalake/curated/cepea_dados_4.csv

- Vantagens:
  - Escalabilidade e disponibilidade.
  - Integração com pipelines AWS (Glue, Athena, Redshift).
  - Controle de versões e permissões.
uso de S3 requer planejamento de custos e governança para evitar desperdício e garantir segurança.

---

## Criação de Tabelas no PostgreSQL

### Descrição da etapa
- Criei tabelas normalizadas a partir dos dados coletados, separando informações de **commodities** e **registros** para melhorar organização e eficiência.
- O processo foi realizado com scripts SQL, garantindo estrutura adequada para consultas futuras.
- O preenchimento automático das tabelas foi feito com um script Python **PostgreSQL/`postgre.py`**, que lê o arquivo **RAW/`cepea_dados_2.csv`** e insere os dados diretamente no banco.Automatizar a inserção via script Python aumenta eficiência e reduz erro
<img width="715" height="390" alt="image" src="https://github.com/user-attachments/assets/e1fb214e-932c-4b3c-a340-ee9b9765a4a3" />
<img width="341" height="401" alt="image" src="https://github.com/user-attachments/assets/6b2a1253-b576-4de7-bd13-9208757537da" />
<img width="719" height="582" alt="image" src="https://github.com/user-attachments/assets/3c89939b-7539-4ccc-b577-3752f1c14016" />

### Estrutura das tabelas
- **commodities:** tabela com lista única de commodities.
- **registros:** tabela contendo preços, datas, regiões e quantidades, referenciando a tabela commodities.

### Chaves primárias e estrangeiras
- Usei **id** como chave primária em ambas as tabelas, garantindo identificação única de registros e commodities.
- Em `registros`, usei **commodity_id** como chave estrangeira, garantindo integridade referencial e evitando duplicação de dados.
- Essa abordagem melhora a organização, evita inconsistências e facilita consultas com `JOIN`.
- 
<img width="341" height="401" alt="image" src="https://github.com/user-attachments/assets/6b2a1253-b576-4de7-bd13-9208757537da" />
<img width="719" height="582" alt="image" src="https://github.com/user-attachments/assets/3c89939b-7539-4ccc-b577-3752f1c14016" />

---
## Tratamento e ETL (Camada Processed)

### Descrição da etapa
- Desenvolvi um script Python (**`etl/etl.py`**) para realizar o processo de **ETL** sobre os dados coletados.
- Objetivo: corrigir tipos de dados, tratar valores ausentes, padronizar categorias e carregar os dados tratados em tabelas PostgreSQL (camada Processed).

### Principais transformações
- Conversão de campos para tipos corretos (`data` → datetime, `preco` e `quantidade` → numérico).
- Padronização de nomes e categorias (ex.: "soja", "SOJA" ," SOJA").
- Separação de `regiao` em colunas `cidade` e `estado`.
- Criação de colunas auxiliares (`dia`, `mes`, `ano`).
- Remoção de colunas desnecessárias e duplicatas.
- Geração da tabela de commodities com IDs únicos e mapeamento para registros.

### Resultados
- Arquivo tratado salvo como **`PROCESSED/cepea_dados_3.csv`**.
- Tabelas atualizadas no banco PostgreSQL:
  - `commodities_processados`
  - `registros_processados`
<img width="1104" height="592" alt="image" src="https://github.com/user-attachments/assets/4e65fe82-392c-48e5-b2ac-32b967c11581" />

### observação da etapa:
- O processo ETL foi necessario para manter os dados consistentes e organizados, essenciais para consultas eficientes.

---

## Estruturação do Data Lake

objetivo -- organiza dados em camadas, permitindo melhor governança, rastreabilidade e eficiência no processamento.  
### 1. RAW (dados brutos)
- Contém dados coletados diretamente da fonte, sem qualquer tratamento.
- Objetivo: manter a versão original para reprocessamento ou auditoria.
- Exemplo no projeto: **`cepea_dados_1.csv`**, **`cepea_dados_2.csv`**.
- Pasta: `/RAW`

### 2. PROCESSED (dados tratados)
- Contém dados após limpeza, padronização e transformação.
- Objetivo: garantir dados consistentes e estruturados para análises posteriores.
- Exemplo no projeto: **`cepea_dados_3.csv`**.
- Pasta: `/PROCESSED`

### 3. CURATED (dados prontos para análise)
- Contém dados refinados e organizados para consumo final (BI, dashboards, relatórios).
- Pode incluir agregações, métricas calculadas e modelos aplicados.
- Objetivo: otimizar performance de análise e tomada de decisão.
  - foi criado essa pasta , com um arquivo para ela **CURATED/cepea_dados_4.csv**, a partir do script **ETL/elt_curent.py**

<img width="308" height="340" alt="image" src="https://github.com/user-attachments/assets/a10d405b-7d7f-47dd-a908-9db9db66a28c" />

### Observação 
- Separar dados em camadas melhora rastreabilidade e facilita manutenção.
- Essa organização facilita integração com ferramentas analíticas e sistemas em nuvem.
- Em escala, o Data Lake pode ser hospedado em **AWS S3** , com gerenciamento de versionamento

---
## Análises SQL – Tendências e Indicadores

### Consultas realizadas

1. **Preço médio mensal por commodity**
   - Cálculo do preço médio mensal, agrupado por commodity e estado.
   - Uso da função `LAG` para calcular a variação percentual em relação ao mês anterior.
   - Resultado permite identificar tendências de preço e sazonalidades.

<img width="658" height="434" alt="image" src="https://github.com/user-attachments/assets/70e96eab-768d-4439-a4a5-75b4c2b40491" />
<img width="624" height="628" alt="image" src="https://github.com/user-attachments/assets/e765fd66-f71e-4e71-ac57-a132c4d31546" />


2. **Produtos mais negociados**
   - Listagem dos 5 produtos com maior volume negociado no último ano.
   - Análise útil para entender a dinâmica de mercado e focar em commodities estratégicas.

<img width="519" height="187" alt="image" src="https://github.com/user-attachments/assets/d9dfd5d1-c1f6-4f6f-9081-277b29aceb26" />
<img width="322" height="211" alt="image" src="https://github.com/user-attachments/assets/af6d3b98-4b12-4fb8-adce-d567f51cde00" />


3. **Detecção de registros anômalos**
   - Identificação de registros com preços negativos ou fora de faixa plausível, bem como quantidades inválidas.
   - Fundamental para garantir qualidade dos dados antes de análises mais profundas.

<img width="510" height="414" alt="image" src="https://github.com/user-attachments/assets/6fc143f6-704f-4176-9cfa-830358806ab3" />
<img width="1015" height="547" alt="image" src="https://github.com/user-attachments/assets/b84c4f44-9394-4885-bf1a-9756d451056c" />


---

### Otimização e Indexação

utilizado o EXPLAIN ANALYZE nas 3 query para analisar performance das consultas da questão , olhando principalmente a Execution Time q é o tempo total de execução
a)
<img width="890" height="556" alt="image" src="https://github.com/user-attachments/assets/c647fa19-0a08-4e80-8986-fee04f5089aa" />
b)
<img width="872" height="474" alt="image" src="https://github.com/user-attachments/assets/3873e00b-8049-40d9-a520-ffd79ea05410" />
c)
<img width="891" height="529" alt="image" src="https://github.com/user-attachments/assets/aaf10af0-5fb0-4d00-8a62-ed4396bc6c47" />


#### Avaliação de performance
As consultas realizadas na etapa anterior envolvem `JOIN`, `GROUP BY` e funções analíticas (`LAG`). Essas operações podem ter desempenho impactado em bases grandes, especialmente sem índices adequados.

#### Sugestões de otimização
- Criar índices compostos nas colunas mais usadas em filtros e agrupamentos (`commodity_id`, `estado`, `ano`, `mes`).
- Criar índice específico para `commodity_id` para acelerar `JOINs`.
- Considerar particionamento da tabela `registros_processados` por ano ou commodity
- Monitorar consultas usando `EXPLAIN ANALYZE` para validar ganhos de performance.

#### Justificativa
Essas otimizações melhoram o tempo de resposta das consultas, reduzem custo computacional e garantem escalabilidade, mantendo a integridade dos dados. Índices adequados são essenciais para garantir eficiência em análises periódicas de grandes volumes de dados.

---
### Análise Exploratória em Pandas

#### Descrição da etapa
- Realizei uma análise exploratória arquivo **exploratória/exploratória.ipynb** para compreender melhor a base de dados tratada (**PROCESSED/`cepea_dados_3.csv`**).
- Objetivo: gerar estatísticas descritivas, detectar outliers e visualizar padrões nos dados.

#### Principais análises realizadas
1. **Estatísticas descritivas**
   - Média, mediana e desvio padrão dos preços e quantidades.
   - Permitem compreender tendências centrais e dispersão dos dados.

2. **Detecção de outliers**
   - Utilização do método **IQR** para identificar valores extremos em preços e quantidades(valores maior ou menor que 3 desvio padrao).
   - Identificação fundamental para evitar distorções em análises futuras.

3. **Visualizações**
   - **Boxplot**: análise de dispersão e outliers por commodity.
   - **Histogramas**: distribuição de preços e quantidades.
   - **Scatter plot**: relação entre quantidade e preço, segmentada por commodity.

#### Observações
- A análise exploratória revelou padrões importantes e permitiu validar a qualidade dos dados tratados.
- Visualizações facilita muito para interpretação e comunicação dos resultados

---
### Visualização em Streamlit

#### Descrição da etapa
- Desenvolvi uma aplicação interativa em **Streamlit** para visualização de preços e tendências das commodities.
- Objetivo: fornecer uma interface intuitiva para exploração dos dados tratados e análises geradas. arquivo em **Streamlit/app.py**

#### Funcionalidades implementadas
- **Dashboards interativos** com gráficos de linhas, barras e boxplots.
- **Filtros dinâmicos** por:
  - Produto (commodity)
  - Região
  - Período (data inicial e final)
- **Visualização de tendências**: acompanhamento histórico de preços médios e variações percentuais.
- **Exploração de dados**: possibilidade de analisar distribuições, identificar outliers e comparar commodities.

<img width="1332" height="853" alt="image" src="https://github.com/user-attachments/assets/7f92a7ee-f75b-4184-b58b-943f3b8a4251" />
<img width="1557" height="739" alt="image" src="https://github.com/user-attachments/assets/b2af6ad6-b740-4b90-bc43-d601d38f2611" />
<img width="1596" height="811" alt="image" src="https://github.com/user-attachments/assets/e7dc7ca8-11f7-46da-bb97-05feb544a4a1" />
<img width="1543" height="778" alt="image" src="https://github.com/user-attachments/assets/77ebe7c9-d5dd-4a96-a9e6-cdd0eb2c5192" />

---

### Insights e Documentação

#### Principais Padrões Identificados 
- **Variação regional**: Cuiabá/MT e Ribeirão Preto/SP tendem a preços mais altos; Paranaguá/PR e Santos/SP mostram maior volatilidade.  
- **Preço x Quantidade**: grandes volumes costumam pressionar preços para baixo (lei da oferta e demanda).
- **Sazonalidade**: preços do algodão sobem no fim de 2023, caem no início de 2024 e se recuperam em meados de 2024; arroz apresenta estabilidade maior, mas com leve alta no fim de 2024/início de 2025.  
- **Anomalias**: registros negativos e picos extremos sugerem erros de digitação, ajustes ou liquidações atípicas.  

#### Aplicações Práticas no Agronegócio
- **Precificação**: identificar melhores épocas e regiões para venda.  
- **Gestão de risco**: detectar volatilidade para hedge e seguros agrícolas.  
- **Inteligência de mercado**: usar séries históricas como referência para contratos futuros e planejamento de safra.  

#### Limitações da Fonte
- Dados com **erros e valores negativos** em preço/quantidade.  
- Abrangência restrita (foco em algodão e arroz, poucas regiões).  
- Falta de **metadados claros** (unidade de medida, origem primária, tipo de preço).  
- Atualização limitada a registros recentes (sem séries longas prontas).  
