from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import SignalManager
import spiders
import time
import commons


class GetResults(object):

    def process_item(self, item, spider):
        results.append(dict(item))


class FailLogger(object):

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
        return ext

    def spider_error(self, failure, response, spider):
        print("Error on {0}, traceback: {1}").format(
            response.url, failure.getTraceback())


# def spider_closed(spider):
#     print results

# set up settings
settings = get_project_settings()

settings.set('EXTENSIONS', {'__main__.FailLogger': 1}, priority='cmdline')
crawler = CrawlerProcess(settings)
# sig = SignalManager()
# sig.connect(receiver=spider_closed, signal=signals.spider_closed)


def check_spider_list():

    missing = []
    spider_list = crawler.spider_loader.list()
    for i in spider_list:
        if i not in spiders.arg_dict:
            missing.append(i)

    print '----------------------------------------------------------------'
    if missing:
        print 'These spiders are missing in arg_dict:'
        for missing_spider in missing:
            print missing_spider
    else:
        print 'All spiders are defined in arg_dict.'


def test_all():
    print '----------------------------------------------------------------'
    print 'TEST FOR ALL SPIDERZ ARE OVERKILL!'
    print 'READYSETGO!!!'
    check_spider_list()
    start_time = time.time()
    times_runned = 0
    print '----------------------------------------------------------------'
    for i in spiders.arg_dict.iteritems():
        commons.teststart(name=i[0], target=i[1])
        times_runned += 1
    crawler.start()
    time_used = time.time() - start_time
    return (time_used, times_runned)

run = test_all()
time_used = run[0]
time_runned = run[1]

print '----------------------------------------------------------------'
print 'Done'
print 'Ran %s spiders in %s seconds' % (time_runned, time_used)
