# -*- coding: utf-8 -*-

import scrapy
import logging


class CarbonpulsebotSpider(scrapy.Spider):
    name = "carbonpulsebot"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/articles.csv',
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # To track the evolution of scrapping
        self.page = 0

    # start_requests method
    def start_requests(self):
        """ Give scrapy the urls to follow
                - function automatically called when using "scrapy crawl my_spider"
                """
        url = 'https://carbon-pulse.com/category/us/'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Display a message in the console
        self.logger.info(f' > PARSING NEW PAGE OF ARTICLES ({self.page})')
        self.page += 1

        for article in response.css('div.post'):
            body = article.css('p::text').getall()
            yield {
                'title': article.css('h2.posttitle > a::text').get(),
                'tags': article.css('a[rel="category tag"]::text').getall(),
                'dates': body[0],
                'text': body[-1]
            }

        next_page = response.css('div#nextpage > a::attr(href)').getall()[-1]
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
