# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 上午8:31
# @Author  : jingyoushui
# @Email   : jingyoushui@163.com
# @File    : wechat.py
# @Software: PyCharm
import pandas as pd
from wxpy import *

from unused.WeixinSipder import WeixinSpider

bot = Bot(cache_path=True, console_qr=True)
found1 = bot.mps().search('TeacherGwen')
print(found1)


@bot.register(found1)
def print_found1(msg):
    articles = msg.articles
    if articles is not None:
        # 一次推送可能有多篇文章
        for article in articles:
            a = str(article.source)
            print('title:' + str(article.title))
            print('url:' + str(article.url))
            print('pub_time:' + article.pub_time)
            print('source:' + a)
            content_list = []
            items = []
            # 文章标题
            items.append(str(article.title))
            # 文章链接
            url = str(article.url)
            items.append(url)
            # 发布时间
            pub_time = article.pub_time
            items.append(pub_time)
            content_list.append(items)
            # 保存到csv文件
            name = ['title', 'link', 'create_time']
            test = pd.DataFrame(columns=name, data=content_list)
            test.to_csv("everyday_url/beijing.csv", mode='a', encoding='utf-8')
            print("保存成功")
            # 调用WeixinSpider_1，完成url解析，数据抽取与保存到数据库等操作
            weixin_spider_1 = WeixinSpider()
            weixin_spider_1.wechat_run(url, pub_time)


# # 打印来自其他好友、群聊和公众号的消息
# @bot.register()
# def print_others(msg):
#     print('msg:' + str(msg))
#     articles = msg.articles
#     if articles is not None:
#         for article in articles:
#             a = str(article.source)
#             print('title:' + str(article.title))
#             print('url:' + str(article.url))
#             print('pub_time:' + article.pub_time)
#             print('source:' + a)
#             if a != "KMTV" and a != "北京行政裁判观察":
#                 pass
#             else:
#                 content_list = []
#                 items = []
#                 items.append(str(article.title))
#                 url = str(article.url)
#                 items.append(url)
#                 pub_time = article.pub_time
#                 items.append(pub_time)
#                 content_list.append(items)
#                 name = ['title', 'link', 'create_time']
#                 test = pd.DataFrame(columns=name, data=content_list)
#                 if a == "KMTV":
#                     test.to_csv("everyday_url/kmtv.csv", mode='a', encoding='utf-8')
#                     print("保存成功")
#
#                 if a == "北京行政裁判观察":
#                     test.to_csv("everyday_url/beijing.csv", mode='a', encoding='utf-8')
#                     print("保存成功")
#                     weixin_spider_1 = WeixinSpider()
#                     weixin_spider_1.wechat_run(url, pub_time)


if __name__ == '__main__':
    # 堵塞线程
    bot.join()
