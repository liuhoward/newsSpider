#encoding: utf-8
import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from newsSpider.items import NewsspiderItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class ExampleSpider(CrawlSpider):
    name = "newsSpider"
    allowed_domains = ["www.cnn.com"]
    start_urls = ["http://www.cnn.com/health",
                  "http://www.cnn.com/entertainment",
                  "http://www.cnn.com/travel",
                  ]
    rules=(
        Rule(LinkExtractor(allow=r"/2016/02/\d\d/health/*"),
        callback="parse_news",follow=True),
        Rule(LinkExtractor(allow=r"/2016/02/\d\d/entertainment/*"),
        callback="parse_news",follow=True),
        Rule(LinkExtractor(allow=r"/2016/02/\d\d/travel/*"),
        callback="parse_news",follow=True),
    )

    def parse_news(self,response):

        item = NewsspiderItem()
        self.get_title(response,item)
        self.get_category(response,item)
        self.get_url(response,item)
        self.get_text(response,item)
        return item

    def get_title(self,response,item):
        title=response.xpath("/html/head/title/text()").extract()
        if title:
            # print 'title:'+title[0][:-5].encode('utf-8')
            item['newsTitle']=title[0].split(" - ")[0].replace("\n", " ").strip().encode('utf-8')

    def get_category(self,response,item):
        category = response.url.strip().split('/')[-3]
        if category:
            item['newsCategory']=category

    def  get_text(self,response,item):
        text = ""
        soup = BeautifulSoup(response.body, 'html.parser')
        for paragraph in soup.find_all("p", class_="zn-body__paragraph"):
            text += " " + paragraph.get_text().strip()
            #print paragraph.get_text()

        item['newsContext'] = text.encode('utf-8')

    def get_url(self,response,item):
        news_url=response.url
        if news_url:
            #print news_url
            item['newsURL']=news_url