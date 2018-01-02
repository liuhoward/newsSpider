#encoding: utf-8
import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from newsSpider.items import NewsspiderItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule,BaseSpider
from scrapy.http import Request,FormRequest
from selenium import webdriver
import time
import random
import json
import datetime
import logging
import urllib
import threading
import logging
import csv

class ExampleSpider(scrapy.Spider):

    name = "newsSpider"

    index_url = '''https://www.class-central.com'''

    cookies = None

    count_page = 0

    driver = None
    index = 0

    def __init__(self):

        service_args = ['--load-images=false', '--disk-cache=true']
        self.driver = webdriver.PhantomJS(
            service_args=service_args)
        self.driver.implicitly_wait(10)

        data_path = "../data/class_central/"
        urls_file = data_path + "class_central_urls_20171231.txt"
        self.class_dict, self.user_dict = self._import_urls(urls_file)

    def __del__(self):
        self.driver.close()

    def _import_urls(self, src_file):

        class_urls = dict()
        user_urls = dict()

        with open(src_file, "rb") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                category = row['category']
                url = row['url']
                if category == 'user':
                    user_urls[url] = category
                else:
                    class_urls[url] = category

        return class_urls, user_urls

    def start_requests(self):

        domain = self.index_url
        yield scrapy.Request(domain, meta={})

    def parse(self, response):

        for current_url in self.class_dict.keys():
            category = self.class_dict[current_url]
            yield scrapy.Request(current_url, callback=self.parse_class,
                                 meta={'driver': self.driver, 'PhantomJS': True, 'category': category})

        for current_url in self.user_dict.keys():
            category = 'user'
            yield scrapy.Request(current_url, callback=self.parse_user,
                                 meta={'driver': self.driver, 'PhantomJS': True, 'category': category})

    def parse_class(self, response):

        soup = BeautifulSoup(response.body, "lxml")
        meta = response.request.meta
        category = meta['category']
        current_url = response.url
        content = soup.find("div", class_="container cc-body-content")
        if content is not None:
            item = NewsspiderItem()
            item['category'] = category
            item['url'] = current_url
            item['page'] = content.decode()
            yield item

        else:
            logging.info("failed to get content: " + current_url)

        all_reviews = soup.find("div", class_="course-all-reviews")
        if all_reviews:

            for review_title in all_reviews.find_all("div", class_="review-title title-with-image"):
                a = review_title.find("a")
                if a is not None:
                    link = self.index_url + a['href']
                    if link not in self.user_dict.keys():
                        logging.info("add new user: " + link)
                        self.user_dict[link] = 'user'

    def parse_user(self, response):

        soup = BeautifulSoup(response.body, "lxml")
        meta = response.request.meta
        category = meta['category']
        current_url = response.url

        content = soup.find("div", class_="container cc-body-content")
        if content is not None:
            item = NewsspiderItem()
            item['category'] = category
            item['url'] = current_url
            item['page'] = content.decode()
            yield item
        else:
            logging.info("failed to get content: " + current_url)
