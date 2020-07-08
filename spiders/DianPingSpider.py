# -*- coding: utf-8 -*-
import scrapy
import re
from ..tools import conver_font as cf
from ..items import DianpingscrapyItem


class DianpingspiderSpider(scrapy.Spider):
    name = 'DianPingSpider'
    allowed_domains = ['dianping.com']
    start_urls = ['http://www.dianping.com/guangzhou/ch10/p'+str(i) for i in range(1, 50)]
    # start_urls = ['http://www.dianping.com/shop/H6gH2PKWAAufkfSD/review_all']
    @staticmethod
    def is_verify(response):
        """
        判断是否弹出验证
        :param response:
        :return:
        """
        return False if response.url.find("verify.meituan.com") >= 0 else True

    def parse(self, response):
        """
        获取所有店铺信息
        :param response:
        :return:
        """
        if not self.is_verify(response):  # 检测是否需要验证
            yield response.request.replace(url=response.request.meta["redirect_urls"][0])  # 出现需要验证则再次提交
            return
        # items = DianpingscrapyItem()
        fonts = cf.font2dict(cf.get_font(response.text))  # 调用函数生成文字字典
        response = response.replace(body=response.text.replace('&#x', 'uni'))  # 将字体反爬编码中的&#x替换为uni，便于文字替换
        # selector = etree.HTML(html)
        shop_items = response.xpath('//div[@id="shop-all-list"]/ul/li')  # 利用xpath获取每一家店
        for shop in shop_items:
            items = dict()
            items['title'] = shop.xpath('.//div[@class="tit"]//h4/text()').extract_first()  # 店名标题
            items['det_link'] = shop.xpath('.//a[@data-click-name="shop_title_click"]/@href').extract_first()  # 详细页链接
            items['review'] = cf.font_convert(fonts, shop.xpath('.//a[@class="review-num"]//text()').extract()[1:-1],'PingFangSC-Regular-shopNum')  # 评论数
            items['mean'] = cf.font_convert(fonts, shop.xpath('.//a[@class="mean-price"]//text()').extract()[1:-1],'PingFangSC-Regular-shopNum')  # 人均消费
            items['score'] = shop.xpath('.//div[@class="nebula_star"]/div[last()]//text()').extract_first()  # 评分
            items['tag'] = cf.font_convert(fonts, shop.xpath('.//div[@class="tag-addr"]/a[1]//text()').extract(),'PingFangSC-Regular-tagName')  # 类别标签
            items['addr'] = cf.font_convert(fonts, shop.xpath('.//div[@class="tag-addr"]/a[2]//text()').extract(),'PingFangSC-Regular-tagName')  # 地址
            items['addr_det'] = cf.font_convert(fonts, shop.xpath('.//span[@class="addr"]//text()').extract(), 'PingFangSC-Regular-address')  # 详细地址
            items['flavor'] = cf.font_convert(fonts, shop.xpath('.//span[@class="comment-list"]/span[1]/b//text()').extract(), 'PingFangSC-Regular-shopNum')  # 口味评分
            items['env'] = cf.font_convert(fonts, shop.xpath('.//span[@class="comment-list"]/span[2]/b//text()').extract(), 'PingFangSC-Regular-shopNum')  # 环境评分
            items['service'] = cf.font_convert(fonts, shop.xpath('.//span[@class="comment-list"]/span[3]/b//text()').extract(), 'PingFangSC-Regular-shopNum')  # 服务评分
            items['recommend'] = shop.xpath('.//div[@class="recommend"]//a/text()').extract()  # 推荐菜
            yield scrapy.Request(url=items['det_link'] + '/review_all', callback=self.parse_comment, meta={'item': items}, dont_filter=False)  # 将评论页加入到scrapy请求队列
            # print(f'title:{title} link:{det_link} review:{review} mean:{mean} score:{score} flavor:{flavor} env:{env} service:{service} tag:{tag} addr:{addr} addr-det:{addr_det} recommend:{recommend}')

    def parse_comment(self, response):
        """
        获取对应店铺评论页信息
        :param response:
        :return:
        """
        if not self.is_verify(response):  # 检测是否需要验证
            yield response.request.replace(url=response.request.meta["redirect_urls"][0])   # 出现需要验证则再次提交
            return
        # items = CommentScrapyItem()
        items = DianpingscrapyItem()
        items.update(response.meta['item'])
        review_font_map = cf.get_svg_html(response.text)  # 调用函数生成css反爬文字编码字典
        review_class_set = re.findall('<svgmtsi class="(.*?)"></svgmtsi>', response.text, re.S)  # 拿到所有的文字标签类名
        html = response.text
        for class_name in review_class_set:  # 将所有svg替换为文字
            html = re.sub('<svgmtsi class="{}"></svgmtsi>'.format(class_name), review_font_map.get(class_name), html)
        # selector = etree.HTML(html)
        response = response.replace(body=html)
        comments = response.xpath('//div[@class="reviews-items"]/ul/li')  # 获取每一项评论信息
        if len(comments) > 15:
            comments = comments[:15]

        data = list()
        for comment in comments:
            data.append({
                'name': comment.xpath('.//a[@class="name"]/text()').extract_first().replace(' ', '').replace('\n', ''),  # 评论人昵称
                'comm': ''.join(comment.xpath('.//div[@class="review-words Hide"]//text()').extract()).replace('收起评论', '').replace(' ', '').replace('\n', '').replace('\xa0', ' '),  # 评论内容
                'comm_score': ''.join(comment.xpath('.//span[@class="score"]//text()').extract()).replace('收起评论', '').replace(' ', '').replace('\n', ''),  # 分数
                'menu': '、'.join(comment.xpath('.//div[@class="review-recommend"]/a/text()').extract()).replace(' ', '').replace('\n', ''),  # 推荐菜
                'set_time': comment.xpath('//span[@class="time"]/text()').extract_first().replace(' ', '').replace('\n', '')  # 评论时间
            })
        items['comment'] = data
        yield items

            # print(f'name: {name} score:{score} menu:{menu} time:{set_time} comm:{comm}')
