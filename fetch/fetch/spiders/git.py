import scrapy
import json
from scrapy.http import Request
from scrapy.loader import ItemLoader
import re
from fetch.items import RepoInfo, UserInfo
import logging

class GitSpider(scrapy.Spider):
    name = 'git'

    start_urls = ['https://api.github.com/users/Ocramius',
                  'https://api.github.com/users/michalbe',
                  'https://api.github.com/users/kevinsawicki',
                  'https://api.github.com/users/brianchandotcom',
                  'https://api.github.com/users/fabpot',
                  'https://api.github.com/users/weierophinney',
                  'https://api.github.com/users/GrahamCampbell',
                  'https://api.github.com/users/mrmrs',
                  'https://api.github.com/users/rkh',
                  'https://api.github.com/users/md-5']

    http_user = 'evanslify'
    http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def pageturn(self, header):
        # check whether this is the last page.
        # logging.info('Pageturn is running.')

        if header.find('next') != -1:
        # if 'next' is found, this is not the last page
            new_page = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', header)[0][:-2]
            # long fucking regex
            # returns the first URL
        else:
            new_page = 'last'
        return str(new_page)


    def parse(self, response):

        # parse user page.
        jr = json.loads(response.body_as_unicode())
        item = UserInfo()
        item.update({
            'user_public_repo_counts': jr.get('public_repos'),
            'user_hireable': jr.get('hireable'),
            'user_id': jr.get('login'),
            'user_name': jr.get('name'),
            'user_blog': jr.get('blog'),
            'user_followers_count': jr.get('followers'),
            })

        yield item
        new_url = jr.get('repos_url') + '?per_page=100'
        yield scrapy.Request(new_url, self.parse_all_repos)
        # go to repos page
        
        if int(response.headers.get('X-RateLimit-Remaining')) < 100:
            logging.critical('Remaining ratelimit <100, stopping')
            return

        # stops while remaining ratelimit <100......

    def parse_all_repos(self, response):
        
        # parse repo list, extract individual repo link.
        # a user can have many repos so we create a iterating list
        # to parse every repo
        # this may cause some bandwith problems
        jr = json.loads(response.body_as_unicode())
        repo_urls = []
        for i in range(1, len(jr)):
            repo_urls.append(jr[i]['url'])
        for url in repo_urls:
            # yield scrapy.Request(url, self.parse_repo)
            yield scrapy.Request(url, self.parse_repo)

    def parse_repo(self, response):
        
        # parse details from a repo.

        jr = json.loads(response.body_as_unicode())
        item = RepoInfo()
        item.update({
            'forks_from': jr.get('fork'),
            'url': jr.get('html_url'),
            'apiurl': jr.get('url'),
            'zipurl': jr.get('html_url') + "/archive/master.zip",
            })
        
        if 'parent' in jr:
            item.update({
             'forks_from_url': jr.get('parent').get('url'),
             })
        # yield item
        new_url = jr.get('forks_url') + '?per_page=100'
        yield item
        yield scrapy.Request(new_url, self.parse_repo_forks)
        

    def parse_repo_forks(self, response):
    # parse repo forks
    # fork can have many items, github API gives 100 max each page using ?per_page=x
        
        jr = json.loads(response.body_as_unicode())
        item = RepoInfo()
        
        item.update({
            'forks': item.get('forks', int()) + len(jr)
            })        

        # check whether this repo has fork
        if len(jr) > 1:
        # then proceed to parse every username who forked this repo.
            for i in range(1, len(jr)):
                fork_usernames = jr[i].get('owner').get('login')
                item.update({
                    'fork_usernames': item.get('fork_usernames', '') + ", " + fork_usernames
                    })

        # implant the method to "turn page" here..
        turn = ""

        if 'Link' in response.headers:
            # logging.info('sending to pageturn: ' + response.headers.get('Link'))
            turn = self.pageturn(response.headers.get('Link'))
            # logging.info('now querying url: ' + response.url)
            # logging.info('got link header: ' + response.headers.get('Link'))
            # logging.info('pageturn replies: ' + turn)

        if turn != 'last' and turn != "":
            yield scrapy.Request(turn, self.parse_repo_forks)

        else:
            yield item
            # this is a whack way "reverse replace"
            new_url = 'contributors'.join(response.url.rsplit('forks', 1))
            yield scrapy.Request(new_url, self.parse_repo_contributors)

    def parse_repo_contributors(self, response):
        # parse this repo's count of contributors
        jr = json.loads(response.body_as_unicode())
        item = RepoInfo()
        item.update({
        'contributed_times': len(jr),
        })

        # check whether this repo has contributors
        if len(jr) > 1:
            # ... then proceed to parse every username who contributed to this repo.
            for i in range(1, len(jr)):
                contributed_users = jr[i].get('login')
                item.update({
                    'contributed_users': item.get('contributed_users', '') + ", " + contributed_users
                    })

        return item
        return