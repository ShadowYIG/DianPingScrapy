#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time       : 2020/5/31 23:00
# @Author     : ShadowY
# @File       : start.py.py
# @Software   : PyCharm
# @Version    : 1.0
# @Description: 运行

from scrapy import cmdline

# cmdline.execute(['scrapy','crawl','qsbk'])
cmdline.execute('scrapy crawl DianPingSpider'.split())