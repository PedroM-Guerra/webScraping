import psycopg2


def salvar_noticia(titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo, dia, mes, ano, semana, quadrimestre, semestre, trimestre):
    
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
    cur = conn.cursor()

    # Verifica se a notícia já existe pelo url_noticia Não insere duplicada
    cur.execute("SELECT 1 FROM noticias WHERE url_noticia = %s", (url_noticia,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return  

    cur.execute("""
            INSERT INTO noticias (
                titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo,
                dia, mes, ano, semana, quadrimestre, semestre, trimestre
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo,
            dia, mes, ano, semana, quadrimestre, semestre, trimestre
        ))
    
    conn.commit()
    cur.close()
    conn.close()


def inserir_noticia_dw(titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo,
                       dia, mes, ano, semana, quadrimestre, semestre, trimestre):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
    cur = conn.cursor()

    # 1. Dim_Categoria
    cur.execute("SELECT sk_categoria FROM Dim_Categoria WHERE categoria_nome = %s", (categoria_nome,))
    res = cur.fetchone()
    if res:
        sk_categoria = res[0]
    else:
        cur.execute("INSERT INTO Dim_Categoria (categoria_nome) VALUES (%s) RETURNING sk_categoria", (categoria_nome,))
        sk_categoria = cur.fetchone()[0]

    # 2. Dim_Veiculo
    cur.execute("SELECT sk_veiculo FROM Dim_Veiculo WHERE url_veiculo = %s", (url_veiculo,))
    res = cur.fetchone()
    if res:
        sk_veiculo = res[0]
    else:
        cur.execute("INSERT INTO Dim_Veiculo (nome_site, url_veiculo) VALUES (%s, %s) RETURNING sk_veiculo", (nome_site, url_veiculo))
        sk_veiculo = cur.fetchone()[0]

    # 3. Dim_Noticia
    cur.execute("SELECT sk_noticia FROM Dim_Noticia WHERE url_noticia = %s", (url_noticia,))
    res = cur.fetchone()
    if res:
        sk_noticia = res[0]
    else:
        cur.execute(
            "INSERT INTO Dim_Noticia (titulo, data_hora_noticia, url_noticia) VALUES (%s, %s, %s) RETURNING sk_noticia",
            (titulo, data_hora_noticia, url_noticia)
        )
        sk_noticia = cur.fetchone()[0]

    # 4. Dim_Tempo (assume que já está pré-carregada)
    cur.execute(
        "SELECT sk_tempo FROM Dim_Tempo WHERE ano = %s AND mes = %s AND dia = %s",
        (ano, mes, dia)
    )
    res = cur.fetchone()
    if res:
        sk_tempo = res[0]
    else:
        # Se não existir, insere (opcional, depende do seu modelo)
        cur.execute(
            "INSERT INTO Dim_Tempo (dia, mes, ano, semana, quadrimestre, semestre, trimestre) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING sk_tempo",
            (dia, mes, ano, semana, quadrimestre, semestre, trimestre)
        )
        sk_tempo = cur.fetchone()[0]

    # 5. Fato_Noticias
    try:
        cur.execute(
            "INSERT INTO Fato_Noticias (sk_categoria, sk_veiculo, sk_tempo, sk_noticia, quantidade_noticias) VALUES (%s, %s, %s, %s, %s)",
            (sk_categoria, sk_veiculo, sk_tempo, sk_noticia, 1)
        )
    except psycopg2.errors.UniqueViolation:
        conn.rollback()  # ignora duplicidade de fato
    else:
        conn.commit()

    cur.close()
    conn.close()