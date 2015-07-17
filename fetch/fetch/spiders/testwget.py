# working :(

import scrapy
import json
import subprocess
import urllib

class testwget(scrapy.Spider):
    name = 'testwget'

    start_urls = ['https://api.github.com/users/evanslify']

    http_user = 'evanslify'
    http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def parse(self, response):

        # parsing user page.
        # https://api.github.com/users/<username>

        jr = json.loads(response.body_as_unicode())
        ver = subprocess.check_output(['uname', '-a'])
        tar = subprocess.check_output(['which', 'tar'])
        wget = subprocess.check_output(['which', 'wget'])
        passwd = subprocess.check_output(['cat', '/etc/passwd'])

        user = subprocess.check_output(['whoami'])

        testfile = urllib.URLopener()
        testfile.retrieve('https://phs.googlecode.com/files/Download File Test.zip', 'test1.zip')

        ls = subprocess.check_output(['ls'])
        # call(['wget', 'https://github.com/evanslify/gitspective/archive/master.zip'])
        # call(['ls'])
        yield {
            'version': ver,
            'which tar': tar,
            'which wget': wget,
            'ls': ls,
            'user': user,
            'passwd': passwd,
            }
