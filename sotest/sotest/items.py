# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class RepoInfo(Item):
    user_public_repos = Field()
    user_hireable = Field()
    forks_from = Field()
    url = Field()
    apiurl = Field()
    zipurl = Field()
    forks_from_url = Field()
    parent_forked_times = Field()
    forks = Field()
    fork_usernames = Field()
