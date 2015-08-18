## Speakerdeck CrawlBot

* * *

    Usage
        target: <Speakerdeck user login>
    Type: 
        Website scraping

    Speakerdeck is slow, so this bot won't be fast like it's siblings.

* * * 

| Name        | Type | Description                   | May absent | 
|-------------|------|-------------------------------|------------| 
| SlideInfo   | dict | Dict of user's slides.        | y          | 
| UserInfo    | dict | Dict of user's infomations.   |            | 

### Slide
| Name        | Type | Description                   | May absent | 
|-------------|------|-------------------------------|------------| 
| category    | str  | Slide's category              |            | 
| description | str  | Description                   |            | 
| views       | int  | Views                         |            | 
| title       | str  | Slide's name                  |            | 
| star_counts | str  | Slide's star counts           |            | 
| date        | str  | Date uploaded                 |            | 
| stargazers  | list | List of slide's stargazers.   | y          | 
| id          | str  | Slide UID                     |            | 

### stargazers
| Name        | Type | Description                   | May absent | 
|-------------|------|-------------------------------|------------| 
| login       | str  | User login                    |            | 
| Name        | str  | User display name             |            | 
| stars       | int  | # of slides that user starred |            | 

### UserInfo
| Name        | Type | Description                   | May absent | 
|-------------|------|-------------------------------|------------| 
| Name        | str  | User display name             |            | 
| stars       | str  | # of slides that user starred |            | 
| bio         | str  | User bio                      |            | 
| stars_list  | int  | List of slides starred        | y          | 
