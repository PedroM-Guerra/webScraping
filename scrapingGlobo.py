import requests
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
import re

from dataBaseInsert import inserir_noticia_dw, salvar_noticia
from dataBaseCreate import create_database

def get_news():
    create_database()

    url = 'https://www.globo.com/'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    noticias = soup.find_all('a')
    tgt_class1 = 'post__title'
    tgt_class2 = 'post-multicontent__link--title__text'

    news_dict = {}

    for noticia in noticias:
        if (noticia.h2 != None) and (noticia.h2.get('class') != None):
            if tgt_class1 in noticia.h2.get('class'):
                news_dict[noticia.h2.text] = noticia.get('href')

            if tgt_class2 in noticia.h2.get('class'):
                news_dict[noticia.h2.text] = noticia.get('href')

            access_news(noticia.get('href'))
            

    return news_dict

def limpar_texto(texto):
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

    # Remove caracteres especiais (mantém apenas letras, números e espaço)
    texto = re.sub(r'[^A-Za-z0-9 ]+', '', texto)

    # Coloca em maiúsculo
    return texto.upper()

def limpar_titulo(titulo):
    STOPWORDS = {
        "a", "o", "as", "os", "de", "do", "da", "das", "dos", "em", "no", "na", "nos", "nas",
        "por", "para", "com", "um", "uma", "uns", "umas", "e", "ou", "que", "se", "é", "ao"
    }
    # Remove acentos
    titulo = unicodedata.normalize('NFKD', titulo).encode('ASCII', 'ignore').decode('ASCII')

    # Remove caracteres especiais
    titulo = re.sub(r'[^A-Za-z0-9 ]+', '', titulo)

    # Remove stopwords
    palavras = titulo.split()
    palavras_filtradas = [p for p in palavras if p.lower() not in STOPWORDS]

    # Junta e coloca em maiúsculo
    return " ".join(palavras_filtradas).upper()

def access_news(newsUrl):
    page = requests.get(newsUrl)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    siteName = get_veiculo(soup)
    category, title, siteUrl  = get_categoria(soup, newsUrl)
    date, year, month, day, week, trimester, quadrimester, semester = get_date(soup)

    # Não inclui notícias sem data
    if date == "0001-01-01 00:00:00":
        return
    
     # Tratar título e nome do site
    title = limpar_titulo(title)
    siteName = limpar_texto(siteName)

    print_info(siteName, category, title, newsUrl, date, year, month, day, week, trimester, quadrimester, semester)

    #salva num banco normal e num data warehouse
    salvar_noticia(title, newsUrl, date, category, siteName, siteUrl, day, month, year, week, quadrimester, semester, trimester)
    inserir_noticia_dw(title, newsUrl, date, category, siteName, siteUrl, day, month, year, week, quadrimester, semester, trimester)

def print_info(siteName, category, title, newsUrl, date, year, month, day, week, trimester, quadrimester, semester):
    print("\n--------------------------------------------------------")

    print(f"Nome do site (veículo): {siteName}")
    print(f"Link: {newsUrl}")
    print(f"Categoria: {category}")
    print(f"Título da Notícia: {title}")
    print(f"Data da Notícia: {date}")

    print(f"Ano: {year}")
    print(f"Mês: {month}")
    print(f"Dia: {day}")
    print(f"Semana: {week}")
    print(f"Trimestre: {trimester}")
    print(f"Quadrimestre: {quadrimester}")
    print(f"Semestre: {semester}")

def get_veiculo(soup):
    nomeSite = "NA"

    #nome site
    meta_site = soup.find("meta", property="og:site_name")
    nomeSite = meta_site['content']


    return nomeSite

def get_categoria(soup, url):
    # Extrai siteUrl e categoria pela URL
    try:
        # Remove 'https://' ou 'http://'
        url_path = url.split('//')[-1]
        # Separa pelo '/' e pega o primeiro elemento (índice 0) para siteUrl
        site_url = url_path.split('/')[0] if len(url_path.split('/')) > 0 else "NA"
        # Pega o segundo elemento (índice 1) para categoria
        categoria_url = url_path.split('/')[1] if len(url_path.split('/')) > 1 else "NA"
    except Exception:
        site_url = "NA"
        categoria_url = "NA"

    # Título
    title = soup.title.string if soup.title else "NA"

    return categoria_url, title, site_url

def get_date(soup):
    dt_str = dt_str = "0001-01-01 00:00:00"
    year = month = day = week = trimester = quadrimester = semester = 0

    #data
    date = soup.find('time', itemprop='datePublished')

    if date:
        dt_str = date.get('datetime') 
        dt = datetime.fromisoformat(dt_str)

        year = dt.year
        month = dt.month
        day = dt.day
        week = dt.isocalendar()[1]
        trimester = (month - 1) // 3 + 1
        quadrimester = (month - 1) // 4 + 1
        semester = (month - 1) // 6 + 1

    return dt_str, year, month, day, week, trimester, quadrimester, semester
    
get_news()


