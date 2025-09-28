import psycopg2

def create_database():
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="admin123", port="5432")
    cur = conn.cursor()
    cur.execute("""
CREATE SEQUENCE IF NOT EXISTS noticias_id_seq;

CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER NOT NULL DEFAULT nextval('noticias_id_seq'),
                titulo VARCHAR(255) NOT NULL,
                url_noticia VARCHAR(1024) NOT NULL UNIQUE,
                data_hora_noticia TIMESTAMP NOT NULL,
                categoria_nome VARCHAR(255) NOT NULL,
                nome_site VARCHAR(255) NOT NULL,
                url_veiculo VARCHAR(1024) NOT NULL,
                dia SMALLINT NOT NULL,
                mes SMALLINT NOT NULL,
                ano SMALLINT NOT NULL,
                semana SMALLINT NOT NULL,
                quadrimestre SMALLINT NOT NULL,
                semestre SMALLINT NOT NULL,
                trimestre SMALLINT NOT NULL,
                CONSTRAINT noticias_pk PRIMARY KEY (id)
);

ALTER SEQUENCE noticias_id_seq OWNED BY noticias.id;

-- Dim_Noticia
CREATE SEQUENCE IF NOT EXISTS public.dim_noticia_sk_noticia_seq_1;

CREATE TABLE IF NOT EXISTS public.Dim_Noticia (
    sk_noticia INTEGER NOT NULL DEFAULT nextval('public.dim_noticia_sk_noticia_seq_1'),
    titulo VARCHAR(512) NOT NULL,
    data_hora_noticia TIMESTAMP NOT NULL,
    url_noticia VARCHAR(1024) NOT NULL,
    CONSTRAINT dim_noticia_pk PRIMARY KEY (sk_noticia),
    CONSTRAINT dim_noticia_url_unique UNIQUE (url_noticia)
);

ALTER SEQUENCE public.dim_noticia_sk_noticia_seq_1 OWNED BY public.Dim_Noticia.sk_noticia;

-- Dim_Veiculo
CREATE SEQUENCE IF NOT EXISTS public.dim_veiculo_sk_veiculo_seq_1;

CREATE TABLE IF NOT EXISTS public.Dim_Veiculo (
    sk_veiculo INTEGER NOT NULL DEFAULT nextval('public.dim_veiculo_sk_veiculo_seq_1'),
    nome_site VARCHAR(255) NOT NULL,
    url_veiculo VARCHAR(1024) NOT NULL,
    CONSTRAINT dim_veiculo_pk PRIMARY KEY (sk_veiculo),
    CONSTRAINT dim_veiculo_url_unique UNIQUE (url_veiculo)
);

ALTER SEQUENCE public.dim_veiculo_sk_veiculo_seq_1 OWNED BY public.Dim_Veiculo.sk_veiculo;

-- Dim_Categoria
CREATE SEQUENCE IF NOT EXISTS public.dim_categoria_sk_categoria_seq_1;

CREATE TABLE IF NOT EXISTS public.Dim_Categoria (
    sk_categoria INTEGER NOT NULL DEFAULT nextval('public.dim_categoria_sk_categoria_seq_1'),
    categoria_nome VARCHAR(255) NOT NULL,
    CONSTRAINT dim_categoria_pk PRIMARY KEY (sk_categoria),
    CONSTRAINT dim_categoria_nome_unique UNIQUE (categoria_nome)
);

ALTER SEQUENCE public.dim_categoria_sk_categoria_seq_1 OWNED BY public.Dim_Categoria.sk_categoria;

-- Dim_Tempo
CREATE SEQUENCE IF NOT EXISTS public.dim_tempo_sk_tempo_seq_1;

CREATE TABLE IF NOT EXISTS public.Dim_Tempo (
    sk_tempo INTEGER NOT NULL DEFAULT nextval('public.dim_tempo_sk_tempo_seq_1'),
    dia SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    ano SMALLINT NOT NULL,
    semana SMALLINT NOT NULL,
    quadrimestre SMALLINT NOT NULL,
    semestre SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    CONSTRAINT dim_tempo_pk PRIMARY KEY (sk_tempo)
);

ALTER SEQUENCE public.dim_tempo_sk_tempo_seq_1 OWNED BY public.Dim_Tempo.sk_tempo;

-- Fato_Noticias
CREATE TABLE IF NOT EXISTS public.Fato_Noticias (
    sk_categoria INTEGER NOT NULL,
    sk_veiculo INTEGER NOT NULL,
    sk_tempo INTEGER NOT NULL,
    sk_noticia INTEGER NOT NULL,
    quantidade_noticias INTEGER NOT NULL,
    CONSTRAINT fato_noticias_pk PRIMARY KEY (sk_noticia, sk_tempo, sk_categoria, sk_veiculo)
);

-- Chaves Estrangeiras (só cria se não existir)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'dim_noticia_fato_noticias_fk'
    ) THEN
        ALTER TABLE public.Fato_Noticias 
            ADD CONSTRAINT dim_noticia_fato_noticias_fk
            FOREIGN KEY (sk_noticia)
            REFERENCES public.Dim_Noticia (sk_noticia)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
            NOT DEFERRABLE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'dim_veiculo_fato_noticias_fk'
    ) THEN
        ALTER TABLE public.Fato_Noticias 
            ADD CONSTRAINT dim_veiculo_fato_noticias_fk
            FOREIGN KEY (sk_veiculo)
            REFERENCES public.Dim_Veiculo (sk_veiculo)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
            NOT DEFERRABLE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'dim_categoria_fato_noticias_fk'
    ) THEN
        ALTER TABLE public.Fato_Noticias 
            ADD CONSTRAINT dim_categoria_fato_noticias_fk
            FOREIGN KEY (sk_categoria)
            REFERENCES public.Dim_Categoria (sk_categoria)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
            NOT DEFERRABLE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'dim_tempo_fato_noticias_fk'
    ) THEN
        ALTER TABLE public.Fato_Noticias 
            ADD CONSTRAINT dim_tempo_fato_noticias_fk
            FOREIGN KEY (sk_tempo)
            REFERENCES public.Dim_Tempo (sk_tempo)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
            NOT DEFERRABLE;
    END IF;
END $$;

    """)

    conn.commit()
    cur.close()
    conn.close()
