import requests
import json
from pprint import pprint as pp
from pathlib import Path
import time
from itertools import cycle

import urllib.request, socket

socket.setdefaulttimeout(180)

ROOT_DIR = Path(__file__).absolute().parent.parent

def load_proxy_json(filename):
    if not ROOT_DIR.joinpath(filename).is_file():
        print("Proxy file not found")
        return
    hideme_filename = str(ROOT_DIR.joinpath(filename))
    hideme_ip_list = []
    with open(hideme_filename, 'r') as inp:
        hideme_ip_list = json.load(inp)
    return hideme_ip_list

def check_and_filter_proxy_json(proxy_list):
    http_proxies = []
    https_proxies = []
    socks4_proxies = []
    socks5_proxies = []

    for item in proxy_list:
        assert type(item) == dict
        assert 'ip' in item
        assert 'port' in item
        assert 'type' in item or 'protocols' in item

        protocols = []
        if 'protocols' in item:
            protocols.extend(item['protocols'])
        if 'type' in item:
            protocols.append(item['type'].lower())

        print('checking proxy for protocols', protocols)
        
        ip_port = item['ip']+':'+item['port']
        is_bad, resp_time = is_bad_proxy(ip_port, item['type'])

        if is_bad:
            print ("Bad Proxy", ip_port)
        else:
            good_proxies.append({item['type']: ip_port})
            print (ip_port, item['type'], "is working", resp_time, 'ms')

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
        # sock = urllib.request.urlopen('https://req-checker.herokuapp.com')
        after_time = time.perf_counter_ns()
        response_time_ms = int((after_time - before_time) * 1e-6)
        # print(type(sock))
        # pp(sock)

    except urllib.error.HTTPError as e:        
        print('Error code: ', e.code)
        return e.code, response_time_ms
    except Exception as detail:

        print( "ERROR:", detail)
        return 1, response_time_ms
    return 0, response_time_ms

def load_proxy_geonode(limit, country_code = "", proxy_type = ""):
    if country_code:
        country_code = "&country=" + country_code
    if proxy_type:
        proxy_type = "&protocols=" + proxy_type
    url = f'https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc{country_code}{proxy_type}'
    print(url)
    resp = requests.get(url)
    return resp.json()

# def check_country(proxy: dict):
def check_country(ip_port: str):
    '''
    proxy in the {'http': '127.0.0.1'} form
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        # 'Referer': 'https://www.nmpa.gov.cn/datasearch/home-index.html?79QlcAyHig6m=1636513393895',
        'Host': 'req-checker.herokuapp.com',
        'Origin': 'https://req-checker.herokuapp.com/',
        # 'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'close'
    }
    url = 'https://req-checker.herokuapp.com/v1/get_my_ip_data'
    def start_requests():
        # r = json.loads(r.text)
        # headers['Set-Cookie'] = coo
        s = requests.get(url=url, stream=True, timeout=(5, 5), verify=False)
        s.encoding = 'utf8'
        print('requests status code', s.status_code)
        return s.json()

    while True:
        proxy = {'http': 'http://' + ip_port}
        print(proxy)
        try:
            sess = requests.Session()
            sess.keep_alive = False  # close connections we don't need
            res = sess.get(url='https://req-checker.herokuapp.com', headers={'User-Agent': 'Chrome'}, proxies=proxy, timeout=10,
                        verify=True)
            res.close()
            print(res.status_code)
            res.encoding = 'utf8'
            cookie = res.headers['Set-Cookie']
            print(cookie)
            if res.status_code == 200:
                print(res.status_code)
                time.sleep(1)
                print('starting requests')
                res = start_requests()
                return res
                break
        except Exception as error:
            time.sleep(10)
            print("Can't connect", error)

def check_country2(proxy_dict):
    print('checking country for', proxy_dict)
    resp = None
    try:
        resp = requests.get('https://req-checker.herokuapp.com/v1/get_my_ip_data', proxies=proxy_dict, verify=False)
        resp = resp.json()
        with open(str(ROOT_DIR.joinpath('api.myip.com.html')), 'w') as f:
            f.write(resp.text)
    except Exception as e:
        print("ERROR", e)
    return resp

if __name__ == '__main__':
    # get proxies from json files
    pxies_hideme = load_proxy_json('oxypar/hideme_ip.json')
    pxies_fpl = load_proxy_json('oxypar/hideme_ip.json')
    # get proxies from geonode api
    pxies_geonode = load_proxy_geonode(10, 'RU', 'https')

    # pp(pxies_geonode)

    # http_proxies_hideme = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_hideme if pxy['type'] == 'HTTP']
    # https_proxies_hideme = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_hideme if pxy['type'] == 'HTTPS']

    # get free proxy list proxies
    
    # http_proxies_fpl = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_fpl if pxy['type'] == 'HTTP']
    # https_proxies_fpl = [pxy['ip'] + ":" + pxy['port'] for pxy in pxies_fpl if pxy['type'] == 'HTTPS']
    
    good_proxies = []
    # check hideme proxies
    # print('-------hideme proxies--------')
    # for item in pxies_hideme:
    #     ip_port = item['ip']+':'+item['port']
    #     # continue
    #     is_bad, resp_time = is_bad_proxy(ip_port, item['type'])
    #     if is_bad:
    #         print ("Bad Proxy", ip_port)
    #     else:
    #         good_proxies.append({item['type']: ip_port})
    #         print (ip_port, item['type'], "is working", resp_time, 'ms')

  
    # check fpl proxies
    # print('-------fpl proxies--------')
    # for item in pxies_fpl:
    #     ip_port = item['ip']+':'+item['port']
    #     good_proxies.append({item['type']: ip_port})
    #     continue
    #     is_bad, resp_time = is_bad_proxy(ip_port, 'https')
    #     if is_bad:
    #         print ("Bad Proxy", ip_port)
    #     else:
    #         good_proxies.append({'https': ip_port})
    #         print (ip_port, "is working", resp_time, 'ms')

    # check geonode proxies
    # print('-------geonode proxies--------')
    for item in pxies_geonode['data']:
        print('Check proxy with', item['protocols'], 'protocols')
        ip_port = item['ip']+':'+item['port']
        is_bad, resp_time = is_bad_proxy(ip_port, item['protocols'][0])
        if is_bad:
            print ("Bad Proxy", ip_port)
        else:
            good_proxies.append({item['protocols'][0]: ip_port})
            print (ip_port, item['protocols'][0], "is working", resp_time, 'ms')

    # countries = []
    # print('-------check country--------')
    # for px in good_proxies:
    #     country_json = check_country(px)
    #     if country_json:
    #         print(country_json['cc'])
    #     else:
    #         print(px, 'timeout exception')
    #     countries.append(country_json)

    # pp(countries)

    country_json = check_country(good_proxies[0]['https'])
    pp(country_json)


    # print(http_proxies)
    # print(len(http_proxies))

    # print(https_proxies)
    # print(len(https_proxies))

    # checked_ips = check_ips(ips)

