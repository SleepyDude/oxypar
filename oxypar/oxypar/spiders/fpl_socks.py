import scrapy
from scrapy.http.response.html import HtmlResponse
from pathlib import Path
from oxypar.items import ProxyItem
from scrapy.loader import ItemLoader

BASEDIR = Path(__file__).resolve().parent.parent.parent

class FPLSocksSpider(scrapy.Spider):
    name = 'fpl_socks'
    allowed_domains = ['socks-proxy.net']
    url = 'https://www.socks-proxy.net/'
    custom_settings = {
        'FEEDS': {'fpl_socks.json': {'format': 'json', 'encoding': 'utf-8'}}
    }

    def start_requests(self):
        # print(BASEDIR)
        # if BASEDIR.joinpath('fpl_ip.json').is_file():
        #     Path.unlink(BASEDIR.joinpath('fpl_ip.json'))

        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        table = response.css('div.fpl-list table')
        rows = table.css('tbody tr') # SelectorList
        for row in rows:
            loader = ItemLoader(ProxyItem(), selector=row)
            loader.add_css('ip', 'td:nth-child(1)::text')
            loader.add_css('port', 'td:nth-child(2)::text')
            loader.add_css('cc', 'td:nth-child(3)::text')
            loader.add_css('country', 'td:nth-child(4)::text')
            loader.add_css('protocols', 'td:nth-child(5)::text')
            loader.add_css('isanon', 'td:nth-child(6)::text')
            loader.add_css('https', 'td:nth-child(7)::text')
            loader.add_value('source', response.url)
            
            yield loader.load_item()
            
