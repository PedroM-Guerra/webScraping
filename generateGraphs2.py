import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import psycopg2

# --- CONFIGURAÇÕES E ESTILO ---
sns.set_style("whitegrid")
plt.style.use('fivethirtyeight')

# Parâmetros de Conexão (Centralizados)
DB_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin123",
    "port": "5432"
}

# ------------- FUNÇÕES DE CONEXÃO E EXTRAÇÃO -------------

def connect_to_db():
    """Tenta estabelecer e retorna a conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("INFO: Conexão com o banco de dados realizada com sucesso.")
        return conn
    except Exception as e:
        print(f"ERRO DE CONEXÃO FATAL: Não foi possível conectar ao DW. {e}")
        # Retorna None em caso de falha de conexão
        return None

def fetch_data_from_dw(conn=None):
    """
    Extrai todos os dados brutos da Tabela Fato e Dimensões usando nomes completos
    e retorna um DataFrame do Pandas.
    """
    if not conn:
        print("ERRO: Conexão com o banco de dados não estabelecida.")
        return pd.DataFrame()

    # --- QUERY SQL CORRIGIDA (SEM APELIDOS) ---
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
    -- Onde F.quantidade_de_noticias, F.fk_tempo, F.fk_categoria, F.fk_veiculo foram assumidos como
    -- Fato_Noticias.quantidade_noticias, Fato_Noticias.sk_tempo, etc., respectivamente.
    """
    
    try:
        df = pd.read_sql(query, conn)
        print("INFO: Dados extraídos do banco de dados com sucesso.")
        
        # Cria a coluna de data completa a partir das colunas de dimensão
        df['data_completa'] = pd.to_datetime(df[['ano', 'mes', 'dia']].rename(columns={'ano':'year', 'mes':'month', 'dia':'day'}))
        
        # Padroniza os nomes das colunas de string para uso nos gráficos
        df = df.rename(columns={'titulo': 'titulo_original', 'url_veiculo': 'url'})
        
        return df
    except Exception as e:
        print(f"ERRO AO EXECUTAR CONSULTA SQL: {e}")
        return pd.DataFrame() # DataFrame vazio em caso de erro

# ------------- FUNÇÕES DE GERAÇÃO DE GRÁFICOS (mantidas) -------------

def plot_news_over_time_by_category(df):
    """Gera o gráfico de Linha: Quantidade de notícias por categoria ao longo do tempo."""
    print("INFO: Gerando Gráfico 1 - Notícias por Categoria ao Longo do Tempo...")
    
    # Agrupa a contagem total de notícias por data e categoria
    df_plot = df.groupby(['data_completa', 'categoria_nome'])['quantidade_noticias'].sum().reset_index()

    # Filtra apenas as categorias mais relevantes para a plotagem (opcional)
    top_categories = df_plot.groupby('categoria_nome')['quantidade_noticias'].sum().nlargest(4).index
    df_plot = df_plot[df_plot['categoria_nome'].isin(top_categories)]

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
    plt.xlabel('Data de Publicação (Mês/Dia)', fontsize=12)
    plt.ylabel('Total de Notícias', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_top_vehicles(df, target_category='mundo'):
    """Gera o gráfico de Barras: Top 3 veículos que mais publicaram sobre um tema."""
    print(f"INFO: Gerando Gráfico 2 - Top 3 Veículos por Notícias sobre '{target_category}'...")

    df_filtered = df[df['categoria_nome'] == target_category]
    df_vehicle_sum = df_filtered.groupby('nome_site')['quantidade_noticias'].sum().reset_index()
    df_top_vehicles = df_vehicle_sum.nlargest(3, 'quantidade_noticias')

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

def generate_word_cloud(df):
    """Gera a Nuvem de Palavras com os títulos mais frequentes."""
    print("INFO: Gerando Gráfico 3 - Nuvem de Palavras dos Títulos...")

    # A coluna renomeada 'titulo_original' é usada aqui
    text = " ".join(title for title in df['titulo_original'].astype(str) if title.strip())

    if not text.strip():
        print("AVISO: String de texto vazia. Não é possível gerar a Nuvem de Palavras.")
        return

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        max_words=100,
        colormap='magma'
    ).generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nuvem de Palavras dos Títulos Mais Frequentes', fontsize=16, fontweight='bold')
    plt.tight_layout(pad=0)
    plt.show()


# ------------- FUNÇÃO PRINCIPAL E EXECUÇÃO -------------

def main():
    """Função principal para execução da análise e visualizações."""
    db_connection = connect_to_db()
    data_df = fetch_data_from_dw(db_connection)

    # Verifica se os dados foram carregados corretamente (não vazio e não None)
    if not data_df.empty:
        # Gera as Visualizações
        plot_news_over_time_by_category(data_df)
        plot_top_vehicles(data_df, target_category='mundo')
        generate_word_cloud(data_df)
    else:
        print("ERRO: Não foi possível obter dados para a visualização. Verifique a conexão e a Query SQL.")

    # Garante que a conexão seja fechada
    if db_connection:
        db_connection.close()
        print("INFO: Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    # Remove a importação e o código de geração de dados falsos do escopo principal
    # e assume que a execução deve ser feita apenas contra o banco de dados.
    main()