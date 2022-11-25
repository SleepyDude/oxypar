import scrapy
from pprint import pprint as pp
from scrapy.http.response.html import HtmlResponse
import json
import time
from pathlib import Path

BASEDIR = Path(__file__).resolve().parent.parent.parent

class FPLSpider(scrapy.Spider):
    name = 'fpl'
    allowed_domains = ['free-proxy-list.net']
    url = 'https://free-proxy-list.net/'

    def start_requests(self):
        print(BASEDIR)
        if BASEDIR.joinpath('fpl_ip.json').is_file():
            Path.unlink(BASEDIR.joinpath('fpl_ip.json'))

        yield scrapy.Request(url=self.url, callback=self.parse)


    def parse(self, response: HtmlResponse):
        result = []
        print('parsing ', response.url)
        # with open('fpl.html', 'w') as f:
        #     f.write(response.text)
        table = response.css('div.fpl-list table')
        rows = table.css('tbody tr') # SelectorList
        for row in rows:
            pp(row.get())
            row_data = {}
            columns = row.css('td') # SelectorList

            row_data['ip'] = columns[0].css('::text').get()
            row_data['port'] = columns[1].css('::text').get()
            row_data['country-code'] = columns[2].css('::text').get()
            row_data['country'] = columns[3].css('::text').get()
            row_data['isanon'] = columns[4].css('::text').get()
            row_data['isgoogle'] = columns[5].css('::text').get()
            https = columns[6].css('::text').get()
            if https == 'yes':
                row_data['type'] = 'HTTPS'
            else:
                row_data['type'] = 'HTTP'
            row_data['refresh'] = columns[7].css('::text').get()
            result.append(row_data)

        with open("fpl_ip.json", 'a') as f:
            f.write(json.dumps(result, indent=2, ensure_ascii=False))
