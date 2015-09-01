# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy import Selector
from fetch.items import FacebookItem
from scrapy.utils.project import get_project_settings
import redis
import re
from urlparse import urljoin


class FacebookSpider(scrapy.Spider):

    name = 'facebook'

    def __init__(self, *args, **kwargs):
        super(FacebookSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')

    def callnext(self, response, cookies=None, start_meta=None):

        try:
            meta = response.request.meta
        except AttributeError:
            meta = start_meta
        headers = {
            'Host': 'm.facebook.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://m.facebook.com/',
            'Accept-Encoding': 'gzip, deflate'
        }
        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            url = target['url']
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext,
                cookies=cookies, headers=headers)
        else:
            items = FacebookItem()
            loader = response.meta.get('Loader')
            items['identifier'] = loader['identifier']
            items['FacebookInfo'] = loader['FacebookInfo']
            yield items

    def start_requests(self):
        # override scrapy's own method to start requests.
        meta = scrapy.Request.meta
        # declaring item loader's layout.
        meta = {
            'callstack': [],
            'Loader': {
                'FacebookInfo': {},
                'identifier': self.target
            }
        }
        callstack = meta['callstack']

        cookiez = self.get_cookiez()
        self.profile_id = cookiez.get('c_user')
        profile_url = (
            'https://m.facebook.com/profile.php?'
            'v=info&id=%s') % self.profile_id

        callstack.append({
            'url': profile_url, 'callback': self.parse_mobile
        })
        return self.callnext(self, start_meta=meta, cookies=cookiez)

    def get_cookiez(self):
        # read from redis!
        settings = get_project_settings()
        redis_uri = settings.get('REDIS_DB_URI', 'localhost')
        redis_port = settings.get('REDIS_DB_PORT', 6379)
        redis_auth = settings.get('REDIS_DB_AUTH', '')
        redis_db = 0
        pool = redis.ConnectionPool(
            host=redis_uri, port=redis_port,
            db=redis_db, password=redis_auth)
        r = redis.StrictRedis(connection_pool=pool)
        cookiez = r.get(self.target)
        if cookiez is None:
            error_message = (
                'No cookies found in DB #%s at %s') % (redis_db, redis_uri)
            raise Exception(error_message)
        else:
            jr = json.loads(cookiez)
        return jr

    def parse_mobile(self, response):

        loader = response.meta['Loader']

        loader.update({
            'FacebookInfo': {},
            'identifier': self.profile_id
        })

        items = loader['FacebookInfo']
        callstack = response.meta['callstack']

        # parse dispay name
        name = response.xpath(
            '//strong[@class]/text()').extract_first()

        # parse work!
        works = []
        for work in response.xpath(
                '//div[@id="work"]//div[starts-with(@id, "exp")]'):
            # conditions in <div class="bq">:
            # 4 <div> elements: comment / date / location supplied
            # 3 <div> elements: one of date / location is supplied
            # 2 <div> elements: one of date / location is supplied
            # 1 <div> elements: only company name supplied
            work_name = work.xpath(
                'div/div/div/div[1]/span[1]/a/text()').extract_first()
            work_facebook_uri = work.xpath(
                'div/div/div/div[1]/span[1]/a/@href').extract_first()

            work = {
                'work_name': work_name,
                'work_facebook_uri': work_facebook_uri,
            }
            works.append(work)

        # parse education!
        edus = []
        for school in response.xpath(
                '//div[@id="education"]//div[starts-with(@id, "exp")]'):
            edu_name = school.xpath(
                'div/div/div/div[1]//a/text()').extract_first()
            edu_facebook_uri = school.xpath(
                'div/div/div/div[1]//a/@href').extract_first()
            edu_desc = school.xpath(
                'div/div/div/div[2]//span/text()').extract_first()
            edu = {
                'edu_name': edu_name,
                'edu_facebook_uri': edu_facebook_uri,
                'edu_description': edu_desc
            }
            edus.append(edu)

        # parse skillz!
        skills = response.xpath(
            '//div[@id="skills"]/div/div[2]//span/text()'
        ).extract_first()

        # parse living ah!
        current_city = response.xpath(
            '//div[@id="living"]//div[@title="Current City"]//a/text()'
        ).extract_first()
        hometown = response.xpath(
            '//div[@id="living"]//div[@title="Hometown"]//a/text()'
        ).extract_first()
        living = {
            'hometown': hometown,
            'current_city': current_city
        }

        # parse contact info
        contact_info = response.xpath(
            '//div[@id="contact-info"]/div')

        contact_phone = contact_info.xpath(
            'div//div[@title="Mobile"]//span[@dir]/text()').extract_first()
        contact_skype = contact_info.xpath(
            'div//div[@title="Skype"]//td[2]/div/text()').extract_first()
        contact_email = contact_info.xpath(
            'div//div[@title="Email"]//td[2]/div/text()').extract_first()
        contact_site = contact_info.xpath(
            'div//div[@title="Website"]//td[2]/div/a/@href'
        ).extract_first()

        contact_info = {
            'phone': contact_phone,
            'website': contact_site,
            'skype': contact_skype,
            'email': contact_email
        }

        # parse basic info
        basics_infos = response.xpath(
            '//div[@id="basic-info"]/div/div[2]')

        basic_birthday = basics_infos.xpath(
            'div[@title="Birthday"]//td[2]//text()').extract_first()
        basic_bloodtype = basics_infos.xpath(
            'div[@title="Blood Type"]//td[2]//text()').extract_first()
        basic_languages = basics_infos.xpath(
            'div[@title="Languages"]//td[2]//text()').extract_first()
        basic_gender = basics_infos.xpath(
            'div[@title="Gender"]//td[2]//text()').extract_first()
        basic_info = {
            'birthday': basic_birthday,
            'bloodtype': basic_bloodtype,
            'languages': basic_languages,
            'gender': basic_gender
        }

        items.update({
            'name': name,
            'works': works,
            'educations': edus,
            'skills': skills,
            'living': living,
            'contact_info': contact_info,
            'basic_infos': basic_info
        })

        url = 'https://m.facebook.com/events/past'
        callstack.append({
            'url': url, 'callback': self.crawl_event})
        return self.callnext(response)

    def crawl_event(self, response):

        loader = response.meta['Loader']
        items = loader['FacebookInfo'].setdefault('events', [])
        callstack = response.meta['callstack']
        for events in response.xpath('//div[@class="bg bo"]'):
            title = events.xpath(
                'div/div[1]//h4/text()').extract_first()
            event_month = events.xpath(
                'div/div[2]/span/span[1]/text()').extract_first()
            event_day = events.xpath(
                'div/div[2]/span/span[2]/text()').extract_first()
            event_time = events.xpath(
                'div/div[2]/div[1]/span/text()').extract_first()
            event_loc = events.xpath(
                'div/div[2]/div[2]/span/text()').extract_first()
            event_city = events.xpath(
                'div/div[2]/div[3]/span/text()').extract_first()
            event_id = re.findall('(?<=events\/).*?(?=\?)', events.xpath(
                'div/div[2]//a/@href').extract_first())[0]
            result = {
                'month': event_month,
                'day': event_day,
                'time': event_time,
                'loc': event_loc,
                'city': event_city,
                'id': event_id,
                'title': title
            }
            items.append(result)
        more = response.xpath('//div[@id="event_list_seemore"]')
        if more:
            url1 = more.xpath('a/@href').extract_first()
            url = urljoin(response.url, url1)
            callstack.append({
                'url': url, 'callback': self.crawl_event})
        else:
            group_url = 'https://m.facebook.com/groups/?seemore'
            callstack.append({
                'url': group_url, 'callback': self.crawl_groups})

        return self.callnext(response)

    def crawl_groups(self, response):

        loader = response.meta['Loader']
        callstack = response.meta['callstack']
        item = loader['FacebookInfo'].setdefault('groups', [])

        for group in response.xpath('//li[@class="bi"]'):
            url = group.xpath('table//a/@href').extract_first()
            name = group.xpath('table//a/text()').extract_first()
            item.append({
                'url': url,
                'name': name})
        return self.callnext(response)
