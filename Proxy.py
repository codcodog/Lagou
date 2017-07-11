#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import requests
import queue
import threading
from bs4 import BeautifulSoup

class Proxy(object):

    def __init__(self):
        self.path = 'htmls'
        self.tmp_proxies = queue.Queue()
        self.proxies = queue.Queue()

    def get_proxy(self):
        """ 由于获取proxy的网站需要翻墙,
        因此, 用浏览器保存html文件, 再从本地解释获取proxy

        从html文件解释参数
        获取proxy
        """
        if (os.path.exists(self.path)):
            for i in os.listdir(self.path):
                with open(self.path + '/' + i, 'r') as fp:
                    html = fp.read()

                soup        = BeautifulSoup(html, 'lxml')
                tr_odd_res  = soup.find_all('tr', class_  = 'odd')
                tr_even_res = soup.find_all('tr', class_  = 'even')

                self.pase_res(tr_odd_res)
                self.pase_res(tr_even_res)
        else:
            print('htmls目录不存在, 找不到需要解释的html文件')

    def pase_res(self, tr_res):
        """ 解析tr获取的td list, 拼接proxy, 放入队列
        """
        for i in tr_res:
            td_res = i.find_all('td')
            protocol = 'http://' if td_res[-2].string=='no' else 'https://'
            host = td_res[0].string
            port = td_res[1].string
            
            proxy = protocol + host + ':' + port
            self.tmp_proxies.put(proxy)

    def is_active(self):
        """ 判断proxy是否可用
        """
        url = "http://www.baidu.com"

        while (not self.tmp_proxies.empty()):
            proxy = self.tmp_proxies.get()
            protocol = proxy.split(':')[0]
            
            proxy_dict = {
                protocol : proxy
            }

            try:
                res = requests.get(url, proxies = proxy_dict, timeout = 3)
                print(res.status_code)
                res.status_code == 200 and self.proxies.put(proxy)
            except:
                continue

    def save_proxy(self):
        """ 保存proxy到本地proxy.txt文件
        """
        with open('proxy.txt', 'w') as fp:
            while (not self.proxies.empty()):
                fp.write(self.proxies.get() + '\n')

        print('获取Proxy代理完成, 保存在proxy.txt')

    def run(self):
        """ 多线程验证proxy是否可用
        """
        thread_list = []
        thread_num  = 10

        for i in range(0, thread_num):
            thread_list.append(threading.Thread(target = self.is_active))

        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()

        self.save_proxy()


if __name__ == "__main__":
    proxy = Proxy()

    print('正在努力获取proxy ip...')

    proxy.get_proxy()
    proxy.run()
