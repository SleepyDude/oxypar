from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from pprint import pprint as pp
from pathlib import Path

import queue
import json
import requests
import threading

#import spiders
from oxypar.spiders import (
    GeonodeSpider,
    HidemeSpider,
    FPLHttpSpider,
    FPLSocksSpider,
    ShiftySpider
)

def collect_proxies(geonode_cc="", geonode_limit=100, geonode_protocols=""):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    # configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    # shiftyTR
    runner.crawl(ShiftySpider)
    # geonode   
    runner.crawl(GeonodeSpider,  limit=geonode_limit, cc=geonode_cc, ptype=geonode_protocols)
    # hideme
    runner.crawl(HidemeSpider)
    # fpl socks
    runner.crawl(FPLSocksSpider)
    # # fpl http
    runner.crawl(FPLHttpSpider)
    
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

def get_json_filenames():
    return Path(__file__).absolute().parent.glob('*.json')

def remove_old_data():
    json_files = get_json_filenames()
    for file in json_files:
        file.unlink()

def read_proxies() -> list:
    result = []
    json_files = get_json_filenames()
    for filename in json_files:
        with open(str(filename), 'r') as f:
            data = json.load(f)
            result.extend(data)
    return result

def check_proxies(qin: queue.Queue, qout: queue.Queue):
    while not qin.empty():
        print('checking proxy in {} thread, {} tasks in `qin`'.format(threading.get_ident(), qin.qsize()))
        proxy = qin.get() # get a task
        ip_port = proxy['protocols'][0] + '://' + proxy['ip'] + ':' + proxy['port']
        try:
            res = requests.get('http://ipinfo.io/json',
                proxies={'http': ip_port, 'https': ip_port},
                timeout=3)
        except:
            continue
        finally:
            qin.task_done() # mark the task as completed
        if res.status_code == 200:
            print(ip_port)
            res_cc = res.json()['country']
            if 'cc' in proxy:
                proxy_cc = proxy['cc']
                if proxy_cc.lower() != res_cc.lower():
                    print('WARNING: Countries for proxy {} are not the same:\n\
                        proxy - {}, response - {}'.format(ip_port, proxy_cc, res_cc))
            else:
                # print('res_cc', res_cc)
                proxy['cc'] = res_cc

            qout.put(proxy)

def check_countries(qin: queue.Queue, qout: queue.Queue):
    '''
    If proxy object haven't cc field then we will check it's country
    '''
    


if __name__ == '__main__':
    remove_old_data()
    collect_proxies(geonode_cc='RU', geonode_limit=500) # creating json files with data
    proxies = read_proxies() # read all proxies from jsons
    qin = queue.Queue() # input queue with all collected proxies
    for p in proxies:
        qin.put(p)
    qout = queue.Queue() # output queue with working proxies
    # launch 10 threads
    for _ in range(10):
        threading.Thread(target=check_proxies, args=(qin, qout)).start()
    qin.join() # wait in main thread untill all tasks done
    results = list()
    while not qout.empty():
        proxy = qout.get()
        pp(proxy)
        results.append(proxy)
   
    with open('working_proxies.json', 'w') as f:
        f.write(json.dumps(results, indent=2))
