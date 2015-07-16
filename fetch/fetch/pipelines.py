# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis


class FetchPipeline(object):

    def process_item(self, item, spider):
        return item


class RedisPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, redis_uri, redis_port, redis_db, redis_auth):
        self.redis_uri = redis_uri
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_auth = redis_auth

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_uri='localhost',
            redis_port=6379,
            redis_auth='',
            redis_db=crawler.settings.get('redis_db', '0')
        )

    def open_spider(self, spider):
        self.r = redis.StrictRedis(host=self.redis_uri, port=self.redis_port, db=self.redis_db, password=self.redis_auth)

    # def close_spider(self, spider):
    #     self.client.close()

    def process_item(self, item, spider):
        self.r.set(self.collection_name, item)
        return item
