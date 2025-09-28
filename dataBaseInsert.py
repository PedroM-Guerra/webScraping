import psycopg2
import unicodedata
import re


def limpar_titulo(titulo):
    STOPWORDS = {
        "a", "o", "as", "os", "de", "do", "da", "das", "dos", "em", "no", "na", "nos", "nas",
        "por", "para", "com", "um", "uma", "uns", "umas", "e", "ou", "que", "se", "é", "ao"
    }

    # Remove acentos
    titulo = unicodedata.normalize('NFKD', titulo).encode('ASCII', 'ignore').decode('ASCII')

    # Remove caracteres especiais (mantém apenas letras, números e espaço)
    titulo = re.sub(r'[^A-Za-z0-9 ]+', '', titulo)

    # Remove stopwords
    palavras = titulo.split()
    palavras_filtradas = [p for p in palavras if p.lower() not in STOPWORDS]
    
    # Junta e coloca em maiúsculo
    return " ".join(palavras_filtradas).upper()

def salvar_noticia(titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo, dia, mes, ano, semana, quadrimestre, semestre, trimestre):
    
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
    cur = conn.cursor()

    # Verifica se a notícia já existe pelo url_noticia Não insere duplicada
    cur.execute("SELECT 1 FROM noticias WHERE url_noticia = %s", (url_noticia,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return  

    titulo_limpo = limpar_titulo(titulo)

    cur.execute("""
            INSERT INTO noticias (
                titulo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo,
                dia, mes, ano, semana, quadrimestre, semestre, trimestre
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            titulo_limpo, url_noticia, data_hora_noticia, categoria_nome, nome_site, url_veiculo,
            dia, mes, ano, semana, quadrimestre, semestre, trimestre
        ))
    
    conn.commit()
    cur.close()
    conn.close()
