# -*- coding: utf-8 -*-
import scrapy
from fetch.items import SpeakerdeckItems


class SpeakerdeckSpider(scrapy.Spider):
    name = "speakerdeck"

    def __init__(self, *args, **kwargs):
        super(SpeakerdeckSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')
        self.base_url = 'https://speakerdeck.com/'

    def callnext(self, response=None, caller=None, start_meta=None):

        if start_meta:
            meta = start_meta
        elif not start_meta and response:
            meta = response.request.meta
        else:
            raise Exception

        callstack = meta['callstack']

        if len(callstack) > 0:
            target = callstack.pop(0)
            url = target['url']
            yield scrapy.Request(
                url=url, meta=meta, callback=target['callback'],
                errback=self.callnext)

        else:
            items = SpeakerdeckItems()
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
                'SlideInfo': {},
                'identifier': self.target,
            }
        }
        callstack = meta['callstack']

        calls = self.parse_arguments()
        callstack.extend(calls)
        return self.callnext(start_meta=meta)

    def parse_arguments(self):

        actions = []

        user_url = self.base_url + self.target
        user_star_url = user_url + '/stars'

        if self.target:
            actions.extend([
                {'url': user_url, 'callback': self.crawl_user},
                {'url': user_star_url, 'callback': self.crawl_user_starred}
            ])
        else:
            raise Exception('Parsing mode invalid.')

        return actions

    def list_to_str(self, input):

        result = ''.join(input)
        return result

    def extract_int(self, input):
        return int(filter(lambda x: x.isdigit(), input))

    def crawl_user(self, response):

        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']

        name = response.xpath('//h2/text()').extract_first()
        bio = response.xpath('//div[@class="bio"]/p/text()').extract_first()
        stars = response.xpath(
            '//a[contains(@href, "stars")]/text()').extract_first()

        items.update({
            'name': name,
            'bio': bio,
            'stars': stars
        })

        slides = response.xpath(
            '//div[@class="talk public"]//h3/a/@href').extract()

        for slide_url in slides:
            url = self.base_url + slide_url[1:]
            callstack.append({
                'url': url, 'callback': self.crawl_slide
            })

        return self.callnext(response)

    def crawl_user_starred(self, response):

        loader = response.meta['Loader']
        items = loader['UserInfo'].setdefault('stars_list', [])

        stars = response.xpath('//div[@class="talk public"]')
        if stars:
            for one_star in stars:
                id = one_star.xpath('@data-id').extract_first()
                title = one_star.xpath('div/h3/a/text()').extract_first()
                author_name = one_star.xpath('div/p/a/text()').extract_first()
                author_login = one_star.xpath(
                    'div/p/a/@href').extract_first()[1:]

                one_star = {
                    'id': id,
                    'title': title,
                    'author_name': author_name,
                    'author_login': author_login
                }
                items.append(one_star)

        return self.callnext(response)

    def crawl_slide(self, response):

        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['SlideInfo']

        title = response.xpath(
            '//div[@id="talk-details"]/header/h1/text()').extract_first()

        description_raw = response.xpath(
            '//div[@id="talk-details"]/div//*').extract()
        description = ''.join(description_raw)

        category = response.xpath(
            '//li[@class="category"]/a/text()').extract_first()
        date = response.xpath(
            '//div[@id="talk-details"]/header/p/mark/text()').extract_first()
        id = response.xpath(
            '//meta[@property="og:image"]/@content'
        ).extract_first().split('/')[-2]

        result = {
            'title': title,
            'description': description,
            'category': category,
            'date': date,
            'id': id,
        }

        views_raw = response.xpath(
            '//li[@class="views"]/span/text()').extract_first()
        views = self.extract_int(views_raw)

        if views:
            result['views'] = views
        star_counts_raw = response.xpath(
            '//li[@class="star signed_out"]//a[@class="stargazers"]/text()'
        ).extract_first()
        star_counts = self.extract_int(star_counts_raw)

        if star_counts:
            result['stargazers'] = []
            result['star_counts'] = star_counts
            star_url = response.url + '/stargazers'
            callstack.append({
                'url': star_url, 'callback': self.crawl_slide_stargazers
            })

        url_title = response.url.split('/')[-1]
        items[url_title] = result

        return self.callnext(response)

    def crawl_slide_stargazers(self, response):

        loader = response.meta['Loader']
        url_title = response.url.split('/')[-2]
        items = loader['SlideInfo'][url_title]
        users = response.xpath('//a')
        pretty_user_list = []
        while users:
            one_user = []
            for i in range(3):
                cursor = users.pop(0)
                one_user.append(cursor)
            pretty_user_list.append(one_user)

        # explaination:
        # original: (flattened html.....)
        # 0 <---|
        # 1 <---|---- one user
        # 2 <---|
        # 0 <---|
        # 1 <---|---- one user
        # 2 <---|
        # turns into:
        # [[0, 1, 2], [0, 1, 2]]
        # both xrange(py<3) and range works.

        for user in pretty_user_list:
            name = user[1].xpath('text()').extract_first()
            login = user[1].xpath('@href').extract_first()[1:]
            stars = user[2].xpath('text()').extract_first()

            result = {
                'name': name,
                'login': login,
                'stars': self.extract_int(stars)
            }
            items['stargazers'].append(result)

        return self.callnext(response)
