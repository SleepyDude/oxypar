import scrapy
from scrapy.http.response.html import HtmlResponse
from pathlib import Path
from oxypar.items import ProxyItem
from scrapy.loader import ItemLoader

BASEDIR = Path(__file__).resolve().parent.parent.parent

class GeonodeSpider(scrapy.Spider):
    name = 'geonode'
    allowed_domains = ['proxylist.geonode.com']
    url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'

    custom_settings = {
        'FEEDS': {'geonode.json': {'format': 'json', 'encoding': 'utf-8'}}
    }

    def __init__(self, limit=100, cc="", ptype="", *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.ptype = ptype
        self.cc = cc
        if cc:
            cc = "&country=" + cc
        if ptype:
            ptype = "&protocols=" + ptype
        self.url = f'https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc{cc}{ptype}'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        proxies = response.json()['data']
        for proxy in proxies:
            loader = ItemLoader(ProxyItem())
            loader.add_value('ip', proxy['ip'])
            loader.add_value('port', proxy['port'])
            loader.add_value('cc', proxy['country'])
            loader.add_value('protocols', proxy['protocols'])
            loader.add_value('isanon', proxy['anonymityLevel'])
            loader.add_value('google_pass', proxy['google'])
            loader.add_value('https', 'Yes')
            loader.add_value('source', 'geonode')
            
            yield loader.load_item()
            
