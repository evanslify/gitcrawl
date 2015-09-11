# -*- coding: utf-8 -*-
import scrapy


class GrabberSpider(scrapy.Spider):
    name = "grabber"
    allowed_domains = ["127.0.0.1"]
    start_urls = (
        'http://www.127.0.0.1/',
    )

    def parse(self, response):
        pass
