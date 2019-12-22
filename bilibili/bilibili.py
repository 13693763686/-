import requests
import json
import re
import time
from datetime import timedelta,datetime
import pandas as pd
from pandas import DataFrame


def strdelta(tdelta,fmt = "{hours}:{minutes}:{seconds}"):
    "定义如何把时间间隔数据转化为字符串用于excel读入和数据库录入"
    d = {"days" : tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds,3600)
    d["minutes"], d["seconds"] = divmod(rem,60)
    return fmt.format(**d)

# 将所有的待爬取的url集中到一个txt文件中,便于读入
url_list = open("/home/xiaolong/bilibili/url.txt","r").read().split("\n")
# 设置爬取头部，不至于被简单的阻塞
header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"}
# 通过对网页的分析发现,所有的数据以json格式存在于网页中或者异步加载于网页中,下面是所要求数据对应的url的基础部分,缺少部分主要为视频id和up主id
base_url_1 = "https://api.bilibili.com/x/relation/stat"
base_url_2 = "https://api.bilibili.com/x/space/upstat"
base_url_3 = "https://api.bilibili.com/x/space/navnum"
#　用pandas的数据框的数据结构储存信息,从而可以利用pandas的接口来更方便的读入excel文件
df1 = DataFrame(columns=["video_url","up_id","up_username","video_name","video_published_at","video_playback_num","video_barrage_num","video_like_num","video_coin_num",
                        "video_favorite_num","video_forward_name","video_tag","video_length","created_at"])
df2 = DataFrame(columns = ["up_id","up_video_num","up_follow_num","up_like_num","up_playback_num"])

count = 1
#　循环读入url开始爬取
for base_url in url_list:
    #　首先确定爬取时间并对日期进行格式化
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    # 拿到视频所在页的html文件,里面有对应的信息
    r1 = requests.get(base_url, headers=header)
    #　提取视频ｉｄ，把它作为视频信息的表的主键
    id = re.findall(r"av(\d+)",base_url)[0]
    # 所有的数据并不以html标记形式存在于body中，而是以json格式串存在head标签中，因此观察规律，用正则表达式提取对应json字符串并解析为字典
    data = json.loads(re.findall(r'>window.__INITIAL_STATE__=(.*);\(function',r1.text)[0])
    # 提取信息
    # 时间长度以duration即秒数存在与字典中,需要提取然后转换
    seconds = data["videoData"]["duration"]
    video_url = base_url
    up_id = data["upData"]["mid"]
    up_username = data["upData"]["name"]
    video_name = data["videoData"]["title"]
    video_published_at = datetime.fromtimestamp(data["videoData"]["pubdate"]).strftime("%Y-%m-%d %H:%M")
    # 将时间间隔类型数据转换为字符串
    video_length = strdelta(timedelta(seconds=seconds))
    # 关于观看量,点赞等等数据存在与另一个异步加载的文件中,此处进行构造url提取
    r2 = requests.get("https://api.bilibili.com/x/web-interface/archive/stat",headers=header, params = {"aid":id})
    video_stats = json.loads(r2.text)["data"]
    video_playback_num = video_stats["view"]
    video_barrage_num = video_stats["danmaku"]
    video_like_num = video_stats["like"]
    video_coin_num = video_stats["coin"]
    video_favorite_num = video_stats["favorite"]
    video_forward_num = video_stats["share"]
    #　将提取到的tagname整合到一个字符串中
    video_tag = ",".join([tag["tag_name"] for tag in data["tags"]])
    # 下面开始爬取关于ｕｐ主信息，以ｕｐ主ｉｄ为纽带
    # up主的所有信息均已回调函数的形式以json格式数据返回,下面是对应的参数
    params_1 = {"vmid":up_id,"jsonp":"jsonp"}
    params_2 = {"mid":up_id,"jsonp":"jsonp"}
    #　下面是对于的基础url
    r3 = requests.get(base_url_1,headers = header, params = params_1)
    r4 = requests.get(base_url_2,headers = header, params = params_2)
    r5 = requests.get(base_url_3,headers = header, params = params_2)
    # 提取ｕｐ主相关信息
    up_video_num = json.loads(r5.text)["data"]["video"]
    up_follow_num = json.loads(r3.text)["data"]["follower"]
    up_like_num = json.loads(r4.text)["data"]["likes"]
    up_playback_num = json.loads(r4.text)["data"]["archive"]["view"]
    # 插入信息pandas数据框内
    df1.loc[id] = [video_url,up_id,up_username,video_name,video_published_at,video_playback_num,video_barrage_num,video_like_num,video_coin_num,
                        video_favorite_num,video_forward_num,video_tag,video_length,created_at]
    df2.loc[up_id] = [up_id,up_video_num,up_follow_num,up_like_num,up_playback_num]
    # 爬取过程中给予一定提示,提示程序的正常运行
    print(str(count) + " " + base_url + " is finished......", )
    count += 1
    # 休眠减少爬取频率，遵照爬取规范，减少被封禁ip的可能
    time.sleep(3)

# 利用pandas对应的模块进行数据框到excel数据的转换
writer = pd.ExcelWriter("test.xlsx")
# index_label 确认索引可以有一个名字标识
df1.to_excel(writer,"sheet1",index_label="aid")
df2.to_excel(writer,"sheet2",index=False)
writer.save()

