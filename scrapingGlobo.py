import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
            #print(noticia.get('href'))

    return news_dict

def access_news(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    print("\n--------------------------------------------------------")
    get_veiculo(soup, url)
    get_categoria(soup)
    get_date(soup)

    
def get_veiculo(soup, url):
    #nome site
    meta_site = soup.find("meta", property="og:site_name")

    if meta_site and meta_site.get("content"):
        print(f"Nome do site (veículo): {meta_site['content']}")


    #url
    print(f"Link: {url}")

    return


def get_categoria(soup):
    #categoria

    meta_categorias = soup.find_all("meta", property="article:section")
    if meta_categorias:
        for meta in meta_categorias:
            if meta.get("content"):
                print(f"Categoria: {meta['content']}")

    #titulo
    title = soup.title.string if soup.title else None
    print(f"Título da Notícia: {title}")

    return

def get_date(soup):
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

        print(f"Ano: {year}")
        print(f"Mês: {month}")
        print(f"Dia: {day}")
        print(f"Semana: {week}")
        print(f"Trimestre: {trimester}")
        print(f"Quadrimestre: {quadrimester}")
        print(f"Semestre: {semester}")

    return
    
get_news()


