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
    start_urls = ["http://www.indeed.com/cmp/Abra-Auto-Body-&-Glass/reviews",

                  ]
    rules = (
        #((\?fcountry=US)(&start=[0-9]*))?
        Rule(LinkExtractor(allow=r"/cmp/Abra-Auto-Body-&-Glass/reviews$"),
        callback="parse_news",follow=False),
    )

    def parse_news(self,response):

        print "======================================================"
        print(response.url)

        soup = BeautifulSoup(response.body, 'lxml')

        content = soup.find("div", id = "cmp-content")

        companyName = soup.find("h2", itemprop="name")
        if companyName and companyName.string:
            company = companyName.string
        else:
            company = response.url.strip().split("/")[4].strip().replace('-', ' ')

        firstPage = False
        if "start=" in response.url.strip():
            firstPage = False
        else:
            firstPage = True

        #if firstPage:
        #    headContainer = content.find("div", id = "cmp-reviews-header-container")
        #    headReviewContainer = content.find("div", id="cmp-review-container")
        #    parse_review(headReviewContainer)

        index = 1
        for container in content.find_all("div", class_ = "cmp-review-container"):

            if (not firstPage) and (index == 1):
                index += 1
                continue
            else:
                item = NewsspiderItem()
                ret = self.get_review(container, company, item)
                index += 1
                yield item



        domain = "http://www.indeed.com"
        nextlink=soup.find("a", attrs={"data-tn-element": "next-page"})
        if nextlink:
            link=domain + nextlink['href']
            print "==================================link " + link
            yield scrapy.Request(link, callback=self.parse_news, dont_filter=True)



    def get_review(self, container, company, item):

        item['company'] = company

        reviewID = container.find("div", attrs={"data-tn-entitytype": "reviewId"})
        if reviewID:
            item['reviewID'] = reviewID['data-tn-entityid']

        reviewRating = container.find("meta", itemprop="ratingValue")
        if reviewRating:
            item['reviewRating'] = float(reviewRating['content'])

        tbody = container.find("table", class_="cmp-ratings-expanded")

        aspects = []
        for innerRating in tbody.find_all("span", class_="cmp-rating-inner rating"):
            tmp = innerRating['style']

            val = tmp[tmp.find(":") + 1:tmp.find("px")]
            aspects.append(float(val) / 17.2)

        if len(aspects) != 5:
            print "================================number of aspects is wrong"

        item['workRating'] = aspects[0]
        item['compensationRating'] = aspects[1]
        item['securityRating'] = aspects[2]
        item['managementRating'] = aspects[3]
        item['cultureRating'] = aspects[4]

        titleTmp = container.find("div", class_ = "cmp-review-title")
        reviewTitle = titleTmp.find("span", itemprop = "name")
        item['reviewTitle'] = reviewTitle.get_text().strip()

        jobTitle = container.find("span", class_ = "cmp-reviewer-job-title")
        item['jobTitle'] = jobTitle.get_text().strip()

        jobLocation = container.find("span", class_ = "cmp-reviewer-job-location")
        item['jobLocation'] = jobLocation.get_text().replace("-", "").strip()

        reviewDate = container.find("span", class_ = "cmp-review-date-created")
        item['reviewDate'] = reviewDate.get_text().strip()

        text = container.find("span", class_ = "cmp-review-text")
        item['text'] = text.get_text().strip()

        pros = container.find("div", class_ = "cmp-review-pro-text")
        if pros:
            item['pros'] = pros.get_text().strip()
        else:
            item['pros'] = ""

        cons = container.find("div", class_ = "cmp-review-con-text")
        if cons:
            item['cons'] = cons.get_text().strip()
        else:
            item['cons'] = ""

        reviewVote = container.find("span", class_="cmp-review-vote")
        for vote in reviewVote.find_all("span", class_="cmp-vote-count"):
            if vote['name'] == "upVoteCount":
                if vote.string:
                    item['upVoteCount'] = float(vote.string.strip())
                else:
                    item['upVoteCount'] = 0
            elif vote['name'] == "downVoteCount":
                if vote.string:
                    item['downVoteCount'] = float(vote.string.strip())
                else:
                    item['downVoteCount'] = 0

