# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy import Selector
from fetch.items import FacebookItem


class FacebookSpider(scrapy.Spider):

    name = 'facebook'
    start_urls = ['http://52.68.90.91/cookiez.json']

    def callnext(self, response, cookies=None):
        meta = response.request.meta
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
            items['UserInfo'] = loader['UserInfo']
            items['FacebookInfo'] = loader['FacebookInfo']
            yield items

    def parse(self, response):
        # go to somewhere and fetch cookiez.
        # init data before parsing
        response.meta.update({
            'callstack': [],
            'Loader': {},
            })
        callstack = response.meta['callstack']
        jr = json.loads(response.body_as_unicode())
        self.profile_id = jr.get('c_user')
        # construct profile URL
        profile_url = (
            'https://m.facebook.com/profile.php?'
            'v=info&id=%s') % self.profile_id

        callstack.append({
            'url': profile_url, 'callback': self.parse_mobile
            })
        return self.callnext(response, cookies=jr)

    def parse_mobile(self, response):

        loader = response.meta['Loader']
        loader.update({
            'FacebookInfo': {},
            'UserInfo': {
                'user_id': self.profile_id}
            })
        items = loader['FacebookInfo']
        sel = Selector(text=response.body_as_unicode())

        # parse dispay name
        name = sel.xpath(
            '//div[@class="bi"]//strong[@class="br"]/text()').extract()

        # parse work!
        works = []
        for i in sel.xpath('//div[@id="work"]//div[@class="da cr"]'):
            i_selector = Selector(text=i.extract())
            # conditions in <div class="bq">:
            # 4 <div> elements: comment / date / location supplied
            # 3 <div> elements: one of date / location is supplied
            # 2 <div> elements: one of date / location is supplied
            # 1 <div> elements: only company name supplied

            work_name = i_selector.xpath(
                '//span[@class="dd de ce"]/a/text()').extract()
            work_facebook_uri = i_selector.xpath(
                '//span[@class="dd de ce"]/a/@href').extract()

            work = {
                'work_name': work_name,
                'work_facebook_uri': work_facebook_uri,
            }
            works.append(work)

        # parse education!
        edus = []
        for i in sel.xpath('//div[@id="education"]//div[@class="da cr"]'):
            i_selector = Selector(text=i.extract())
            edu_name = i_selector.xpath(
                '//span[@class="dd de ce"]/a/text()').extract()
            edu_facebook_uri = i_selector.xpath(
                '//span[@class="dd de ce"]/a/@href').extract()
            edu_desc = i_selector.xpath(
                '//span[@class="df dg"]/text()').extract()
            edu = {
                'edu_name': edu_name,
                'edu_facebook_uri': edu_facebook_uri,
                'edu_description': edu_desc
            }
            edus.append(edu)

        # parse skillz!
        skills = sel.xpath(
            '//div[@id="skills"]//div[@class="da dr cr ds"]/span/text()'
            ).extract()

        # parse living ah!
        current_city = sel.xpath(
            '//div[@id="living"]//div[@title="Current City"]'
            '//div[@class="dx"]/a/text()'
            ).extract()
        hometown = sel.xpath(
            '//div[@id="living"]//div[@title="Hometown"]'
            '//div[@class="dx"]/a/text()'
            ).extract()
        living = {
            'hometown': hometown,
            'current_city': current_city
            }

        # parse contact info
        contacts_infos = sel.xpath(
            '//div[@id="contact-info"]//div[@class="cp"]')
        contacts_selector = Selector(text=contacts_infos[0].extract())

        contact_phone = contacts_selector.xpath(
            '//div[@title="Mobile"]//div[@class="dx"]/span/span/text()'
            ).extract()
        contact_site = contacts_selector.xpath(
                    '//div[@title="Website"]//div[@class="dx"]/a/text()'
                    ).extract()

        contact_info = {
            'phone': contact_phone,
            'website': contact_site
        }

        # parse basic info
        basics_infos = sel.xpath(
            '//div[@id="basic-info"]//div[@class="cp"]')
        basics_selector = Selector(text=basics_infos[0].extract())

        basic_birthday = basics_selector.xpath(
            '//div[@title="Birthday"]//div[@class="dx"]/text()').extract()
        basic_bloodtype = basics_selector.xpath(
            '//div[@title="Blood Type"]//div[@class="dx"]/text()').extract()
        basic_languages = basics_selector.xpath(
            '//div[@title="Languages"]//div[@class="dx"]/text()').extract()
        basic_gender = basics_selector.xpath(
            '//div[@title="Gender"]//div[@class="dx"]/text()').extract()

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
        return self.callnext(response)
