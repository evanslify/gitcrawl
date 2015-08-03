# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class GithubItem(Item):
    UserInfo = Field()
    GistInfo = Field()
    RepoInfo = Field()


class BitbucketItem(Item):
    UserInfo = Field()
    RepoInfo = Field()


class GeeklistItem(Item):
    UserInfo = Field()


class HashListItem(Item):
    HashInfo = Field()
