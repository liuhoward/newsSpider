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

        data_path = "../data/class_central/"
        user_urls_file = data_path + "user_urls.txt"
        self.user_urls = self._import_user_urls(user_urls_file)

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

    def _import_user_urls(self, src_file):

        user_urls = set()
        with open(src_file, "rb") as fp:

            while True:
                lines = fp.readlines(3000)
                if not lines:
                    break
                for line in lines:
                    user_urls.add(str(line).replace("\n", "").strip())

        return user_urls

    def _export_urls(self, user_file):

        with open(user_file, "wb") as fp:
            header = ['category', 'url']
            writer = csv.DictWriter(fp, fieldnames=header)
            writer.writeheader()
            for url in self.class_dict.keys():
                writer.writerow({header[0]: self.class_dict[url], header[1]: url})

            for url in self.user_dict.keys():
                writer.writerow({header[0]: self.user_dict[url], header[1]: url})

    def start_requests(self):

        domain = self.index_url
        yield scrapy.Request(domain, meta={})

    def parse(self, response):

        #for current_url in self.class_dict.keys():
        #    category = self.class_dict[current_url]
        #    yield scrapy.Request(current_url, callback=self.parse_class,
        #                         meta={'category': category})

        for current_url in self.user_urls:
            yield scrapy.Request(url=current_url, callback=self.parse_user, meta={})

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
        category = 'user' #meta['category']
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
