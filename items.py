# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DianpingscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()  # 标题
    det_link = scrapy.Field()  # 详细页链接
    review = scrapy.Field()  # 评论数
    mean = scrapy.Field()  # 人均消费
    score = scrapy.Field()  # 评分
    tag = scrapy.Field()  # 品类标签
    addr = scrapy.Field()  # 地址
    addr_det = scrapy.Field()  # 详细地址
    flavor = scrapy.Field()  # 口味评分
    env = scrapy.Field()  # 环境评分
    service = scrapy.Field()  # 服务评分
    recommend = scrapy.Field()  # 推荐菜
    comment = scrapy.Field()  # 评论数据
    pass


# class CommentScrapyItem(scrapy.Item):
#     name = scrapy.Field()
#     comm = scrapy.Field()
#     comm_score = scrapy.Field()
#     menu = scrapy.Field()
#     set_time = scrapy.Field()