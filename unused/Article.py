import re
import sys
import pymysql
import pandas as pd
import lxml.html as ETree
import itchat
from itchat.content import *
class Article():

    def __init__(self):
        pass

    @property
    def articles(self):
        """
        公众号推送中的文章列表 (首篇的 标题/地址 与消息中的 text/url 相同)

        其中，每篇文章均有以下属性:

        * `title`: 标题
        * `summary`: 摘要
        * `url`: 文章 URL
        * `cover`: 封面或缩略图 URL
        """

        from wxpy import MP
        if self.type == SHARING and isinstance(self.sender, MP):
            tree = ETree.fromstring(self.raw['Content'])
            # noinspection SpellCheckingInspection
            items = tree.findall('.//mmreader/category/item')
            article_list = list()

            for item in items:
                def find_text(tag):

                    found = item.find(tag)
                    if found is not None:
                        return found.text

                article = Article()
                article.title = find_text('title')
                article.summary = find_text('digest')
                article.url = find_text('url')
                article.cover = find_text('cover')
                article.pub_time = find_text('pub_time')
                article.source = find_text('.//name')
                article_list.append(article)


            return article_list


def wechat_run(self, url, pub_time):  # 实现主要逻辑

    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "root", "weixin_database")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    html_str = self.parse_url(url)
    content_list = self.get_content_list(html_str)
    title = ''.join(content_list[0]["title"])
    #             other1 = ''.join(content_list[0]["other"])
    other = '\n'.join(content_list[0]["other"])
    create_time = pub_time

    #             print(other)
    p1 = re.compile(r'\s*[（|(]20\d+[）|)]\s*[\u4e00-\u9fa5]*[\d]*[\u4e00-\u9fa5]+[\d]+号', re.S)
    anhao = re.search(p1, other)
    if (anhao):
        anhao = anhao.group().replace("\n", "")
    else:
        anhao = ""

    p2 = re.compile(r'\s[【]*裁判要[\u4e00-\u9fa5]\s*.*?(?=[【]|裁判文)', re.S)
    zhaiyao = ''.join(re.findall(p2, other)).replace("\n", "")
    #             print(zhaiyao)
    p3 = re.compile('<div class="rich_media_content " id="js_content">.*?</div>', re.S)
    html = re.search(p3, html_str)
    if (html):
        html = re.search(p3, html_str).group().replace("\n", "")

    else:
        html = html_str.replace("\n", "")
    sql = """INSERT INTO weixin_table(title,url,anhao,yaozhi,other,html,create_time,type_id)
        VALUES ({},{},{},{},{},{},{},{})""".format('"' + title + '"', '"' + url + '"', '"' + anhao + '"',
                                                   '"' + zhaiyao + '"', '"' + other + '"', "'" + html + "'",
                                                   create_time, 4)
    #             print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print("数据插入成功")
    except:
        print("数据插入失败:")
        info = sys.exc_info()
        print(info[0], ":", info[1])
        # 如果发生错误则回滚
        db.rollback()

    # 3.保存html
    page_name = title
    self.save_html(html, page_name)
    # 关闭数据库连接
    db.close()
