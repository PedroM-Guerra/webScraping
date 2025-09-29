import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import psycopg2
import sys 

# config de stopwords e estilo
sns.set_style("whitegrid")
plt.style.use('fivethirtyeight')

STOPWORDS_PT = set([
    'noticia', 'notícias', 'um', 'uma', 'o', 'a', 'os', 'as', 'e', 'do', 'da', 
    'dos', 'das', 'no', 'na', 'nos', 'nas', 'de', 'para', 'com', 'por', 'em', 
    'é', 'ser', 'ao', 'à', 'se', 'mas', 'ou', 'como', 'que', 'qual', 'pelo', 'pela',
    'menos', 'após', 'diz', 'vai', 'sobre', 'ter', 'pode', 'apos', 'faz', 'mais' 
])

# Parâmetros de Conexão 
DB_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin123",
    "port": "5432"
}

# conexão e extração de dados

def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("INFO: Conexão com o banco de dados realizada com sucesso.")
        return conn
    except Exception as e:
        print(f"ERRO DE CONEXÃO FATAL: Não foi possível conectar ao DW. {e}")
        return None

def fetch_data_from_dw(conn=None):
    if not conn:
        print("ERRO: Conexão com o banco de dados não estabelecida.")
        return pd.DataFrame()

    query = """
    SELECT
        Dim_Tempo.dia,
        Dim_Tempo.mes,
        Dim_Tempo.ano,
        Dim_Categoria.categoria_nome,
        Dim_Veiculo.nome_site,
        Dim_Veiculo.url_veiculo, 
        Dim_Noticia.titulo, 
        Fato_Noticias.quantidade_noticias
    FROM
        Fato_Noticias
    JOIN 
        Dim_Tempo ON Fato_Noticias.sk_tempo = Dim_Tempo.sk_tempo
    JOIN 
        Dim_Categoria ON Fato_Noticias.sk_categoria = Dim_Categoria.sk_categoria
    JOIN 
        Dim_Veiculo ON Fato_Noticias.sk_veiculo = Dim_Veiculo.sk_veiculo
    JOIN
        Dim_Noticia ON Fato_Noticias.sk_noticia = Dim_Noticia.sk_noticia
    """
    
    try:
        df = pd.read_sql(query, conn)
        print("INFO: Dados extraídos do banco de dados com sucesso.")
        
        # Cria a coluna de data completa
        df['data_completa'] = pd.to_datetime(df[['ano', 'mes', 'dia']].rename(columns={'ano':'year', 'mes':'month', 'dia':'day'}))
        
        # Padroniza os nomes das colunas de string
        df = df.rename(columns={'titulo': 'titulo_original', 'url_veiculo': 'url'})
        
        return df
    except Exception as e:
        print(f"ERRO AO EXECUTAR CONSULTA SQL: {e}")
        return pd.DataFrame() 


# geração de gráficos

# noticias ao longo do tempo por categoria
def plot_news_over_time_by_category(df):
    print("\n--- Gerando Gráfico 1 (Linha) ---")
    
    df_plot = df.groupby(['data_completa', 'categoria_nome'])['quantidade_noticias'].sum().reset_index()

    top_categories = df_plot.groupby('categoria_nome')['quantidade_noticias'].sum().nlargest(4).index
    df_plot = df_plot[df_plot['categoria_nome'].isin(top_categories)]

    if df_plot.empty:
        print("AVISO: Dados insuficientes para o Gráfico 1.")
        return

    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=df_plot,
        x='data_completa',
        y='quantidade_noticias',
        hue='categoria_nome',
        marker='o',
        markersize=5,
        linewidth=2
    )

    plt.title('Tendência: Volume de Notícias por Categoria (Top 4)', fontsize=16, fontweight='bold')
    plt.xlabel('Data de Publicação', fontsize=12)
    plt.ylabel('Total de Notícias', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

# top veiculos por categoria específica
def plot_top_vehicles(df, target_category='mundo'):
    print(f"\n--- Gerando Gráfico 2 (Barras) - Top 3 Veículos em '{target_category}' ---")

    df_filtered = df[df['categoria_nome'] == target_category]
    df_vehicle_sum = df_filtered.groupby('nome_site')['quantidade_noticias'].sum().reset_index()
    df_top_vehicles = df_vehicle_sum.nlargest(3, 'quantidade_noticias')

    if df_top_vehicles.empty:
        print(f"AVISO: Não há dados para a categoria '{target_category}' no Gráfico 2.")
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_top_vehicles,
        x='quantidade_noticias',
        y='nome_site',
        palette='viridis',
        edgecolor='black'
    )

    plt.title(f'Top 3 Veículos que mais publicaram sobre {target_category}', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Notícias Publicadas', fontsize=12)
    plt.ylabel('Veículo (Site)', fontsize=12)
    plt.tight_layout()
    plt.show()

# Nuvem de Palavras dos títulos das notícias
def plot_word_cloud(df):
    print("\n--- Gerando Gráfico 3 (Nuvem de Palavras) ---")

    text_content = ' '.join(df['titulo_original'].dropna().astype(str).tolist())

    if not text_content.strip():
        print("AVISO: Nenhum conteúdo de título encontrado para a Nuvem de Palavras.")
        return

    wordcloud = WordCloud(
        width=1000, 
        height=600, 
        background_color='white', 
        stopwords=STOPWORDS_PT,
        min_font_size=10,
        max_words=100, 
        colormap='cividis' 
    ).generate(text_content)

    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off') 
    plt.title('Nuvem de Palavras dos Títulos de Notícias', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()


# Distribuição de noticias totais de veículos 
def plot_all_vehicles_distribution(df):
    print("\n--- Gerando Gráfico 4 (Barras) - Distribuição Total por Veículo ---")

    # Agregação em Pandas: Conta o total de notícias por 'nome_site'
    df_veiculos = df.groupby('nome_site')['quantidade_noticias'].sum().reset_index()
    df_veiculos = df_veiculos.sort_values(by='quantidade_noticias', ascending=False)
    
    if df_veiculos.empty:
        print("AVISO: Nenhum dado encontrado para gerar o gráfico de veículos.")
        return

    altura_figura = max(6, len(df_veiculos) * 0.4) 
    plt.figure(figsize=(10, altura_figura))

    barplot_veiculos = sns.barplot(
        x='quantidade_noticias', 
        y='nome_site', 
        data=df_veiculos, 
        palette='magma'
    )

    plt.title('Distribuição Total de Notícias por Veículo de Mídia', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Notícias Publicadas', fontsize=13)
    plt.ylabel('Veículo de Mídia', fontsize=13)
    
    max_val = df_veiculos['quantidade_noticias'].max()
    for index, value in enumerate(df_veiculos['quantidade_noticias']):
        barplot_veiculos.text(
            value + max_val * 0.01, 
            index, 
            f'{value:,}', 
            color='black', 
            ha="left", 
            va='center', 
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


# Top N Categorias
def plot_top_categories(df, num_top_categorias=10):
    print(f"\n--- Gerando Gráfico 5 (Barras) - Top {num_top_categorias} Categorias ---")
    
    # Agregação em Pandas: Conta o total de notícias por 'categoria_nome' e pega o Top N
    df_categorias = df.groupby('categoria_nome')['quantidade_noticias'].sum().reset_index()
    df_top_categorias = df_categorias.nlargest(num_top_categorias, 'quantidade_noticias')
    
    if df_top_categorias.empty:
        print("AVISO: Nenhum dado encontrado para gerar o gráfico de categorias.")
        return

    plt.figure(figsize=(10, 7))

    barplot_categorias = sns.barplot(
        x='quantidade_noticias', 
        y='categoria_nome', 
        data=df_top_categorias, 
        palette='plasma_r'
    )

    plt.title(f'Top {num_top_categorias} Categorias com Maior Quantidade de Notícias', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Notícias Publicadas', fontsize=13)
    plt.ylabel('Categoria', fontsize=13)
    
    max_val = df_top_categorias['quantidade_noticias'].max()
    for index, value in enumerate(df_top_categorias['quantidade_noticias']):
        barplot_categorias.text(
            value + max_val * 0.01, 
            index, 
            f'{value:,}', 
            color='black', 
            ha="left", 
            va='center', 
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


# FUNÇÃO PRINCIPAL E EXECUÇÃO

def main():
    db_connection = connect_to_db()
    data_df = fetch_data_from_dw(db_connection)

    # Verifica se os dados foram carregados corretamente (não vazio e não None)
    if not data_df.empty:
        # Gera as Visualizações
        plot_news_over_time_by_category(data_df)
        plot_top_vehicles(data_df, target_category='mundo')
        plot_word_cloud(data_df) 
        plot_all_vehicles_distribution(data_df) 
        plot_top_categories(data_df)


    else:
        print("ERRO: Não foi possível obter dados para a visualização. Verifique a conexão e a Query SQL.")

    # Garante que a conexão seja fechada
    if db_connection:
        db_connection.close()
        print("INFO: Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()