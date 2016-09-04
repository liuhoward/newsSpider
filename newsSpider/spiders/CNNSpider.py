#encoding: utf-8
import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from newsSpider.items import NewsspiderItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request

class ExampleSpider(CrawlSpider):
    name = "newsSpider"
    allowed_domains = ["www.indeed.com"]
    start_urls = ["http://www.indeed.com/Best-Places-to-Work",

                  ]
    rules = (
        #((\?fcountry=US)(&start=[0-9]*))?   [A-Za-z0-9-,'&\.,]+
        Rule(LinkExtractor(allow=r"/Best-Places-to-Work$"),
             callback="parse_company", follow=False),
        Rule(LinkExtractor(allow=r"/cmp/[A-Za-z0-9-,'&\.,]/reviews$"),
        callback="parse_news",follow=False),
    )

    def parse_company(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        domain = "http://www.indeed.com"

        for comLink in soup.find_all("a", attrs={"data-tn-element": "title-link"}):
            titleLink = domain + comLink['href']
            yield scrapy.Request(titleLink, callback=self.parse_news)



        nextlink = soup.find("span", attrs={"data-tn-element": "next-page"})
        if nextlink:
            link = domain + nextlink.a['href']
            #print "==================================link " + link
            yield scrapy.Request(link, callback=self.parse_company, dont_filter=True)



    def parse_news(self,response):

        soup = BeautifulSoup(response.body, 'lxml')

        companyName = soup.find("h2", itemprop="name")
        if companyName and companyName.string:
            company = companyName.string

        item = NewsspiderItem()
        item['company'] = company

        sidebar = soup.find("dl", id = "cmp-company-details-sidebar")
        if sidebar:
            #dtlist = []
            #ddlist = []
            for dt in sidebar.find_all("dt"):
                item[dt.string] = dt.next_sibling.string

        return item
