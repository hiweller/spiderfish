# import logging
# from scrapy import signals
# from scrapy.exceptions import NotConfigured

# logger = logging.getLogger(__name__)

# crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

# class SpiderOpenCloseLogging(object):
# 	def __init__(self, item_count):
# 		self.item_count = item_count
# 		self.items_scraped = 0

# 	@classmethod
# 	def from_crawler(cls, crawler):
# 		if not crawler.settings.getbool('MYEXT_ENABLED'):
# 			raise NotConfigured

# 		# get the number of items from settings
#         item_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

#         # instantiate the extension object
#         ext = cls(item_count)

# 		crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

# 	def spider_closed(self, spider):
