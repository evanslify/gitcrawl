# working :(

import scrapy
# import subprocess
# import os
# import fnmatch
# import hashlib
# from urllib2 import urlopen
from StringIO import StringIO
from zipfile import ZipFile
import requests
import hashlib
import json
from fetch.items import HashListItem


class testwget(scrapy.Spider):
    name = 'testwget'

    # start_urls = []

    # def __init__(self, *args, **kwargs):
    #     super(testwget, self).__init__(*args, **kwargs)
    #     self.start_urls = [kwargs.get('start_url')]

    def parse(self, response):

        jr = json.loads(response.body_as_unicode())
        for i in jr:
            request = requests.get(i)
            zip = ZipFile(StringIO(request.content))
            hashlist = {}
            for ii in zip.namelist():
                doc = zip.open(ii)
                hashlist[ii] = hashlib.md5(doc.read()).hexdigest()

            item = HashListItem()
            item['HashInfo'] = hashlist
            # return item
            return hashlist