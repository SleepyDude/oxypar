import requests
import json
from pprint import pprint as pp
from pathlib import Path
import time

import urllib.request, socket

socket.setdefaulttimeout(180)

ROOT_DIR = Path(__file__).absolute().parent.parent

def load_proxies(filename):
    if not ROOT_DIR.joinpath(filename).is_file():
        print("Proxy file not found")
        return
    hideme_filename = str(ROOT_DIR.joinpath(filename))
    hideme_ip_list = []
    with open(hideme_filename, 'r') as inp:
        hideme_ip_list = json.load(inp)
    return hideme_ip_list

def check_ip(ip: dict):
    resp = requests.get('https://ipapi.co/8.8.8.8/json/')

def check_ips(ips: list) -> list:
    filter_res = []
    for ip in ips:
        stats = check_ip(ip)

def is_bad_proxy(p_ip, p_type):
    response_time_ms = 999  
    try:        
        proxy_handler = urllib.request.ProxyHandler({p_type: p_ip})        
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        before_time = time.perf_counter_ns()
        sock=urllib.request.urlopen('http://www.google.com')
        # sock=urllib.request.urlopen('http://www.ozon.ru')
        after_time = time.perf_counter_ns()
        response_time_ms = int((after_time - before_time) * 1e-6)

    except urllib.error.HTTPError as e:        
        print('Error code: ', e.code)
        return e.code, response_time_ms
    except Exception as detail:

        print( "ERROR:", detail)
        return 1, response_time_ms
    return 0, response_time_ms



if __name__ == '__main__':
    # get hideme proxies
    pxies_hideme = load_proxies('oxypar/hideme_ip.json')
    http_proxies_hideme = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_hideme if pxy['type'] == 'HTTP']
    https_proxies_hideme = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_hideme if pxy['type'] == 'HTTPS']

    # get free proxy list proxies
    pxies_fpl = load_proxies('oxypar/hideme_ip.json')
    http_proxies_fpl = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_fpl if pxy['type'] == 'HTTP']
    https_proxies_fpl = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_fpl if pxy['type'] == 'HTTPS']
    
    # check hideme proxies
    print('-------hideme proxies--------')
    for item in https_proxies_hideme:
        is_bad, resp_time = is_bad_proxy(item, 'https')
        if is_bad:
            print ("Bad Proxy", item)
        else:
            print (item, "is working", resp_time, 'ms')

    # check fpl proxies
    print('-------fpl proxies--------')
    for item in https_proxies_fpl:
        is_bad, resp_time = is_bad_proxy(item, 'https')
        if is_bad:
            print ("Bad Proxy", item)
        else:
            print (item, "is working", resp_time, 'ms')

    # print(http_proxies)
    # print(len(http_proxies))

    # print(https_proxies)
    # print(len(https_proxies))

    # checked_ips = check_ips(ips)

