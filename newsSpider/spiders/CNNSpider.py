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

class ExampleSpider(scrapy.Spider):

    name = "newsSpider"

    start_urls = ["http://apps.webofknowledge.com",
                  ]

    index_url = '''http://apps.webofknowledge.com'''

    search_url = "https://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&qid=2&SID=7ABAN91brcaBl7wjFU6&colName=WOS&page=1&action=changePageSize&pageSize=50"
    cookies = None

    count_page = 0

    mutex = threading.Lock()

    def __init__(self):

        service_args_debug = ['--load-images=false', '--disk-cache=true', '--debug=true', '--webdriver-loglevel=debug']
        service_args = ['--load-images=false', '--disk-cache=true']
        self.driver = webdriver.PhantomJS(
            service_args=service_args)
        #self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        #time.sleep(5)
        # self.driver.set_window_size(1280, 1024)#640, 960)

    def __del__(self):
        self.driver.close()

    def start_requests(self):

        self.driver.get(self.search_url)
        time.sleep(1)
        self.cookies = self.driver.get_cookies()

        return [
            scrapy.Request(self.search_url, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
        ]

    def parse(self, response):

        yield scrapy.Request(self.search_url, callback=self.parse_search, cookies=self.cookies, dont_filter=True)

    def parse_search(self, response):
        """
        search main lists
        :param response:
        :return:
        """
        
        soup = BeautifulSoup(response.body, 'lxml')

        domain = self.index_url

        for record in soup.find_all("div", class_="search-results-content"):
            view_abstract = record.find("span", class_="button-abstract", id=re.compile("ViewAbstract"))
            if view_abstract is None:
                continue
            link = record.find("a", class_="smallV110")
            if link:
                paper_link = domain + link['href']
                yield scrapy.Request(paper_link, callback=self.parse_main_paper, cookies=self.cookies, dont_filter=True)

        if self.count_page < 1000:
            self.count_page += 1
            # request next list
            next_a = soup.find("a", class_="paginationNext")
            if next_a:
                next_link = next_a['href']
                yield scrapy.Request(next_link, callback=self.parse_search, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)

    def parse_cite_search(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        domain = self.index_url

        # request each item
        for record in soup.find_all("div", class_="search-results-content"):
            view_abstract = record.find("span", class_="button-abstract", id=re.compile("ViewAbstract"))
            if view_abstract is None:
                continue
            link = record.find("a", class_="smallV110")
            if link:
                paper_link = domain + link['href']
                yield scrapy.Request(paper_link, callback=self.parse_cite_paper, cookies=self.cookies, dont_filter=True)


    def parse_refer_search(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        domain = self.index_url

        # request each item
        for record in soup.find_all("div", class_="search-results-item"):
            view_abstract = record.find("span", class_="button-abstract", id=re.compile("ViewAbstract"))
            if view_abstract is None:
                continue
            link = record.find("a", class_="smallV110")
            if link:
                paper_link = domain + link['href']
                yield scrapy.Request(paper_link, callback=self.parse_refer_paper, cookies=self.cookies, dont_filter=True)

    def parse_main_paper(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        domain = self.index_url

        item = NewsspiderItem()

        title = soup.find("div", class_="title")

        if title is None:
            print "=======================================no title"
            print(response.url)
            return

        item['title'] = title.value.get_text().strip()

        item['category'] = 'main'

        authors_list = ""

        for author in soup.find_all("a", title="Find more records by this author"):
            new_author = author.next_sibling.string.strip()
            authors_list += author.get_text().strip() + new_author + ";"

        item['authors'] = authors_list

        source_title = soup.find("p", class_="sourceTitle")
        if not source_title:
            return

        item['publisher'] = source_title.value.get_text().strip()

        record_info = soup.find("div", class_="block-record-info-source-values")
        # print "================================================FR_lable"
        volume = record_info.find("span", class_="FR_label", text=re.compile(r"Volume:"))
        if volume and volume.parent and volume.parent.value:
            item['volume'] = volume.parent.value.string.strip()

        issue = record_info.find("span", class_="FR_label", text=re.compile(r"Issue:"))
        if issue and issue.parent and issue.parent.value:
            item['issue'] = issue.parent.value.string.strip()

        year = soup.find("span", class_="FR_label", text=re.compile(r"Published:"))
        if year and year.parent and year.parent.value:
            item['year'] = year.parent.value.string.strip()

        abstract = soup.find("div", class_="title3", text=re.compile(r"Abstract"))
        if abstract and abstract.parent and abstract.parent.p:
            item['abstract'] = abstract.parent.p.get_text().strip()

        keywords_list = ""
        for keyword in soup.find_all("a", title="Find more records by this author keywords"):
            keywords_list += keyword.string.strip() + ";"

        item['keywords'] = keywords_list

        num_cite = soup.find("span", class_="TCcountFR")
        if num_cite:
            item['num_cite'] = int(str(num_cite.string.strip()).replace(",", ""))
        else:
            item['num_cite'] = 0

        sidebar2 = soup.find("div", class_="l-column-sidebar2")
        if sidebar2:
            block_content = sidebar2.find("div", class_="block-text-content")
            if block_content:
                num_refer = soup.find("a", text=re.compile(r" Cited References"))
                if num_refer:
                    item['num_refer'] = int(str(num_refer.string.strip()).split(" ")[0])
                    link = domain + "/" + num_refer['href']
                    yield scrapy.Request(link, callback=self.parse_refer_search, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
                else:
                    item['num_refer'] = 0

                cite_a = block_content.p.a
                if cite_a:
                    link = domain + cite_a['href']
                    yield scrapy.Request(link, callback=self.parse_cite_search, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)

        yield item

    def parse_cite_paper(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        item = NewsspiderItem()

        title = soup.find("div", class_="title")

        if title is None:
            print "=======================================no title"
            print(response.url)
            return

        item['title'] = title.value.get_text().strip()

        item['category'] = 'cite'

        authors_list = ""

        for author in soup.find_all("a", title="Find more records by this author"):
            new_author = author.next_sibling.string.strip()
            authors_list += author.get_text().strip() + new_author + ";"

        item['authors'] = authors_list

        source_title = soup.find("p", class_="sourceTitle")
        if not source_title:
            return

        item['publisher'] = source_title.value.get_text().strip()

        record_info = soup.find("div", class_="block-record-info-source-values")
        # print "================================================FR_lable"
        volume = record_info.find("span", class_="FR_label", text=re.compile(r"Volume:"))
        if volume and volume.parent and volume.parent.value:
            item['volume'] = volume.parent.value.string.strip()

        issue = record_info.find("span", class_="FR_label", text=re.compile(r"Issue:"))
        if issue and issue.parent and issue.parent.value:
            item['issue'] = issue.parent.value.string.strip()

        year = soup.find("span", class_="FR_label", text=re.compile(r"Published:"))
        if year and year.parent and year.parent.value:
            item['year'] = year.parent.value.string.strip()

        abstract = soup.find("div", class_="title3", text=re.compile(r"Abstract"))
        if abstract and abstract.parent and abstract.parent.p:
            item['abstract'] = abstract.parent.p.get_text().strip()

        keywords_list = ""
        for keyword in soup.find_all("a", title="Find more records by this author keywords"):
            keywords_list += keyword.string.strip() + ";"

        item['keywords'] = keywords_list

        num_cite = soup.find("span", class_="TCcountFR")
        if num_cite:
            item['num_cite'] = int(str(num_cite.string.strip()).replace(",", ""))
        else:
            item['num_cite'] = 0

        sidebar2 = soup.find("div", class_="l-column-sidebar2")
        if sidebar2:
            block_content = sidebar2.find("div", class_="block-text-content")
            if block_content:
                num_refer = soup.find("a", text=re.compile(r" Cited References"))
                if num_refer:
                    item['num_refer'] = int(str(num_refer.string.strip()).split(" ")[0])
                else:
                    item['num_refer'] = 0

        yield item


    def parse_refer_paper(self, response):


        soup = BeautifulSoup(response.body, 'lxml')

        item = NewsspiderItem()

        title = soup.find("div", class_="title")

        if title is None:
            print "=======================================no title"
            print(response.url)
            return

        item['title'] = title.value.get_text().strip()

        item['category'] = 'refer'

        authors_list = ""

        for author in soup.find_all("a", title="Find more records by this author"):
            new_author = author.next_sibling.string.strip()
            authors_list += author.get_text().strip() + new_author + ";"

        item['authors'] = authors_list

        source_title = soup.find("p", class_="sourceTitle")
        if not source_title:
            return

        item['publisher'] = source_title.value.get_text().strip()

        record_info = soup.find("div", class_="block-record-info-source-values")
        # print "================================================FR_lable"
        volume = record_info.find("span", class_="FR_label", text=re.compile(r"Volume:"))
        if volume and volume.parent and volume.parent.value:
            item['volume'] = volume.parent.value.string.strip()

        issue = record_info.find("span", class_="FR_label", text=re.compile(r"Issue:"))
        if issue and issue.parent and issue.parent.value:
            item['issue'] = issue.parent.value.string.strip()

        year = soup.find("span", class_="FR_label", text=re.compile(r"Published:"))
        if year and year.parent and year.parent.value:
            item['year'] = year.parent.value.string.strip()

        abstract = soup.find("div", class_="title3", text=re.compile(r"Abstract"))
        if abstract and abstract.parent and abstract.parent.p:
            item['abstract'] = abstract.parent.p.get_text().strip()

        keywords_list = ""
        for keyword in soup.find_all("a", title="Find more records by this author keywords"):
            keywords_list += keyword.string.strip() + ";"

        item['keywords'] = keywords_list

        num_cite = soup.find("span", class_="TCcountFR")
        if num_cite:
            item['num_cite'] = int(str(num_cite.string.strip()).replace(",", ""))
        else:
            item['num_cite'] = 0

        sidebar2 = soup.find("div", class_="l-column-sidebar2")
        if sidebar2:
            block_content = sidebar2.find("div", class_="block-text-content")
            if block_content:
                num_refer = soup.find("a", text=re.compile(r" Cited References"))
                if num_refer:
                    item['num_refer'] = int(str(num_refer.string.strip()).split(" ")[0])
                else:
                    item['num_refer'] = 0

        yield item
