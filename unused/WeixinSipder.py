import re
import requests
import pymysql
import pandas as pd
from lxml import etree
import sys

class WeixinSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

    def get_url_list(self):
        file_path = "url/beijing.csv"
        df = pd.read_csv(file_path)
        url_list = df["link"].tolist()
        time_list = df["create_time"].tolist()

        return url_list, time_list

    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_content_list(self, html_str):  # 提取数据
        html = etree.HTML(html_str)
        content_list = []
        item = {}
        item["title"] = html.xpath("//*[@id=\"activity-name\"]/text()")
        item["title"] = [i.replace("\n", "").replace(" ", "") for i in item["title"]]
        item["laiyuan"] = html.xpath("//*[@id=\"js_name\"]/text()")
        item["laiyuan"] = [i.replace("\n", "").replace(" ", "") for i in item["laiyuan"]]
        item["other"] = html.xpath("//*[@id=\"js_content\"]//text()")

        content_list.append(item)

        return content_list
    def save_html(self, html_str, page_name):
        file_path = "html/lufa/{}.html".format(page_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_str)

    def run(self):
        # 获取url列表和时间列表
        url_list, time_list = self.get_url_list()

        # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
        db = pymysql.connect("localhost", "root", "root", "weixin_database")

        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()

        # 遍历url列表，发送请求，获取响应
        for url in url_list:
            num = url_list.index(url)
            print(num)
            # 解析url，获得html
            html_str = self.parse_url(url)
            # 获取内容
            content_list = self.get_content_list(html_str)
            # list转字符串
            title = ''.join(content_list[0]["title"])
            other = '\n'.join(content_list[0]["other"])
            # 根据下标取发布时间
            create_time = time_list[num]

            p1 = re.compile(r'\s*[（|(]20\d+[）|)]\s*[\u4e00-\u9fa5]*[\d]*[\u4e00-\u9fa5]+[\d]+号', re.S)
            anhao = re.search(p1, other)
            if (anhao):
                anhao = anhao.group().replace("\n", "")
            else:
                anhao = ""


            p2 = re.compile(r'\s[【]*裁判要点\s*.*?(?=[【]|裁判文)', re.S)
            zhaiyao = ''.join(re.findall(p2, other)).replace("\n", "")

            p3 = re.compile('<div class="rich_media_content " id="js_content">.*?</div>', re.S)
            html = re.search(p3, html_str)
            if (html):
                html = re.search(p3, html_str).group().replace("\n", "")

            else:
                html = html_str.replace("\n", "")

                page_name = title


            self.save_html(html, page_name)


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
            except:
                print("数据插入失败:")
                info = sys.exc_info()
                print(info[0], ":", info[1])
                # 如果发生错误则回滚
                db.rollback()

            # 关闭数据库连接
            db.close()
    def wechat_run(self,url,pub_time):  # 实现主要逻辑

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


if __name__ == '__main__':
    weixin_spider = WeixinSpider()
    weixin_spider.run()