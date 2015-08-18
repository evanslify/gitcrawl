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
    identifier = Field()


class BitbucketItem(Item):
    UserInfo = Field()
    RepoInfo = Field()
    identifier = Field()


class GeeklistItem(Item):
    UserInfo = Field()
    identifier = Field()


class FacebookItem(Item):
    UserInfo = Field()
    FacebookInfo = Field()
    identifier = Field()


class StackOverflowItem(Item):
    UserInfo = Field()
    PostInfo = Field()
    identifier = Field()


class LeetCodeItem(Item):
    UserInfo = Field()
    QuestionInfo = Field()
    AnswerInfo = Field()
    identifier = Field()


class slideshareItem(Item):
    UserInfo = Field()
    SlideInfo = Field()
    identifier = Field()


class HashListItem(Item):
    HashInfo = Field()
