## 📄 README.md (Revisado e Limpo)

# 📰 WebScraping de Notícias para Data Warehouse (ETL)

Este projeto de laboratório foca na aplicação prática de **Web Scraping**, na construção de um processo de **ETL (Extract, Transform, Load)** e na modelagem e armazenamento de dados em um **Data Warehouse (DW)** utilizando **PostgreSQL**.

O objetivo é coletar dados de notícias do portal **Globo.com**, estruturá-los em dimensões (temporais, categóricas e de veículos) e, finalmente, gerar **visualizações de análise de dados**.

-----

## 🚀 Funcionalidades e Estrutura dos Scripts

O projeto é dividido em três etapas principais, gerenciadas por scripts Python:

### 1\. Criação do Banco de Dados (`dataBaseCreate.py`)

Define a estrutura do **Data Warehouse** (esquema Estrela), incluindo as tabelas Fato e Dimensões (**Tempo, Notícia, Categoria, Veículo**).

### 2\. Scraping e ETL (`scrapingGlobo.py` e `dataBaseInsert.py`)

  * **Extração (E):** Coleta títulos, URLs, datas e metadados da home do portal Globo.com.
  * **Transformação (T):** Realiza a limpeza de texto e calcula as dimensões temporais (dia, mês, trimestre, etc.).
  * **Carregamento (L):** Insere os dados nas dimensões e na tabela **`Fato_Noticias`** do DW.

### 3\. Visualização de Dados (`generateGraphs.py`)

Utiliza os dados consolidados no DW (lidos em um único **DataFrame** Pandas) para gerar diversos gráficos analíticos, incluindo tendências por categoria, distribuição por veículo e Nuvem de Palavras.

-----

## 📦 Estrutura do Data Warehouse

O DW utiliza o **esquema Estrela** com a seguinte modelagem:

| Tabela | Conteúdo Principal |
| :--- | :--- |
| **`Fato_Noticias`** | Contagem de notícias (fatos) e chaves estrangeiras das dimensões. |
| **`Dim_Tempo`** | Detalhes temporais (ano, mês, dia, semana, trimestre, etc.). |
| **`Dim_Noticia`** | Metadados da notícia (título, URL, data/hora original). |
| **`Dim_Categoria`** | Nome da categoria (e.g., 'mundo', 'politica'). |
| **`Dim_Veiculo`** | Informações sobre o site/veículo (nome, URL). |

-----

## 🛠️ Tecnologias Utilizadas

  * **Linguagem:** Python
  * **Banco de Dados:** PostgreSQL
  * **Web Scraping:** `requests`, `BeautifulSoup`
  * **ETL/Acesso DB:** `psycopg2`, `pandas`
  * **Visualização:** `matplotlib`, `seaborn`, `wordcloud`

-----

## ⚙️ Como Executar o Projeto

Siga os passos abaixo para configurar e rodar o projeto localmente.

### 1\. Pré-requisitos

1.  **PostgreSQL:** O serviço deve estar rodando localmente (assumindo `localhost:5432`).
2.  **Credenciais:** As credenciais de acesso ao DB estão configuradas nos scripts (DB: `postgres`, User: `postgres`, Pass: `admin123`).
3.  **Ambiente Python:** Instale as bibliotecas necessárias:
    ```bash
    pip install psycopg2-binary requests beautifulsoup4 pandas matplotlib seaborn wordcloud
    ```

### 2\. Configurar o Banco de Dados

Execute o script de criação das tabelas para configurar a estrutura do DW:

```bash
python dataBaseCreate.py
```

### 3\. Rodar o Web Scraping e o ETL

Execute o script principal de scraping para coletar as notícias e carregá-las no DW:

```bash
python scrapingGlobo.py
```

### 4\. Gerar os Gráficos de Análise

Com os dados populados, execute o script de visualização:

```bash
python generateGraphs.py
```

Este script lerá todos os dados do DW e exibirá os 6 gráficos analíticos na tela.
