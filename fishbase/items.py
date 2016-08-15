# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
IMAGES_URLS_FIELD = 'image_urls'
IMAGES_RESULT_FIELD = 'images'

class FishItem(scrapy.Item):
	species = scrapy.Field()
	image_urls = scrapy.Field()
	images = scrapy.Field()

# class FishbaseItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
