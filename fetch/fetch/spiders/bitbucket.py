# -*- coding: utf-8 -*-
import scrapy
import json
import re
from fetch.items import BitbucketItem


class BitbucketSpider(scrapy.Spider):
    name = "bitbucket"
    allowed_domains = ['bitbucket.org', 'localhost']
    start_urls = ['http://localhost/']
    handle_httpstatus_list = [404, 403]
    http_user = 'ctbotter'
    http_pass = 'zgXFKqEHHKed'

    def __init__(self, *args, **kwargs):
        super(BitbucketSpider, self).__init__(*args, **kwargs)
        self.parsing_mode = kwargs.get('mode', 'all').split(',')
        self.target_login = kwargs.get('start_url', '').split(',').pop(0)
        self.baseurl = 'https://api.bitbucket.org/2.0/'

        valid_parsing_mode = ['all', 'user', 'repo']
        for i in self.parsing_mode:
            if i not in valid_parsing_mode:
                raise Exception('Invalid parsing mode.')

    def callnext(self, response, body=None, caller=None):
        meta = response.request.meta
        if body is not None:
            page_turn_url = body.get('next', None)
            if page_turn_url is not None:
                meta['callstack'].insert(
                    0,
                    {'url': page_turn_url, 'callback': caller})
        # old callnext from gitspider, now combined with page turning.
        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            yield scrapy.Request(
                url=target['url'], meta=meta,
                callback=target['callback'], errback=self.callnext)
        else:
            items = BitbucketItem()
            loader = response.meta.get('Loader')
            items['RepoInfo'] = loader['RepoInfo']
            items['UserInfo'] = loader['UserInfo']
            yield items

    def parse(self, response):

        response.meta.update({
            'callstack': [],
            'Loader': {},
        })

        callstack = response.meta['callstack']
        loader = response.meta['Loader']

        loader['UserInfo'] = {}
        loader['RepoInfo'] = []

        current_target_login = self.target_login
        user_start_url = self.baseurl + 'users/' + current_target_login
        repo_start_url = self.baseurl + 'repositories/' + \
            current_target_login + '?pagelen=100'

        if 'all' in self.parsing_mode:
            callstack.extend([
                {'url': user_start_url, 'callback': self.parse_user},
                {'url': repo_start_url, 'callback': self.parse_repo}]),
        else:
            for arg_mode in self.parsing_mode:
                if arg_mode == 'repo':
                    callstack.append(
                        {'url': repo_start_url, 'callback': self.parse_repo})
                elif arg_mode == 'user':
                    callstack.append(
                        {'url': user_start_url, 'callback': self.parse_user})
        return self.callnext(response)

    def parse_user(self, response):

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']

        items.update({
            'user_login': jr.get('username'),
            'user_website': jr.get('website'),
            'user_display_name': jr.get('display_name'),
            'user_id': jr.get('uuid')[1:-1],
            'user_created_on': jr.get('created_on'),
            'user_location': jr.get('location'),
            'user_followers': [],
            'user_following': [],
        })

        user_links = jr.get('links')
        user_followers_url = user_links.get(
            'followers').get('href') + '?pagelen=100'
        user_following_url = user_links.get(
            'following').get('href') + '?pagelen=100'

        callstack.extend([
            {'url': user_followers_url, 'callback': self.parse_user_followers},
            {'url': user_following_url, 'callback': self.parse_user_following}
            ])

        return self.callnext(response)

    def parse_repo(self, response):

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['RepoInfo']
        useritem = loader['UserInfo']

        if jr.get('size') > 0:
            for i in jr.get('values'):
                repo = {}
                repo_is_fork = True if i.get('parent') is not None else False
                repo.update({
                    'repo_has_wiki': i.get('has_wiki'),
                    'repo_name': i.get('name'),
                    'repo_id': i.get('uuid')[1:-1],
                    'repo_language': i.get('language'),
                    'repo_created_on': i.get('created_on'),
                    'repo_updated_on': i.get('updated_on'),
                    'repo_description': i.get('description'),
                    'repo_clone_url': i.get(
                        'links').get('clone')[1].get('href'),
                    'repo_zipurl': i.get(
                        'links').get('html').get('href') + 'get/tip.zip',
                    'repo_is_fork': repo_is_fork,
                    'repo_has_issues': i.get('has_issues'),
                    'repo_full_name': i.get('full_name'),
                    'repo_forks': [],
                })

                if repo_is_fork:
                    repo_parent = i.get('parent')
                    repo_parent_full_name = i.get('full_name')
                    repo_parent_login = re.findall(
                        '(.*?)(?=/)', i.get('full_name'))[0]
                    repo.update({
                        'repo_parent_full_name': repo_parent_full_name,
                        'repo_parent_id': repo_parent.get('uuid')[1:-1],
                        'repo_parent_login': repo_parent_login
                    })
                items.append(repo)
                fork_url = i.get(
                    'links').get('forks').get('href') + '?pagelen=100'
                callstack.append(
                    {'url': fork_url, 'callback': self.parse_repo_forks})

            # in case of only querying for repositories
            useritem.update({
                'user_id': jr.get('values')[0].get('owner').get('uuid')[1:-1]})

            return self.callnext(response, body=jr, caller=self.parse_repo)
        else:
            return self.callnext(response)

    def parse_repo_forks(self, response):

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['RepoInfo']
        full_name = re.findall(
            '(?<=repositories/)(.*?)(?=/forks)', response.url)[0]
        if jr.get('size') > 0:
            target_repo = filter(
                lambda x: x['repo_full_name'] == full_name, items)[0]
            all_forks = jr.get('values')

            for i in all_forks:
                target_repo['repo_forks'].append({
                    'repo_fork_name': i.get('name'),
                    'repo_fork_id': i.get('uuid')[1:-1],
                    'repo_fork_created_on': i.get('created_on'),
                    'repo_fork_full_name': i.get('full_name'),
                    'repo_fork_has_issues': i.get('has_issues'),
                    'repo_fork_updated_on': i.get('updated_on'),
                    'repo_fork_description': i.get('description')
                })
            return self.callnext(
                response, body=jr, caller=self.parse_repo_forks)
        else:
            return self.callnext(response)

    def parse_user_followers(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']

        followers_list = items.get('user_followers')
        body = jr.get('values')
        if len(body) > 0:
            for i in body:
                followers_list.append({
                    'user_followers_login': i.get('username'),
                    'user_followers_website': i.get('website'),
                    'user_followers_display_name': i.get('display_name'),
                    'user_followers_id': i.get('uuid')[1:-1],
                    'user_followers_created_on': i.get('created_on'),
                    'user_followers_location': i.get('location'),
                })
            return self.callnext(
                response, body=jr, caller=self.parse_user_followers)
        else:
            return self.callnext(response)

    def parse_user_following(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']

        following_list = items.get('user_following')
        body = jr.get('values')
        if len(body) > 0:
            for i in body:
                following_list.append({
                    'user_following_login': i.get('username'),
                    'user_following_website': i.get('website'),
                    'user_following_display_name': i.get('display_name'),
                    'user_following_id': i.get('uuid')[1:-1],
                    'user_following_created_on': i.get('created_on'),
                    'user_following_location': i.get('location'),
                })
            return self.callnext(
                response, body=jr, caller=self.parse_user_following)
        else:
            return self.callnext(response)
