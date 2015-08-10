## Codetalnet CrawlerBot for websites

### To launch spiders directly in CLI:
    > scrapy -a <arguments> <spidername>

On this page:

* [Spiders]
    * [StackOverflow](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-stackoverflow)
    * [Github](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Github)
    * [Geeklist](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Geeklist)
    * [Facebook](https://bitbucket.org/codetalent/gitcrawl/overview#markdown-header-Facebook)

## StackOverflow
    > target: <stackoverflow user display name>
    > size: 30 <int, maxinum # of questions/answers to fetch>
    > sort: activity <to sort discussion topics, use one of the following:>
    > > activity – last_activity_date
    > > creation – creation_date
    > > votes – score
[JSON outputs]

## Github
    > mode: all <parsing mode, one of following:>
    > > all
    > > user
    > > gist
    > > repo
    > target: <github username>
[JSON outputs explained][github]

## Facebook
### This spider can't work on it's own, Needs to 'feed' cookies for authorization
    [JSON outputs explained][facebook]

## Geeklist
    > Uses OAuth 1 Authorization
    > > target: <geeklist username>
[JSON outputs explained][github]

[stackoverflow]: http://pygments.org/docs/lexers/
[github]: 
[facebook]: 
[geeklist]: 