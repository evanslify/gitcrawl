# -*- coding: utf-8 -*-
import scrapy
from fetch.items import slideshareItem
import re


class slideshareSpider(scrapy.Spider):
    name = "slideshare"

    def __init__(self, *args, **kwargs):
        super(slideshareSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')

    def callnext(self, response=None, caller=None, start_meta=None):

        if start_meta:
            meta = start_meta
        elif not start_meta and response:
            meta = response.request.meta
        else:
            raise Exception
            meta = response.request.meta

        callstack = meta['callstack']

        ios_agent = (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) '
            'AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mob'
            'ile/9B176 Safari/7534.48.3')

        if len(callstack) > 0:
            target = callstack.pop(0)
            url = target['url']
            status = target.get('status', '')

            req = scrapy.Request(
                url=url, meta=meta, callback=target['callback'],
                errback=self.callnext)

            if 'mobile' in status:
                req.headers['User-Agent'] = ios_agent
                yield req
            else:
                yield req

        else:
            items = slideshareItem()
            loader = response.meta.get('Loader')
            for key in loader.iterkeys():
                items[key] = loader[key]
            yield items

    def start_requests(self):
        # override scrapy's own method to start requests.
        meta = scrapy.Request.meta
        # declaring item loader's layout.
        meta = {
            'callstack': [],
            'Loader': {
                'UserInfo': {},
                'SlideInfo': [],
                'identifier': self.target,
            }
        }
        callstack = meta['callstack']

        calls = self.parse_arguments()
        callstack.extend(calls)
        return self.callnext(start_meta=meta)

    def parse_arguments(self):
        """
        Returns a list which of URL which is generated by parsing start arguments.

        Returns:
            list: A list of dict
        """
        # returns a list, generated by parsing start arguments
        # which can be extended into callstack
        # raises exception while mode is invalid

        actions = []
        base_url = 'http://www.slideshare.net/'
        user_url = base_url + self.target

        if self.target:
            actions.append({
                'url': user_url, 'callback': self.crawl_user
            })
        else:
            raise Exception('No target argument given.')

        return actions

    def list_to_str(self, input):

        result = ''.join(input)
        return result

    def crawl_user(self, response):

        callstack = response.meta['callstack']
        loader = response.meta['Loader']

        slide_count = response.xpath(
            '//a[@title="Presentations"]/span/span/text()').extract_first()

        if int(slide_count):
            slide_list_url = (
                'http://www.slideshare.net/mobile/%s/more?more=1&'
                'page_number=1') % self.target
            callstack.append({
                'url': slide_list_url, 'callback': self.crawl_slides,
                'status': 'mobile'
            })

        # start parsing info
        location_xpath = response.xpath(
            '//li[@class="location"]//text()').extract()
        location = self.list_to_str(location_xpath)
        work = response.xpath(
            '//span[@itemprop="jobTitle"]//text()').extract_first()
        name = response.xpath(
            '//h1[@itemprop="name"]//text()').extract_first()
        industry = response.xpath(
            '//span[@title="Industry"]/span[2]/text()').extract_first()
        bio = response.xpath(
            '//span[@itemprop="description"]/text()').extract_first()
        website = response.xpath(
            '//span[@title="Website"]/a/@href').extract_first()

        social = response.xpath(
            '//div[@class="profile-social-links"]')

        result = {
            'location': location,
            'work': work,
            'industery': industry,
            'bio': bio,
            'website': website,
            'name': name
        }

        if social:
            twitter = response.xpath(
                '//a[@class="notranslate spriteProfile twitter"]'
                '/@href').extract_first()
            facebook = response.xpath(
                '//a[@class="notranslate spriteProfile facebook"]'
                '/@href').extract_first()
            linkedin = response.xpath(
                '//a[@class="notranslate spriteProfile linkedin"]'
                '/@href').extract_first()
            googleplus = response.xpath(
                '//a[@class="notranslate spriteProfile google-plus"]'
                '/@href').extract_first()
            social_links = {
                'twitter': twitter,
                'facebook': facebook,
                'linkedin': linkedin,
                'googleplus': googleplus
            }
            result['social_links'] = social_links

        loader['UserInfo'] = result

        return self.callnext(response)

    def crawl_slides(self, response):

        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['SlideInfo']

        slides = response.xpath('//li[@class="result"]')

        # There is no way to tell whether there's a next page.
        # We can only do it the dumb way.
        # The maximum slides per page is 20.
        # So if len(slides) == 20 -> go to the next page

        if len(slides) == 20:
            page = re.findall('(?<=page_number=)\d+', response.url).pop()
            page = str(int(page) + 1)
            url = re.sub('(?<=page_number=)\d+', page, response.url)
            callstack.append({
                'url': url, 'callback': self.crawl_slides,
                'status': 'mobile'
            })
        for slide in slides:
            title = slide.xpath(
                'div//span[@class="title"]/text()').extract_first()
            views = slide.xpath(
                'div//span[@class="views"]/text()').extract_first()
            result = {
                'title': title,
                'views': views
            }
            items.append(result)

        return self.callnext(response)
