import subprocess

# scrapy crawl -a target={1} github

l = [
    #'xingularity',
    'euphoris',
    #'teddychoi',
    #'shimika',
    #'limeburst',
    #'earthreader',
    #'clicheio',
    #'spoqa',
    'dahlia',
    #'ZongHanXie'
]

for user in l:
    t = 'target=%s' % user
    subprocess.Popen(['scrapy', 'crawl', '-a', t, 'github'])
