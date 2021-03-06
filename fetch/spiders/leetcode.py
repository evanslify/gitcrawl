# -*- coding: utf-8 -*-
import scrapy
from fetch.items import LeetCodeItem


class LeetcodeSpider(scrapy.Spider):
    name = "leetcode"

    def __init__(self, *args, **kwargs):
        super(LeetcodeSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')
        self.mode = kwargs.get('mode', 'all').split(',')
        self.visited_url = []

        # these are caches for storing visited answer / question ID
        # which can tell whether this topic is a question or answer by the
        # user we are scrapping for.
        # (you cannot distunguish a question or answer by url on leetcode)
        self._temp_a_list = []
        self._temp_q_list = []

    def callnext(self, response=None, caller=None, start_meta=None):

        if not start_meta and response:
            meta = response.request.meta
        elif start_meta and not response:
            meta = start_meta
        else:
            raise Exception

        callstack = meta['callstack']

        if len(callstack) > 0:
            target = callstack.pop(0)
            url = target['url']

            if url in self.visited_url:
                # url has been visited, draw the next card from callstack.
                target = callstack.pop(0)
                url = target['url']
            else:
                self.visited_url.append(url)

            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext)

        else:
            items = LeetCodeItem()
            loader = response.meta.get('Loader')
            for key in loader.iterkeys():
                items[key] = loader[key]
            yield items

    def start_requests(self):
        # override scrapy's own method to start requests.

        meta = scrapy.Request.meta
        # actually I'm not sure why this works without declaring a new
        # instance of scrapy.Request :(

        # declaring item loader's layout.
        meta = {
            'callstack': [],
            'Loader': {
                'UserInfo': {},
                'QuestionInfo': [],
                'AnswerInfo': [],
                'identifier': self.target,
            }
        }
        callstack = meta['callstack']

        calls = self.parse_arguments()
        callstack.extend(calls)
        return self.callnext(start_meta=meta)

    def parse_arguments(self):
        actions = []
        base_url = 'https://leetcode.com/discuss/user/'
        user_url = base_url + self.target
        question_url = user_url + '/questions'
        answer_url = user_url + '/answers'

        url_dict = {
            'user': (user_url, self.crawl_user),
            'question': (question_url, self.crawl_topic_list),
            'answer': (answer_url, self.crawl_topic_list)
        }

        if 'all' in self.mode:
            for value in url_dict.itervalues():
                actions.append({
                    'url': value[0], 'callback': value[1]
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
        if self.target is None:
            raise Exception('No username entered.')
        return actions

    # define reuseable object

    def parse_user(self, input):

        score = input.xpath(
            '//span[@class="qa-uf-user-points"]/text()').extract_first()
        questions = input.xpath(
            '//span[@class="qa-uf-user-q-posts"]/text()').extract_first()
        answers = input.xpath(
            '//span[@class="qa-uf-user-a-posts"]/text()').extract_first()
        comments = input.xpath(
            '//span[@class="qa-uf-user-c-posts"]/text()').extract_first()
        voted_question = input.xpath(
            '//span[@class="qa-uf-user-q-votes"]/text()').extract_first()
        voted_answer = input.xpath(
            '//span[@class="qa-uf-user-a-votes"]/text()').extract_first()
        give_upvote = input.xpath(
            '//span[@class="qa-uf-user-upvotes"]/text()').extract_first()
        give_downvote = input.xpath(
            '//span[@class="qa-uf-user-downvotes"]/text()').extract_first()
        got_upvote = input.xpath(
            '//span[@class="qa-uf-user-upvoteds"]/text()').extract_first()
        got_downvote = input.xpath(
            '//span[@class="qa-uf-user-downvoteds"]/text()').extract_first()

        result = {
            'score': score,
            'questions': questions,
            'answers': answers,
            'comments': comments,
            'voted_answer': voted_answer,
            'voted_question': voted_question,
            'give_downvote': give_downvote,
            'give_upvote': give_upvote,
            'got_downvote': got_downvote,
            'got_upvote': got_upvote
        }

        return result

    def parse_topic_list(self, input):
        # parses input
        # returns a 2-list
        # first element, {'url': url, 'id': id} or none
        # second element, url of nextpage or None

        urls = input.xpath(
            '//div[@class="qa-q-item-title"]/a/@href').extract()

        if urls:
            base = 'https://leetcode.com/discuss'
            url_list = []
            for topic_url in urls:
                id = topic_url.split('/')[2]
                url = base + topic_url[5:]
                url_list.append({
                    'url': url, 'id': id})

            next = input.xpath(
                '//a[@class="qa-page-next"]/@href').extract_first()
            if next:
                next_url = base + next[5:]
            else:
                next_url = None

            return [url_list, next_url]
        else:
            return

    def parse_post_meta(self, input):

        time = input.xpath(
            'span[2]/span[contains(@class, "when")]//'
            'span[@class="value-title"]/@title').extract_first()
        author = input.xpath(
            'span[2]/span[contains(@class, "who")]//'
            'a[@class="qa-user-link"]/text()').extract_first()
        author_score = input.xpath(
            'span[2]/span[contains(@class, "who")]//'
            'span[contains(@class, "who-points-data")]/text()').extract_first()
        result = {
            'time': time,
            'author': author,
            'author_score': author_score,
        }

        catagory = input.xpath(
            'span[2]/span[contains(@class, "where")]//'
            'a[@class="qa-category-link"]/text()').extract_first()

        if catagory:
            result['catagory'] = catagory

        return result

    def parse_post(self, input, answer=None):
        content = input.xpath(
            '(div[1]//div[contains(@class, "entry-content")])[1]//*'
        ).extract()

        if not content:
            # weird. returns none. fallback.
            content = input.xpath(
                '(div[1]//div[contains(@class, "entry-content")])//text()'
            ).extract()
        else:
            content = ''.join(content)

        meta_raw = input.xpath(
            'div[1]//span[contains(@class, "avatar-meta")]')

        if not meta_raw:
            # means we're parsing comment then
            meta_raw = input.xpath(
                'div[2]//span[@class="qa-c-item-avatar-meta"]')
            votes_info = None

        else:
            votes = input.xpath(
                'form[1]//span[@class="qa-netvote-count-data"]')
            votes_up = votes.xpath(
                'span[@class="votes-up"]/span/@title').extract_first()
            votes_down = votes.xpath(
                'span[@class="votes-down"]/span/@title').extract_first()
            votes_info = {
                'up': votes_up,
                'down': votes_down
            }

        meta = self.parse_post_meta(meta_raw)

        result = {
            'content': content,
            'meta': meta,
            'votes': votes_info
        }

        if answer:
            # parsing an answer
            best_answer = input.xpath(
                'div[1]//div[@class="qa-a-selected"]')
            if best_answer:
                result['best_answer'] = True

        comment_raw = input.xpath(
            'div[1]//div[@class="qa-c-list-item  hentry comment"]')
        if comment_raw:
            comments_list = []
            for one_comment in comment_raw:
                comment = self.parse_post(one_comment)
                comments_list.append(comment)
            result['comments'] = comments_list

        return result

    def parse_topic(self, input):
        title = input.xpath(
            '//span[@class="entry-title"]/text()').extract_first()
        question_item = input.xpath(
            '//div[contains(@class, "hentry question")]')
        question = self.parse_post(question_item)

        answer_item = input.xpath(
            '//div[contains(@class, "hentry answer")]')
        answer_list = []
        if answer_item:
            for posts in answer_item:
                answer = self.parse_post(posts, answer=True)
                answer_list.append(answer)

        result = {
            'title': title,
            'question': question,
            'answers': answer_list
        }
        return result

    # end define reuseable object

    def crawl_user(self, response):

        loader = response.meta['Loader']
        loader['UserInfo'] = self.parse_user(response)

        return self.callnext(response)

    def crawl_topic_list(self, response):

        callstack = response.meta['callstack']
        loader = response.meta['Loader']

        mode = response.url.split('/')[-1]

        if 'questions' in mode:
            id_list = self._temp_q_list
        elif 'answers' in mode:
            id_list = self._temp_a_list
        else:
            raise Exception('Something went wrong.')

        urls = self.parse_topic_list(response)
        if urls:
            for one_url in urls[0]:
                callstack.append({
                    'url': one_url['url'], 'callback': self.crawl_topic
                })
                id_list.append(one_url['id'])

            if urls[1]:
                # next page exists
                callstack.append({
                    'url': urls[1], 'callback': self.crawl_topic_list
                })
        return self.callnext(response)

    def crawl_topic(self, response):

        loader = response.meta['Loader']

        topic_id = response.url.split('/')[4]
        if topic_id in self._temp_q_list:
            items = loader['QuestionInfo']
        elif topic_id in self._temp_a_list:
            items = loader['AnswerInfo']
        else:
            raise Exception('Something went wrong.')

        result = self.parse_topic(response)
        items.append(result)

        return self.callnext(response)
