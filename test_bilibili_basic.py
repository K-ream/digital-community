#!/usr/bin/env python3
"""
简化版 bilibili_chart 测试脚本
测试基本的网络请求和数据获取功能
"""
import json
import requests
from datetime import datetime

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def test_bilibili_api():
    """测试 B站番剧排行榜 API"""
    print("=" * 60)
    print("测试 B站番剧排行榜 API")
    print("=" * 60)
    
    try:
        url = 'https://api.bilibili.com/pgc/season/index/result'
        params = {
            'season_version': -1,
            'is_finish': -1,
            'copyright': -1,
            'season_status': -1,
            'year': -1,
            'style_id': -1,
            'order': 3,
            'st': 4,
            'sort': 0,
            'page': 1,
            'season_type': 4,
            'pagesize': 5,  # 只获取前5条测试
            'type': 1
        }
        
        print(f"\n请求 URL: {url}")
        print(f"参数: {json.dumps(params, indent=2)}")
        
        response = requests.get(url, headers=HEADER, params=params, timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'list' in data['data']:
                items = data['data']['list']
                print(f"\n成功获取 {len(items)} 条数据")
                print("\n前3条番剧信息：")
                for i, item in enumerate(items[:3], 1):
                    print(f"\n{i}. {item.get('title', 'N/A')}")
                    print(f"   链接: {item.get('link', 'N/A')}")
                    print(f"   追番数: {item.get('stat', {}).get('favorites', 'N/A')}")
                    print(f"   播放数: {item.get('stat', {}).get('view', 'N/A')}")
                return True
            else:
                print("\n⚠️ 返回数据格式异常")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return False
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求异常: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 其他异常: {e}")
        return False


def test_bilibili_manga_api():
    """测试 B站漫画排行榜 API"""
    print("\n" + "=" * 60)
    print("测试 B站漫画排行榜 API")
    print("=" * 60)
    
    try:
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/GetRankInfo'
        params = {'device': 'pc', 'platform': 'web', 'nov': 24}
        payload = {'id': 7}
        
        print(f"\n请求 URL: {url}")
        print(f"参数: {params}")
        print(f"数据: {payload}")
        
        response = requests.post(url, headers=HEADER, params=params, json=payload, timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'list' in data['data']:
                items = data['data']['list']
                print(f"\n成功获取 {len(items)} 条漫画数据")
                print("\n前3条漫画信息：")
                for i, item in enumerate(items[:3], 1):
                    print(f"\n{i}. {item.get('title', 'N/A')}")
                    print(f"   作者: {item.get('author', 'N/A')}")
                    print(f"   排名: {item.get('last_rank', 'N/A')}")
                    print(f"   更新: {item.get('last_ord', 'N/A')} 话")
                return True
            else:
                print("\n⚠️ 返回数据格式异常")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                return False
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求异常: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 其他异常: {e}")
        return False


if __name__ == '__main__':
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 环境: Python 3.x with requests")
    
    result1 = test_bilibili_api()
    result2 = test_bilibili_manga_api()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"番剧 API: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"漫画 API: {'✅ 成功' if result2 else '❌ 失败'}")
    
    if result1 and result2:
        print("\n✅ 所有测试通过！基本网络请求功能正常。")
        print("\n⚠️ 注意：完整的 bilibili_chart.py 脚本需要以下依赖：")
        print("   - mur-data-common (腾讯内部库)")
        print("   - 数据湖配置和权限")
        print("   - beautifulsoup4, pandas, dpath 等第三方库")
    else:
        print("\n❌ 部分测试失败，请检查网络连接或 API 变更。")
