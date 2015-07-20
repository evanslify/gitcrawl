# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import time


class FetchPipeline(object):

    def process_item(self, item, spider):
        return item


class RedisPipeline(object):

    def __init__(self, redis_uri, redis_port, redis_db, redis_auth):
        self.redis_uri = redis_uri
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_auth = redis_auth

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_uri=crawler.settings.get('REDIS_DB_URI', 'localhost'),
            redis_port=crawler.settings.get('REDIS_DB_PORT', 6379),
            redis_auth=crawler.settings.get('REDIS_DB_AUTH', ''),
            redis_db=crawler.settings.get('REDIS_DB_INDEX', 0)
            )

    def open_spider(self, spider):
        self.connection_pool = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=self.redis_db, password=self.redis_auth)
        self.r = redis.StrictRedis(connection_pool=self.connection_pool)

    def process_item(self, item, spider):
        epoch = str(int(time.time()))
        user_login = item.get('UserInfo').get('user_id')
        key_name = user_login + ";" + epoch
        self.r.hset('gitcrawl', key_name, item)
        return item
