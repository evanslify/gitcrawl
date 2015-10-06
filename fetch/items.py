# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class FlexibleItem(Item):
    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        super(FlexibleItem, self).__setitem__(key, value)


class GithubItem(Item):
    UserInfo = Field()
    GistInfo = Field()
    RepoInfo = Field()
    identifier = Field()


class BitbucketItem(FlexibleItem):
    pass


class GeeklistItem(FlexibleItem):
    pass


class FacebookItem(FlexibleItem):
    pass


class StackOverflowItem(Item):
    UserInfo = Field()
    PostInfo = Field()
    identifier = Field()


class LeetCodeItem(FlexibleItem):
    pass


class slideshareItem(Item):
    UserInfo = Field()
    SlideInfo = Field()
    identifier = Field()


class SpeakerdeckItems(Item):
    UserInfo = Field()
    SlideInfo = Field()
    identifier = Field()


class MeetupItem(FlexibleItem):
    pass


class HashListItem(Item):
    HashInfo = Field()
