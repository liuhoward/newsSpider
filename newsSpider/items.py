# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()

    publisher = scrapy.Field()
    year = scrapy.Field()
    volume = scrapy.Field()
    issue = scrapy.Field()

    abstract = scrapy.Field()
    keywords = scrapy.Field()

    # main, cite, refer, other
    category = scrapy.Field()

    # times cited
    num_cite = scrapy.Field()

    # cited reference
    num_refer = scrapy.Field()








