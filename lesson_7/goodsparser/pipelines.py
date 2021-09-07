# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
import os
from urllib.parse import urlparse


class GoodsparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017, username='root', password='password')
        self.mongobase = client.test_database

    def process_item(self, item, spider):
        params = {}
        for param in item['characteristics']:
            param_name = param.xpath("./dt/text()").get()
            param_val = param.xpath("./dd/text()").get().strip()
            params[param_name] = param_val

        item['characteristics'] = params
        adapter = ItemAdapter(item)
        collection = self.mongobase[spider.name]
        collection.insert_one(dict(adapter))

        return item


class GoodsparserImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['url'][0].split('/')[4]}/{os.path.basename(urlparse(request.url).path)}"

