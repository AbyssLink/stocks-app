import json
import re
import ssl
import time
from os import path
from urllib.request import urlopen

from bs4 import BeautifulSoup as soup


def fetch_news(xml_news_url):
    '''Print select details from a html response containing xml
      @param xml_news_url: url to parse
      '''

    context = ssl._create_unverified_context()
    Client = urlopen(xml_news_url, context=context)
    xml_page = Client.read()
    Client.close()

    soup_page = soup(xml_page, "xml")

    news_items = soup_page.findAll("item")

    news_list = []

    for news in news_items:
        cover_url = get_cover_img(news.description.text)
        description = get_description(news.description.text)
        news_dict = {
            'img': cover_url,
            'title': news.title.text,
            'description': description,
            'link': news.link.text,
            'date': news.pubDate.text,
        }
        news_list.append(news_dict)

    return news_list


def get_cover_img(text):
    match = re.search(r'http.*.jpg', text)
    return match.group()


def get_description(text):
    return re.sub(r'<img.*./> ',  '', text)


    # you can add google news 'xml' URL here for any country/category
news_url = "https://news.google.com/news/rss/?ned=us&gl=US&hl=en"
sports_url = "https://news.google.com/news/rss/headlines/section/topic/SPORTS.en_in/Sports?ned=in&hl=en-IN&gl=IN"
business_url = "https://news.google.com/news/rss/headlines/section/topic/BUSINESS.en_in/Business?ned=in&hl=en-IN&gl=IN"
moneycontrol = 'https://www.moneycontrol.com/rss/latestnews.xml'

# now call news function with any of these url or BOTH
# news(news_url)
# news(sports_url)
if __name__ == "__main__":
    fetch_news(moneycontrol)
