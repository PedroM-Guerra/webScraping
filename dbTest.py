import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")

cur = conn.cursor()

#logica aqui
def salvar_noticia(site_name, url, categoria, titulo, data):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id SERIAL PRIMARY KEY,
            site_name VARCHAR(255),
            url TEXT,
            categoria TEXT,
            titulo TEXT,
            data TEXT
        );
    """)
    cur.execute("""
        INSERT INTO noticias (site_name, url, categoria, titulo, data)
        VALUES (%s, %s, %s, %s, %s)
    """, (site_name, url, categoria, titulo, data))
    conn.commit()
    cur.close()
    conn.close()
