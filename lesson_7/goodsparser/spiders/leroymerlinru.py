import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from lesson_7.goodsparser.items import GoodsparserItem
from urllib import parse
"""
● название
● все фото
● параметры товара в объявлении
● ссылка
● цена
"""


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/search/?q=лампочки']

    def parse(self, response: HtmlResponse, **kwargs):
        urls = response.xpath("//a[@data-qa='product-name']")
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.parse_goods)

    def parse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=GoodsparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', "//uc-pdp-price-view[@slot='primary-price']/span[@slot='price']/text()")
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src")
        loader.add_value('characteristics', response.xpath("//dl[@class='def-list']/div"))
        loader.add_value('url', response.url)
        yield loader.load_item()
