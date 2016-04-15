#!/usr/bin/env python
# encoding: utf-8

import subprocess
import shlex

s = '''durin42,bitbucket
nash,geeklist
PCman,github
cbmbbz,leetcode
152743422,meetup
paulgordonbrown,slideshare
cassininazir,speakerdeck
22656,stackexchangesites'''

arg_list = []
def gen_arg(user, site):
    arg = 'scrapy crawl -a target={user} {site} -o output={site}.json'.format(
            **{
                'user': user,
                'site': site }
            )
    arg_list.append(arg)

for i in s.splitlines():
    i_ = i.split(',')
    username = i_[0]
    site = i_[1]
    gen_arg(username, site)
