# working :(

import scrapy


class grabber(scrapy.Spider):
    name = 'grabber'

    def __init__(self, *args, **kwargs):
        super(grabber, self).__init__(*args, **kwargs)
        self.target_url = kwargs.get('url')
        if self.target_url == None:
            raise Exception('No URL entered.')

    def start_requests(self):
        yield scrapy.Request(url='file://\/dev/null', callback=self.parse)

        #  yield scrapy.Request(url='', callback=self.parse)
    #  def get(self, response)j:
        #  return

    # start_urls = []

    # def __init__(self, *args, **kwargs):
    #     super(testwget, self).__init__(*args, **kwargs)
    #     self.start_urls = [kwargs.get('start_url')]

    def parse(self, response):
        items = {'file_urls': [self.target_url]}
        return items
