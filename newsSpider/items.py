# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field()
    fbShare = scrapy.Field()
    mainCategory = scrapy.Field()
    subCategory = scrapy.Field()
    pubRating = scrapy.Field()
    pubVotes = scrapy.Field()
    proRating = scrapy.Field()
    proVotes = scrapy.Field()



