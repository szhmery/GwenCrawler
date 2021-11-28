# -*- coding: utf-8 -*-
import datetime
import random
import time
import configparser
import pandas as pd
import requests


class ArticlesList:
    def __init__(self):
        self.BEGIN = '0'

        conf = configparser.ConfigParser()
        conf.read('conf/cookies.cfg')
        cookie = conf.get("weixin", "cookie")
        token = conf.get("weixin", "token")
        fake_id = conf.get("weixin", "fake_id")
        user_agent = conf.get("weixin", "user_agent")
        self.FAKEID = fake_id
        # 使用Cookie，跳过登陆操作
        self.headers = {
            "Cookie": cookie,
            "User-Agent": user_agent,
        }
        self.TOKEN = token

        self.data = {
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "query": "TeacherGwen",
            "fakeid": fake_id,
            "type": "9",
        }

    def get_articles_list(self, cut_date):
        content_list = []
        break_flag = False
        for i in range(30):
            self.BEGIN = str(i * 5)
            # url里面包含了参数信息，不需要用data，如果url不带信息只有data参数也不行。
            # 目标url
            # url = "https://mp.weixin.qq.com/cgi-bin/appmsg" # incorrect. It's just search the articles.
            url = "https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin={BEGIN}&count=5&fakeid={FAKEID}&type=9&query=&token={TOKEN}&lang=zh_CN&f=json&ajax=1".format(
                BEGIN=self.BEGIN, FAKEID=self.FAKEID, TOKEN=self.TOKEN)

            s = requests.Session()

            # 使用get方法进行提交
            # content_json = requests.get(url, headers=headers, payload=data).json()
            res = requests.request("GET", url, headers=self.headers)
            if res.status_code == 200:
                content_json = res.json()
                if res.cookies.get_dict():  # 保持cookie有效
                    s.cookies.update(res.cookies)
                if 'app_msg_list' in content_json.keys():
                    # 返回了一个json，里面是每一页的数据
                    for item in content_json["app_msg_list"]:
                        # 提取每页文章的标题及对应的url
                        items = []
                        tupTime = time.localtime(item['update_time'])
                        cut_date_struct = time.strptime(cut_date, "%Y%m%d")
                        if tupTime < cut_date_struct:
                            break_flag = True
                            break
                        # standardTime = time.strftime("%Y-%m-%d %H:%M:%S", tupTime)
                        standardTime = time.strftime("%Y%m%d", tupTime)  # 获得日期
                        items.append(standardTime)
                        items.append(item["title"])
                        items.append(item["link"])
                        content_list.append(items)
                    print("Get page " + str(i + 1))
                    if break_flag:
                        break
                    sleep_time = random.randint(5, 15)  # 随机sleep时间
                    time.sleep(sleep_time)
                else:
                    print("Invalid session!")
            else:
                print("Can't access to Weixin Dingyuehao.")

        print(content_list)
        name = ['title', 'date', 'link']
        test = pd.DataFrame(columns=name, data=content_list)
        this_date = datetime.datetime.today().date()
        this_date = this_date.strftime(format='%Y%m%d')
        list_file = "articles/GwenList" + this_date + ".csv"
        test.to_csv(list_file, mode='a', encoding='utf-8')
        print("保存成功")
        return list_file
