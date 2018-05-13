# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JingdongItem(scrapy.Item):
    pid = scrapy.Field()
    image_link = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    comment_num = scrapy.Field()
    shop_name = scrapy.Field()
    shop_link = scrapy.Field()
    second_link = scrapy.Field()
    # time = scrapy.Field()
