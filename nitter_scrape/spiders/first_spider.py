import scrapy
import dateutil
from dateutil.parser import parse as date_parse
from datetime import datetime, timedelta

def get_untildate(last_date):
    date_parsed = date_parse(last_date.replace("·",""))
    return (date_parsed + timedelta(days=1)).strftime("%Y-%m-%d")


class FirstSpiderSpider(scrapy.Spider):
    name = 'first_spider'
    allowed_domains = ['nitter.it']
    # start_urls = ['https://nitter.it/roywiggins?scroll=true']
    last_date = None
    get_images = True
    only_pfps = False
    get_videos = False
    allFullImages = False

    def start_requests(self):
        return [scrapy.Request(f"https://nitter.it/{self.settings.get('TWITTER_USERNAME')}/with_replies")]
        #if getattr(self,"until", None):
        #    start_date = date_parse(self.until)
        #else:
        #    start_date = datetime.now()
        #date = (start_date + timedelta(days=1)).strftime("%Y-%m-%d")
        #return [scrapy.Request(f"https://nitter.it/search?f=tweets&q=from%3A{self.settings.get("TWITTER_USERNAME")}&since=&until={date}&near=")]
        
    def parse(self, response):
        global last_date
        for item in response.css('div .timeline-item'):
            result = {
                "html": item.get(),
                "url": response.request.url,
                "link": item.css("a.tweet-link::attr(href)").get(),
                "date": item.css(".tweet-date a::attr(title)").get(),
                "is_retweet": item.css('.retweet-header').getall() != [],
                "is_quote": item.css('.quote').getall() != [],
                "is_thread": item.css('.thread').getall() != [],
                "is_reply": item.css('.replying-to').getall() != [],
                "text": item.css('.tweet-content').xpath("string(.)").extract(),
                "username": item.css(".username::text").get(),
                "attachments": item.css(".attachments .attachment a::attr(href)").getall(),
            }
            if result["date"]:
                result["date"] = result["date"].replace("·","")
            
            result["is_my_tweet"] = (result["username"] == "@"+self.settings.get("TWITTER_USERNAME") and not result["is_retweet"])
            result["is_my_quote"] = result["is_my_tweet"] and result["is_quote"]
            # Only get full-sized images from my own tweets.

            if self.get_videos:
                result["file_urls"] = list(map(response.urljoin, item.css('source::attr(src)').getall()))
                result["file_urls"] += list(map(response.urljoin, item.css('video::attr(data-url)').getall()))
            if self.get_images:
                if self.only_pfps:
                    result["image_urls"] = list(map(response.urljoin, item.css("img.avatar::attr(src)").getall()))
                else:
                    result["image_urls"] = list(map(response.urljoin, item.css("img::attr(src)").getall()))
                    result["image_urls"] += list(map(response.urljoin, item.css("video::attr(poster)").getall()))
                    if result["is_my_tweet"] or self.allFullImages:
                        result["image_urls"] += list(map(response.urljoin, item.css("a.still-image::attr(href)").getall()))
            # file.write(result["html"])
            if result["date"] and not result["is_retweet"]:
                last_date = result["date"]
            yield result

        next_page = response.css('div.show-more > a').xpath("//*[contains(., 'Load more')]/@href").extract()
        
        if len(next_page):
            next_page = next_page[0]
        else:
            date_parsed = date_parse(last_date.replace("·",""))
            date_plus1 = (date_parsed + timedelta(days=1)).strftime("%Y-%m-%d")
            next_page = f"/search?f=tweets&q=from%3A{self.settings.get('TWITTER_USERNAME')}&since=&until={date_plus1}&near=&scroll=true"
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)