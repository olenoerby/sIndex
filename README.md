Set up a python bot using NO OAUTH to grab all posts from the Reddit user /u/WeirdPineapple weekly Friday posts of "/r/wowthissubexists Official Fap Friday Thread" posts and grab all comments containing one or more subreddit names or lists of NSFW subreddit name URLs, then save them in a SQL database, count how many times the subreddit has been commented, if the subreddit is still available or banned - and if the subreddit is still active, how many users are active in it, the date of the subreddits creation and the subreddit description.

This will be hosted in a docker SQL database on a website with search and filtering capabilities to see and sort the lists of the NSFW Subreddits.

The bot must be using NO OAUTH, meaning a maximum of 10 API calls/minute, so the bot must only grab the earlier posts of /u/WeirdPineapple once, based on the post ID in its URL, such as "1q8bzx8" from the post https://www.reddit.com/r/wowthissubexists/comments/1q8bzx8.

The  code must therefore be a little slower, but will be running within the limit on an internet faced publicly available Ubuntu Server, hosting the bot, the website and the database. The website must be secured against code injection and will be hosted behind a Cloudflare Tunnel.

The code must be written easy to understand and include code comments. 


The goal involves:
- Running this in a docker container on a Ubuntu Server LTS headless.
- Monitoring a specific Reddit user (u/WeirdPineapple) and archiving a list of all their future and past posts with the name containing "Fap Friday", making sure to only scan the specific posts for comments once, identifying the post on by the postID in the URL. They usually do not receive new subreddits after the day is over. Include in the database the unique ID, post ID, post Title, Post URL and Post timestamp.
- Extracting comments which contain NSFW subreddit names/URLs from each of the posts, normalizing the names to lowercase without slashes, ignore invalid subreddit names containing special characters or being shorter than 3 characters or longer than 21 characters, ignore known non‑subreddit patterns (such as "r/all", "r/random")
- Storing every identified subreddit url in a SQL database, including: unique ID, subreddit ID, Post Timestamp, Comment ID
- Routinely analysing the database table containing the subreddits and making a database table containing: unique ID, subreddit URL, subreddit Name, count of occurrences, subreddit creation date, subreddit first mentioned timestamp, status (banned/private/publicly available), active users at the moment of the scan, subreddit description, marked as over 18 NSFW status - and check routinely if the subreddits are still available, maybe on a schedule once a week, still keeping within the 10 API calls/minute.
- Hosting a Nginx/Apache website in a another Docker container behind a cloudflare tunnel, secured from injection in the database which will be read-only from the webserver with filtering and searching cababilities.
- Running the whole scanner continuously keeping within the 10 API calls/minute limit but also prepare the project to be able to set up OAUTH if this becomes available later.

The weekly pipeline will follow this sequence:
1. Identify the correct Friday post
2. Fetch all comments
3. Extract subreddit names
4. Normalize and deduplicate
5. Fetch subreddit metadata
6. Store everything in SQL
7. Expose a read‑only API for your website



A clean relational schema:

posts
column	type
id	PK
reddit_post_id	text
title	text
created_utc	int
url	text
comments
column	type
id	PK
reddit_comment_id	text
post_id	FK
body	text
created_utc	int
subreddits
column	type
id	PK
name	text unique
created_utc	int
subscribers	int
active_users	int
description	text
is_banned	boolean
last_checked	timestamp
mentions
column	type
id	PK
subreddit_id	FK
comment_id	FK
post_id	FK
timestamp	int

This gives you:
⦁	Frequency counts
⦁	Historical trends
⦁	Ability to detect banned/active changes



Backend API for Website
Expose a read‑only API (FastAPI):

Endpoints:
GET /subreddits
Pagination
Sort by:
mentions
subscribers
active_users
created_utc

GET /subreddits/{name}
Full metadata
Mention history
Status (active/banned)

GET /mentions
Filter by:
date range
subreddit
post

GET /stats/top
Most mentioned subreddits
Fastest‑growing
Most banned




What I need:

⦁	The full database schema with indexes
⦁	The backend API routes in detail
⦁	A caching strategy for subreddit metadata
⦁	A full sequence diagram
⦁	A Dockerized architecture
