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
        if 'github' in getattr(spider, 'name'):
            self.connection_pool_github = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=3, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.connection_pool_github)
        if 'bitbucket' in getattr(spider, 'name'):
            self.connection_pool_bitbucket = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=4, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.connection_pool_bitbucket)
        if 'geeklist' in getattr(spider, 'name'):
            self.connection_pool_geeklist = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=5, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.connection_pool_geeklist)
        if 'facebook' in getattr(spider, 'name'):
            self.connection_pool_facebook = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=6, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.connection_pool_facebook)
        if 'stackoverflow' in getattr(spider, 'name'):
            self.connection_pool_stackoverflow = redis.ConnectionPool(host=self.redis_uri, port=self.redis_port, db=7, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.connection_pool_stackoverflow)

    def process_item(self, item, spider):
        # delete empty keys in items.
        item = dict([(a, b) for a, b in item.items() if len(str(b)) > 0])
        epoch = int(time.time())

        user_id = item.pop('identifier')

        self.r.sadd('index', user_id)
        self.r.hset(user_id, epoch, item)
