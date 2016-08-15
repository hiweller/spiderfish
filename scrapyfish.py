from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from fishbase.spiders.spider_fish import FishSpider
from scrapy.utils.project import get_project_settings

# from scrapy.settings import Settings
# from fishbase import settings
# from scrapy.xlib.pydispatch import dispatcher


# def stop_reactor():
#     reactor.stop()

# dispatcher.connect(stop_reactor, signal=signals.spider_closed)

spider = FishSpider(family='Banjosidae')
settings = get_project_settings()
crawler = Crawler(FishSpider, settings)
# crawler = Crawler(settings)
crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start()
log.msg('Running reactor...')
reactor.run()  # the script will block here until the spider is closed
log.msg('Reactor stopped.')