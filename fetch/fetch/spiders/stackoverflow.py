# -*- coding: utf-8 -*-
import scrapy
from fetch.items import StackOverflowItem
import json


class StackOverflowSpider(scrapy.Spider):
    name = "stackoverflow"

    def __init__(self, *args, **kwargs):
        super(StackOverflowSpider, self).__init__(*args, **kwargs)
        self.target = kwargs.get('target')
        if self.target is None:
            raise Exception('No username entered.')
        self.sorting = kwargs.get('sorting', 'activity')
        allow_sortings = ['activity', 'creation', 'votes']
        if self.sorting not in allow_sortings:
            raise Exception('Invalid sorting method given.')
        self.query_size = int(kwargs.get('size', 30))

        self.key = '&key=Hqgd6TsMOJsOSdR3UNkVmg(('
        self.search_user_filter = '!bZPqQ_eGrS84JR'
        self.question_filter = (
            ')jxf1*W)HMRItxIKZut.fsS_MratGaN(M0.UccqWSSk2wP_V')
        self.answer_filter = '!--pn9sThVUTv'

    def callnext(self, response=None, caller=None, start_meta=None):
        try:
            meta = response.request.meta
        except AttributeError:
            meta = start_meta

        if len(meta['callstack']) > 0:
            target = meta['callstack'].pop(0)
            url = target['url']
            yield scrapy.Request(
                url=url, meta=meta,
                callback=target['callback'], errback=self.callnext)
        else:
            items = StackOverflowItem()
            loader = response.meta.get('Loader')
            items['UserInfo'] = loader['UserInfo']
            items['PostInfo'] = loader['PostInfo']
            items['identifier'] = loader['identifier']
            yield items

# ----------------------------------------------------------------
# Start declaring methods to parse JSON items.
# ----------------------------------------------------------------

    def parse_shallow_user(self, input):
        '''
        Parses one shallow user object.
        '''
        if input is None:
            shallow_user = None
        else:
            shallow_user = {
                'user_repuation': input.get('repuation'),
                'user_stackoverflow_id': input.get('user_id'),
                'user_type': input.get('user_type'),
                'user_display_name': input.get('display_name'),
                'user_accept_rate': input.get('accept_rate')
                }
        return shallow_user

    def parse_comment(self, input):
        '''
        Parses a list of comment objects,
        and returns a list of parsed comments
        '''
        if input is None:
            comment_list = None
        else:
            comment_list = []
            for i in input:
                owner = i.get('owner')
                reply_to = i.get('reply_to_user')
                reply_to_user = self.parse_shallow_user(reply_to)
                comment = {
                    'comment_owner': self.parse_shallow_user(owner),
                    'comment_reply_to_user': reply_to_user,
                    'comment_edited': i.get('edited'),
                    'comment_score': i.get('score'),
                    'comment_creation_date': i.get('creation_date'),
                    'comment_id': i.get('comment_id'),
                    'comment_body': i.get('body')
                    }
                comment_list.append(comment)
        return comment_list

    def parse_answer(self, input):
        '''
        Parses a list of answer objects,
        and returns a list of answer comments
        '''
        if input is None:
            answer_list = None
        else:
            answer_list = []
            for i in input:
                owner = i.get('owner')
                editor = i.get('last_editor')
                comment = i.get('comments')
                answer = {
                    'answer_owner': self.parse_shallow_user(owner),
                    'answer_comments': self.parse_comment(comment),
                    'answer_tags': i.get('tags'),
                    'answer_last_editor': self.parse_shallow_user(editor),
                    'answer_comment_count': i.get('comment_count'),
                    'answer_down_vote_count': i.get('down_vote_count'),
                    'answer_up_vote_count': i.get('up_vote_count'),
                    'answer_is_accepted': i.get('is_accepted'),
                    'answer_score': i.get('score'),
                    'answer_last_activity': i.get('last_activity_date'),
                    'answer_last_edit_date': i.get('last_edit_date'),
                    'answer_creation_date': i.get('creation_date'),
                    'answer_id': i.get('answer_id'),
                    'answer_body':  i.get('body'),
                }
                answer_list.append(answer)
        return answer_list

    def parse_question(self, input):
        '''
        Parse a list of question objects,
        returns a list of parsed questions.
        '''
        if input is None:
            question_list = None
        else:
            question_list = []
            for i in input:
                answers = i.get('answers')
                owner = i.get('owner')
                comments = i.get('comments')
                editor = i.get('last_editor')
                question = {
                    'question_answers': self.parse_answer(answers),
                    'question_tags': i.get('tags'),
                    'question_owner': self.parse_shallow_user(owner),
                    'question_comments': self.parse_comment(comments),
                    'question_last_editor': self.parse_shallow_user(editor),
                    'question_comment_count': i.get('comment_count'),
                    'question_del_vote_count': i.get('delete_vote_count'),
                    'question_reopen_vote_count': i.get('reopen_vote_count'),
                    'question_close_vote_count': i.get('close_vote_count'),
                    'question_is_answered': i.get('is_answered'),
                    'question_view_count': i.get('view_count'),
                    'question_favorite_count': i.get('favorite_count'),
                    'question_down_vote_count': i.get('down_vote_count'),
                    'question_up_vote_count': i.get('up_vote_count'),
                    'question_accepted_answer_id': i.get('accepted_answer_id'),
                    'question_answer_count': i.get('answer_count'),
                    'question_community_owned_date': i.get(
                        'community_owned_date'),
                    'question_score': i.get('score'),
                    'question_last_activity': i.get('last_activity_date'),
                    'question_creation_date': i.get('creation_date'),
                    'question_edit_date': i.get('last_edit_date'),
                    'question_id': i.get('question_id'),
                    'question_title': i.get('title'),
                    'question_body': i.get('body')
                }
                question_list.append(question)
        return question_list

# ----------------------------------------------------------------
# End declaring methods to parse JSON items.
# ----------------------------------------------------------------

    def start_requests(self):
        # override scrapy's own method to start requests.
        meta = scrapy.Request.meta
        # declaring item loader's layout.
        meta = {
            'callstack': [],
            'Loader': {
                'UserInfo': {},
                'PostInfo':
                    {
                        'QuestionInfo': [],
                        'AnswerInfo': []
                    },
                'identifier': '',
                # 'temp': {}
            }
        }

        callstack = meta['callstack']

        # generate the query URI to search for username
        url = (
            'https://api.stackexchange.com/2.2/users?'
            'pagesize=1&order=asc&min=1&sort=name&inname=%s&site='
            'stackoverflow&filter=%s') % (
            self.target, self.search_user_filter + self.key)
        callstack.extend([
            {'url': url, 'callback': self.search_user}])

        return self.callnext(start_meta=meta)

    def search_user(self, response):
        '''
            StackExchange sites does not support searching for users
            by email or other identifiers.
            The only way to make sure the user is that we're looking for,
            is by kindly asking user to send us OAuth tokens and
            use that token to make API queries.
            This not viable for now(August 7 2015) so unfortunately
            we go to API search page and humbly takes the first result
            that API returned as the user that we're looking for.
        '''
        '''
            Parses user search page for user infomation.
        '''
        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']
        loader = response.meta['Loader']
        items = loader['UserInfo']

        # user_items
        u_item = jr.get('items')[0]
        u_id = u_item.get('user_id')
        user_answer_count = u_item.get('answer_count')
        user_question_count = u_item.get('question_count')
        items.update({
            'user_badges': u_item.get('badge_counts'),
            'user_view_count': u_item.get('view_count'),
            'user_down_vote_count': u_item.get('down_vote_count'),
            'user_up_vote_count': u_item.get('up_vote_count'),
            'user_answer_count': user_answer_count,
            'user_question_count': user_question_count,
            'user_stackexchange_id': u_item.get('account_id'),
            'user_is_employee': u_item.get('is_employee'),
            'user_last_modified': u_item.get('last_modified_date'),
            'user_last_access': u_item.get('last_access_date'),
            'user_age': u_item.get('age'),
            'user_repuation_change_stat': {
                'day': u_item.get('repuation_change_day'),
                'month': u_item.get('repuation_change_month'),
                'quarter': u_item.get('repuation_change_quarter'),
                'week': u_item.get('repuation_change_week'),
                'year': u_item.get('repuation_change_year')},
            'user_repuation': u_item.get('repuation'),
            'user_creation_date': u_item.get('creation_date'),
            'user_type': u_item.get('user_type'),
            'user_stackoverflow_id': u_id,
            'user_accept_rate': u_item.get('accept_rate'),
            'user_about_me': u_item.get('about_me'),
            'user_location': u_item.get('location'),
            'user_website_url': u_item.get('website_url'),
            'user_profile_link': u_item.get('link'),
            'user_display_name': u_item.get('display_name')
        })

        # use stackoverflow ID as our unique identifier.
        loader['identifier'] = u_id

        # generate the next url:
        # to parse the list of top voted ~100 posts by this user
        if user_question_count > 0:
            asked_by_user_url = (
                'https://api.stackexchange.com/2.2/users/%s/questions?'
                'pagesize=%s&order=desc&sort=%s&site=stackoverflow'
                '&filter=%s') % (
                u_id, self.query_size, self.sorting,
                self.question_filter + self.key)
            callstack.append(
                {'url': asked_by_user_url, 'callback': self.parse_user_asked})

        if user_answer_count > 0:
            answer_list_url = (
                'https://api.stackexchange.com/2.2/users/%s/answers?'
                'pagesize=%s&order=desc&sort=%s&site=stackoverflow&'
                'filter=%s') % (
                u_id, self.query_size, self.sorting,
                self.answer_filter + self.key)
            callstack.append({
                'url': answer_list_url,
                'callback': self.parse_user_answer_list})

        return self.callnext(response)

    def parse_user_asked(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['PostInfo']['QuestionInfo']

        questions = jr.get('items')
        items.append(self.parse_question(questions))

        return self.callnext(response)

    def parse_user_answer_list(self, response):

        jr = json.loads(response.body_as_unicode())
        callstack = response.meta['callstack']

        ids = jr.get('items')
        id_list = []
        for i in ids:
            id = i.get('question_id')
            id_list.append(id)
        id_list_str = ';'.join(str(x) for x in id_list)
        url = (
            'http://api.stackexchange.com/2.2/questions/%s?pagesize=%s&'
            'order=desc&sort=%s&site=stackoverflow&filter=%s') % (
            id_list_str, self.query_size, self.sorting,
            self.question_filter + self.key)
        callstack.append({
            'url': url,
            'callback': self.parse_user_answered_questions})

        return self.callnext(response)

    def parse_user_answered_questions(self, response):
        jr = json.loads(response.body_as_unicode())
        loader = response.meta['Loader']
        items = loader['PostInfo']['AnswerInfo']

        questions = jr.get('items')
        items.append(self.parse_question(questions))

        return self.callnext(response)
