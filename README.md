# An emergency scraper for Twitter, using Nitter
 
This was developed on Windows and will probably not work on elsewhere without some modification. It scrapes Nitter as a proxy for Twitter, which means it can get nice clean HTML representations of public tweets, along with downloading images. It first scrolls through as far down as it can on a user's profile, and therafter tries to use a Search query to retrieve as many tweets as it can. It absolutely *will not* get everything, but it's what's available. 

It can handle images, but not most videos. 

It produces both json output and will output Nitter html, including rewriting images to point to your local copies. The results are good when it works:
![image](https://user-images.githubusercontent.com/5290850/202627882-3fb85a04-9820-4527-8d3e-d691da0fb958.png)

Once you have a scrape result, *copy it somewhere safe*. This code is entirely willing to overwrite previously-generated stuff or append to an existing scrape.

Caveat: the code quality is awful. I don't really know how to use Scrapy. I wrote this in a couple hours. 

# Usage

First, set the username (`TWITTER_USERNAME = "<USERNAME>"`) in `nitter-scrape/settings.py` to the user you want. This is CASE SENSITIVE but there will be no warnings. 

# Initial crawl
Set the current working directory to the top level of the repository.

To start crawling, run

`scrapy crawl first_spider`

You can set various settings on what to download:

The settings are, by default:
```
	# If True, download images
    get_images = True 
	# If True, always download the full-sized image from gallery.
	# If it's False, it will still download full-sized images that the user posted
    allFullImages = False 
	# If True, only download profile images
    only_pfps = False 
	# Try and download videos (usually fails, doesn't understand streams)
    get_videos = False 
```
## Example
`scrapy crawl first_spider -a allFullImages=True -a get_videos=True`

The tweet data will be in `./<User>/items.json`. The images will be in a folder next to it.

## Generate browseable HTML pages

Run `python process.py <Username>`. It will generate html files in `./<Username>`.

# Scrape replies

Want to get the context for this account's replies? You can additionally index those once you're done with the first index.

## VERY IMPORTANT: DATA LOSS MIGHT OCCUR

Edit FEEDS in `nitter-scrape/settings.py` to read

```FEEDS = {
    TWITTER_USERNAME+"\\items_threads.json": {
	...```
If you don't do this, you will overwrite your existing `items.json`. 

Run `scrapy crawl thread_spider`. You can set the following options like above:

Defaults:
```
    get_images = True
    only_pfps = False
    get_videos = False
```

This will generate `items_threads.json`.

## Generate browseable threads

Run `python thread_process.py <Username>`. It will generate html files in `./<Username>/threads`. You should now be able to click on a user's replies and see the thread in context.


# Other stuff

This thing hammers `https://nitter.it`, and ignores `robots.txt`. It's a bad citizen. Don't use this recklessly. If `nitter.it` is slow, you can replace it with another nitter instance; `nitter.it` is somewhat hardcoded, though, so you'll have to search-and-replace.
