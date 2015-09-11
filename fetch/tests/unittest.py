from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import SignalManager
import spiders
import commons
import argparse
from jsonschema import Draft4Validator
import codecs
import time
import glob
import json


class GetResults(object):

    def process_item(self, item, spider):
        spider_name = getattr(spider, 'name')
        if args.validate:
            schema_validate(item, spider_name)
        if args.save:
            saver(item, spider_name)


def saver(item, spider_name):
    filename = spider_name + '.json'
    with codecs.open(filename, 'w+', 'utf-8') as file:
        thing = dict(item)
        file.write(json.dumps(thing))


def schema_validate(input, spider_name):

    query = 'schemas/schema_%s.json' % spider_name
    filename = glob.glob(query)
    print '----------------------------------------------------------------'
    print 'Validating...'
    global error_count
    if filename:
        file = codecs.open(filename[0], 'r', 'utf-8').read()
        schema = json.loads(file)

        validator = Draft4Validator(schema)
        errors = sorted(
            validator.iter_errors(dict(input)), key=lambda e: e.path)
        if errors:
            for error in errors:
                error_count += 1
                print list(error.path), error.context, error.message

    else:
        print 'JSON Schema is not found. Generating one automatically...'
        commons.generate_schema(input, spider_name)
        print 'Done. Please review it manually.'

def check_spider_list(name):

    spider_list = crawler.spider_loader.list()
    for i in spider_list:
        if name not in spiders.arg_dict:
            raise Exception('Spider missing in arg_dict')
    else:
        return True


def get_arg_list(name):

    if check_spider_list(name):
        target = spiders.arg_dict[name]
        return target


def test_one(name, target):

    target_query = get_arg_list(name)
    if target_query:
        target = target_query

    print '----------------------------------------------------------------'
    print 'Running test for %s.' % name
    print 'Tests are leet!'

    start_time = time.time()
    commons.teststart(name=name, target=target, crawler=crawler)
    crawler.start()
    time_used = time.time() - start_time
    return time_used

# settings
settings = get_project_settings()
settings.set('ITEM_PIPELINES', {'__main__.GetResults': 1}, priority='cmdline')
crawler = CrawlerProcess(settings)
sig = SignalManager()
# sig.connect(receiver=schema_validate, signal=signals.spider_closed)
# parser

parser = argparse.ArgumentParser(description='Run one spider.')

parser.add_argument(
    'name', metavar='name', type=str, help='Spider name')

parser.add_argument(
    "target", type=str,
    help='target username (if absent: lookup in the spiders.py)')

parser.add_argument(
    "-validate", dest='validate', action='store_true',
    help='Validate with JSON schema')

parser.add_argument(
    "-save", dest='save', action='store_true',
    help='save JSON')

# parser
args = parser.parse_args()
error_count = 0
run = test_one(name=args.name, target=args.target)


print '----------------------------------------------------------------'
print 'Done with %s errors' % error_count
print 'Ran 1 spider in %s seconds' % run
