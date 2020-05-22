# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime


class CarbonMarketWatchBotSpider(scrapy.Spider):
    name = 'carbon_market_watch_bot'

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/carbon_market_watch.csv',
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # To track the evolution of scrapping
        self.page_nb = 0
        self.article_nb = 0

    # start_requests method
    def start_requests(self):
        """ Give scrapy the urls to follow
                - function automatically called when using "scrapy crawl my_spider"
                """
        url = 'https://carbonmarketwatch.org/news-press/'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Display a message in the console
        self.logger.warn(f' > PARSING NEW PAGE OF ARTICLES ({self.page_nb})')
        self.page_nb += 1

        articles_url = response.css('article.post > a::attr(href)').getall()

        for article_url in articles_url:
            yield response.follow(url=article_url, callback=self.parse_article)

        next_page = response.css('div.next > a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        self.logger.info(' > PARSING ARTICLE NUMBER ({})'.format(self.article_nb))
        self.article_nb += 1

        yield get_article_info(response)


def get_article_info(response):
    d = {}
    headers = set(response.css('h3.heading > span::text').getall()[:-1])
    paragraph = response.css('p.area-title::text').getall()

    d['author'] = paragraph[0].strip()
    d['area_of_interest'] = get_area_of_interest(response)
    d['categories'] = get_categories(response)
    d['tags'] = get_tags(response) if "Tagged in" in headers else []
    d["title"] = response.css('h1::text').get().strip()
    d["sub_title"] = response.css('h1::text').get().strip()
    try:
        d["abstract"] = response.css('i > span::text').get().strip()
        d['date_published'] = datetime.strptime(paragraph[1].strip(), '%d %b %Y')
    except:
        d["abstract"] = None
        d['date_published'] = None
    d['link'] = response.url

    # print(d)
    return d


def get_area_of_interest(response):
    link = response.css('p.area-title > a::attr(href)').re(r'.*interests=.*')
    if len(link) > 0:
        area = link[0].split('=')[-1]
        return area
    return None


def get_categories(response):
    links = response.css('p.area-title > a::attr(href)').re(r'.*categories=.*')
    if len(links) > 0:
        categories = [link.split('=')[-1] for link in links]
        return categories
    return []


def get_tags(response):
    links = response.css('ul.tags >  li > a::attr(href)').getall()
    if len(links) > 0:
        tags = [link.split('/')[-2] for link in links]
        return tags
    return []
