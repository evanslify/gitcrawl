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
        pass

    def connect_redis_storage(self, spider):
        db_dict = {
            'github': 3,
            'bitbucket': 4,
            'geeklist': 5,
            'facebook': 6,
            'stackoverflow': 7,
            'leetcode': 8,
            'slideshare': 9
        }

        spider_name = getattr(spider, 'name')
        if spider_name in db_dict.iterkeys():
            db = db_dict[spider_name]
            self.pool = redis.ConnectionPool(
                    host=self.redis_uri, port=self.redis_port,
                    db=db, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.pool)
        else:
            db_not_found_error = (
                '%s is not found in RedisPipeline\'s db table.') % spider_name
            raise Exception(db_not_found_error)
        return

    def process_item(self, item, spider):

        # connect to redis first.
        self.connect_redis_storage(spider)

        # delete empty keys in items.
        item = dict([(a, b) for a, b in item.items() if len(str(b)) > 0])
        epoch = int(time.time())

        user_id = item.pop('identifier')

        self.r.sadd('index', user_id)
        self.r.hset(user_id, epoch, item)
        return item
