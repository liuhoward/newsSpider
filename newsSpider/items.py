# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company = scrapy.Field()
    reviewID = scrapy.Field()

    reviewRating = scrapy.Field()
    workRating = scrapy.Field()
    compensationRating = scrapy.Field()
    careerRating = scrapy.Field()
    managementRating = scrapy.Field()
    cultureRating = scrapy.Field()

    reviewTitle = scrapy.Field()
    jobTitle = scrapy.Field()
    jobLocation = scrapy.Field()
    reviewDate = scrapy.Field()

    workingYear = scrapy.Field()
    advice = scrapy.Field()
    pros = scrapy.Field()
    cons = scrapy.Field()

    voteCount = scrapy.Field()






