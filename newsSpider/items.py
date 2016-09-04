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
    Headquarters = scrapy.Field()

    Revenue = scrapy.Field()
    Employees = scrapy.Field()
    Industry = scrapy.Field()
    Links = scrapy.Field()






