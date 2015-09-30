# -*- coding: utf-8 -*-
import scrapy
import json
from fetch.items import BitbucketItem


class BitbucketSpider(scrapy.Spider):
    name = "bitbucket"
    allowed_domains = ['bitbucket.org']
    handle_httpstatus_list = [404]
    http_user = 'ctbotter'
    http_pass = 'zgXFKqEHHKed'

    def __init__(self, *args, **kwargs):
        super(BitbucketSpider, self).__init__(*args, **kwargs)
        self.mode = kwargs.get('mode', 'all').split(',')
        self.target = kwargs.get('target', '')

    def callnext(
            self, response=None, body=None, caller=None, starting_meta=None):

        if starting_meta:
            meta = starting_meta
        elif not starting_meta and response:
            meta = response.request.meta
        else:
            raise Exception

        if body is not None:
            page_turn_url = body.get('next')
            if page_turn_url is not None:
                meta['callstack'].append(
                    {'url': page_turn_url, 'callback': caller})

        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)

            url = target['url']
            if 'pagelen=' not in url:
                url = url + '?pagelen=100'
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext)
        else:
            items = BitbucketItem()
            loader = response.meta.get('Loader')
            for key in loader.iterkeys():
                items[key] = loader[key]
            yield items

# ------------
# Parsing methods starts here.
# ------------
    def parse_user_object(self, input, extra_field=False):
        result = {
            'login': input.get('username'),
            'website': input.get('website'),
            'display_name': input.get('display_name'),
            'uuid': input.get('uuid')[1:-1],
            'created_on': input.get('created_on'),
            'location': input.get('location'),
            'type': input['type']
        }
        if extra_field:
            result.update({
                'followers': [],
                'following': [],
            })
        return result

    def parse_mini_user_object(self, input):
        result = {
            'login': input['username'],
            'display_name': input['display_name'],
            'type': input['type'],
            'uuid': input['uuid']
        }
        return result

    def parse_repo_object(self, input, parsing_fork=False):
        links = input['links']
        is_fork = True if input.get('parent') is not None else False

        result = {
            'has_wiki': input['has_wiki'],
            'name': input['name'],
            'uuid': input['uuid'][1:-1],
            'language': input['language'],
            'created_on': input['created_on'],
            'updated_on': input['updated_on'],
            'description': input['description'],
            'clone_url': links['clone'],
            'zipurl': links['html']['href'] + 'get/tip.zip',
            'is_fork': is_fork,
            'has_issues': input['has_issues'],
            'full_name': input['full_name'],
            'forks': [],
        }

        links = {
            'fork': links['forks']['href']
        }

        if is_fork:
            parent = input['parent']
            full_name = parent['full_name']
            parent_info = {
                'repo_name': parent['name'],
                'full_name': full_name,
                'login': full_name.split('/')[-2],
                'uuid': parent['uuid']
            }
            result['parent'] = parent_info

        if parsing_fork:
            owner = input['owner']
            owner_info = self.parse_mini_user_object(owner)
            result['owner'] = owner_info

        result_list = [result, links]
        return result_list

# ------------
# Parsing methods stops here.
# ------------

    def start_requests(self):

        meta = scrapy.Request.meta
        meta = {
            'callstack': [],
            'Loader': {
                'RepoInfo': {},
                'UserInfo': {},
                'identifier': self.target,
            }
        }
        callstack = meta['callstack']
        calls = self.parse_arguments()
        callstack.extend(calls)

        return self.callnext(starting_meta=meta)

    def parse_arguments(self):
        """
        Parses arguments from self.mode.
        @returns list
        """

        actions = []
        base_url = 'https://api.bitbucket.org/2.0'
        target = self.target
        user_url = base_url + '/users/%s' % target
        repo_url = base_url + '/repositories/%s' % target

        url_dict = {
            'user': (user_url, self.crawl_user),
            'repo': (repo_url, self.crawl_repo)
        }

        if 'all' in self.mode:
            for i in url_dict.itervalues():
                actions.append({
                    'url': i[0], 'callback': i[1]
                })
        else:
            for mode in self.mode:
                if mode in url_dict.iterkeys():
                    detail = url_dict[mode]
                    actions.append({
                        'url': detail[0], 'callback': detail[1]
                    })
                else:
                    raise Exception('Parsing mode invalid.')
        return actions

    def crawl_user(self, response):

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']

        if jr.get('error') is not None:
            # Here we check if this is a team account
            team_error = 'is a team account'
            if jr['error']['message'].endswith(team_error):
                url = response.url.replace('users', 'teams')
                callstack.append({
                    'url': url, 'callback': self.crawl_user})
        else:
            loader['UserInfo'] = self.parse_user_object(jr, extra_field=True)

            links = jr['links']
            followers_url = links['followers']['href']
            following_url = links['following']['href']

            callstack.extend([
                {'url': followers_url, 'callback': self.crawl_user_followers},
                {'url': following_url, 'callback': self.crawl_user_following}
            ])

        return self.callnext(response)

    def crawl_repo(self, response):

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['RepoInfo']
        body = jr['values']
        if body:
            for repo in body:
                result = self.parse_repo_object(repo)
                repo_info = result[0]
                name = repo_info['name'].lower()
                links = result[1]
                fork_url = links['fork']
                items[name] = repo_info
                callstack.append(
                    {'url': fork_url, 'callback': self.crawl_repo_forks})
        return self.callnext(response, body=jr, caller=self.crawl_repo)

    def crawl_repo_forks(self, response):

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['RepoInfo']
        body = jr['values']
        if body:
            repo_name = response.url.split('/')[-2]
            target = items[repo_name]
            for fork in body:
                fork_info = self.parse_repo_object(fork, parsing_fork=True)
                target['forks'].append(fork_info)
        return self.callnext(
            response, body=jr, caller=self.crawl_repo_forks)

    def crawl_user_followers(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']

        body = jr['values']
        if body:
            body = jr['values']
            for follower in body:
                info = self.parse_user_object(follower)
                items['followers'].append(info)
        return self.callnext(
            response, body=jr, caller=self.crawl_user_followers)

    def crawl_user_following(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']

        body = jr['values']
        if body:
            body = jr['values']
            for following in body:
                info = self.parse_user_object(following)
                items['following'].append(info)
        return self.callnext(
            response, body=jr, caller=self.crawl_user_following)
