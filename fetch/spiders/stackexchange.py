# -*- coding: utf-8 -*-
import scrapy
import json


class StackExchangeSpider(scrapy.Spider):
    name = "stackexchange"
    # debug = True

    def __init__(self, *args, **kwargs):

        super(StackExchangeSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')
        self.site = kwargs.get('site').split(',')

        if self.target and self.site is None:
            error = '%s%s' % (self.target, self.site)
            # raise Exception('Missing argument.')
            raise Exception(error)

    def start_requests(self):

        url = (
            'https://api.stackexchange.com/2.2/users?pagesize=1&order=asc&'
            'sort=name&inname=%s&site=stackoverflow&filter=!.ugP9'
            'KmrGS1QwABy' % self.target)
        yield scrapy.Request(url=url, callback=self.crawl_account_id)

    def crawl_account_id(self, response):

        jr = json.loads(response.body_as_unicode())
        items = jr['items']

        for item in items:
            account_id = item['account_id']

        url = (
            'https://api.stackexchange.com/2.2/users/%s/associated?'
            'pagesize=100&filter=!GeAzHAla9bmIm' % account_id)
        yield scrapy.Request(url=url, callback=self.crawl_user_id)

    def extract_site_name(self, input):
        '''
        @input: URL
        @returns: str
        This function parses URL and returns the sitename.
        '''
        fragments = input.split('.')
        length = len(fragments)

        if length == 2:
            # short url, like "http://stackoverflow.com"
            result = fragments[-2]
        elif length == 3 and 'stackexchange' in fragments:
            # long url, like "http://meta.stackexchange.com"
            result = fragments[-3]
        else:
            urlerror = 'Weird URL. %s' % input
            raise Exception(urlerror)

        # "http://stackoverflow" -> "stackoverflow"
        return result[7:]

    def crawl_user_id(self, response):

        jr = json.loads(response.body_as_unicode())
        items = jr['items']
        container = {}

        for item in items:
            user_id = item['user_id']
            site_name = self.extract_site_name(item['site_url'])
            container[site_name] = user_id

        result = {
            'StackUserInfo': container,
            'identifier': self.target
        }

        return result