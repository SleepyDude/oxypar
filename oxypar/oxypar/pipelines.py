# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from itertools import cycle
import json
from pathlib import Path
from scrapy import signals
from pydispatch import dispatcher
import scrapy
from scrapy.exceptions import DropItem
import requests
import requests_random_user_agent
import time

ROOT_DIR = Path(__file__).absolute().parent.parent

class CheckPipeline:
    """
    Checking proxy object and calculating ping
    """
    def __init__(self):
        # self.check_url = 'https://httpbin.org/ip'
        self.check_url = 'https://req-checker.herokuapp.com/v1/get_my_ip_data'

    def process_item(self, item, spider):
        ip_port = item['ip'] + ':' + item['port']
        
        protocol = item['protocols'][0]
        proxies = None
        # it's important to set protocol before ip_port
        # seen from experiment, at least for socks4 proxy
        if item['https'] == 'Yes':
            proxies = {"http": protocol + "://" + ip_port, "https": protocol + "://" + ip_port}
        else:
            proxies = {"http": protocol + "://" + ip_port}

        # if item['https'] == 'Yes':
        #     proxies = {"http": ip_port, "https": ip_port}
        # else:
        #     proxies = {"http": ip_port}

        print(proxies)

        try:
            # s = requests.Session()
            # s.proxies.update(proxies)
            start = time.perf_counter_ns()
            # print(s.headers)
            # response = s.get(self.check_url, timeout = 5)
            response = requests.get(self.check_url, proxies=proxies, timeout=5)
            end = time.perf_counter_ns()
            ping = (end - start) * 1e-6 # ms
            item['ping'] = ping
            if response.status_code == 200:
                print(response.json())
                return item
        except Exception as e:
            print("Skipping {}. Connnection error:\n{}\n\n".format(ip_port, e))
        
        raise DropItem('bad proxy')

class JSONDumpPipeline:
    """
    Dump item into json file
    """
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        self.items_count = 0
        spider_protocol = getattr(spider, 'ptype', '')
        if spider_protocol:
            spider_protocol = '_' + spider_protocol
        cc = getattr(spider, 'cc', '')
        if cc:
            cc = '_' + cc

        self.filename = '{}{}{}.json'.format(spider.name, spider_protocol, cc)
        self.file = open(self.filename, 'w', encoding='utf-8')
        self.file.write('[\n')

    def process_item(self, item, spider):
        print('Got {} in JsonDump Pipeline'.format(item))
        if item is not None:
            self.items_count += 1
            line = json.dumps(dict(item), ensure_ascii=False) + ',\n'
            self.file.write(line)
            return item
    
    def spider_closed(self, spider):
        if self.items_count:
            self.file.seek(self.file.tell()-2, 0)
            self.file.truncate()
        self.file.write('\n]')
        self.file.close()

