爬虫
====

场景
----
基于想了解PHP职位信息在深圳各区域分布的的情况

爬虫目标
--------
主要爬取拉勾在深圳区域的PHP职位信息.

如何使用
--------
```
$ git clone https://github.com/codcodog/Lagou.git
$ cd Lagou

$ virtualenv venv
$ source venv/bin/active

(venv) $ pip install -r requirements.txt
(venv) $ python lagou.py
```
笔者运行环境：`Arch Linux` + `Python 3.6.4`  
数据存储在 `lagou.db`，数据库：`sqlite3`  
职位信息：`行政区`, `商区`, `薪资`, `工作年限`, `行业类别`

遇到的问题
----------
主要的问题：反爬虫机制

遇到的反爬虫策略有:
- 接口User-agent做了判别
- 接口请求referer做了辨认
- 每个ip的访问频率做了限制
- 每个ip的访问量做了限制

解决办法
--------
- 对于User-agent, 简单点, 就是模拟浏览器, 这个是最基本, 一般网站都会有的反爬虫. 因为Python 爬虫中的User-agent 不做模拟的话, 输出直接是python的.
- 对于职位接口做的 `referer` 辨认, 是本身接口后台接口加的一个辨认, 直接在拉勾网, 用`F12`查看后台接口(Ajax请求)即可知道.
- 对于访问频率, 尽可能慢点, 同人差不多是最好的.
- 对于访问量, 则需要代理ip了. 网上有很多免费代理ip, 可以爬取使用

结语
----
从此次爬虫中, 遇到了一些常见的反爬虫策略, 对爬虫以及 `Python` 这门语言都有了深刻的认识.  

附上数据分析的一个图表: [图表数据](http://lagou.codcodog.me)
