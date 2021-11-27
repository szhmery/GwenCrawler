# -*- coding: utf-8 -*-
import datetime
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from chinese_calendar import is_workday
from lxml import etree


class ParseArticles:
    def __init__(self, list_file):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}
        self.list_file = list_file

    def get_url_list(self):
        file_path = self.list_file
        df = pd.read_csv(file_path)
        lines = df.values.tolist()
        # url_list = df["link"].tolist()
        # time_list = df["create_time"].tolist()

        return lines

    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def parse_date_format(self, article_date):
        # 原来根据title来解析日期，后面直接有了date这一列，注释这一段。
        # if '早读' in title:
        #     p = re.compile(r'^(\d+)\.(\d+)早读', re.S)
        # else:
        #     p = re.compile(r'\|(\d+)\.(\d+)', re.S)
        #
        # title_date = re.search(p, title)
        # if title_date:
        #     date = str(title_date.group(1)).zfill(2) + str(title_date.group(2)).zfill(2)
        #     year = str(datetime.datetime.now().year)
        #     this_date = datetime.datetime.strptime(year + date, "%Y%m%d").date()
        #     self.pre_date = this_date
        # else:
        #     if self.pre_date:
        #         this_date = self.pre_date
        #     else:
        #         this_date = datetime.datetime.today().date()
        this_date = datetime.datetime.strptime(str(article_date), "%Y%m%d").date()
        weekday = this_date.weekday() + 1  # 周几
        year_int = this_date.isocalendar()[0]
        week_int = this_date.isocalendar()[1]
        day_int = this_date.isocalendar()[2]
        week_begin = (this_date - datetime.timedelta(day_int - 1)).strftime(format='%Y%m%d')
        week_end = (this_date + datetime.timedelta(7 - day_int)).strftime(format='%Y%m%d')
        file_name = str(year_int) + 'Y' + str(week_int) + 'W_' + week_begin + '-' + week_end
        return this_date, weekday, file_name

    # 在src字符串里，从end出往前找，找到第count个sub子字符串。
    def rfind_n_substr(self, src, sub, count, end):
        index = src.rfind(sub, 0, end)
        if index != -1 and count > 1:
            return self.rfind_n_substr(src, sub, count - 1, index - 1)
        return index

    def parse_content(self, article_date, title, html_str):  # 提取数据
        item = {}
        # html = etree.HTML(html_str)

        item['title'] = title

        this_date, weekday, file_name = self.parse_date_format(article_date)
        item['date'] = article_date
        # item['date'] = this_date.strftime(format='%Y%m%d')

        result, html_content = '', ''
        # source = html.xpath("//*[@id=\"js_name\"]/text()")
        # source = [i.replace("\n", "").replace(" ", "") for i in item["laiyuan"]]
        # doc = html.xpath("//*[@id=\"js_content\"]")
        # doc = etree.tostring(doc[0])
        soup = BeautifulSoup(html_str, 'html.parser')
        for k in soup.find_all('div'):
            if k.has_attr('id') and k['id'] == 'js_content':
                html_content = str(k)

        html_content = re.sub(r'\n+', '', html_content)
        result = re.sub("<div class=\"rich_media_content\" id=\"js_content\" style=\"visibility: hidden;\">", "",
                        html_content)
        result = re.sub("</div>", "", result)
        result = re.sub("<section><svg.*?></svg></section>", "", result)
        result = re.sub("<svg.*?></svg>", "", result)
        result = re.sub("<iframe.*?></iframe>", "", result)
        result = re.sub("<img.*?></img>", "", result)
        result = re.sub("<mpvoice.*?></mpvoice>", "", result)
        result = re.sub("<qqmusic.*?></qqmusic>", "", result)
        result = re.sub("<animate.*?></animate>", "", result)

        if '早读' in title or '国庆特刊' in title:
            if '国庆特刊' in title or is_workday(this_date):
                print("是工作日")
                # 从英音讲解前面两个section，删除到Longman Dictionary后面一个</section>
                idx1 = result.find('英音讲解')
                idx2 = self.rfind_n_substr(result, '<section', 2, idx1)

                idx3 = result.find('Longman Dictionary')
                idx4 = result.find('</section>', idx3)
                result = result[0:idx2] + result[idx4 + 10:]  # 10 is length of '</section>'

                idx3 = result.find('随意造句')
                idx4 = result[idx3:].find('<section')
                result = result[0:idx3 + idx4]
            else:
                print("是休息日")
                if weekday == 6:
                    print("Saturday")
                    idx1 = result.find('周末没有朗读版哦')
                    idx2 = self.rfind_n_substr(result, '<section', 2, idx1)
                    idx3 = result.find('本周早读小测')
                    idx4 = self.rfind_n_substr(result, '<section', 2, idx3)
                    result = result[0:idx2] + result[idx4:]
                    idx5 = result.find('答案在哪里呢')
                    # 往前找到第四个section，删除
                    idx6 = self.rfind_n_substr(result, '<section', 4, idx5)
                    result = result[0:idx6]

                elif weekday == 7:
                    print("Sunday")
                    idx1 = result.find('周末没有朗读版哦')
                    idx2 = self.rfind_n_substr(result, '<section', 2, idx1)
                    idx3 = result.find('本周早读小测答案')
                    idx4 = self.rfind_n_substr(result, '<section', 2, idx3)
                    result = result[0:idx2] + result[idx4:]
                    idx5 = result.find('底部点击')
                    idx6 = self.rfind_n_substr(result, '<section', 1, idx5)
                    result = result[0:idx6]
                else:
                    print("Other holiday.")

        if '每日听写|' in title:
            idx1 = result.find('词汇补充')
            idx2 = self.rfind_n_substr(result, '<section', 3, idx1)
            idx3 = result.find('加入我们')
            idx4 = self.rfind_n_substr(result, '<section', 1, idx3)
            result = result[idx2:idx4]

        if '翻译' in title:
            idx1 = result.find('>美文</p><p style=')
            idx2 = self.rfind_n_substr(result, '<section', 1, idx1)
            idx3 = result.find(
                '</section></section><section powered-by="xiumi.us" style="text-align: justify;box-sizing: border-box;"><p style="white-space: normal;margin: 0px;padding: 0px;box-sizing: border-box;"><br style="box-sizing: border-box;"/></p></section><section powered-by="xiumi.us" style="text-align: justify;box-sizing: border-box;"><p style="white-space: normal;margin: 0px;padding: 0px;box-sizing: border-box;"><br style="box-sizing: border-box;"/></p></section>')
            result = result[idx2:idx3]

        if '每日一句' in title:
            index = result.find('<section class="channels_iframe_wrp"><mpvideosnap')
            result = result[0:index]

        if '老外说' in title:
            idx1 = result.find('大家还想听“老外”说些什么')
            # result = result[0:idx1]
            idx2 = self.rfind_n_substr(result, '<section', 1, idx1)
            # idx2 = result.rfind('<section')
            result = result[0:idx2]

        if '每日听写飞鸟集' in title:
            idx1 = result.find('本文挖了几个空')
            idx2 = self.rfind_n_substr(result, '<section', 2, idx1)
            idx3 = result.find('图片与资料来源')
            idx4 = self.rfind_n_substr(result, '<section', 2, idx3)
            result = result[idx2:idx4]

        section_num1 = result.count('<section')
        section_num2 = result.count('</section>')
        if section_num1 > section_num2:
            result += '</section>' * (section_num1 - section_num2)
        item['content'] = result
        self.save_md(result, file_name)
        print("Save to " + file_name)

        item['filename'] = file_name + '.md'
        return item

    def save_md(self, html_str, page_name):
        file_path = "articles/{}.md".format(page_name)
        with open(file_path, 'a+', encoding="utf-8") as f:
            f.write(html_str)

    def reorder_list(self, url_list):
        split_list = []
        update_time = ''
        begin = 0
        for i, line in enumerate(url_list):
            if line[1] != update_time:
                if i > 0:
                    split_list.append(url_list[begin:i])
                begin = i
                update_time = line[1]
        if begin == 0:
            split_list.append(url_list[:])
        else:
            split_list.append(url_list[begin:])

        ans_list = []
        for one_day in split_list[::-1]:
            ans_list.extend(one_day)
        return ans_list

    # 运行入口函数
    def run(self):
        # 获取url列表和时间列表
        url_list = self.get_url_list()
        url_list = self.reorder_list(url_list)
        articles_files = set()
        # 遍历url列表，发送请求，获取响应
        for line in url_list:
            num = line[0]
            article_date = line[1]
            title = line[2]
            if '为你读诗' in title or '汇总' in title or '听歌学英文' in title:
                continue
            url = line[3]
            print(str(num) + " Title:" + title)

            # 解析url，获得html
            html_str = self.parse_url(url)

            # 获取内容
            items = self.parse_content(article_date, title, html_str)
            articles_files.add(items['filename'])
        return articles_files
