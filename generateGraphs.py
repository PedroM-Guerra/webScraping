import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import sys

# --- CONFIGURAÇÕES GLOBAIS ---
# Stopwords em Português para a Nuvem de Palavras
STOPWORDS_PT = set([
    'noticia', 'notícias', 'um', 'uma', 'o', 'a', 'os', 'as', 'e', 'do', 'da', 
    'dos', 'das', 'no', 'na', 'nos', 'nas', 'de', 'para', 'com', 'por', 'em', 
    'é', 'ser', 'ao', 'à', 'se', 'mas', 'ou', 'como', 'que', 'qual', 'pelo', 'pela',
    'mais', 'menos', 'após', 'diz', 'vai', 'sobre', 'ter', 'pode', 'apos', 'faz'
])



def conectar_db():
    """Tenta estabelecer a conexão com o banco de dados e retorna o objeto de conexão."""
    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        print(f"ERRO: Falha ao conectar ao banco de dados. Detalhes: {e}")
        sys.exit(1) # Sai do programa em caso de falha


def gerar_nuvem_palavras(conn):
    """
    Gera a Nuvem de Palavras a partir dos títulos das notícias.
    Assume que os títulos já estão limpos e pré-processados.
    """
    print("\n--- 1. Gerando Nuvem de Palavras ---")
    
    query_titulos = """
    SELECT titulo FROM Dim_Noticia;
    """

    try:
        df_titulos = pd.read_sql(query_titulos, conn)
    except Exception as e:
        print(f"ERRO ao obter títulos das notícias: {e}")
        return

    # Concatena todos os títulos em uma única string
    text_content = ' '.join(df_titulos['titulo'].dropna().tolist())

    if not text_content:
        print("Atenção: Nenhum conteúdo de título encontrado para a Nuvem de Palavras.")
        return

    # Gera a Nuvem de Palavras
    wordcloud = WordCloud(
        width=1000, 
        height=600, 
        background_color='white', 
        stopwords=STOPWORDS_PT,
        min_font_size=10,
        max_words=100, 
        colormap='cividis' 
    ).generate(text_content)

    # Exibe a Nuvem de Palavras
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off') 
    plt.title('Nuvem de Palavras dos Títulos de Notícias', fontsize=16, fontweight='bold')
    plt.show()

def gerar_distribuicao_veiculos(conn):
    """
    Gera o gráfico de barras mostrando a distribuição total de notícias por todos os veículos.
    """
    print("\n--- 2. Gerando Distribuição de Notícias por Veículo ---")

    # CONSULTA SQL CORRIGIDA: Não usa LIMIT, ordena apenas para visualização
    query_veiculos = """
    SELECT
        dv.nome_site,
        SUM(fn.quantidade_noticias) AS total_noticias
    FROM 
        Fato_Noticias fn
    JOIN 
        Dim_Veiculo dv ON fn.sk_veiculo = dv.sk_veiculo
    GROUP BY 
        dv.nome_site
    ORDER BY 
        total_noticias DESC; -- Apenas ordena para melhor visualização, mas pega todos.
    """

    try:
        df_veiculos = pd.read_sql(query_veiculos, conn)
    except Exception as e:
        print(f"ERRO ao obter dados de veículos: {e}")
        return

    if df_veiculos.empty:
        print("Atenção: Nenhum dado encontrado para gerar o gráfico de veículos.")
        return

    print("Distribuição de Notícias por Veículos:")
    print(df_veiculos)

    # Geração do gráfico de barras horizontal (Melhor para mais de 5 itens)
    sns.set_style("whitegrid")
    # A altura da figura deve ser ajustada para o número de veículos (e.g., 0.5 por veículo)
    altura_figura = max(6, len(df_veiculos) * 0.5) 
    plt.figure(figsize=(10, altura_figura))

    barplot_veiculos = sns.barplot(
        x='total_noticias',     # Eixo X: Contagem
        y='nome_site',          # Eixo Y: Nomes dos Veículos
        data=df_veiculos, 
        palette='magma'
    )

    plt.title('Distribuição Total de Notícias por Veículo de Mídia', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Notícias Publicadas', fontsize=13)
    plt.ylabel('Veículo de Mídia', fontsize=13)
    
    # Adiciona os rótulos de valores ao lado das barras
    for index, value in enumerate(df_veiculos['total_noticias']):
        barplot_veiculos.text(
            value + df_veiculos['total_noticias'].max() * 0.01, 
            index, 
            str(value), 
            color='black', 
            ha="left", 
            va='center', 
            fontsize=10
        )

    plt.tight_layout()
    plt.show()

def gerar_top_categorias(conn):
    """
    Gera o gráfico de barras das categorias com a maior quantidade de notícias (Top 10).
    """
    print("\n--- 3. Gerando Gráfico de Categorias Mais Frequentes ---")
    
    query_categorias = """
    SELECT
        dc.categoria_nome,
        SUM(fn.quantidade_noticias) AS total_noticias
    FROM 
        Fato_Noticias fn
    JOIN 
        Dim_Categoria dc ON fn.sk_categoria = dc.sk_categoria
    GROUP BY 
        dc.categoria_nome
    ORDER BY 
        total_noticias DESC
    LIMIT 10; -- Top 10 categorias
    """
    
    try:
        df_categorias = pd.read_sql(query_categorias, conn)
    except Exception as e:
        print(f"ERRO ao obter Top Categorias: {e}")
        return

    if df_categorias.empty:
        print("Atenção: Nenhum dado encontrado para gerar o gráfico de categorias.")
        return

    # Geração do gráfico de barras horizontal (melhor para muitas categorias)
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 7))

    barplot_categorias = sns.barplot(
        x='total_noticias', 
        y='categoria_nome', 
        data=df_categorias, 
        palette='plasma_r' # Paleta de cores invertida
    )

    plt.title('Top 10 Categorias com Maior Quantidade de Notícias', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Notícias Publicadas', fontsize=13)
    plt.ylabel('Categoria', fontsize=13)
    
    # Adiciona os rótulos de valores ao lado das barras
    for index, value in enumerate(df_categorias['total_noticias']):
        barplot_categorias.text(
            value + df_categorias['total_noticias'].max() * 0.01, 
            index, 
            str(value), 
            color='black', 
            ha="left", 
            va='center', 
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


def gerar_tendencia_categoria(conn, num_top_categorias=5):
    """
    Gera um gráfico de linha mostrando a tendência mensal da quantidade de notícias 
    para as categorias mais frequentes.
    """
    print(f"\n--- 4. Gerando Tendência Mensal para Top {num_top_categorias} Categorias ---")

    # A consulta SQL agrega por Mês/Ano (para a série temporal) e por Categoria.
    # Usamos o Subselect/CTE para primeiramente identificar as categorias mais relevantes.
    query_tendencia = f"""
    WITH TopCategorias AS (
        SELECT
            sk_categoria
        FROM
            Fato_Noticias
        GROUP BY
            sk_categoria
        ORDER BY
            SUM(quantidade_noticias) DESC
        LIMIT {num_top_categorias}
    )
    SELECT
        dt.ano,
        dt.mes,
        dc.categoria_nome,
        SUM(fn.quantidade_noticias) AS total_noticias
    FROM 
        Fato_Noticias fn
    JOIN 
        Dim_Tempo dt ON fn.sk_tempo = dt.sk_tempo
    JOIN 
        Dim_Categoria dc ON fn.sk_categoria = dc.sk_categoria
    WHERE
        fn.sk_categoria IN (SELECT sk_categoria FROM TopCategorias)
    GROUP BY
        dt.ano,
        dt.mes,
        dc.categoria_nome
    ORDER BY
        dt.ano,
        dt.mes;
    """

    try:
        df_tendencia = pd.read_sql(query_tendencia, conn)
    except Exception as e:
        print(f"ERRO ao obter dados de tendência: {e}")
        return

    if df_tendencia.empty:
        print("Atenção: Nenhum dado encontrado para gerar o gráfico de tendência.")
        return

    # Prepara o eixo X: Cria uma coluna de data formatada (Ano-Mês)
    df_tendencia['periodo'] = df_tendencia['ano'].astype(str) + '-' + df_tendencia['mes'].apply(lambda x: '{:02d}'.format(x))
    
    # Define o estilo do gráfico
    sns.set_style("whitegrid")
    plt.figure(figsize=(14, 7))

    # Gera o gráfico de linha (Line Plot)
    lineplot = sns.lineplot(
        x='periodo', 
        y='total_noticias', 
        hue='categoria_nome', # Usamos a categoria para diferenciar as linhas
        data=df_tendencia,
        marker='o' # Adiciona marcadores para visualizar cada ponto de dados
    )

    # Configuração dos rótulos e título
    plt.title(f'Tendência Mensal de Notícias para as Top {num_top_categorias} Categorias', fontsize=16, fontweight='bold')
    plt.xlabel('Período (Ano-Mês)', fontsize=13)
    plt.ylabel('Total de Notícias', fontsize=13)
    
    # Melhorar a visualização do eixo X (exibe menos rótulos se houver muitos meses)
    n_ticks = 10
    ticks_to_show = df_tendencia['periodo'].unique()[::len(df_tendencia['periodo'].unique()) // n_ticks]
    plt.xticks(ticks=ticks_to_show, rotation=45, ha='right')
    
    plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def main():
    """Função principal que coordena a execução de todas as tarefas."""
    conn = conectar_db()
    
    try:
        # 1. Nuvem de Palavras
        # gerar_nuvem_palavras(conn)
        
        # 2. Distribuição de Veículos
        # gerar_distribuicao_veiculos(conn) 
        
        # 3. Top Categorias (BARRAS)
        # gerar_top_categorias(conn)
        
        # 4. TENDÊNCIA POR CATEGORIA (LINHA)
        gerar_tendencia_categoria(conn, num_top_categorias=5)
        
    finally:
        # Garante que a conexão seja sempre fechada
        if conn:
            conn.close()
            print("\nConexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()