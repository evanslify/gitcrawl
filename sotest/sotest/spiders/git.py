import scrapy
import json
from scrapy.http import Request
from scrapy.loader import ItemLoader
import re
from sotest.items import RepoInfo

class gitSpider(scrapy.Spider):

    name = 'git'
    start_urls = ['https://api.github.com/users/wchill']
    http_user = 'evanslify'
    http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def pageturn(link, callback):
        # grabs url, parsing its 'link' header
        # return the URL of next page to function which called this function 


        position = response.headers.get('link')
        # check whether this is the last page.
        # if yes set the callback param 'lastpage' to true, otherwise false
        # search where the second 'page' is at
        if position[-5:-1] == 'last':
            # not first page
            last_page_state = False
        else:
            last_page_state = True

        new_page = re.findall(r'\d+', response.headers.get('link')[position:])

        callback(new_url, state=last_page_state)

    def parse(self, response):
        # parse user page.
        jr = json.loads(response.body_as_unicode())
        l = ItemLoader(item=RepoInfo(), response=response)
        l.add_value({
            'user_public_repos': jr.get('public_repos'),
            'user_hireable': jr.get('hireable'),
            })

        yield item
# testing item loader
        # yield scrapy.Request(jr.get('repos_url'), self.parse_all_repos)
        # must add second arg self.___ or jr will turn into list. 

    # def parse_all_repos(self, response):
    #     # parse repo list, extract individual repo link.
        
    #     jr = json.loads(response.body_as_unicode())
    #     for i in range(1, len(jr)):
    #         yield scrapy.Request((jr[i]['url']), self.parse_repo)
    #     # a user can have many repos so we create a iterating list
    #     # to parse every repo
    #     # this may cause some bandwith problems

    # def parse_repo(self, response):
    #     # parse details from a repo.
    #     jr = json.loads(response.body_as_unicode())
    #     item = RepoInfo()
    #     item.update({
    #         'forks_from': jr.get('fork'),
    #         'url': jr.get('html_url'),
    #         'apiurl': jr.get('url'),
    #         'zipurl': jr.get('html_url') + "/archive/master.zip",
    #         })
        
    #     if 'parent' in jr:
    #         item.update({
    #          'forks_from_url': jr.get('parent').get('url'),
    #          })

    #     # yield item
    #     new_url = jr.get('forks_url') + '?per_page=100'
    #     yield scrapy.Request(new_url, self.parse_repo_forks)

    # def parse_repo_forks(self, response, state=''):
    # # parse repo forks
    # # fork can have many items, github API gives 100 max each page using ?per_page=x

    #     jr = json.loads(response.body_as_unicode())
    #     item = RepoInfo()

    #     item.update({
    #         'forks': item.get('forks', int()) + len(jr)
    #         })

    #     # check whether this repo has fork
    #     if len(jr) > 1:
    #         # ... then proceed to parse every username who forked this repo.
    #         for i in range(1, len(jr)):
    #             fork_usernames = jr[i].get('owner').get('login')
    #             item.update({
    #                 'fork_usernames': item.get('fork_usernames', '') + ", " + fork_usernames
    #                 })
    #     # implant the method to "turn page" here..
    #     headers_link = response.headers.get('Link')
    #     if state == False:
    #         # self.parse_repo_forks is a ugly way to describe itself....
    #         # call this method and this method will callback this function.
    #         self.pageturn(headers_link, self.parse_repo_forks)
    #     else:
    #         yield item
# testing item loader
# unfinished below 
        # this is a whack way "reverse replace"
        # new_url = 'contributors'.join(response.url.rsplit('forks', 1))
        # yield scrapy.Request(new_url, self.parse_repo_contributors)

    # def parse_repo_contributors(self, response):
    #     # parse this repo's count of contributors
    #     jr = json.loads(response.body_as_unicode())
    #     item = RepoInfo()
    #     item.update({
    #     'contributed_times': len(jr),
    #     })

    #     # check whether this repo has contributors
    #     if len(jr) > 1:
    #         # ... then proceed to parse every username who contributed to this repo.
    #         for i in range(1, range(1, len(jr)):
    #             fork_usernames = jr[i].get('owner').get('login')
    #             item.update({
    #                 'contributed_times': item.get('fork_usernames'), fork_usernames
    #                 })
    #     yield item
  