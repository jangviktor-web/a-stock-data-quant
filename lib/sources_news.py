"""
新闻资讯数据源 — 新浪财经 + 东财搜索 + akshare 个股新闻

无认证，纯 HTTP 请求
"""

import requests
import json
import re
from datetime import datetime


_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def _session():
    """创建绕过环境代理的 Session"""
    s = requests.Session()
    s.trust_env = False
    return s


def get_sina_finance(page_size=30):
    """
    新浪财经 7x24 快讯

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '新浪财经'}]
    """
    url = (
        f"https://feed.mix.sina.com.cn/api/roll/get"
        f"?pageid=153&lid=2516&k=&num={page_size}&page=1"
    )
    r = _session().get(url, headers=_HEADERS, timeout=10)
    data = r.json()

    items = data.get('result', {}).get('data', []) or []
    rows = []
    for item in items:
        ts = int(item.get('ctime', 0) or 0)
        time_str = ''
        if ts:
            time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

        title = item.get('title', '') or ''
        content = item.get('intro', '') or item.get('summary', '') or title
        content = re.sub(r'<[^>]+>', '', content)

        rows.append({
            'time': time_str,
            'title': re.sub(r'<[^>]+>', '', title),
            'content': content[:300],
            'source': '新浪财经',
        })

    return rows


def get_eastmoney_7x24(page_size=50):
    """
    东方财富 7x24 快讯 (备用，可能不稳定)

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '东财7x24'}]
    """
    url = (
        f"https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
        f"?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize={page_size}"
    )
    r = _session().get(url, headers=_HEADERS, timeout=10)
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


def get_eastmoney_stock_news(code, page_size=10):
    """
    东财个股新闻 (via akshare)

    Parameters
    ----------
    code : str - 纯数字股票代码

    Returns
    -------
    list of dict
    """
    try:
        import akshare as ak
        df = ak.stock_news_em(symbol=code)
        if df is None or df.empty:
            return []
        rows = []
        for _, r in df.head(page_size).iterrows():
            rows.append({
                'time': str(r.get('发布时间', '')),
                'title': str(r.get('新闻标题', '')),
                'content': str(r.get('新闻内容', ''))[:300],
                'source': str(r.get('文章来源', '')),
            })
        return rows
    except Exception:
        return []


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

    r = _session().get(url, headers=_HEADERS, timeout=10)
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

    for name, fn in [('新浪财经', get_sina_finance), ('东财7x24', get_eastmoney_7x24)]:
        try:
            items = fn(page_size=page_size)
            results.extend(items)
        except Exception:
            pass

    results.sort(key=lambda x: x.get('time', ''), reverse=True)
    return results
