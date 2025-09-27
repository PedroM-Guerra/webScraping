import requests
from bs4 import BeautifulSoup
from datetime import datetime

from dbTest import salvar_noticia



#import sqlite3
#conn = sqlite3.connect('noticias.db')

def get_news():
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

def access_news(newsUrl):
    page = requests.get(newsUrl)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    siteName = get_veiculo(soup, newsUrl)
    category, title  = get_categoria(soup)
    date, year, month, day, week, trimester, quadrimester, semester = get_date(soup)

    print_info(siteName, category, title, newsUrl, date, year, month, day, week, trimester, quadrimester, semester)

    salvar_noticia(siteName,newsUrl, category, title,  date)

    
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

def get_veiculo(soup, url_noticia):
    nomeSite = "NA"

    #nome site
    meta_site = soup.find("meta", property="og:site_name")
    nomeSite = meta_site['content']


    return nomeSite

def get_categoria(soup):
    categories = []
    title = "NA"

    #categoria
    meta_categorias = soup.find_all("meta", property="article:section")
    if meta_categorias:
        for meta in meta_categorias:
            if meta.get("content"):
                categories.append(meta['content'])

    category = ", ".join(categories) if categories else "NA"

    #titulo
    title = soup.title.string if soup.title else "NA"
    

    return category, title

def get_date(soup):
    dt_str = year = month = day = week = trimester = quadrimester = semester = "NA"

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
#conn.close()

