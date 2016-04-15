#!/usr/bin/env python
# encoding: utf-8

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class HandbagCrawler(CrawlSpider):
    name = 'handbags'
    start_urls = [
        'http://www.herstationwholesale.com/wholesale-montana-west/wholesale-montana-west-handbags.html?limit=100&p=1']
    rules = [
        Rule(LinkExtractor(
            allow=r'/wholesale-montana-west/wholesale-montana-west-handbags.html\?limit=\d+&p=\d+'), follow=True),
        Rule(LinkExtractor(
            allow=r'/wholesale-montana-west/wholesale-montana-west-handbags',
            restrict_xpaths='//ul[contains(@class, "products")]'),
            callback='parse_item')
    ]

    def parse_item(self, response):

        self.logger.info('Page reached at %s', response.url)

        item = {}

        item['description'] = response.xpath(
            '//div[@class="box-collateral"]/*')
        item['name'] = response.xpath(
            '//div[@class="product-name"]//text()')
        item['images'] = response.xpath(
            '//a[@class="cloud-zoom-gallery"]/@href').extract()
        item['stock'] = response.xpath(
            '//p[@class="availability in-stock"]/span/text()').extract_first()
        item['url'] = response.url
        return item
