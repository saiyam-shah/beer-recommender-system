import scrapy
from scraper.items import ScraperItem
from scrapy.selector import Selector
import requests
import re
import urllib.request
from urllib.parse import urlparse
from w3lib.html import  remove_tags
import unicodedata
import datetime
from urllib.parse import urljoin
from scraper import settings
import logging
from w3lib.http import basic_auth_header
from scrapy import signals
from pydispatch import dispatcher
from scrapy.http import FormRequest
from lxml.html import fromstring
from bs4 import BeautifulSoup


class scraper(scrapy.Spider):
    name="scraper"
    allowed_domains = ["beeradvocate.com"]
    
    PROJECT_ROOT=settings.PROJECT_ROOT

    def start_requests(self):
        url_list=['https://www.beeradvocate.com/beer/popular/','https://www.beeradvocate.com/beer/worst/',\
            'https://www.beeradvocate.com/beer/top-rated/','https://www.beeradvocate.com/beer/fame/',\
            'https://www.beeradvocate.com/beer/top-styles/','https://www.beeradvocate.com/beer/trending/']
        for i in url_list:
            yield scrapy.Request(i, callback=self.parse)

    def parse(self, response):
        hxs = Selector(response)
        urls= hxs.xpath(r'//*[@id="ba-content"]//td[2]/a/@href').extract()
        for quote in urls:
            print(quote)
            yield scrapy.Request(urljoin('https://www.beeradvocate.com',quote), callback=self.reviews)
    
    def reviews(self, response):
        hxs= Selector(response)
        name= hxs.xpath('//h1//text()').extract()[0]
        print(name)
        for i in hxs.xpath('//div[@id="rating_fullview_content_2"]'):
            body = BeautifulSoup(' '.join(i.xpath('./div/text()').extract()),'html.parser')
            body = body.get_text().strip()
            # print(body)
            if i.xpath('./span[@class="BAscore_norm"]'):
                rating = i.xpath('./span[@class="BAscore_norm"]/text()').extract()
            else:
                # continue
                rating = i.xpath("./span[@class='muted']/b/text()").extract()
            item= ScraperItem()
            item["item"]=name
            item["body"]= body
            item["rating"]= rating
            yield item
            