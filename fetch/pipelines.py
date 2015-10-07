# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import time
import ujson as json
import warnings


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
            'stackexchange': 7,
            'stackexchangesites': 8,
            'leetcode': 9,
            'slideshare': 10,
            'speakerdeck': 11,
            'meetup': 12
        }

        spider_name = getattr(spider, 'name')
        if spider_name in db_dict.iterkeys():
            db = db_dict[spider_name]
            self.pool = redis.ConnectionPool(
                host=self.redis_uri, port=self.redis_port,
                db=db, password=self.redis_auth)
            self.r = redis.StrictRedis(connection_pool=self.pool)
        elif not getattr(spider, 'debug', False):
            db_not_found_error = (
                '%s is not found in RedisPipeline\'s db table.') % spider_name
            warnings.warn(db_not_found_error)
        return

    def process_item(self, item, spider):

        # connect to redis first.
        if not getattr(spider, 'debug', False):
            self.connect_redis_storage(spider)

            epoch = int(time.time())

            try:
                user_id = item.pop('identifier')
                self.r.sadd('index', user_id)
                self.r.hset(user_id, epoch, json.dumps(dict(item)))
            except KeyError:
                warnings.warn('identifier not found!')

        return item
