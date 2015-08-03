import scrapy
import oauthlib.oauth1
import json
import re
from fetch.items import GeeklistItem


class GeeklistSpider(scrapy.Spider):
    name = 'geeklist'
    handle_httpstatus_list = [404, 403]

    def __init__(self, *args, **kwargs):
        super(GeeklistSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target', '')
        if self.target == '':
            raise Exception('No username entered.')
        self.baseurl = 'http://api.geekli.st/v1/'
        self.client = oauthlib.oauth1.Client(
            'MCYiDVpKltiM-BrxR7scJA2JOI8',
            client_secret='ZuzBUwGw1143L4xDALNO0FQnrMFvO4jvfGMP_M_DpXc',
            resource_owner_key='oR68e1cmMU9RinlPqqGQ8n-LNZI',
            resource_owner_secret='eKmoNnVeHXj7zhMFYPYdzRJZFlr_'
            'oguYFRZVihTuPfA')

    def page_plus_one(self, input):
        # determine previous page number and +1
        pagination = re.findall(
                '(?<=page=)(\d+)', input)[0]
        if len(pagination) > 0:
            # a pagination query string already exists
            new_pagination = int(pagination) + 1
            next_page_url = re.sub(
                '(?<=page=)(\d+)', new_pagination, input)
        else:
            # no pagination query string exists
            if input.find('?') == -1:
                # check if we need to write a '?' to the end of url
                url = ''.join((input, '?'))
            next_page_url = url + '&page=1'

        return next_page_url

    def callnext(self, response, caller=None, status=False):

        # trick to override the default parsing method :D
        try:
            meta = response.request.meta
        except AttributeError:
            meta = response

        if status is not False:
            url = self.page_plus_one(input=response.url)
            meta['callstack'].insert(
                    0,
                    {'url': url, 'callback': caller})

        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            url = target['url']
            headers = self.client.sign(url)[1]
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext,
                headers=headers)
        else:
            # from pudb import set_trace; set_trace()
            items = GeeklistItem()
            loader = response.meta.get('Loader')
            items['UserInfo'] = loader['UserInfo']
            yield items

    def start_requests(self):
        # trick to override default parse method :D
        # from pudb import set_trace; set_trace()

        meta = scrapy.Request.meta
        meta = {
            'callstack': [],
            'Loader': {}
            }
        callstack = meta['callstack']

        # start generating dict of urls
        names_list = ['micros', 'contribs', 'cards']
        urls = {}
        for i in names_list:
            url = (
                self.baseurl + 'users/' + self.target + '/' + i + '?count=50')
            urls.update({
                i: url
                })
        user_url = self.baseurl + 'users/' + self.target
        urls.update({
            'user': user_url
            })
        self.urls = urls
        # stop of generating dict of urls

        # we will decide whether to parse cards / contribs later
        callstack.extend([
            {'url': urls['user'], 'callback': self.parse_user_page},
            {'url': urls['micros'], 'callback': self.parse_user_micros}])
        return self.callnext(response=meta)

    def parse_user_page(self, response):

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        loader['UserInfo'] = {}
        items = loader['UserInfo']
        data = jr.get('data')
        stats = data.get('stats')
        items.update({
            'user_id': data.get('_id'),
            'user_bio': data.get('bio'),
            'user_blog_link': data.get('blog_link'),
            'user_created_at': data.get('created_at'),
            'user_email': data.get('email'),
            'user_location': data.get('location'),
            'user_name': data.get('name'),
            'user_login': data.get('screen_name'),
            'user_social_links': data.get('social_links'),
            'user_trending_at': data.get('trending_at'),
            'user_trending_by': data.get('trending_by'),
            'user_github': data.get('github'),
            'user_stats': stats,
            'user_social': data.get('social'),
            'user_company': data.get('company'),
            'user_micros': [],
            'user_contribs': [],
            'user_cards': [],
            })

        next_urls = []
        if stats.get('number_of_cards') is not 0:
            next_urls.append(
                {'url': self.urls['cards'],
                 'callback': self.parse_user_cards})

        if stats.get('number_of_contributions') is not 0:
            next_urls.append(
                {'url': self.urls['contribs'],
                 'callback': self.parse_user_contribs})

        return self.callnext(response)

    def parse_user_micros(self, response):

        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']['user_micros']

        # this function is called on every query
        # make sure to check whether there are items
        data = jr.get('data')
        if data.get('total_micros') == 0:
            return self.callnext(response)

        data_micro = jr.get('data').get('micros')

        for i in data_micro:
            items.append({
                'micro_status': i.get('status'),
                'micro_slug': i.get('slig'),
                'micro_permalink': i.get('permalink'),
                'micro_uuid': i.get('_id'),
                'micro_trending_at': i.get('trending_at'),
                'micro_trending_by': i.get('trending_by'),
                'micro_updated_at': i.get('updated_at'),
                'micro_updated_by': i.get('updated_by'),
                'micro_stats': i.get('stats'),
                })

        total_counts = data.get('total_micros')

        if len(items) < total_counts:
            status = True
        else:
            status = False

        return self.callnext(
            response, status=status, caller=self.parse_user_micros)

    def parse_user_contribs(self, response):
        # only called when contrib > 0
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']['user_contribs']

        data_contribs = jr.get('data').get('cards')
        for i in data_contribs:
            items.append({
                'contrib_uuid': i.get('_id'),
                'contrib_author_uuid': i.get('author_id'),
                'contrib_created_at': i.get('created_at'),
                'contrib_headline': i.get('headline'),
                'contrib_permalink': i.get('permalink'),
                'contrib_stats': i.get('stats'),
                'contrib_trending_history': i.get('trending_history'),
                'contrib_link': i.get('link'),
                'contrib_skills': i.get('skills'),
                'contrib_tasks': i.get('tasks'),
                'contrib_updated_at': i.get('updated_at'),
                'contrib_endorsement': i.get('endorsement'),
                'contrib_given_to': i.get('given_to'),
                })
        total_counts = jr.get('data').get('total_cards')

        if len(items) < total_counts:
            status = True
        else:
            status = False
        return self.callnext(
            response, status=status, caller=self.parse_user_contribs)

    def parse_user_cards(self, response):
        # only called when cards > 0
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['UserInfo']['user_cards']

        cards = jr.get('data').get('cards')
        for i in cards:
            items.append({
                'card_stats': i.get('stats'),
                'card_headline': i.get('headline'),
                'card_tasks': i.get('tasks'),
                'card_created_at': i.get('created_at'),
                'card_updated_at': i.get('updated_at'),
                'card_trending_at': i.get('trending_at'),
                'card_skills': i.get('skills'),
                'card_link': i.get('link'),
                'card_endorsement': i.get('endorsement'),
                'card_given_to': i.get('given_to'),
                'card_uuid': i.get('_id'),
                'card_author_uuid': i.get('author_id'),
                'card_permalink': i.get('permalink')
                })

        total_counts = jr.get('data').get('total_cards')
        if len(items) < total_counts:
            status = True
        else:
            status = False
        return self.callnext(
            response, status=status, caller=self.parse_user_cards)
