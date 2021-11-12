
import urllib.request
import re

def openUrl():
    print("启动爬虫，打开搜狗搜索微信界面")
    # 加载页面
    url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=TeacherGwen'
    htmlContentObj = urllib.request.urlopen(url)
    # 将页面转化为文本
    html = htmlContentObj.read()
    # 正则匹配
    str = re.findall(r"http://mp.weixin.qq.com/profile.+==",html)
    # 替换转义符得到可访问的链接地址
    tempHref = re.sub(r"&amp;","&",str[0])
    print(tempHref)
    return tempHref

openUrl()