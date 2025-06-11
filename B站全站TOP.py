import requests
import pandas as pd
import datetime
from loguru import logger

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

def parse():
        data = AllStation(0, "all")
        save_to_csv(data, f"B站全站TOP100.csv")
        logger.info(f"保存数据到csv文件：B站全站TOP100.csv")

def AllStation(tid, rank_type):
    url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    params = {
        'rid': tid,
        'type': 'all',
    }
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
    df = pd.DataFrame(data)
    df.to_csv(csv_name, index=False, encoding="utf_8_sig")


if __name__ == '__main__':
    parse()






