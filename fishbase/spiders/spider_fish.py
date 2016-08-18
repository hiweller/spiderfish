import scrapy
from twisted.internet import reactor
import urlparse
import re
from fishbase.items import FishItem
import argparse
from pydispatch import dispatcher
from scrapy import cmdline
from scrapy import signals

def stop_reactor():
    reactor.stop()

class FishSpider(scrapy.Spider):
    name = "fish"

    def __init__(self, family=None, *args, **kwargs):
        super(FishSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(stop_reactor, signal=signals.spider_closed)
        self.allowed_domains = ["fishbase.tw"]
        self.start_urls = ["http://www.fishbase.tw/Nomenclature/FamilySearchList.php?Family="+family]

    def parse(self, response):
        # picks up all the links to species pages for this family
        for href in response.xpath("//td/a/@href").extract():
            species_url = response.urljoin(href)

            # changes out PHP query with permalink to species page
            parl = urlparse.urlparse(species_url)
            parl2 = parl.scheme + "://" + parl.netloc + re.sub("SpeciesSummary.php", "", parl.path) + parl.query[3:]
            
            yield scrapy.Request(parl2, self.parse_species)

    def parse_species(self, response):
        # get link to pictures page
        pics = response.css('span.slabel8').xpath("a[contains(., 'Pictures')]")
        pics_url = response.urljoin(pics.xpath("@href").extract_first())
        yield scrapy.Request(pics_url, self.parse_pics)

    def parse_pics(self, response):
        # thumbs = response.xpath("//span/img/@src[contains(., 'species')]").extract()
        # species = response.xpath("//td/font/i/a/text()").extract_first()
        picpage = response.xpath("//td/a/@href[contains(., 'PicturesSummary')]").extract()

        for link in picpage:
            link_url = response.urljoin(link)
            yield scrapy.Request(link_url, self.parse_picture)

    def parse_picture(self, response):
        table = response.xpath("//form//tr/td/text()").extract()
        table = table[9:22]

        thumb = response.xpath("//img/@src[contains(., 'species')]").extract_first()
        thumb = response.urljoin(thumb)

        species = response.xpath("//tr/td/center/i/a/text()").extract_first()

        yield FishItem(species=species, image=[thumb], table=table)

    def spider_closed(self, spider):
        if spider is not self:
            return


