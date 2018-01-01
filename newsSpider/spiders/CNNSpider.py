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

class ExampleSpider(scrapy.Spider):

    name = "newsSpider"

    start_urls = [("https://www.class-central.com/subject/cs", "Computer Science"),
                  ("https://www.class-central.com/subject/data-science", "Data Science"),
                  ("https://www.class-central.com/subject/programming-and-software-development", "Programming"),
                  ("https://www.class-central.com/subject/business", "Business"),
                  ("https://www.class-central.com/subject/engineering", "Engineering"),
                  ("https://www.class-central.com/subject/social-sciences", "Social Sciences"),
                  ("https://www.class-central.com/subject/personal-development", "Personal Development"),
                  ("https://www.class-central.com/subject/maths", "Mathematics"),
                  ("https://www.class-central.com/subject/education", "Education & Teaching"),
                  ("https://www.class-central.com/subject/humanities", "Humanities"),
                  ("https://www.class-central.com/subject/art-and-design", "Art & Design"),
                  ("https://www.class-central.com/subject/health", "Health & Medicine"),
                  ("https://www.class-central.com/subject/science", "Science")
                  ]

    index_url = '''https://www.class-central.com'''

    categories = [
        "Computer Science",
        "Data Science",
        "Programming",
        "Business",
        "Engineering",
        "Social Sciences",
        "Personal Development",
        "Mathematics",
        "Education & Teaching",
        "Humanities",
        "Art & Design",
        "Health & Medicine",
        "Science"
    ]

    cookies = None

    count_page = 0

    driver = None
    index = 0

    def __init__(self):

        service_args = ['--load-images=false', '--disk-cache=true']
        self.driver = webdriver.PhantomJS(
            service_args=service_args)
        self.driver.implicitly_wait(10)

    def __del__(self):
        self.driver.close()

    def start_requests(self):

        domain = self.index_url
        yield scrapy.Request(domain, meta={})

    def parse(self, response):

        domain = self.index_url

        for i in range(len(self.start_urls)):
            url = self.start_urls[i][0]
            category = self.start_urls[i][1]

            self.driver.get(url)

            while True:
                try:
                    self.driver.find_element_by_id("show-more-courses").click()
                    time.sleep(1)
                except:
                    break

            self.cookies = self.driver.get_cookies()
            body = self.driver.page_source.encode('utf8')
            soup = BeautifulSoup(body, 'lxml')

            tbody = soup.find("tbody", class_="table-body-subjectstable")
            if tbody is not None:
                for tr in tbody.find_all("tr", itemtype="http://schema.org/Event"):
                    a = tr.find("a", class_="text--charcoal text-2 medium-up-text-1 block course-name")
                    if a is None:
                        continue
                    link = domain + a['href']
                    logging.info("get class " + link)

                    item = NewsspiderItem()
                    item['category'] = category
                    item['url'] = link
                    yield item

                    interested_link = link + "/interested"
                    yield scrapy.Request(interested_link, callback=self.parse_interested_users, meta={})

    def parse_interested_users(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        domain = self.index_url

        for a in soup.find_all("a", class_="flip-card"):
            link = domain + a['href']
            logging.info("get interested user " + link)
            item = NewsspiderItem()
            item['category'] = 'user'
            item['url'] = link
            yield item
            #yield scrapy.Request(link, callback=self.parse_user, meta={'driver': self.driver, 'PhantomJS': True})


