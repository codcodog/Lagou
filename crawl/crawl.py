import time
import json
import random
import queue
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .crawl_db import Crawldb


class Crawl:
    def __init__(self, proxy):
        self.proxies_queue = proxy
        self.city  = '深圳'
        self.proxy = None
        self.db    = Crawldb()

        # 行政区: 商业区
        self.district = dict()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
        }
        self.browesers = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) ",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ",
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
        ]

    def change_proxy(self):
        """ 修改代理
        """
        if not self.proxies_queue.empty():
            proxy = self.proxies_queue.get()
            protocol = proxy.split(':')[0]

            self.proxy = {protocol: proxy}
        else:
            print('代理用完了.')

    def get_administrative(self):
        """ 获取行政区信息
        """
        url = "https://www.lagou.com/jobs/list_php?city={city}&cl=false&fromSearch=true&labelWords=&suginput=".format(city=self.city)

        html = requests.get(url, headers=self.headers).content.decode('utf-8')
        soup = BeautifulSoup(html, 'lxml')
        res  = soup.find_all('div', class_='contents')

        for tag in res[0].find_all('a'):
            tag.string != "不限" and self.district.setdefault(tag.string, [])

    def get_business(self):
        """获取商业区信息
        """
        for i in self.district.keys():
            url = 'https://www.lagou.com/jobs/list_php?px=default&city={city}&district={district}#filterBox'.format(city=self.city, district=i)
            html = requests.get(url, headers = self.headers).content.decode('utf-8')
            soup = BeautifulSoup(html, 'lxml')
            res  = soup.find_all('li', class_='detail-bizArea-area')

            for tag in res[0].find_all('a'):
                tag.string != '不限' and self.district[i].append(tag.string)

            # 每爬完一次, 等待15~30s
            time.sleep(random.randint(15, 30))

    def crawel_district_positions(self, district):
        """ 获取行政区职位信息
        """
        url = "https://www.lagou.com/jobs/positionAjax.json?px=new&city="+self.city+"&district="+district+"&needAddtionalResult=false"
        referer_url = "https://www.lagou.com/jobs/list_PHP?px=new&city="+quote(self.city)+"&district="+quote(district)

        self.headers['User-Agent'] = self.browesers[random.randint(0, 5)]
        self.headers['Referer'] = referer_url

        page = 1
        flag = 'true'
        result = queue.Queue()

        while True:
            if (page != 1):
                flag = 'false'

            data = {
                'first': flag,
                'pn': page,
                'kd': 'PHP'
            }

            res = self.analysis_data(url, data)

            if(not res['content']['positionResult']['result']):
                break

            for i in res['content']['positionResult']['result']:
                data = district, '', i['salary'], i['workYear'], i['industryField']
                result.put(data)

            page = page + 1
            time.sleep(random.randint(30, 60))

        return result

    def crawel_biz_area_positions(self, district, biz_area):
        """ 获取商业区职位信息
        """
        url = "https://www.lagou.com/jobs/positionAjax.json?px=new&city="+self.city+"&district="+district+"&bizArea="+biz_area+"&needAddtionalResult=false"
        referer_url = "https://www.lagou.com/jobs/list_PHP?px=new&city="+quote(self.city)+"&district="+quote(district)+"&bizArea="+quote(biz_area)

        self.headers['User-Agent'] = self.browesers[random.randint(0, 5)]
        self.headers['Referer'] = referer_url

        page = 1
        flag = 'true'
        result = queue.Queue()

        while True:
            if page != 1:
                flag = 'false'

            data = {
                'first': flag,
                'pn': page,
                'kd': 'PHP'
            }

            res = self.analysis_data(url, data)

            if not res['content']['positionResult']['result']:
                break

            for i in res['content']['positionResult']['result']:
                data = district, biz_area, i['salary'], i['workYear'], i['industryField']
                result.put(data)

            page = page + 1
            time.sleep(random.randint(30, 60))

        return result

    def get_data(self, url, data):
        """ 从url中获取数据
        """
        try:
            res = requests.post(url, headers = self.headers, proxies = self.proxy, data = data, timeout = 5)
        except:
            print('代理失效, 修改代理, 重新获取请求.')
            self.change_proxy()
            res = self.get_data(url, data)

        return res

    def analysis_data(self, url, data):
        """ 分析数据是否有key error
        """
        res = self.get_data(url, data)
        res = json.loads(res.content.decode('utf-8'))

        try:
            if not res['content']['positionResult']['result']:
                pass
        except KeyError:
            print('KeyError, 修改代理, 继续请求')
            self.change_proxy()
            res = self.analysis_data(url, data)

        return res

    def crawel_positions(self):
        """ 爬取职位信息主程序
        """
        for i in self.district.keys():
            if (self.district[i]):   # 有商业区的职位信息爬取
                for biz_area in self.district[i]:
                    res_queue = self.crawel_biz_area_positions(i, biz_area)
                    print('%s %s 的职位信息爬取完毕: %d' % (i, biz_area, res_queue.qsize()))

                    # 保存职位信息到数据库
                    while not res_queue.empty():
                        data = res_queue.get()
                        row = self.db.insert_data(data)

                        if not row:
                            print('插入数据失败.')


                # 爬完一个商业区, 睡眠30~60s
                time.sleep(random.randint(30, 45))

            else:                    # 没有商业区的职位信息爬取
                res_queue = self.crawel_district_positions(i)
                print('%s 的职位信息爬取完毕: %d' % (i, res_queue.qsize()))

                # 保存职位信息到数据库
                while (not res_queue.empty()):
                    data = res_queue.get()
                    row = self.db.insert_data(data)

                    if not row:
                        print('插入数据失败.')

            # 爬完一个行政区, 睡眠15s
            time.sleep(30)

    def run(self):
        # 爬取行政区
        print('\n########## 爬取行政区 ##########')
        self.get_administrative()
        print(self.district)

        # 爬取商业区
        print('\n########## 爬取商业区 ##########')
        self.get_business()
        print(self.district)

        # 爬取各区职位信息
        print('\n########## 爬取职位信息 ##########')
        self.crawel_positions()
