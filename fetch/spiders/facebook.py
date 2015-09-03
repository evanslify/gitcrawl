# -*- coding: utf-8 -*-
import scrapy
import json
from fetch.items import FacebookItem
from scrapy.utils.project import get_project_settings
import redis
import re
from urlparse import urljoin


class FacebookSpider(scrapy.Spider):

    name = 'facebook'

    def __init__(self, *args, **kwargs):
        super(FacebookSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')
        self.mode = kwargs.get('mode')

    def callnext(self, response, cookies=None, start_meta=None):

        try:
            meta = response.request.meta
        except AttributeError:
            meta = start_meta
        headers = {
            'Host': 'm.facebook.com',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:39.0) Gecko/20100101 '
                'Firefox/39.0'),
            'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9'
                       ',*/*;q=0.8'),
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://m.facebook.com/',
            'Accept-Encoding': 'gzip, deflate'
        }
        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            url = target['url']
            if target.get('arg') == 'noheader':
                headers = ''
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext,
                cookies=cookies, headers=headers)
        else:
            items = FacebookItem()
            loader = response.meta.get('Loader')
            for key in loader.iterkeys():
                items[key] = loader[key]
            yield items

    def start_requests(self):
        # override scrapy's own method to start requests.
        meta = scrapy.Request.meta
        meta = {
            'callstack': [],
            'Loader': {
                'identifier': self.target
            }
        }
        callstack = meta['callstack']
        cookiez = self.get_cookiez()
        c_user = cookiez['c_user']
        # Checks whether self.target(argument) matches with the cookie c_user
        # If assert fails means that you have given the wrong cookie.
        assert c_user == self.target
        callstack.extend(self.parse_argument())
        return self.callnext(self, start_meta=meta, cookies=cookiez)

    def parse_argument(self):
        """
        Parse arguments from self.mode, which is
        > scrapy -a mode=(friends|profile|events|groups)
        @returns List of dicts contains url and callback
        """
        # pase user info
        profile_url = (
            'https://m.facebook.com/profile.php?v=info'
            '&id=%s') % self.target
        friends_url = 'https://m.facebook.com/friends/center/friends'
        events_url = 'https://m.facebook.com/events/past'
        group_url = 'https://m.facebook.com/groups?seemore'

        url_dict = {
            'profile': (profile_url, self.parse_mobile),
            'friends': (friends_url, self.crawl_friend_list),
            'events': (events_url, self.crawl_event),
            'groups': (group_url, self.crawl_groups)}
        results = []
        if self.mode:
            mode_list = self.mode.split(',')
            for mode in mode_list:
                if mode in url_dict.iterkeys():
                    cursor = url_dict[mode]
                    results.append(
                        {'url': cursor[0], 'callback': cursor[1]})
                else:
                    raise Exception('Weird mode given.')
        else:
            for url, func in url_dict.itervalues():
                results.append({
                    'url': url, 'callback': func})
        return results

    def get_cookiez(self):
        # read from redis!
        settings = get_project_settings()
        redis_uri = settings.get('REDIS_DB_URI', 'localhost')
        redis_port = settings.get('REDIS_DB_PORT', 6379)
        redis_auth = settings.get('REDIS_DB_AUTH', '')
        redis_db = 0
        pool = redis.ConnectionPool(
            host=redis_uri, port=redis_port,
            db=redis_db, password=redis_auth)
        r = redis.StrictRedis(connection_pool=pool)
        cookiez = r.get(self.target)
        if cookiez is None:
            error_message = (
                'No cookies found in DB #%s at %s') % (redis_db, redis_uri)
            raise Exception(error_message)
        else:
            jr = json.loads(cookiez)
        return jr

    def parse_mobile(self, response):

        loader = response.meta['Loader']

        items = loader.setdefault('UserInfo', {})

        # parse dispay name
        name = response.xpath(
            '//div[@id="root"]//strong[@class]/text()').extract_first()

        # parse work!
        works = []
        for work in response.xpath(
                '//div[@id="work"]//div[starts-with(@id, "exp")]'):
            # conditions in <div class="bq">:
            # 4 <div> elements: comment / date / location supplied
            # 3 <div> elements: one of date / location is supplied
            # 2 <div> elements: one of date / location is supplied
            # 1 <div> elements: only company name supplied
            work_name = work.xpath(
                'div/div/div/div[1]/span[1]/a/text()').extract_first()
            work_facebook_uri = work.xpath(
                'div/div/div/div[1]/span[1]/a/@href').extract_first()

            work = {
                'work_name': work_name,
                'work_facebook_uri': work_facebook_uri,
            }
            works.append(work)

        # parse education!
        edus = []
        for school in response.xpath(
                '//div[@id="education"]//div[starts-with(@id, "exp")]'):
            edu_name = school.xpath(
                'div/div/div/div[1]//a/text()').extract_first()
            edu_facebook_uri = school.xpath(
                'div/div/div/div[1]//a/@href').extract_first()
            edu_desc = school.xpath(
                'div/div/div/div[2]//span/text()').extract_first()
            edu = {
                'edu_name': edu_name,
                'edu_facebook_uri': edu_facebook_uri,
                'edu_description': edu_desc
            }
            edus.append(edu)

        # parse skillz!
        skills = response.xpath(
            '//div[@id="skills"]/div/div[2]//span/text()'
        ).extract_first()

        # parse living ah!
        current_city = response.xpath(
            '//div[@id="living"]//div[@title="Current City"]//a/text()'
        ).extract_first()
        hometown = response.xpath(
            '//div[@id="living"]//div[@title="Hometown"]//a/text()'
        ).extract_first()
        living = {
            'hometown': hometown,
            'current_city': current_city
        }

        # parse contact info
        contact_info = response.xpath(
            '//div[@id="contact-info"]/div')

        contact_phone = contact_info.xpath(
            'div//div[@title="Mobile"]//span[@dir]/text()').extract_first()
        contact_skype = contact_info.xpath(
            'div//div[@title="Skype"]//td[2]/div/text()').extract_first()
        contact_email = contact_info.xpath(
            'div//div[@title="Email"]//td[2]/div/text()').extract_first()
        contact_site = contact_info.xpath(
            'div//div[@title="Website"]//td[2]/div/a/@href'
        ).extract_first()

        contact_info = {
            'phone': contact_phone,
            'website': contact_site,
            'skype': contact_skype,
            'email': contact_email
        }

        # parse basic info
        basics_infos = response.xpath(
            '//div[@id="basic-info"]/div/div[2]')

        basic_birthday = basics_infos.xpath(
            'div[@title="Birthday"]//td[2]//text()').extract_first()
        basic_bloodtype = basics_infos.xpath(
            'div[@title="Blood Type"]//td[2]//text()').extract_first()
        basic_languages = basics_infos.xpath(
            'div[@title="Languages"]//td[2]//text()').extract_first()
        basic_gender = basics_infos.xpath(
            'div[@title="Gender"]//td[2]//text()').extract_first()
        basic_info = {
            'birthday': basic_birthday,
            'bloodtype': basic_bloodtype,
            'languages': basic_languages,
            'gender': basic_gender
        }

        items.update({
            'name': name,
            'works': works,
            'educations': edus,
            'skills': skills,
            'living': living,
            'contact_info': contact_info,
            'basic_infos': basic_info
        })

        return self.callnext(response)

    def crawl_event(self, response):

        loader = response.meta['Loader']
        items = loader.setdefault('EventInfo', {})
        callstack = response.meta['callstack']
        #  for events in response.xpath('//div[@class="bg bo"]'):

        for events in response.xpath(
                '//td[@id="events_card_list"]/div[@class][not(id)]'
                '[contains(@class," ")][string-length(@class) = 5]'):
                # wtf?

            title = events.xpath(
                'div/div[1]//h4/text()').extract_first()
            #  event_month = events.xpath(
            #      'div/div[2]/span/span[1]/text()').extract_first()
            #  event_day = events.xpath(
            #      'div/div[2]/span/span[2]/text()').extract_first()
            #  event_time = events.xpath(
            #      'div/div[2]/div[1]/span/text()').extract_first()
            event_loc = events.xpath(
                'div/div[2]/div[2]/span/text()').extract_first()
            event_city = events.xpath(
                'div/div[2]/div[3]/span/text()').extract_first()
            event_id = re.findall('(?<=events\/).*?(?=\?)', events.xpath(
                'div/div[2]//a/@href').extract_first())[0]
            result = {
                #  'month': event_month,
                #  'day': event_day,
                #  'time': event_time,
                'loc': event_loc,
                'city': event_city,
                'id': event_id,
                'title': title
            }
            items[event_id] = result
            event_url = 'https://m.facebook.com/events/%s' % event_id
            event_json_url = (
                'https://www.facebook.com/events/typeahead/guest_list/?event_'
                'id=%s&tabs[0]=going&tabs[1]=maybe&tabs[2]=invited&tabs[3]=de'
                'clined&order[declined]=affinity&order[going]=affinity&order['
                'invited]=affinity&order[maybe]=affinity&order[watched]=affin'
                'ity&bucket_schema[going]=friends&bucket_schema[maybe]=friend'
                's&bucket_schema[invited]=friends&bucket_schema[declined]=fri'
                'ends&__user=1582133957&__a=1&__req=10') % event_id
            callstack.extend([
                {'url': event_url, 'callback': self.crawl_event_detail},
                {'url': event_json_url, 'callback': self.crawl_event_json,
                    'arg': 'noheader'}])

        more = response.xpath('//div[@id="event_list_seemore"]')
        if more:
            url1 = more.xpath('a/@href').extract_first()
            url = urljoin(response.url, url1)
            callstack.append({
                'url': url, 'callback': self.crawl_event})

        return self.callnext(response)

    def crawl_groups(self, response):

        loader = response.meta['Loader']
        item = loader.setdefault('GroupInfo', [])
        for group in response.xpath(
                '//h3[text() = "Groups"]/following-sibling::ul/li'):
            info = group.xpath('table//a')
            url = info.xpath('@href').extract_first()
            name = info.xpath('text()').extract_first()
            item.append({
                'url': url,
                'name': name})
        return self.callnext(response)

    def crawl_event_json(self, response):
        # monkey hack :D see the magic here.
        """
        Magic JSON function to parse a event's participants.
        """
        loader = response.meta['Loader']
        event_id = re.findall('(?<=event_id=)\d+(?=&)', response.url)[0]
        items = loader['EventInfo'].setdefault(event_id, {})
        """
        JSON response:
            'bootloadable'
            'lid'
            '__ar'
        --->'payload' --> 'maybe'    --> 'cursor'
            'ixData'      'invited'      'sections' ----> [0]: useless
                          'going'        'emailCursor'    [1]: friends
                          'declined'                      [2]: not friends
                                                          [3]: email invite(?)
        """
        jr = json.loads(response.body_as_unicode()[9:])
        items['participants'] = jr['payload']
        return self.callnext(response)

    def crawl_event_detail(self, response):

        loader = response.meta['Loader']
        event_id = response.url.split('/')[-1]
        items = loader['EventInfo'][event_id]

        for st in response.xpath('//div[@id="event_button_bar"]//a'):
            tag_class = st.xpath('@class').extract()
            for tag in tag_class:
                tag_size = len(tag.split())
                if tag_size == 6:
                    status = st.xpath('/span/text()').extract_first()
                else:
                    status = None
        time = response.xpath(
            '//div[@id="event_summary"]/div[1]/@title').extract_first()
        x_hoster = response.xpath(
            '//div[@id="event_header"]//a[starts-with(@href, "/profile.php")]')
        hoster = []
        for host in x_hoster:
            host_id = host.xpath('@href')
            host_name = host.xpath('text()')
            hoster.append({
                'id': host_id,
                'name': host_name})
        x_inviter = response.xpath(
            '//div[@id="event_summary"]/div[starts-with(@title, "Invited by")]'
            '/@title').extract()
        inviter = []
        for one_inviter in x_inviter:
            inviter.append(one_inviter.strip('Invited by '))

        desc = response.xpath(
            '//div[@id="event_description"]/div/div').extract_first()

        items.update({
            'status': status,
            'time': time,
            'inviter': inviter,
            'description': desc})

        return self.callnext(response)

    def crawl_friend_list(self, response):

        loader = response.meta['Loader']
        items = loader.setdefault('FriendInfo', [])
        callstack = response.meta['callstack']

        for friend in response.xpath(
                '//div[@id="friends_center_main"]/div[2]/*'):
            url = friend.xpath('table//a/@href').extract_first()
            name = friend.xpath('table//a/text()').extract_first()
            mutuals = friend.xpath(
                'table//a/following-sibling::div/text()').extract_first()
            items.append({
                'url': url,
                'name': name,
                'mutuals': mutuals})
        more = response.xpath('//span[text() = "See More"]')
        if more:
            raw_new_url = more.xpath('../@href').extract_first()
            url = urljoin(response.url, raw_new_url)
            callstack.append({
                'url': url, 'callback': self.crawl_friend_list})
        return self.callnext(response)
