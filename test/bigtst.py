import scrapy
from urlparse import urljoin
import json

class bigSpider(scrapy.Spider):
    name = 'big'
    start_urls = ['https://api.github.com/search/repositories?q=test+language:python&sort=stars&order=desc&per_page=10']
    
    def parse(self, response):
        jr = json.loads(response.body_as_unicode())
        # print json.dumps(jr, sort_keys=True, indent=4, separators=(',', ': '))
        # print type(jr)
        # print type(jr['items'])
        print jr['items'][1]['owner'][u'url']

    #     # print jr['items'][0]['owner']['url']
    #     # print "length", len(jr['items'])
    #     # counts = len(jr['items'])

    #     for x in range(1, len(jr['items'])+1):
    #         yield scrapy.Request(jr['items'][x]['owner']['url'])

    # def parse_2(self, response):
    #     for x in response.xpath("//div[@class='repo-tab']/ul/li/h3/a/@href").extract():
    #         yield scrapy.Request(urljoin(response.url, x), self.parse_repo)

    # def parse_repo(self, response):
    #     yield {
    #         'title': response.xpath("//strong/a/text()").extract(),
    #         'commits': response.xpath("(//span[@class='num text-emphasized'])[1]/text()").extract(),
    #         'branches': response.xpath("(//span[@class='num text-emphasized'])[2]/text()").extract(),
    #         'releases': response.xpath("(//span[@class='num text-emphasized'])[3]/text()").extract(),
    #         'contributor': response.xpath("(//span[@class='num text-emphasized'])[4]/text()").extract(),
    #         'readme': response.xpath("//article[@class='markdown-body entry-content']").extract(),
    #         'timeauthored': response.xpath("//time[@class='updated']/text()").extract(),
    #         'description': response.xpath("//div[@class='repository-description']/text()").extract(),
    #         'link': response.url,
    #     }