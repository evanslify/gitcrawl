# -*- encoding: utf-8 -*-

import scrapy
from StringIO import StringIO
from zipfile import ZipFile
import hashlib
from fetch.items import HashListItem


class hashcalc(scrapy.Spider):
    name = 'hashcalc'
    debug = True

    """
    I never thought that this would work on ScrapingHub.
    By doing this we can compare files by hash and we will know if someone
    downloaded, copied some and put it on Github.
    Doing this on ScrapingHub we can 'offload' some load off our servers.

    The user account on ScrapingHub can write to disk,
    But cannot read. So that I used StringIO as memdisk instead.

    Actually, anyone can do this:
        import os
        os.system('cat /proc/cpuinfo')
        os.system('cat /etc/passwd')
    I did not check into this but IMO, ScrapingHub is vulnerable
    to anykind of shellshock exploit.
    Any shellshock with 'rm -rf /' will end very badly.

    Also, it might be possible to use ScrapingHub as a web server?
    """

    def __init__(self, *args, **kwargs):
        super(hashcalc, self).__init__(*args, **kwargs)
        self.start_url = kwargs.get('url')

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        if response.status is not 200:
            return

        zipfile = ZipFile(StringIO(response.body))
        hashlist = {}
        for file_ in zipfile.namelist():
            doc = zipfile.open(file_)
            hashlist[file_] = hashlib.md5(doc.read()).hexdigest()

        item = HashListItem()
        item['HashInfo'] = hashlist
        return item
