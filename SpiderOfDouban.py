import os
import re
import requests
from bs4 import BeautifulSoup

wd = input("请输入电影名称：")
path = "D://豆瓣影评//" + wd
os.makedirs(path, exist_ok=True)
url = "https://www.douban.com/search?q=" + wd
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}

def getHtml(args):
    res = requests.get(args)
    return res.text


# 通过搜索功能获取电影页面
searchSoup = BeautifulSoup(getHtml(url))
searchList = searchSoup.select(".title h3 a")[0]
searchUrl = searchList.get("href")
searchWd = searchList.getText()
searchWd = str(searchWd).strip()
if searchWd != wd:
    print("未找到相关内容，将进行模糊匹配。")

# 通过电影链接获取电影编号
try:
    numReg = re.compile(r'%2F(\d+)?%2F')
    num = numReg.findall(searchUrl)[1]
except:
    print("电影未被收录！")
else:
    # 生成电影影评页面的链接
    # 这里只获取首页的评论（20条），如果希望获取更多，则在后面加“?start=n”(n = （页码-1）*20)
    reviewsUrl = "https://movie.douban.com/subject/" + num + "/reviews"

    # 获取前二十条影评
    reviewsSoup = BeautifulSoup(getHtml(reviewsUrl))
    list = reviewsSoup.select(".main-bd h2 a")
    x = 0
    for title_link in list:
        # 获取影评标题
        title = title_link.getText()
        fileName = re.sub(r"\W", "-", title)  # 将特殊字符替换
        # 获取影评链接
        link = title_link.get("href")

        # 获取单条影评的详细内容
        reviewSoup = BeautifulSoup(getHtml(link))

        # 获取评价
        ratingEle = reviewSoup.select(".main-title-hide")
        for ratings in ratingEle:
            rating = ratings.getText()

        # 获取时间
        timeEle = reviewSoup.select(".main-meta")
        for times in timeEle:
            time = times.get("content")

        # 获取内容
        reviewEle = reviewSoup.select(".review-content.clearfix p")
        if len(reviewEle) == 0:
            reviewEle = reviewSoup.select(".review-content.clearfix")
        review = ""
        for reviews in reviewEle:
            review += (reviews.getText() + "\n")

        # 新建以影评标题为文件名的txt文件并写入影评
        x += 1
        try:
            file = open(path + "//" + str(fileName) + ".txt", "w", encoding="utf-8")  # 这里设置utf-8会解决gbk的编码问题，但排版比较难看。
            file.write("评价：%s\n时间：%s\n内容：\n%s" % (rating, time, review.strip()))
            file.close()
            print("已写入%s条。" % x)
        except Exception as err:
            print("第%s条文件写入失败！\n异常原因：%s" % (x, err))
