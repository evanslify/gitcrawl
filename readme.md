## CodeTalent CrawlerBot for websites

### To launch spiders directly in CLI
    scrapy -a <arguments> <spider name>

On this page:

* Crawlers
    * [StackOverflow](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-stackoverflow)
    * [Github](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Github)
    * [Geeklist](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Geeklist)
    * [Facebook](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Facebook)

## StackOverflow
    target: <stackoverflow user display name>
    size: 30 <int, maximum # of questions/answers to fetch>
    sort: activity <the order to sort discussion topics>
        activity – last_activity_date
        creation – creation_date
        votes – score
[JSON output](src/master/docs/output/stack.json)
[JSON output documentation](src/master/docs/output/github.json)

## Github
    mode: all <parsing mode, one of following:>
        all
        user
        gist
        repo
    target: <github username>
[JSON output](src/master/docs/output/github.json)
[JSON output documentation](src/master/docs/output/github.md)

## Facebook
### This spider can't work on it's own, Needs to 'feed' cookies for authorization
[JSON output](src/master/docs/output/facebook.json)
[JSON output](src/master/docs/output/facebook.md)


## Geeklist
Uses OAuth 1 Authorization
    target: <geeklist username>
[JSON outputs](src/master/docs/output/geeklist.json)
[JSON outputs documentation](src/master/docs/output/geeklist.md)