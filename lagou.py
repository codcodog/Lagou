from proxy.proxy import Proxy
from crawl.crawl import Crawl


if __name__ == '__main__':
    proxy = Proxy()
    proxy_queue = proxy.run()

    c = Crawl(proxy_queue)
    c.run()
