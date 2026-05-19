"""
新闻资讯数据源 — 东财7x24 + 财联社快讯 + 东财搜索

无认证，纯 HTTP 请求
"""

import requests
import json
import re


_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}
_PROXIES = {'http': None, 'https': None}


def get_eastmoney_7x24(page_size=50):
    """
    东方财富 7x24 快讯

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '东财7x24'}]
    """
    url = (
        f"https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
        f"?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize={page_size}"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10, proxies=_PROXIES)
    data = r.json()

    items = data.get('data', []) or []
    rows = []
    for item in items:
        rows.append({
            'time': item.get('showTime', '') or item.get('pubTime', ''),
            'title': item.get('title', ''),
            'content': item.get('digest', '') or item.get('content', ''),
            'source': '东财7x24',
        })

    return rows


def get_cailianshe(page_size=30):
    """
    财联社电报快讯

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '财联社'}]
    """
    url = (
        f"https://www.cls.cn/nodeapi/telegraphList"
        f"?app=CailianpressWeb&os=web&sv=8.4.6&rn={page_size}"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10, proxies=_PROXIES)
    data = r.json()

    items = data.get('data', {}).get('roll_data', []) or []
    rows = []
    for item in items:
        # 财联社时间戳是毫秒
        ts = item.get('ctime', 0)
        time_str = ''
        if ts:
            from datetime import datetime
            time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

        content = item.get('content', '') or item.get('brief', '') or ''
        # 去除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)

        rows.append({
            'time': time_str,
            'title': item.get('title', '') or content[:30],
            'content': content,
            'source': '财联社',
        })

    return rows


def get_eastmoney_search(keyword, count=10):
    """
    东方财富搜索 (JSONP 格式)

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'url': ..., 'source': '东方财富'}]
    """
    import urllib.parse
    param = json.dumps({
        "uid": "",
        "keyword": keyword,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": "default",
                "pageIndex": 1,
                "pageSize": count,
                "preTag": "",
                "postTag": "",
            }
        }
    })
    url = f"https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param={urllib.parse.quote(param)}"

    r = requests.get(url, headers=_HEADERS, timeout=10, proxies=_PROXIES)
    text = r.text

    # 解析 JSONP: jQuery({...})
    m = re.search(r'jQuery\((.*)\)', text, re.DOTALL)
    if not m:
        return []

    data = json.loads(m.group(1))
    result = data.get('result', None)
    if result is None or not isinstance(result, dict):
        return []
    cms = result.get('cmsArticleWebOld', None)
    if cms is None or not isinstance(cms, dict):
        return []
    articles = cms.get('list', []) or []

    rows = []
    for item in articles:
        title = item.get('title', '')
        title = re.sub(r'<[^>]+>', '', title)
        content = item.get('content', '') or item.get('mediaName', '')
        content = re.sub(r'<[^>]+>', '', content)

        rows.append({
            'time': item.get('date', ''),
            'title': title,
            'content': content[:200],
            'url': item.get('url', ''),
            'source': '东方财富',
        })

    return rows


def get_all_news(keyword=None, page_size=30):
    """
    聚合所有新闻源

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': ...}]
    按时间降序排序
    """
    results = []

    for name, fn in [('东财7x24', get_eastmoney_7x24), ('财联社', get_cailianshe)]:
        try:
            items = fn(page_size=page_size)
            results.extend(items)
        except Exception:
            pass

    results.sort(key=lambda x: x.get('time', ''), reverse=True)
    return results
