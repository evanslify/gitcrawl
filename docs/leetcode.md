## LeetCode CrawlBot

* * *
    Usage:
        scrapy crawl -a target=<username> -a mode=<mode> leetcode

    Args:
        target: leetcode usermode
        mode: (all) user answer question

* * * 

### AnswerInfo, QuestionInfo and comments
Items in AnswerInfo, QuestionInfo and all the comments are Post objects.
They are handled by the same routine.
Some fields may be absent.

| Name            | Type | Description                             | May absent | 
|-----------------|------|-----------------------------------------|------------| 
| AnswerInfo      | list | List of user's answer in discussions.   | y          | 
| QuestionInfo    | list | List of user's question in discussions. | y          | 
| UserInfo        | dict | List of user's infomations.             |            | 

* * *
### Post Object
| Name            | Type | Description                             | May absent | 
|-----------------|------|-----------------------------------------|------------| 
| question        | dict | Content of the original post.           | y          | 
| answers         | list | List of replies in the topic.           | y          | 

| Name            | Type | Description                             | May absent | 
|-----------------|------|-----------------------------------------|------------| 
| votes           | dict | Votes up/down                           | y          | 
| meta            | dict | Post object's metainfo.                 |            | 
| comments        | list | List of comments                        | y          | 
| content         | str  | Raw HTML                                |            | 
| title           | str  | Topic's title                           | y          | 

* * *

### UserInfo
| Name            | Type | Description                             | May absent | 
|-----------------|------|-----------------------------------------|------------| 
| voted_answer    | str  | # of answers which user voted on.       |            | 
| score           | str  | User's score.                           |            | 
| got_upvote      | str  | # of upvotes which user got             |            | 
| comments        | str  | # of comments which user posted         |            | 
| questions       | str  | # of questions posted by user           |            | 
| voted_questions | str  | # of votes on question which user voted |            | 
| got_downvote    | str  | # of downvotes which user got           |            | 
| give_downvote   | str  | # of downvotes which user gived         |            | 
| give_upvote     | str  | # of upvotes which user gived           |            | 
| answers         | str  | # of answers posted by user             |            | 
