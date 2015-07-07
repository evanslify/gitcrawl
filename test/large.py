#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import re


class TestSpider(BaseSpider):
    name = "test"
    start_urls = ["https://api.github.com/search/repositories?q=test+language:python&sort=stars&order=desc&per_page=200"]

    def parse(self, response):
        xpath = HtmlXPathSelector(response)
        count = 0
        for url in xpath.select('//html_url').xpath():
            print url