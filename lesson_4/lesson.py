"""
Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru, yandex-новости. 
Для парсинга использовать XPath. Структура данных должна содержать:
    название источника;
    наименование новости;
    ссылку на новость;
    дата публикации.
"""

import requests
from fake_headers import Headers
from lxml import html


url = ''

lenta_url = 'https://lenta.ru/'
mail_url = 'https://mail.ru'
yandex_url = 'https://yandex.ru/news'

headers = Headers(headers=True).generate()
response = requests.get(url=url, headers=headers)
