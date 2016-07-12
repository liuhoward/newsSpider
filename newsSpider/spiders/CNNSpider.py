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
    allowed_domains = ["www.medicalnewstoday.com"]
    start_urls = ["http://www.medicalnewstoday.com/categories",
                  #"http://www.medicalnewstoday.com/articles/38085.php",
                  ]
    rules = (
        Rule(LinkExtractor(allow=r"/categories/.*")),
        Rule(LinkExtractor(allow=r"/[a-z]+/[0-9]+\.php.*"),
        callback="parse_news",follow=False),
    )

    def parse_news(self,response):

        item = NewsspiderItem()
        soup = BeautifulSoup(response.body, 'html.parser')

        item['id'] = response.url.strip().split("/")[-1].split(".")[0].strip()
        item['title'] = soup.title.string.strip()
        item['date'] = soup.find("time")["datetime"]

        fbShare = soup.find("span", class_ = re.compile("count_yes"))
        if fbShare:
            item['fbShare'] = fbShare.get_text().strip()
        else:
            item['fbShare'] = "0"

        articleBody = soup.find("div", itemprop = "articleBody")
        #bodySoup = BeautifulSoup(articleBody)
        text = ""
        for paragraph in articleBody.find_all("p"):
           text += " " + paragraph.get_text().strip()
        item['text'] = text.strip()

        mainCategoryTag = soup.find("span", class_ = "category_main")
        #mainCategorySoup = BeautifulSoup(mainCategoryTag)
        item['mainCategory'] = mainCategoryTag.get_text().strip()

        subCategory = []
        for tmpCat in soup.find_all("span", class_ = "category_sub"):
            subCategory.append(tmpCat.get_text().strip())
        item['subCategory'] = subCategory

        pubRating = soup.find("span", class_ = re.compile("pub_average"))
        if pubRating:
            item['pubRating'] = pubRating.get_text().strip()
        else:
            item['pubRating'] = "0"

        pubVotes = soup.find("span", class_ = re.compile("pub_votes"))
        if pubVotes:
            item['pubVotes'] = pubVotes.get_text().strip().split(" ")[0]
        else:
            item['pubVotes'] = "0"

        proRating = soup.find("span", class_ = re.compile("hcp_average"))
        if proRating:
            item['proRating'] = proRating.get_text().strip()
        else:
            item['proRating'] = "0"

        proVotes = soup.find("span", class_ = re.compile("hcp_votes"))
        if proVotes:
            item['proVotes'] = proVotes.get_text().strip().split(" ")[0]
        else:
            item['proVotes'] = "0"


        yield item

        nextlink=response.xpath('//li[@class="next"]/a/@href').extract()
        if nextlink:
            link=nextlink[0]
            #print "==================================link " + link
            yield Request(link, callback=self.parse_news)