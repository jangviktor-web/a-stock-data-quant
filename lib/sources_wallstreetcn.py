"""
华尔街见闻数据源模块
移植自 go-stock (github.com/ArvinLovegood/go-stock) wallstreetcn_api.go
数据源：api-one-wscn.awtmt.com

功能：
- 全球7x24快讯（多频道：A股/美股/港股/外汇/商品/黄金/原油/债券）
- 财经日历（经济数据发布）
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

_BASE_URL = "https://api-one-wscn.awtmt.com/apiv1"

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Referer': 'https://wallstreetcn.com/',
    'Accept': 'application/json',
    'x-client-type': 'pc',
    'x-ivanka-app': 'wscn|web|0.40.40|0.0|0',
}

# 频道映射
CHANNELS = {
    'global-channel': '全球7x24',
    'a-stock-channel': 'A股',
    'us-stock-channel': '美股',
    'hk-stock-channel': '港股',
    'forex-channel': '外汇',
    'commodity-channel': '商品',
    'goldc-channel': '黄金',
    'oil-channel': '原油',
    'bond-channel': '债券',
    'crypto-channel': '加密货币',
    'xgb-channel': '新股',
}


def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()


def get_lives(channel: str = 'global-channel', limit: int = 20) -> List[Dict]:
    """
    获取华尔街见闻快讯

    参数:
        channel: 频道名（见 CHANNELS）
        limit: 获取条数（最大50）

    返回:
        [{'title': 标题, 'content': 内容, 'time': 时间戳, 'uri': 链接,
          'source': 来源, 'is_important': 是否重要}, ...]
    """
    if channel not in CHANNELS:
        channel = 'global-channel'

    limit = max(1, min(limit, 50))

    url = f"{_BASE_URL}/content/lives"
    params = {
        'channel': channel,
        'client': 'pc',
        'limit': str(limit),
        'first_page': 'true',
        'accept': 'live,vip-live',
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取华尔街见闻快讯失败: {e}")
        return []

    if data.get('code') != 20000:
        print(f"  [WARN] 接口返回异常: code={data.get('code')}, msg={data.get('message')}")
        return []

    items = data.get('data', {}).get('items', [])
    results = []

    for item in items:
        content = _safe_str(item.get('content_text'))
        if not content:
            # 从HTML内容提取
            content = _safe_str(item.get('content'))
            import re
            content = re.sub(r'<[^>]+>', '', content).strip()

        if not content:
            continue

        display_time = item.get('display_time', 0)
        time_str = datetime.fromtimestamp(display_time).strftime('%Y-%m-%d %H:%M:%S') if display_time else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'content': content,
            'time': display_time,
            'time_str': time_str,
            'uri': _safe_str(item.get('uri')),
            'source': f"华尔街见闻-{CHANNELS.get(channel, '全球')}",
            'is_important': item.get('score', 0) > 1 or item.get('is_calendar', False),
            'author': _safe_str((item.get('author') or {}).get('display_name')),
        })

    return results


def get_calendar(channel: str = 'global-channel', limit: int = 20) -> List[Dict]:
    """
    获取财经日历

    参数:
        channel: 频道名
        limit: 获取条数

    返回:
        [{'title': 事件, 'country': 国家, 'time': 时间, 'importance': 重要性,
          'actual': 实际值, 'forecast': 预测值, 'previous': 前值}, ...]
    """
    if channel not in CHANNELS:
        channel = 'global-channel'

    url = f"{_BASE_URL}/calendar"
    params = {
        'channel': channel,
        'client': 'pc',
        'limit': str(limit),
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取财经日历失败: {e}")
        return []

    if data.get('code') != 20000:
        return []

    items = data.get('data', {}).get('items', [])
    results = []

    for item in items:
        pub_date = item.get('public_date', 0)
        time_str = datetime.fromtimestamp(pub_date).strftime('%Y-%m-%d %H:%M') if pub_date else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'event': _safe_str(item.get('event')),
            'country': _safe_str(item.get('country')),
            'time': pub_date,
            'time_str': time_str,
            'importance': item.get('importance', 0),
            'actual': _safe_str(item.get('actual')),
            'forecast': _safe_str(item.get('forecast')),
            'previous': _safe_str(item.get('previous')),
            'period': _safe_str(item.get('period')),
        })

    return results


def format_lives(results: List[Dict], channel: str = 'global-channel') -> str:
    """格式化快讯输出"""
    if not results:
        return "未获取到华尔街见闻快讯"

    channel_name = CHANNELS.get(channel, '全球')
    lines = [
        "=" * 70,
        f"  华尔街见闻快讯 - {channel_name}",
        "=" * 70,
    ]

    for i, item in enumerate(results, 1):
        marker = "🔴" if item.get('is_important') else "  "
        title = item.get('title', '')
        content = item.get('content', '')

        if title:
            lines.append(f"\n{marker} [{item.get('time_str', '')}] {title}")
        if content:
            # 截断过长内容
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"   {content}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def format_calendar(results: List[Dict]) -> str:
    """格式化财经日历输出"""
    if not results:
        return "未获取到财经日历数据"

    lines = [
        "=" * 80,
        "  财经日历",
        "=" * 80,
        f"  {'时间':<16} {'国家':<6} {'事件':<20} {'重要性':<6} {'实际':<10} {'预测':<10} {'前值':<10}",
        "-" * 80,
    ]

    for item in results:
        imp = "⭐" * item.get('importance', 0)
        lines.append(
            f"  {item.get('time_str', ''):<16} "
            f"{item.get('country', ''):<6} "
            f"{item.get('title', '')[:18]:<20} "
            f"{imp:<6} "
            f"{item.get('actual', '-'):<10} "
            f"{item.get('forecast', '-'):<10} "
            f"{item.get('previous', '-'):<10}"
        )

    lines.append("=" * 80)
    return "\n".join(lines)
