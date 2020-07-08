#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time       : 2020/6/1 14:56
# @Author     : ShadowY
# @File       : conver_font.py
# @Software   : PyCharm
# @Version    : 1.0
# @Description: None

import re
import requests
from fontTools.ttLib import TTFont
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36',
    'Host': 'www.dianping.com'  # 没有这个会弹出验证
}


def get_font(html):
    """
    获取字体文件存储到电脑中
    :param html:
    :return:
    """
    result = re.search('<link rel="stylesheet" type="text/css" href="//s3plus(.*?)">', html, re.S)  # 利用正则获取CSS链接
    if result:
        css_url = 'http://s3plus' + result.group(1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
        }
        css_res = requests.get(css_url, headers=headers).text  # 请求对应链接拿到字体
        result = re.findall('@font-face\{font-family: "(.*?)";.*?,url\("(.*?)"\);\}', css_res)  # 利用正则方式获取到字体链接
        font_urls = dict(result)
        # 循环获取所有的字体保存在本地
        for font_type, font_url in font_urls.items():
            filename = font_url.split('/')[-1]
            font_url = 'http:' + font_url
            font = requests.get(font_url, headers=headers).content
            filepath = f'{filename}'
            with open(filepath, 'wb') as f:
                f.write(font)
            font_urls[font_type] = filepath  # 将网络路径转换为本地路径
        return font_urls


def font_convert(font_dict, font_list, font_type):
    """
    将编码字体转换为文本
    :param font_type:
    :param font_dict: 字体列表
    :param font_list: 文字
    :return:
    """
    re_text = list()
    font_dict = font_dict[font_type]
    # 将所有编码逐个替换
    for text in font_list:
        if font_dict.get(text.replace(';', '')):
            re_text.append(font_dict.get(text.replace(';', '')))
        else:
            re_text.append(text)
    return ''.join(re_text)


def font2dict(font_urls):
    """
    将字体文件转换为字典
    :param font_urls:
    :return:
    """
    font_dict = {}
    text = ''
    # 由于大众点评的文字顺序不变，直接将所有文字保存下来做字典映射
    with open(r'K:\学校\个人\2019下学期\数据采集\作业\大作业\dianping\font.txt', 'r', encoding='utf8') as f:
        text = list(f.read())
    for name, font_url in font_urls.items():
        font = TTFont(font_url)
        code_list = font.getGlyphOrder()[2:]
        # font_dict[name] = dict(zip([code.replace('uni', '&#x') for code in code_list], text))
        font_dict[name] = dict(zip([code for code in code_list], text))  # 转换为字典，{编码：文字}形式
    return font_dict


#  ====================================评论页=====================================
def get_svg_html(html):
    result = re.search('<svgmtsi class="(.*?)"></svgmtsi>', html, re.S)
    review_prefix = result.group(1)[:2]
    # 正则匹配 css 文件
    result = re.search('<link rel="stylesheet" type="text/css" href="//s3plus(.*?)">', html, re.S)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36',
        'Host': 's3plus.meituan.net'  # 没有这个会弹出验证
    }
    if result:
        css_url = 'http://s3plus' + result.group(1)
        css_res = requests.get(css_url, headers=headers).text
        review_class_list = re.findall('\.%s(.*?){background:(.*?)px (.*?)px;}' % review_prefix, css_res, re.S)  # 拿到所有的css类以及偏移值
        result = re.search('svgmtsi\[class.*?background-image: url\((.*?)\);', css_res, re.S)  # 评论使用的 svg 文件 url
        review_svg_url = 'http:' + result.group(1)
        review_svg = requests.get(review_svg_url, headers=headers).text
        review_svg_y_words = re.findall('<text x=".*?" y="(.*?)">(.*?)</text>', review_svg, re.S)  # 获取每行的字的坐标
        if not review_svg_y_words:  # 由于有两种形式的svg文件随机出现，所以需要做判断，如果第一组类型获取不到就是第二种类型了
            review_svg_y_list = re.findall('<path id="(\d+)" d="M0 (\d+) H600"/>', review_svg, re.S)  # 获取每行字的坐标第二种类型
            review_result = re.findall('<textPath xlink:href="#(\d+)" textLength=".*?">(.*?)</textPath>', review_svg, re.S)  # 获取编码及文字长度
            review_words_dc = dict(review_result)
            review_font_map = review2_class_to_font(review_class_list, review_svg_y_list, review_words_dc, review_prefix)  # 将数据传入字体字典计算函数进行转换为字典
        else:
            review_font_map = review_class_to_font(review_class_list, review_svg_y_words, review_prefix, 14)   # 将数据传入字体字典计算函数进行转换为字典
        return review_font_map


def review_class_to_font(class_list, y_words, prefix, font_size):
    """
    核心算法，将坐标转换为类与文字的映射表，类型1
    :param class_list:
    :param y_words:
    :param prefix:
    :param font_size:
    :return:
    """
    tmp_dc = dict()
    tmp = None
    # 遍历坐标列表和字体文字列表
    for cname, x, y in class_list:
        for text_y, text in y_words:
            if int(text_y) >= abs(int(float(y))):  # 判断文字的y坐标是否比坐标大一点或者相等，但又不超过下一个y坐标
                index = abs(int(float(x))) // font_size  # 横坐标间距是字体大小，利用整除结果获取到坐标作为下标取到原文字
                tmp = text[index]
                break
        tmp_dc[prefix + cname] = tmp
    return tmp_dc


def review2_class_to_font(class_list, y_list, words_dc, prefix, font_size):
    """
    核心算法，将坐标转换为类与文字的映射表， 类型2
    :param class_list:
    :param y_words:
    :param prefix:
    :param font_size:
    :return:
    """
    tmp_dc = dict()
    # 遍历字体
    for i in class_list:
        x_id = None
        for j in y_list:
            if int(j[1]) >= abs(int(float(i[2]))):  # 判断文字的y坐标是否比坐标大一点或者相等，但又不超过下一个y坐标
                x_id = j[0]
                break
        index = abs(int(float(i[1]))) // font_size  # 横坐标间距是字体大小，利用整除结果获取到坐标作为下标取到原文字
        tmp = words_dc[x_id][int(index)]
        tmp_dc[prefix + i[0]] = tmp
    return tmp_dc