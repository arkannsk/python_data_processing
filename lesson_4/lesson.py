"""
Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru, yandex-новости. 
Для парсинга использовать XPath. Структура данных должна содержать:
    название источника;
    наименование новости;
    ссылку на новость;
    дата публикации.

Сложить собранные данные в БД
"""

import requests
from pymongo import MongoClient
from fake_headers import Headers
from datetime import datetime
from lxml import html
from pprint import pprint

lenta_base_url = 'https://lenta.ru'
mail_base_url = 'https://news.mail.ru'
yandex_base_url = 'https://yandex.ru/news'

mail_news_links_xpath = "//div[contains(@class,'daynews__item')]//a[starts-with(@href,'https://news.mail.ru/')]/@href" \
                        "|" \
                        " //ul/li/a[starts-with(@href, 'https://news.mail.ru/')]//@href"

headers = Headers(headers=True).generate()
response = requests.get(url=mail_base_url, headers=headers)
dom = html.fromstring(response.text)
mail_news_links = dom.xpath(mail_news_links_xpath)

result = []
# we need only unique links
for link in set(mail_news_links):
    response = requests.get(url=link, headers=headers)
    if response.status_code == 200:
        tmp = {"link": link}
        dom = html.fromstring(response.text)
        tmp['title'] = dom.xpath('//h1[1]//text()')[0]
        tmp['date'] = dom.xpath("//span[@class='breadcrumbs__item']/span/span[boolean(@datetime)]/@datetime")[0]
        tmp['source'] = dom.xpath("//span[@class='breadcrumbs__item']//"
                                  "a[contains(@class, 'breadcrumbs__link')]/span/text()")[0]
        result.append(tmp)

yandex_news_items_xpath = "//div[contains(@class, 'news-top-flexible-stories')]/div[contains(@class, 'mg-grid__col')]"

response = requests.get(url=yandex_base_url, headers=headers)
dom = html.fromstring(response.text)
yandex_news_items = dom.xpath(yandex_news_items_xpath)

if response.status_code == 200:
    for item in yandex_news_items:
        dt = datetime.now()
        parsed_time = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]
        hours = parsed_time.split(":")[0]
        minutes = parsed_time.split(":")[1]
        tmp = {
            "link": item.xpath(".//a[@class='mg-card__source-link']/@href")[0],
            'title': item.xpath('.//h2/text()')[0],
            'date': dt.replace(hour=int(hours), minute=int(minutes)).isoformat(),
            'source': item.xpath(".//a[@class='mg-card__source-link']/text()")[0]
        }
        result.append(tmp)

lenta_news_items_xpath = "//section[contains(@class, 'b-top7-for-main')]" \
                         "//a[starts-with(@href, '/news/') and not(contains(@class,'js-dh'))]"

response = requests.get(url=lenta_base_url, headers=headers)
dom = html.fromstring(response.text)
lenta_news_items = dom.xpath(lenta_news_items_xpath)

pprint(response.status_code)

if response.status_code == 200:
    for item in lenta_news_items:
        dt = datetime.now()
        parsed_time = item.xpath("./time/text()")[0]
        hours = parsed_time.split(":")[0]
        minutes = parsed_time.split(":")[1]
        tmp = {
            "link": 'https://lenta.ru/' + item.xpath("./@href")[0],
            'title': item.xpath('./text()')[0],
            'date': dt.replace(hour=int(hours), minute=int(minutes)).isoformat(),
            'source': 'lenta.ru'
        }
        result.append(tmp)

client = MongoClient('localhost', 27017, username='root', password='password')
db = client['test_database']
db.news_xpath.drop()

collection = db.news_xpath
collection.insert_many(result)

client.close()
