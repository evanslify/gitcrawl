## StackOverflow API Crawler

* * *

    Usage:
        scrapy crawl -a target=<username> -a site=<sitename> -a size=<size> -a sorting=<sorting> stackexchangesites

    Args:
        target: stackexchange userID on that specific site
        size: 30, the # of questions/answers to look for
        sorting: activity (or 'creation', 'votes'), the way the spider look for questions/answers first
        site: the stackexchange site to crawl with. e.g. stackoverflow, askubuntu, serverfault

* * *
