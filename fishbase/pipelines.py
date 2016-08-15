# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem
# from scrapy import log

class FishbasePipeline(object):
    def process_item(self, item, spider):
        return item

class fishImagesPipeline(ImagesPipeline):
	def file_path(self, request, response=None, info=None):
		image_guide = request.url.split('/')[-1]
		return 'full/%s' % (image_guide)

	def get_media_requests(self, item, info):
		for image in item['image_urls']:
			yield Request(image)
