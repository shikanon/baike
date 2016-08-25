# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class baikeItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    subname = scrapy.Field()
    info = scrapy.Field()
    concept = scrapy.Field()
    abstract = scrapy.Field()
    content = scrapy.Field()
    relation = scrapy.Field()
    recommend = scrapy.Field()
    weak_relation = scrapy.Field()
    tag = scrapy.Field()
    reference = scrapy.Field()
    
