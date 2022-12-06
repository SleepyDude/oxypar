import scrapy
from scrapy.http.response.html import HtmlResponse
from pathlib import Path
from oxypar.items import ProxyItem
from scrapy.loader import ItemLoader

BASEDIR = Path(__file__).resolve().parent.parent.parent

class HidemeSpider(scrapy.Spider):
    name = 'hideme'
    allowed_domains = ['hidemy.name']
    url = 'https://hidemy.name/ru/proxy-list/'
    # url = 'https://hidemy.name/ru/proxy-list/?type=s#list'
    custom_settings = {
        'FEEDS': {'hideme.json': {'format': 'json', 'encoding': 'utf-8'}}
    }

    def start_requests(self):
        print(BASEDIR)
        # remove old hideme_ip.json file if exist
        if BASEDIR.joinpath('hideme_ip.json').is_file():
            Path.unlink(BASEDIR.joinpath('hideme_ip.json'))
        # load 5 pages disallow by robots.txt
        # turn off it for now
        # for i in range(5):
        #     url = self.url + "?start={}".format(64*i)
        #     yield scrapy.Request(url=url, callback=self.parse)
        #     time.sleep(0.5)
        yield scrapy.Request(url=self.url, callback=self.parse)


    def parse(self, response: HtmlResponse):
        print('parsing ', response.url)
        table = response.css('table')
        rows = table.css('tbody tr') # SelectorList
        for row in rows:
            loader = ItemLoader(ProxyItem(), selector=row)
            loader.add_css('ip', 'td:nth-child(1)::text')
            loader.add_css('port', 'td:nth-child(2)::text')
            # loader.add_css('cc', 'td:nth-child(3)::text')
            loader.add_css('country', 'td:nth-child(3) span.country::text')
            protocols = row.css('td:nth-child(5)::text').get()
            protocols = protocols.lower()
            if 'https' in protocols:
                loader.add_value('https', 'yes')
            else:
                loader.add_value('https', 'no')
            loader.add_css('protocols', 'td:nth-child(5)::text')
            loader.add_css('isanon', 'td:nth-child(6)::text')
            loader.add_value('source', response.url)
            
            yield loader.load_item()

