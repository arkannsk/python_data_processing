# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017, username='root', password='password')
        self.mongobase = client.test_database

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['price'].isnumeric():
            adapter['price'] = int(adapter['price'])

        if adapter['discount_price'].isnumeric():
            adapter['discount_price'] = int(adapter['discount_price'])

        adapter['rating'] = float(adapter['rating'])

        collection = self.mongobase[spider.name]
        collection.insert_one(dict(adapter))
        return item

