# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    newsTitle = scrapy.Field()
    newsURL = scrapy.Field()
    #newsDate = scrapy.Field()
    newsContext = scrapy.Field()
    newsCategory = scrapy.Field()


