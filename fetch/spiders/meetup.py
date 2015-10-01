# -*- coding: utf-8 -*-
import scrapy
from fetch.items import MeetupItem
import re
import ujson as json


class MeetupSpider(scrapy.Spider):
    name = "meetup"

    def __init__(self, *args, **kwargs):
        super(MeetupSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target', '')
        if self.target == '':
            raise Exception('No username entered.')

    def set_crawler(self, crawler):
        super(MeetupSpider, self).set_crawler(crawler)
        crawler.settings.set('DOWNLOAD_DELAY', 350)

    def callnext(self, response=None, start_meta=None, callback=None):

        # trick to override the default parsing method :D
        if start_meta:
            meta = start_meta
        elif not start_meta and response:
            meta = response.request.meta
        else:
            raise Exception

        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            url = target['url']
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext)
        else:
            items = MeetupItem()
            loader = response.meta.get('Loader')
            for key in loader.iterkeys():
                items[key] = loader[key]
            yield items

    def start_requests(self):
        # trick to override default parse method :D

        meta = scrapy.Request.meta
        meta = {
            'callstack': [],
            'Loader': {
                'identifier': self.target,
            },
        }

        self.keys = {
            'key': '7a797f482f4f634a6f24165a2b796412',
            'uid': self.target}

        callstack = meta['callstack']

        group_url = (
            'https://api.meetup.com/2/groups?&sign=true&photo-host=public&'
            'member_id={uid}&page=100&key={key}').format(**self.keys)
        member_url = (
            'https://api.meetup.com/2/member/{uid}?&sign=true&photo-host=public&'
            'page=20&key={key}').format(**self.keys)

        callstack.extend([
            {'url': group_url, 'callback': self.crawl_user_group_summary},
            {'url': member_url, 'callback': self.crawl_user_info}])

        return self.callnext(start_meta=meta)

    def next_page(self, response, caller):
        """
        Takes URL and +1 the pagination number

        Args:
            url (str):  The URL to '+1'
        Returns:
            str: The URL which has been +1'd
        """

        callstack = response.meta['callstack']

        old_page = int(re.findall('(?<=offset=)\d+(?=&)', response.url)[0])
        new_url = re.sub(
            '(?<=offset=)\d+(?=&)', (str(old_page + 1)), response.url)
        callstack.append({
            'url': new_url, 'callback': caller})

    def crawl_user_info(self, response):

        loader = response.meta['Loader']

        loader['UserInfo'] = json.loads(response.body_as_unicode())
        return self.callnext(response)

    def crawl_user_group_summary(self, response):

        loader = response.meta['Loader']
        callstack = response.meta['callstack']
        items = loader.setdefault('GroupInfo', {})
        jr = json.loads(response.body_as_unicode())
        results = jr['results']

        if results:
            for group in results:
                group_id = group['id']
                items[group_id] = group
                if group['members'] > 0:
                    group_member_url = (
                        'https://api.meetup.com/2/members?&sign=true&photo-host=public&gr'
                        'oup_id={groupid}&page=100&offset=1&key={key}').format(
                            groupid=group_id, **self.keys)
                    callstack.append({
                        'url': group_member_url, 'callback': self.crawl_group_member})
        if jr['meta']['next']:
            self.next_page(response, self.crawl_user_group_summary)

        return self.callnext(response)

    def crawl_group_member(self, response):

        loader = response.meta['Loader']
        items = loader['GroupInfo']
        group_id = re.findall('(?<=group_id=)\d+(?=&)', response.url)[0]
        member_list = items[int(group_id)].setdefault('member_list', [])

        jr = json.loads(response.body_as_unicode())

        for members in jr['results']:
            member_list.append(members)

        if jr['meta']['next']:
            self.next_page(response, self.crawl_group_member)

        return self.callnext(response)
