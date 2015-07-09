# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class UserInfo(Item):
    user_public_repo_counts = Field()
    user_hireable = Field()
    user_id = Field()
    user_name = Field()
    user_blog = Field()
    user_followers_count = Field()

class RepoInfo(Item):
    forks_from = Field()
    url = Field()
    apiurl = Field()
    zipurl = Field()
    forks_from_url = Field()
    parent_forked_times = Field()
    forks = Field()
    fork_usernames = Field()
    contributed_times = Field()
    contributed_users = Field()