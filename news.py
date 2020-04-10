import json
import ssl
import time
from os import path
from urllib.request import urlopen

from bs4 import BeautifulSoup as soup

from utils import get_cover_img


def fetch_news(xml_news_url):
    '''Print select details from a html response containing xml
      @param xml_news_url: url to parse
      '''

    news_list = try_get_local_news()
    if news_list is not False:
        return news_list

    context = ssl._create_unverified_context()
    Client = urlopen(xml_news_url, context=context)
    xml_page = Client.read()
    Client.close()

    soup_page = soup(xml_page, "xml")

    news_list = soup_page.findAll("item")

    news_list = news_list[0:20]

    news_array = []

    for news in news_list:
        cover_url = get_cover_img(news.link.text)
        news_dict = {
            'img': cover_url,
            'source': news.source.text,
            'title': news.title.text,
            'link': news.link.text,
            'date': news.pubDate.text,
        }
        news_array.append(news_dict)
        print(f'news img:    {cover_url}')
        print(f'news source:    {news.source.text}')
        print(f'news title:   {news.title.text}')
        print(f'news link:    {news.link.text}')
        print(f'news pubDate: {news.pubDate.text}')
        print("+-" * 20, "\n\n")

    with open(path.join('news', 'News.json'), 'w') as f:
        f.write(json.dumps(news_array))
        # print(news_array)
        print('Write local News.json file')

    return news_array()


def try_get_local_news():
    if(path.exists(path.join('news', 'News.json'))):
        if((time.time() - path.getmtime(path.join('news', 'News.json')) <= float(5*24*60*60))):
            with open(path.join('news', 'News.json'), 'r') as f:
                print(f'fetch local data = News.json')
                news = json.loads(f.read())
                return news[0:20]
    else:
        return False


# you can add google news 'xml' URL here for any country/category
news_url = "https://news.google.com/news/rss/?ned=us&gl=US&hl=en"
sports_url = "https://news.google.com/news/rss/headlines/section/topic/SPORTS.en_in/Sports?ned=in&hl=en-IN&gl=IN"
business_url = "https://news.google.com/news/rss/headlines/section/topic/BUSINESS.en_in/Business?ned=in&hl=en-IN&gl=IN"
moneycontrol = 'https://www.moneycontrol.com/rss/latestnews.xml'

# now call news function with any of these url or BOTH
# news(news_url)
# news(sports_url)
if __name__ == "__main__":
    fetch_news(business_url)
