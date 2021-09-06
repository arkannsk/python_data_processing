import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['www.labirint.ru']
    start_urls = ['https://www.labirint.ru/genres/2252/']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//div[@id='catalog']//a[@class='product-title-link']/@href").getall()
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        title = response.xpath("//div[@id='product-info']/@data-name").get()
        price = response.xpath("//div[@id='product-info']/@data-price").get()
        discount_price = response.xpath("//div[@id='product-info']/@data-discount-price").get()
        authors = response.xpath("//div[@class='authors'][1]//a/text()").getall()
        rating = response.xpath("//div[@id='rate']/text()").get()
        url = response.url
        item = BookparserItem(title=title, url=url, price=price, discount_price=discount_price, authors=authors,
                              rating=rating)
        yield item
