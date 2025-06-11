import time
import requests     # 发送请求
import pandas as pd  # 存取csv
import jsonpath     # json解析
import datetime     # 时间操作
from loguru import logger # 日志操作

"""
目标网址：https://www.bilibili.com/v/popular/rank/all/
csv数据格式：标题 链接 作者 分类 发布时间 视频时长 播放数 弹幕数 回复数 点赞数 投币数 分享数 点赞数 不喜欢数 发布位置
"""

# 所有分类
categorys = [{
    "name": "全站",
    "tid": 0,
    "slug": "all"
}, {
    "name": "番剧",
    "type": "bangumi",
    "tid": 13,
    "slug": "bangumi",
    "season_type": 1
}, {
    "name": "国产动画",
    "type": "bangumi",
    "tid": 168,
    "slug": "guochan",
    "season_type": 4
}, {
    "name": "国创相关",
    "tid": 168,
    "slug": "guochuang"
}, {
    "name": "纪录片",
    "type": "cinema",
    "slug": "documentary",
    "tid": 177,
    "season_type": 3
}, {
    "name": "动画",
    "tid": 1,
    "slug": "douga"
}, {
    "name": "音乐",
    "tid": 3,
    "slug": "music"
}, {
    "name": "舞蹈",
    "tid": 129,
    "slug": "dance"
}, {
    "name": "游戏",
    "tid": 4,
    "slug": "game"
}, {
    "name": "知识",
    "tid": 36,
    "slug": "knowledge"
}, {
    "name": "科技",
    "tid": 188,
    "slug": "tech"
}, {
    "name": "运动",
    "tid": 234,
    "slug": "sports"
}, {
    "name": "汽车",
    "tid": 223,
    "slug": "car"
}, {
    "name": "生活",
    "tid": 160,
    "slug": "life"
}, {
    "name": "美食",
    "tid": 211,
    "slug": "food"
}, {
    "name": "动物圈",
    "tid": 217,
    "slug": "animal"
}, {
    "name": "鬼畜",
    "tid": 119,
    "slug": "kichiku"
}, {
    "name": "时尚",
    "tid": 155,
    "slug": "fashion"
}, {
    "name": "娱乐",
    "tid": 5,
    "slug": "ent"
}, {
    "name": "影视",
    "tid": 181,
    "slug": "cinephile"
}, {
    "name": "电影",
    "type": "cinema",
    "slug": "movie",
    "tid": 23,
    "season_type": 2
}, {
    "name": "电视剧",
    "type": "cinema",
    "slug": "tv",
    "tid": 11,
    "season_type": 5
}, {
    "name": "综艺",
    "type": "cinema",
    "slug": "variety",
    "season_type": 7
}, {
    "name": "原创",
    "slug": "origin",
    "tid": 0,
    "rank_type": "origin"
}, {
    "name": "新人",
    "slug": "rookie",
    "tid": 0,
    "rank_type": "rookie"
}]
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

def parse():
    for category in categorys:
        season_type = category.get("season_type")   # 类型
        name = category.get("name")     # 分类名
        logger.info(f"开始爬取：{name}")
        if "番剧" == name:
            # 番剧
            data = parse_fanju(season_type)
        elif season_type:
            # 国产动画、纪录片、电影、电视剧、综艺
            data = parse1(season_type)
        else:
            # 全站、动画、音乐、舞蹈、游戏、知识、科技、运动、汽车、生活、美食、动物圈、鬼畜、时尚、娱乐、影视
            # 国创相关、原创、新人
            data = parse2(category.get("tid"), category.get("rank_type"))
        logger.info(f"数据获取成功：{data}")
        # 保存数据
        save_to_csv(data, f"B站TOP100-{name}.csv")
        logger.info(f"保存数据到csv文件：B站TOP100-{name}.csv")
        logger.info("------------------------------------")
    time.sleep(2)

def parse_fanju(season_type):
    """
    爬取番剧
    @param season_type: 类型
    @return:
    """
    url = 'https://api.bilibili.com/pgc/web/rank/list'
    params = {
        'day': '3',
        'season_type': season_type
    }
    resp = requests.get(url, params=params, headers=headers)
    result = resp.json()

    # 解析数据
    rank_list = result["result"]["list"]
    title_list = []
    url_list = []
    rating_list = []
    desc_list = []
    play_list = []
    view_list = []
    follow_list = []
    danmaku_list = []
    for rank in rank_list:
        title_list.append(rank.get("title"))  # 标题
        url_list.append(rank.get("url"))  # 链接
        rating_list.append(rank["rating"])  # 评分
        desc_list.append(rank["new_ep"]["index_show"])  # 更新至多少集
        play_list.append(rank["icon_font"]["text"])  # 播放数
        stat = rank["stat"]
        view_list.append(stat["view"])  # 播放数
        follow_list.append(stat["follow"])  # 关注数
        danmaku_list.append(stat["danmaku"])  # 弹幕数

    return {
        "标题": title_list,
        "链接": url_list,
        "评分": rating_list,
        "描述": desc_list,
        "播放数1": play_list,
        "播放数": view_list,
        "关注数": follow_list,
        "弹幕数": danmaku_list,
    }

def parse1(season_type):
    """
    爬取：国产动画、纪录片、电影、电视剧、综艺
    @param season_type: 类型
    @return:
    """
    url = 'https://api.bilibili.com/pgc/season/rank/web/list'
    params = {
        'day': '3',
        'season_type': season_type,
    }
    resp = requests.get(url, params=params, headers=headers)
    result = resp.json()

    # 解析数据
    rank_list = result["data"]["list"]
    title_list = []
    url_list = []
    rating_list = []
    desc_list = []
    play_list = []
    view_list = []
    follow_list = []
    danmaku_list = []
    for rank in rank_list:
        title_list.append(rank.get("title"))  # 标题
        url_list.append(rank.get("url"))  # 链接
        rating_list.append(rank["rating"])  # 评分
        desc_list.append(rank["desc"])  # 更新至多少集
        play_list.append(rank["icon_font"]["text"])  # 播放数
        stat = rank["stat"]
        view_list.append(stat["view"])  # 播放数
        follow_list.append(stat["follow"])  # 关注数
        danmaku_list.append(stat["danmaku"])  # 弹幕数

    return {
        "标题": title_list,
        "链接": url_list,
        "评分": rating_list,
        "描述": desc_list,
        "播放数1": play_list,
        "播放数": view_list,
        "关注数": follow_list,
        "弹幕数": danmaku_list,
    }


def parse2(tid, rank_type):
    """
    爬取：全站、动画、音乐、舞蹈、游戏、知识、科技、运动、汽车、生活、美食、动物圈、鬼畜、时尚、娱乐、影视
    @param tid: id
    @param rank_type: 类型
    @return:
    """
    # 发起请求，获得数据
    url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    params = {
        'rid': tid,
        'type': 'all',
    }
    # 如果有值，则使用（针对原创、新人这2个分类）
    if rank_type:
        params['type'] = rank_type
    resp = requests.get(url, params=params, headers=headers)
    result = resp.json()

    # 解析数据：标题 链接 作者 分类 发布时间 视频时长 播放数 弹幕数 回复数 点赞数 投币数 分享数 点赞数 不喜欢数 发布位置
    rank_list = result["data"]["list"]
    title_list = []
    short_link_list = []
    author_list = []
    tname_list = []
    pubdate_list = []
    view_list = []
    danmaku_list = []
    reply_list = []
    favorite_list = []
    coin_list = []
    share_list = []
    like_list = []
    pub_location_list = []
    for rank in rank_list:
        title_list.append(rank.get("title"))    # 标题
        short_link_list.append(rank.get("short_link_v2"))  # 短链
        author_list.append(rank["owner"]["name"])  # 作者
        tname_list.append(rank["tname"])  # 分类
        pubdate = rank["pubdate"]   # 发布时间
        pubdate = datetime.datetime.fromtimestamp(pubdate)
        pubdate = pubdate.strftime('%Y-%m-%d %H:%M:%S')
        pubdate_list.append(pubdate)
        pub_location_list.append(rank.get("pub_location")) # pub_location这个键可能不存在，所以这里用get函数

        stat = rank["stat"]
        view_list.append(stat["view"])  # 播放数
        like_list.append(stat["like"])  # 点赞数
        danmaku_list.append(stat["danmaku"])  # 弹幕数
        reply_list.append(stat["reply"])  # 回复数
        favorite_list.append(stat["favorite"])  # 点赞数
        coin_list.append(stat["coin"])  # 投币数
        share_list.append(stat["share"])  # 分享数

    # jsonpath方式提取
    # title_list = jsonpath.jsonpath(rank_list, "$..title")   # 标题
    # short_link_list = jsonpath.jsonpath(rank_list, "$..short_link_v2")  # 短链
    # author_list = jsonpath.jsonpath(rank_list, "$..owner.name")  # 作者
    # tname_list = jsonpath.jsonpath(rank_list, "$..tname")  # 分类
    # pubdate_list = jsonpath.jsonpath(rank_list, "$..pubdate")  # 发布时间
    # view_list = jsonpath.jsonpath(rank_list, "$..stat.view")  # 播放数
    # danmaku_list = jsonpath.jsonpath(rank_list, "$..stat.danmaku")  # 弹幕数
    # reply_list = jsonpath.jsonpath(rank_list, "$..stat.reply")  # 回复数
    # favorite_list = jsonpath.jsonpath(rank_list, "$..stat.favorite")  # 点赞数
    # coin_list = jsonpath.jsonpath(rank_list, "$..stat.coin")  # 投币数
    # share_list = jsonpath.jsonpath(rank_list, "$..stat.share")  # 分享数
    # like_list = jsonpath.jsonpath(rank_list, "$..stat.like")  # 点赞数
    # pub_location_list = jsonpath.jsonpath(rank_list, "$..pub_location")  # 发布位置
    # print(len(title_list))
    # print(len(pubdate_list))
    # print(len(view_list))
    # print(len(danmaku_list))
    # print(len(reply_list))
    # print(len(favorite_list))
    # print(len(coin_list))
    # print(len(share_list))
    # print(len(like_list))
    # print(len(pub_location_list))

    return {
        "标题": title_list,
        "作者": author_list,
        "链接": short_link_list,
        "分类": tname_list,
        "发布时间": pubdate_list,
        "播放数": view_list,
        "点赞数": like_list,
        "弹幕数": danmaku_list,
        "回复数": reply_list,
        "收藏数": favorite_list,
        "投币数": coin_list,
        "分享数": share_list,
        "发布位置": pub_location_list
    }


def save_to_csv(data, csv_name):
    """
    数据保存到csv
    @param dms: 弹幕列表数据
    @param csv_name: csv文件名字
    @return:
    """
    # 把列表转换成 dataframe
    df = pd.DataFrame(data)
    # 写入数据
    df.to_csv(csv_name, index=False, encoding="utf_8_sig")


if __name__ == '__main__':
    parse()






