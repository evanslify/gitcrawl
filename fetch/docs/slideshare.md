## Slideshare CrawlBot

* * *

    Usage
        target: <Speakerdeck user login>
    Type: 
        Website scraping

* * * 

Crawling individual slides on Slideshare is very slow, will not crawl for it's detail.


| Name         | Type | Description                         | May absent | 
|--------------|------|-------------------------------------|------------| 
| SlideInfo(#SlideInfo)    | dict | Dict of user's slides.              | y          | 
| UserInfo(#UserInfo)     | dict | Dict of user's infomations.         |            | 

### SlideInfo
| Name         | Type | Description                         | May absent | 
|--------------|------|-------------------------------------|------------| 
| views        | int  | Views                               |            | 
| title        | str  | Slide's name                        |            | 

### UserInfo
| Name         | Type | Description                         | May absent | 
|--------------|------|-------------------------------------|------------| 
| Name         | str  | User display name                   |            | 
| bio          | str  | User bio                            |            | 
| social_links(#social_links) | list | List of user's social website links | y          | 
| industry     | str  | User's work industry                |            | 
| work         | str  | User's work info                    |            | 
| location     | str  | User's location                     |            | 

### social_links
| Name         | Type | Description                         | May absent | 
|--------------|------|-------------------------------------|------------| 
| twitter      | str  | URI                                 |            | 
| googleplus   | str  | URI                                 |            | 
| facebook     | str  | URI                                 |            | 
| linkedin     | str  | URI                                 |            | 

