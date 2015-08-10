## Bitbucket API Crawler
* * *
    Usage:

    target: <stackoverflow user display name>
    size: 30 <int, maximum # of questions/answers to fetch>
    sort: 'activity' <the order to sort discussion topics>
        activity – last_activity_date
        creation – creation_date
        votes – score

## [JSON output documentation](src/master/docs/output/bitbucket.json)

* * *

|Name | Description
|------------------------------------------
|[RepoInfo](#RepoInfo) | All of this user's repository and it's info
|[UserInfo](#UserInfo) | This user's infomation

### [RepoInfo](https://confluence.atlassian.com/display/BITBUCKET/repositories+Endpoint)
|Name | Type | Description
|------------------------------------------
|repo_id | str | Repository UUID
|repo_full_name | str | {owner}/{repository name}
|repo_is_fork | bool | Indicating a repository is a fork.
|repo_has_wiki | bool | Indicating if the repository has a wiki.
|repo_description | str | Description.
|repo_clone_url | str | SSH URI for cloning master.
|repo_has_issues | bool | Indicating a repository has an issue tracker.
|repo_language | str | The main (programming) language of this repository.
|repo_created_on | str | ISO-8601 timestamp of this repository's creation date.
|repo_updated_on | str | ISO-8601 timestamp of the last update to this repository.
|[repo_forks](#RepoInfo/repo_forks) | list | List of this repository's forks.
|repo_name | str | Repository's name.

### RepoInfo/repo_forks
|Name | Type | Description
--------------------------------------------
|repo_fork_name | str | Name of the child repository.
|repo_fork_description | str | Description of the child repository.
|repo_fork_created_on | str | Time forked on.
|repo_fork_updated_on | str | Time updated.
|repo_fork_id | str | Repository UUID
|repo_fork_full_name | str | {owner}/{repository name}
|repo_fork_has_issues | str | Indicating if the repository has a wiki.

### UserInfo
|Name | Type | Description
--------------------------------------------
|user_id | str | User UUID.
|user_display_name | str | User display name.
|[user_followers](#UserInfo/user_followers) | list | List of this user's followers.
|user_login | str | Username.
|user_following | list | List of following users. (Clone of user_followers)
|user_location | str | User location.
|user_website | str | User website URI.
|user_created_on | str | ISO-8601 timestamp of user account creation.

### UserInfo/user_followers
|Name | Type | Description
--------------------------------------------
|user_following_website | str | Follower's website URI.
|user_following_display_name | str | Follower's display name.
|user_following_created_on | str | ISO-8601 timestamp of follower's account creation.
|user_following_location | str | Follower's location.
|user_following_login | str | Follower's username.
|user_following_id | str | Follower's UUID.