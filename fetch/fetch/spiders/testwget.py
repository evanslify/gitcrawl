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


class testwget(scrapy.Spider):
    name = 'testwget'

    start_urls = ['http://52.68.90.91/target.json']

    # http_user = 'evanslify'
    # http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def parse(self, response):

        jr = json.loads(response.body_as_unicode())
        for i in jr:
            request = requests.get(i)
            zip = ZipFile(StringIO(request.content))
            hashlist = {}
            for ii in zip.namelist():
                doc = zip.open(ii)
                hashlist[ii] = hashlib.md5(doc.read()).hexdigest()

            yield hashlist
