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
- Script principal: **`1 - Scraping.py`**.
- Função: extrair tabelas, tratar preços e datas, salvar dados.
- Desafios enfrentados: tabelas fragmentadas e necessidade de padronização.

#### Dificuldades e Soluções
- O site exibia apenas dados recentes (últimos 13 a 30 dias).
- Não havia histórico completo disponível.
- **Solução:** criei o script **`2 - Scraping_add_dados.py`**, que preencheu a tabela com dados dos últimos 2 anos.
- **Resultado:** expansão da base de **250 linhas** com os dados reais do site para **5.369 registros**.
- Arquivo Inicial(com dados reais do site): **`cepea_dados_1.csv`**.
- Arquivo final: **`cepea_dados_2.csv`**.

---

## Estruturação da Camada RAW

### Organização atual
- Estrutura local do projeto:
![alt text](image.png)

- Objetivo da pasta RAW: armazenar os dados brutos exatamente como coletados, garantindo rastreabilidade e permitindo reprocessamento se necessário. Funciona como "matéria-prima" para camadas posteriores.

### Formatos de arquivo
- **CSV:** simples, compatível com diversas ferramentas; fácil leitura, mas pode ser menos eficiente em volume grande.
- **JSON:** flexível, bom para dados semi-estruturados; arquivos maiores e leitura mais lenta.
- **Parquet:** formato colunar, ideal para grandes volumes; mais eficiente em armazenamento e performance, mas exige compatibilidade.

**Escolha:** usei **CSV** por simplicidade, compatibilidade e facilidade de uso em Python e PostgreSQL.  
Para projetos em escala, Parquet seria mais indicado por reduzir espaço e aumentar performance.

### Organização em AWS S3
- Estrutura sugerida:
(imagem aqui)

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
- O preenchimento automático das tabelas foi feito com um script Python (`postgre.py`), que lê o arquivo **`cepea_dados_2.csv`** e insere os dados diretamente no banco.Automatizar a inserção via script Python aumenta eficiência e reduz erro humano

### Estrutura das tabelas
- **commodities:** tabela com lista única de commodities.
- **registros:** tabela contendo preços, datas, regiões e quantidades, referenciando a tabela commodities.

### Chaves primárias e estrangeiras
- Usei **id** como chave primária em ambas as tabelas, garantindo identificação única de registros e commodities.
- Em `registros`, usei **commodity_id** como chave estrangeira, garantindo integridade referencial e evitando duplicação de dados.
- Essa abordagem melhora a organização, evita inconsistências e facilita consultas com `JOIN`.

### Observação 
- A normalização garante clareza e evita redundância, mas em grandes volumes pode exigir consultas mais complexas.

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
- Arquivo tratado salvo como **`RAW/cepea_dados_3.csv`**.
- Tabelas atualizadas no banco PostgreSQL:
  - `commodities_processados`
  - `registros_processados`

### observação da etapa:
- O processo ETL garante que o banco contenha dados consistentes e organizados, essenciais para consultas eficientes.
- Automatizar o ETL reduz erros manuais e facilita a atualização da base.
- Limitação: mudanças futuras na estrutura dos dados originais exigirão ajustes no script ETL.
- Melhoria possível: adicionar validações automáticas e logging para monitorar falhas durante o processamento.

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


### Observação 
- Separar dados em camadas melhora rastreabilidade e facilita manutenção.
- Essa organização facilita integração com ferramentas analíticas e sistemas em nuvem.
- Em escala, o Data Lake pode ser hospedado em **AWS S3**, **Azure Data Lake** ou similar, com gerenciamento de versionamento e políticas de acesso.

---
## Análises SQL – Tendências e Indicadores

### Consultas realizadas

1. **Preço médio mensal por commodity**
   - Cálculo do preço médio mensal, agrupado por commodity e estado.
   - Uso da função `LAG` para calcular a variação percentual em relação ao mês anterior.
   - Resultado permite identificar tendências de preço e sazonalidades.

2. **Produtos mais negociados**
   - Listagem dos 5 produtos com maior volume negociado no último ano.
   - Análise útil para entender a dinâmica de mercado e focar em commodities estratégicas.

3. **Detecção de registros anômalos**
   - Identificação de registros com preços negativos ou fora de faixa plausível, bem como quantidades inválidas.
   - Fundamental para garantir qualidade dos dados antes de análises mais profundas.

---

### Otimização e Indexação

#### Avaliação de performance
As consultas realizadas na etapa anterior envolvem `JOIN`, `GROUP BY` e funções analíticas (`LAG`). Essas operações podem ter desempenho impactado em bases grandes, especialmente sem índices adequados.

#### Sugestões de otimização
- Criar índices compostos nas colunas mais usadas em filtros e agrupamentos (`commodity_id`, `estado`, `ano`, `mes`).
- Criar índice específico para `commodity_id` para acelerar `JOINs`.
- Considerar particionamento da tabela `registros_processados` por ano ou commodity em casos de volume elevado.
- Monitorar consultas usando `EXPLAIN ANALYZE` para validar ganhos de performance.

#### Justificativa
Essas otimizações melhoram o tempo de resposta das consultas, reduzem custo computacional e garantem escalabilidade, mantendo a integridade dos dados. Índices adequados são essenciais para garantir eficiência em análises periódicas de grandes volumes de dados.

---
### Análise Exploratória em Pandas

#### Descrição da etapa
- Realizei uma análise exploratória utilizando **Pandas**, **Matplotlib** e **Seaborn** para compreender melhor a base de dados tratada (**`cepea_dados_3.csv`**).
- Objetivo: gerar estatísticas descritivas, detectar outliers e visualizar padrões nos dados.

#### Principais análises realizadas
1. **Estatísticas descritivas**
   - Média, mediana e desvio padrão dos preços e quantidades.
   - Permitem compreender tendências centrais e dispersão dos dados.

2. **Detecção de outliers**
   - Utilização do método **IQR (Interquartile Range)** para identificar valores extremos em preços e quantidades.
   - Identificação fundamental para evitar distorções em análises futuras.

3. **Visualizações**
   - **Boxplot**: análise de dispersão e outliers por commodity.
   - **Histogramas**: distribuição de preços e quantidades.
   - **Scatter plot**: relação entre quantidade e preço, segmentada por commodity.

#### Observações críticas
- A análise exploratória revelou padrões importantes e permitiu validar a qualidade dos dados tratados.
- A identificação de outliers é essencial, mas deve ser complementada com análise contextual — alguns valores extremos podem refletir variações reais de mercado.
- Visualizações facilitam interpretação e comunicação dos resultados, especialmente em etapas posteriores de análise ou apresentação para stakeholders.

---
### Visualização em Streamlit

#### Descrição da etapa
- Desenvolvi uma aplicação interativa em **Streamlit** para visualização de preços e tendências das commodities.
- Objetivo: fornecer uma interface intuitiva para exploração dos dados tratados e análises geradas.

#### Funcionalidades implementadas
- **Dashboards interativos** com gráficos de linhas, barras e boxplots.
- **Filtros dinâmicos** por:
  - Produto (commodity)
  - Região
  - Período (data inicial e final)
- **Visualização de tendências**: acompanhamento histórico de preços médios e variações percentuais.
- **Exploração de dados**: possibilidade de analisar distribuições, identificar outliers e comparar commodities.

#### Tecnologias utilizadas
- **Streamlit** para construção da interface web.
- **Pandas** para manipulação dos dados.
- **Matplotlib / Seaborn / Plotly** para geração dos gráficos interativos.

#### Observações críticas
- Streamlit é excelente para prototipagem rápida e exploração interativa, permitindo ajustes em tempo real.
- A performance pode ser impactada para bases muito grandes — soluções incluem pré-processamento e cache.
- Melhorias futuras poderiam incluir autenticação, dashboards customizados para diferentes perfis de usuário e integração com APIs em tempo real.
---


f

