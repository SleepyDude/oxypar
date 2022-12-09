import scrapy
from scrapy.http.response.html import HtmlResponse
from pathlib import Path
from oxypar.items import ProxyItem
from scrapy.loader import ItemLoader
from pprint import pprint as pp

BASEDIR = Path(__file__).resolve().parent.parent.parent

class ShiftySpider(scrapy.Spider):
    name = 'shifty'
    allowed_domains = ['raw.githubusercontent.com/ShiftyTR/Proxy-List']

    # url = 'https://github.com/ShiftyTR/Proxy-List/blob/master/'

    custom_settings = {
        'FEEDS': {'shifty.json': {'format': 'json', 'encoding': 'utf-8'}}
    }

    def __init__(self, ptypes="", *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        if not ptypes:
            self.ptypes = ['http', 'https', 'socks4', 'socks5']
        else:
            self.ptypes = ptypes.split(',')
        print('ptypes = ', ptypes)
        
        # possible_ptypes = ['http', 'https', 'socks4', 'socks5']
        # if ptype:
        #     if ptype not in possible_ptypes:
        #         raise('Error: supported only', possible_ptypes, 'types of proxy')
        #     self.ptype = ptype
        # else:
        #     self.ptype = 'proxy'

        self.url = 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/{}.txt'

    def start_requests(self):
        for ptype in self.ptypes:
            url = self.url.format(ptype)
            print('parsing {}'.format(url))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        ip_ports = response.text.split('\n')
        protocol = response.url.split('/')[-1][:-4]
        for ip_port in ip_ports:
            ipp = ip_port.split(':')
            if len(ipp) != 2:
                continue
            loader = ItemLoader(ProxyItem())
            loader.add_value('ip', ipp[0])
            loader.add_value('port', ipp[1])
            loader.add_value('protocols', [protocol, ])
            loader.add_value('source', 'shiftyTR')

            yield loader.load_item()
