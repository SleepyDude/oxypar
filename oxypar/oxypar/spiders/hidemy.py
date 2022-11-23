import scrapy
from pprint import pprint as pp
from scrapy.http.response.html import HtmlResponse
import json
import time
from pathlib import Path

BASEDIR = Path(__file__).resolve().parent.parent.parent

class HidemeSpider(scrapy.Spider):
    name = 'hideme'
    allowed_domains = ['hidemy.name']
    url = 'https://hidemy.name/ru/proxy-list/'

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
        result = []
        print('parsing ', response.url)
        table = response.css('table')
        rows = table.css('tbody tr') # SelectorList
        for row in rows:
            row_data = {}
            columns = row.css('td') # SelectorList

            row_data['ip'] = columns[0].get()
            row_data['port'] = columns[1].get()
            row_data['country'] = columns[2].css('#country').get()
            row_data['ping'] = columns[3].css('#bar').get()
            row_data['type'] = columns[4].get()
            row_data['isanon'] = columns[5].get()
            row_data['refresh'] = columns[6].get()

            result.append(row_data)

        with open("hideme_ip.json", 'a') as f:
            f.write(json.dumps(result, indent=2, ensure_ascii=False))
        # self.log(f'Saved file {filename}')
