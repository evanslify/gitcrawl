import scrapy
import json
import re
from fetch.items import GithubItem
'''
GitHub crawler under Scrapy framework
usage: scrapy crawl -a start_url='<github username>' -a mode='<all/user,gist,repo>' git
'''


class GitSpider(scrapy.Spider):
    name = 'github'

    start_urls = ['http://localhost/']
    handle_httpstatus_list = [404, 403]
    http_user = 'evanslify'
    http_pass = '4e4b57cc169d0e7a6812f73a9a48843b84a2200b'

    def __init__(self, *args, **kwargs):
        super(GitSpider, self).__init__(*args, **kwargs)
        self.parsing_mode = kwargs.get('mode', 'all').split(',')
        self.target_login = kwargs.get('target', '').split(',').pop(0)
        self.baseurl = 'https://api.github.com'

        valid_parsing_mode = ['all', 'user', 'gist', 'repo']
        for i in self.parsing_mode:
            if i not in valid_parsing_mode:
                raise Exception('Invalid parsing mode.')

    def callnext(self, response):
        # Call next target for the item loader, or yields it if completed. http://goo.gl/OfMLXG
        # Get the meta object from the request, as the response
        # does not contain it.
        meta = response.request.meta
        # Items remaining in the stack? Execute them
        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            yield scrapy.Request(url=target['url'], meta=meta, callback=target['callback'], errback=self.callnext)
        else:
            item = GithubItem()
            loader = response.meta.get('Loader')
            item['GistInfo'] = loader['GistInfo']
            item['UserInfo'] = loader['UserInfo']
            item['RepoInfo'] = loader['RepoInfo']
            yield item

    def pageturn(self, header, url):
        # called only when response.headers.get('Link') returns valid
        # (indicates that this request has multiple pages)

        if header.find('next') != -1:
            # if valid, first url will be the next page
            new_page_number = re.findall('(?<=&page=)[0-9]', header)[0]
            new_page = re.sub('(?<=&page=)[0-9]', new_page_number, url)
        else:
            new_page = 'last'
        return str(new_page)

    def parse(self, response):

        response.meta.update({
            'callstack': [],
            'Loader': {},
            })

        callstack = response.meta['callstack']
        loader = response.meta['Loader']

        loader['UserInfo'] = {}
        loader['GistInfo'] = []
        loader['RepoInfo'] = []

        user_start_url = self.baseurl + '/users/%s' % self.target_login
        gist_start_url = user_start_url + '/gists?per_page=100&page=1'
        repo_start_url = user_start_url + '/repos?per_page=100&page=1'
        login = self.target_login
        search_id_url = 'https://api.github.com/search/users?q=' + login + '%20in:login&per_page=1'

        callstack.append({
            'url': search_id_url, 'callback': self.parse_user_id
            })
        if 'all' in self.parsing_mode:
            callstack.extend([
                {'url': user_start_url, 'callback': self.parse_user_page},
                {'url': gist_start_url, 'callback': self.parse_user_gists},
                {'url': repo_start_url, 'callback': self.parse_all_repos}])
            return self.callnext(response)
        else:
            for arg_mode in self.parsing_mode:
                if arg_mode == 'repo':
                    callstack.append(
                        {'url': repo_start_url, 'callback': self.parse_all_repos})
                elif arg_mode == 'gist':
                    callstack.append(
                        {'url': gist_start_url, 'callback': self.parse_user_gists})
                elif arg_mode == 'user':
                    callstack.append(
                        {'url': user_start_url, 'callback': self.parse_user_page})
            return self.callnext(response)

    def parse_user_id(self, response):

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']
        user_id = jr.get('items')[0].get('id')
        items.update({
            'user_id': user_id
            })
        return self.callnext(response)

    def parse_user_page(self, response):
        # parsing user page.
        # https://api.github.com/users/<username>

        jr = json.loads(response.body_as_unicode())

        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']

        items.update({
            # 'user_id': jr.get('id'),
            'user_html_url': jr.get('html_url'),
            'user_public_repo_count': jr.get('public_repos'),
            'user_public_gist_count': jr.get('public_gists'),
            'user_email': jr.get('email'),
            'user_followers_count': jr.get('followers'),
            'user_company': jr.get('compant'),
            'user_hireable': jr.get('hireable'),
            'user_id': jr.get('id'),
            'user_login': jr.get('login'),
            'user_name': jr.get('name'),
            'user_blog': jr.get('blog'),
            'user_location': jr.get('location'),
            'user_bio': jr.get('bio'),
            'user_following_count': jr.get('following'),
            'user_created': jr.get('created_at'),
            'user_updated': jr.get('updated_at'),
            'user_api_url': response.url,
            'user_following': [],
            'user_followers': []
        })

        followers_url = response.url + '/followers?per_page=100&page=1'
        html_userpage_followers_url = items.get('user_html_url') + '/followers'
        following_url = response.url + '/following?per_page=100&page=1'
        html_userpage_following_url = items.get('user_html_url') + '/following'
        starred_url = response.url + '/starred?per_page=100&page=1'

        html_userpage_js_url = items.get(
            'user_html_url') + '?tab=contributions&from=2013-01-08&_pjax=.js-contribution-activity'

        if items['user_followers_count'] > 0:
            callstack.extend([
                {'url': followers_url, 'callback': self.parse_user_followers},
                {'url': html_userpage_followers_url, 'callback': self.parse_html_user_followers}])
        if items['user_following_count'] > 0:
            callstack.extend([
                {'url': following_url, 'callback': self.parse_user_following},
                {'url': html_userpage_following_url, 'callback': self.parse_html_user_following}])
        callstack.extend([
            {'url': starred_url, 'callback': self.parse_user_starred},
            {'url': html_userpage_js_url, 'callback': self.parse_html_userpage_js}])

        return self.callnext(response)

    def parse_html_userpage_js(self, response):
        loader = response.meta['Loader']
        items = loader['UserInfo']

        contrib_number = response.selector.xpath(
            '//span[@class="contrib-number"]/text()').extract()

        items.update({
            'user_last_year_contributes': contrib_number[0],
            'user_longest_streak': contrib_number[1],
            'user_current_streak': contrib_number[2],
            })

        return self.callnext(response)

    def parse_html_user_followers(self, response):
        # clone of parse_html_user_following
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']['user_followers']

        user_followers_name_list = response.selector.xpath(
            '//h3[@class="follow-list-name"]/span/a/text()').extract()
        user_followers_info_list = response.selector.xpath(
            '//p[@class="follow-list-info"]/descendant-or-self::text()').extract()
        user_followers_info_list = [name for name in user_followers_info_list if name.strip()]

        for i in range(0, len(user_followers_name_list)):
            current_login = response.selector.xpath(
                '//h3[@class="follow-list-name"]/span/a/@href').extract()[i][1:]
            target_followers_user = filter(lambda x: x['user_followers_login'] == current_login, items)[0]
            target_followers_user.update({
                'user_followers_name': user_followers_name_list[i],
                'user_followers_info': user_followers_info_list[i],
            })

        html_pagination = response.selector.xpath(
            '//div[@class="pagination"]/a[text()[contains(.,"Next")]]/@href').extract()
        if len(html_pagination) > 0:
            callstack.insert(
                0,
                {'url': html_pagination[0], 'callback': self.parse_html_user_followers})

        return self.callnext(response)

    def parse_html_user_following(self, response):
        # clone of parse_html_user_followers
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']['user_following']

        user_following_name_list = response.selector.xpath(
            '//h3[@class="follow-list-name"]/span/a/text()').extract()
        user_following_info_list = response.selector.xpath(
            '//p[@class="follow-list-info"]/descendant-or-self::text()').extract()
        user_following_info_list = [name for name in user_following_info_list if name.strip()]

        for i in range(0, len(user_following_name_list)):
            current_login = response.selector.xpath(
                '//h3[@class="follow-list-name"]/span/a/@href').extract()[i][1:]
            target_followers_user = filter(lambda x: x['user_following_login'] == current_login, items)[0]
            target_followers_user.update({
                'user_following_name': user_following_name_list[i],
                'user_following_info': user_following_info_list[i],
            })

        html_pagination = response.selector.xpath(
            '//div[@class="pagination"]/a[text()[contains(.,"Next")]]/@href').extract()
        if len(html_pagination) > 0:
            callstack.insert(
                0,
                {'url': html_pagination[0], 'callback': self.parse_html_user_following})

        return self.callnext(response)

    def parse_user_followers(self, response):
        # https://api.github.com/users/<username>/followers?per_page=100
        # only called when followers > 0

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']

        followers_list = []
        for i in range(0, len(jr)):
            followers_list.append({
                'user_followers_id': jr[i].get('id'),
                'user_followers_login': jr[i].get('login')})

        items.update({
            'user_followers': followers_list,
        })

        if 'Link' in response.headers:
            headers_link = response.headers.get('Link')
            turn = self.pageturn(headers_link, response.url)
            if turn is not 'last':
                callstack.append({
                    'url': turn, 'callback': self.parse_user_followers,
                })
        return self.callnext(response)

    def parse_user_following(self, response):
        # only called when following > 0
        # https://api.github.com/users/<username>/following?per_page=100

        loader = response.meta['Loader']
        items = loader['UserInfo']

        jr = json.loads(response.body_as_unicode())

        following_list = []

        for i in range(0, len(jr)):
            following_list.append({
                'user_following_id': jr[i].get('id'),
                'user_following_login': jr[i].get('login'),
            })

        items.update({
            'user_following': following_list,
        })

        return self.callnext(response)

    def parse_user_gists(self, response):
        # only called when public_gists > 0
        # https://api.github.com/users/<username>/gists

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['GistInfo']

        for i in range(0, len(jr)):
            gist = jr[i]
            file_info = gist.get('files').values()[0]
            items.append({
                'gist_id': gist.get('id'),
                'gist_created': gist.get('created_at'),
                'gist_comment_counts': gist.get('comments'),
                'gist_file_type': file_info.get('type'),
                'gist_file_language': file_info.get('language'),
                'gist_raw_url': file_info.get('raw_url'),
            })
            if gist.get('comments') > 0:
                callstack.insert(0, {
                    'url': gist.get('comments_url'), 'callback': self.parse_user_gists_comments,
                })
            # callstacks calles by order starting from index 0
            # if gist have comments, that gist comment url will be inserted to front of the callstack
            # so next non-gist-parsing-move must be appended to the end of
            # callstack

        return self.callnext(response)

    def parse_user_gists_comments(self, response):
        # only called when a gist has comment.
        # https://api.github.com/gists/<Gist ID>/comments

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['GistInfo']
        gist_id = re.findall('(?<=gists/)(.*)(?=/)', response.url)[0]
        target_gist = filter(lambda x: x['gist_id'] == gist_id, items)
        # this filters out the dict with current Gist ID we need from the pool of all Gists.
        # only [{dict of Gist ID}] will be left in target_gist.

        comments = []
        for i in range(0, len(jr)):
            comment = jr[i]
            commenting_user = jr[i]['user']
            comments.append({
                'gist_commenting_time': comment.get('created_at'),
                'gist_commenting_content': comment.get('body'),
                'gist_commenting_id': comment.get('id'),
                'gist_commenting_user_id': commenting_user.get('id'),
                'gist_commenting_user_login': commenting_user.get('login'),
            })
        target_gist[0]['comments'] = comments

        return self.callnext(response)
        # self.parse_user_gist_comments doesn't need to fetch URL for
        # callstack!

    def parse_user_starred(self, response):
        # always called. make sure to check whether len(jr) is true.
        # https://api.github.com/users/<username>/starred

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']

        if len(jr) != 0:
            user_starred = []
            for i in range(0, len(jr)):
                # gist_info = jr[i].get('files').values()[0]
                user_starred.append({
                    'user_starred_repo_id': jr[i].get('id'),
                    'user_starred_repo_name': jr[i].get('name'),
                    'user_starred_repo_owner_id': jr[i].get('owner').get('id'),
                    'user_starred_repo_owner_login': jr[i].get('owner').get('login'),
                })

        items['user_starred'] = user_starred

        return self.callnext(response)

    def parse_all_repos(self, response):
        # https://api.github.com/users/<username>/repos
        # parsing repository list of a user
        # includes repo info
        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['RepoInfo']

        for i in range(0, len(jr)):
            target = jr[i]
            # apiurl = target.get('url')
            items.append({
                'repo_id': target.get('id'),
                'repo_name': target.get('name'),
                'repo_created_at': target.get('created_at'),
                'repo_updated_at': target.get('updated_at'),
                'repo_pushed_at': target.get('pushed_at'),
                'repo_homepage': target.get('homepage'),
                'repo_stars_count': target.get('stargazers_count'),
                'repo_watchers_count': target.get('watchers_count'),
                'repo_language': target.get('language'),
                'repo_forks_count': target.get('forks_count'),
                'repo_forks_from': target.get('fork'),
                'repo_open_issues_count': target.get('open_issues_count'),
                'repo_url': target.get('user_html_url'),
                'repo_apiurl': target.get('url'),
                'repo_zipurl': target.get('html_url') + "/archive/master.zip",
                'repo_description': target.get('description'),
            })

            repo_detail_url = target.get('url')
            repo_stargazers_url = target.get(
                'stargazers_url') + '?per_page=100&page=1'
            repo_forks_url = target.get('forks_url') + '?per_page=100&page=1'
            repo_issues_url = target.get('url') + '/issues?per_page=100&page=1'
            repo_contributors_url = target.get(
                'contributors_url') + '?per_page=100&page=1'

            add_urls = []
            if target.get('fork') == True:
                add_urls.append(
                    {'url': repo_detail_url, 'callback': self.parse_repo_detail_url})
                # ok
            if target.get('stargazers_count') > 0:
                add_urls.append(
                    {'url': repo_stargazers_url, 'callback': self.parse_repo_stargazers})
                # ok
            if target.get('forks_count') > 0:
                add_urls.append(
                    {'url': repo_forks_url, 'callback': self.parse_repo_forks})
                # ok
            if target.get('open_issues_count') > 0:
                add_urls.append(
                    {'url': repo_issues_url, 'callback': self.parse_repo_issues})
                # ok
            add_urls.append(
                {'url': repo_contributors_url, 'callback': self.parse_repo_contributors})
            # ok

            callstack.extend(add_urls)

        if 'Link' in response.headers:
            headers_link = response.headers.get('Link')
            turn = self.pageturn(headers_link, response.url)
            if turn is not 'last':
                callstack.append({
                    'url': turn, 'callback': self.parse_all_repos,
                })
        
        return self.callnext(response)

    def parse_repo_forks(self, response):
        # parse repo forks
        # this is loaded only while forked count > 1
        # https://api.github.com/repos/<username>/<repository name>/forks

        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['RepoInfo']

        current_repo_name = response.url.split('/')[-2]
        target_repo = filter(
            lambda x: x['repo_name'] == current_repo_name, items)
        items = target_repo[0]
        jr = json.loads(response.body_as_unicode())
        forking_users = []

        for i in range(0, len(jr)):
            target = jr[i].get('owner')
            forking_user_login = target.get('login')
            forking_user_id = target.get('id')

            forking_users.append({
                'login': forking_user_login,
                'id': forking_user_id,
            })

        if items.get('repo_forks') is not None:
            items['repo_forks'].extend(forking_users)
        else:
            items.update({
                'repo_forks': forking_users,
            })

        # implant the method to "turn page" here

        if 'Link' in response.headers:
            headers_link = response.headers.get('Link')
            turn = self.pageturn(headers_link, response.url)
            if turn is not 'last':
                callstack.insert(0, {
                    'url': turn, 'callback': self.parse_repo_forks,
                })
        return self.callnext(response)

    def parse_repo_contributors(self, response):
        # parse this repo's count of contributors
        # always run, always check whether len() is True.
        loader = response.meta['Loader']
        items = loader['RepoInfo']

        if response.status == 204:
            return self.callnext(response)

        jr = json.loads(response.body_as_unicode())

        current_repo_name = response.url.split('/')[-2]
        target_repo = filter(
            lambda x: x['repo_name'] == current_repo_name, items)
        items = target_repo[0]

        items['repo_contributed_times'] = len(jr)

        # check whether this repo has contributors
        if len(jr) > 1:
            contributed_users = []
            # then proceed to parse every username
            # which contributed to this repository
            for i in range(1, len(jr)):
                contributed_users.append(jr[i].get('login'))
                items.update({
                    'repo_contributed_users': contributed_users,
                })

        return self.callnext(response)

    def parse_repo_detail_url(self, response):
        # go to the details page of a repository
        # to parse the repository's parent.
        # only called while a repository is forked from someone.
        # https://api.github.com/repos/<username>/<repository name>

        loader = response.meta['Loader']
        items = loader['RepoInfo'][0]

        jr = json.loads(response.body_as_unicode())

        fork_parent = jr.get('parent')
        fork_parent_owner = fork_parent.get('owner')
        items.update({
            'repo_fork_parent_login': fork_parent_owner.get('login'),
            'repo_fork_parent_id': fork_parent_owner.get('id'),
            'repo_fork_parent_repository_id': fork_parent.get('id'),
        })
        return self.callnext(response)

    def parse_repo_stargazers(self, response):
        # https://api.github.com/repos/<username>/<repository name>/stargazers
        # only called while a repository has stargazers.
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['RepoInfo']

        current_repo_name = response.url.split('/')[-2]
        target_repo = filter(
            lambda x: x['repo_name'] == current_repo_name, items)
        items = target_repo[0]

        jr = json.loads(response.body_as_unicode())

        stargazers = []
        for i in range(0, len(jr)):
            target = jr[i]
            stargazers.append({
                'repo_stargazer_id': target.get('id'),
                'repo_stargazer_login': target.get('login'),
            })

        if items.get('repo_stargazers') is not None:
            items['repo_stargazers'].extend(stargazers)
        else:
            items.update({
                'repo_stargazers': stargazers,
            })

        if 'Link' in response.headers:
            headers_link = response.headers.get('Link')
            turn = self.pageturn(headers_link, response.url)
            if turn is not 'last':
                callstack.insert(0, {
                    'url': turn, 'callback': self.parse_repo_stargazers,
                })

        return self.callnext(response)

    def parse_repo_issues(self, response):
        # https://api.github.com/repos/<username>/<repository name>/stargazers
        # only called while a repository has stargazers.
        loader = response.meta['Loader']
        items = loader['RepoInfo'][0]
        jr = json.loads(response.body_as_unicode())

        issue_submitters = []
        for i in range(0, len(jr)):
            issue = jr[i]
            issue_submitter = issue.get('user')
            issue_submitters.append({
                'repo_issue_submitter_id': issue_submitter.get('id'),
                'repo_issue_submitter_login': issue_submitter.get('login'),
            })

        items.update({
            'repo_issue_submitters': issue_submitters,
        })

        return self.callnext(response)
