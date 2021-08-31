from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from bookparser import settings
from bookparser.spiders.labirint import LabirintSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    process.crawl(LabirintSpider)

    process.start()
