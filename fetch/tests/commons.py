import genson
import codecs
import json


def teststart(name, target, crawler):

    print('----------------------------------------------------------------')
    print('Scheduled: %s, Target: %s' % (name, target))
    crawler.crawl(name, target=target)


def generate_schema(item, spider_name):

    gen = genson.Schema()
    gen.add_object(dict(item))
    filename = 'schemas/schema_%s.json' % spider_name
    file = codecs.open(filename, 'w+', 'utf-8')
    file.write(gen.to_json())
    file.close()
