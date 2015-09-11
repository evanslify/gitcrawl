## Facebook CrawlBot
* * *

    Usage:
        Run on it's own.
        Fetch cookies from Redis(which takes input from HTTP API POST for now)
        immediately on run.
    Type: 
        Mobile-website scraping

* * * 

### living
Living info
|-------------------|------|-------------------------------------------------| 
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| hometown          | str  | User hometown                                   | 
| current_city      | str  | User current location                           | 

### works
Recent workplaces.
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| work_facebook_uri | str  | Workplace's Facebook page URI                   | 
| work_name         | str  | Workplace's name                                | 

### name
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| name              | str  | User display name                               | 

### contact_info
Contact infos.
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| website           | str  | URI of user's website.                          | 
| phone             | str  | User's phone number.                            | 

### skills
User skills(as provided by user.)
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| skills            | str  | User's skills.                                  | 

### basic_infos
Basic infomation.
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| languages         | str  | User's languages.                               | 
| bloodtype         | str  | User's bloodtype.                               | 
| birthday          | str  | User's birthday.                                | 
| gender            | str  | Usually either Male or Female.                  | 

### educations
Recent educations, starting from high school.
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| edu_facebook_uri  | str  | School's Facebook page URI                      | 
| edu_description   | str  | School's description—usually 'class of X(year)' | 
| edu_name          | str  | School's name                                   | 

### userinfo
| name              | Type | Description                                     | 
|-------------------|------|-------------------------------------------------| 
| user_id           | str  | User's Facebook UID.                            |