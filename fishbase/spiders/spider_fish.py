import scrapy
from twisted.internet import reactor
import urlparse
import re
from fishbase.items import FishItem
import argparse
# from scrapy.signalmanager import SignalManager
from pydispatch import dispatcher
from scrapy import cmdline
from scrapy import signals

# ap = argparse.ArgumentParser()
# ap.add_argument("-f", "--family", required = True, help = "Fish family you want photos from")
# arge = vars(ap.parse_args())

def stop_reactor():
    reactor.stop()

class FishSpider(scrapy.Spider):
    name = "fish"

    def parse(self, response):

        # picks up all the links to species pages for this family
        for href in response.xpath("//td/a/@href").extract():
            species_url = response.urljoin(href)

            # changes out PHP query with permalink to species page
            parl = urlparse.urlparse(species_url)
            parl2 = parl.scheme + "://" + parl.netloc + re.sub("SpeciesSummary.php", "", parl.path) + parl.query[3:]
            
            yield scrapy.Request(parl2, self.parse_species)

    def parse_species(self, response):
        # actually i think this works now?
        pics = response.css('span.slabel8').xpath("a[contains(., 'Pictures')]")
        pics_url = response.urljoin(pics.xpath("@href").extract_first())
        yield scrapy.Request(pics_url, self.parse_pics)

    def parse_pics(self, response):
        thumbs = response.xpath("//span/img/@src[contains(., 'species')]").extract()
        species = response.xpath("//td/font/i/a/text()").extract_first()

        for href in thumbs:
            url = response.urljoin(href)
            yield FishItem(species=species, image_urls=[url])
    
    def __init__(self, family=None, *args, **kwargs):
        super(FishSpider, self).__init__(*args, **kwargs)

        # dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(stop_reactor, signal=signals.spider_closed)
        self.allowed_domains = ["fishbase.tw"]
        self.start_urls = ["http://www.fishbase.tw/Nomenclature/FamilySearchList.php?Family="+family]

    def spider_closed(self, spider):
        if spider is not self:
            return
        print "test"
        # cmdline.execute('echo -e "\xf0\x9f\x8e\xa3 Casting a line... \xf0\x9f\x8e\xa3"'.split())

    # def closed_handler(self, spider):
    #     execute('echo -e "\xf0\x9f\x8e\xa3 Casting a line... \xf0\x9f\x8e\xa3"'.split())


