# working :(
    
import scrapy
import json
import re
from scrapy.http import Request
from scrapy.loader import ItemLoader

class GitSpider(scrapy.Spider):
    name = 'git'

    start_urls = ['https://api.github.com/users/xxg1413']

    http_user = 'evanslify'
    http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def callnext(self, response):

        ''' Call next target for the item loader, or yields it if completed. '''
        # borrowed from http://goo.gl/OfMLXG
        # Get the meta object from the request, as the response
        # does not contain it.
        meta = response.request.meta
        # Items remaining in the stack? Execute them
        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            yield scrapy.Request(url=target['url'], meta=meta, callback=target['callback'], errback=self.callnext)
        else:
            yield response.meta.get('Loader').get('UserInfo')

        if len(meta['callstack']) % 3 == 0:
            yield response.meta.get('Loader').get('RepoInfo')

    def pageturn(self, header):
        # called only when response.headers.get('Link') returns valid 
        # (indicates that this request has multiple pages)

        if header.find('next') != -1:
            # if valid, first url will be the next page
            new_page = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', header)[0][:-2]
        else:
            new_page = 'last'
        return str(new_page)

    def parse(self, response):

        # parsing user page.
        # https://api.github.com/users/<username>

        jr = json.loads(response.body_as_unicode())

        response.meta.update({'Loader': {'UserInfo': {
            'user_public_repo_counts': jr.get('public_repos'),
            'user_hireable': jr.get('hireable'),
            'user_id': jr.get('login'),
            'user_name': jr.get('name'),
            'user_blog': jr.get('blog'),
            'user_followers_count': jr.get('followers')
            }}})
        new_url = jr.get('repos_url') + '?per_page=100'
        response.meta.update({'callstack': [{'url': new_url, 'callback': self.parse_all_repos}]})
        # from pudb import set_trace; set_trace()
        return self.callnext(response)
        
    def parse_all_repos(self, response):
        # parsing repository list of a user
        items = response.meta['Loader']
        jr = json.loads(response.body_as_unicode())

        repo_urls = []
        repo_urls_to_parse = []
        response.meta.update({'callstack': []})
        callstack = response.meta['callstack']
                
        for i in range(0, len(jr)):
            repo_urls.append(jr[i]['url'])

        for ii in range(0, len(repo_urls)):
            # repo_urls[ii] = https://api.github.com/repos/<username>/<reponame>
            callstack.append({'url': repo_urls[ii], 'callback': self.parse_repo})
            callstack.append({'url': repo_urls[ii] + '/forks?per_page=100', 'callback': self.parse_repo_forks})
            callstack.append({'url': repo_urls[ii] + '/contributors?per_page=100', 'callback': self.parse_repo_contributors})

        return self.callnext(response)

    def parse_repo(self, response):
        # parsing details from a repository
        items = response.meta['Loader']
        jr = json.loads(response.body_as_unicode())

        items.update({'RepoInfo': {
            'forks_from': jr.get('fork'),
            'url': jr.get('html_url'),
            'apiurl': jr.get('url'),
            'zipurl': jr.get('html_url') + "/archive/master.zip",
            'forks_from_url': jr.get('parent').get('url') if jr.get('parent') != None else '',
            }})

        return self.callnext(response)
        
    def parse_repo_forks(self, response):
    # parse repo forks
    # fork can have many items, github API gives 100 max each page using ?per_page=x
        items = response.meta['Loader']
        jr = json.loads(response.body_as_unicode())
        fork_usernames = []

        if len(jr) > 1:
            for i in range(1, len(jr)):
                fork_usernames.append(jr[i].get('owner').get('login'))

        old_fork_usernames = items.get('RepoInfo').get('fork_usernames', [])

        items.get('RepoInfo').update({
            'forks': len(jr) + items.get('RepoInfo').get('forks', 0),
            'fork_usernames': old_fork_usernames + fork_usernames,
            })

        # implant the method to "turn page" here..
        turn = ''
        callstack = response.meta['callstack']

        if 'Link' in response.headers:
            turn = self.pageturn(response.headers.get('Link'))

        if turn != 'last' and turn != '':
            callstack.insert(0, {
                            'url': turn, 'callback': self.parse_repo_forks,
                            })
            return self.callnext(response)
        else:
            return self.callnext(response)

    def parse_repo_contributors(self, response):
        # parse this repo's count of contributors
        items = response.meta['Loader']
        jr = json.loads(response.body_as_unicode())
        
        items.get('RepoInfo').update({
            'contributed_times': len(jr),
            })

        # check whether this repo has contributors
        if len(jr) > 1:
            contributed_users = []
            # ... then proceed to parse every username who contributed to this repo.
            for i in range(1, len(jr)):
                contributed_users.append(jr[i].get('login'))
                item.update({
                    'contributed_users': contributed_users,
                    })
        
        return self.callnext(response)