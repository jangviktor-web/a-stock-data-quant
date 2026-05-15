"""
实时行情数据 — 腾讯/东方财富/新浪 多数据源

基于 stock-api (github.com/zhangxiangliang/stock-api) 提取的 API 协议
支持：A股实时报价、股票搜索、批量查询

数据源:
  - 腾讯: qt.gtimg.cn (GBK, ~分隔)
  - 东方财富: push2.eastmoney.com (JSON)
  - 新浪:hq.sinajs.cn (GBK, 分隔)

依赖: requests (无 akshare 依赖，纯 HTTP 请求)
"""

import re
import requests

# ── 编码工具 ──────────────────────────────────────────────

def _decode_gbk(content):
    """GBK 字节解码"""
    if isinstance(content, bytes):
        for enc in ('gbk', 'gb2312', 'utf-8', 'latin-1'):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    return content


# ── 代码标准化 ────────────────────────────────────────────

def _normalize_code(code):
    """
    标准化股票代码 → SH/SZ + 6位数字
    支持: sh600519, SH600519, 600519, 1.600519
    """
    code = str(code).upper().strip()

    # 已是标准格式
    if re.match(r'^(SH|SZ)\d{6}$', code):
        return code

    # 腾讯格式: sh600519 / sz000858
    m = re.match(r'^(SH|SZ)(\d{6})$', code)
    if m:
        return m.group(1) + m.group(2)

    # 东方财富格式: 1.600519 / 0.000858
    m = re.match(r'^([01])\.(\d{6})$', code)
    if m:
        prefix = 'SH' if m.group(1) == '1' else 'SZ'
        return prefix + m.group(2)

    # 纯数字
    if re.match(r'^\d{6}$', code):
        prefix = 'SH' if code.startswith(('6', '9')) else 'SZ'
        return prefix + code

    return code


def _to_tencent_code(code):
    """转腾讯格式: sh600519"""
    std = _normalize_code(code)
    return std.lower()


def _to_eastmoney_secid(code):
    """转东方财富格式: 1.600519"""
    std = _normalize_code(code)
    if std.startswith('SH'):
        return '1.' + std[2:]
    return '0.' + std[2:]


# ── 腾讯数据源 ────────────────────────────────────────────

def _fetch_tencent(codes):
    """
    腾讯实时行情 (qt.gtimg.cn)
    返回: [{'code','name','now','percent','high','low','yesterday'}, ...]
    """
    if isinstance(codes, str):
        codes = [codes]

    tencent_codes = [_to_tencent_code(c) for c in codes]
    url = f"https://qt.gtimg.cn/q={','.join(tencent_codes)}"

    try:
        r = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        text = _decode_gbk(r.content)
    except Exception as e:
        return [{'error': f'腾讯接口失败: {e}'}]

    results = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or '=' not in line:
            continue

        # 格式: v_sh600519="1~贵州茅台~600519~1332.95~..."
        parts = line.split('"')
        if len(parts) < 2:
            continue

        code_key = parts[0].split('_')[-1].replace('v_', '').rstrip('=')
        fields = parts[1].split('~')

        if len(fields) < 35:
            continue

        try:
            name = fields[1]
            now = float(fields[3]) if fields[3] else 0
            yesterday = float(fields[4]) if fields[4] else 0
            high = float(fields[33]) if fields[33] else 0
            low = float(fields[34]) if fields[34] else 0
            change = (now - yesterday) / yesterday * 100 if yesterday else 0
            volume = float(fields[36]) if len(fields) > 36 and fields[36] else 0  # 成交量(手)
            amount = float(fields[37]) if len(fields) > 37 and fields[37] else 0   # 成交额(元)

            # 时间字段
            time_str = fields[30] if len(fields) > 30 else ''

            std_code = _normalize_code(code_key)

            results.append({
                'code': std_code,
                'name': name,
                'now': now,
                'percent': round(change, 2),
                'high': high,
                'low': low,
                'yesterday': yesterday,
                'time': time_str,
            })
        except (ValueError, IndexError):
            continue

    return results


def _search_tencent(keyword):
    """腾讯股票搜索 (smartbox.gtimg.cn)"""
    url = f"https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={keyword}"

    try:
        r = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        text = _decode_gbk(r.content)
    except Exception:
        return []

    # 格式: v_hint="sz~000858~五粮液^sh~600519~贵州茅台"
    m = re.search(r'v_hint="([^"]*)"', text)
    if not m:
        return []

    results = []
    for item in m.group(1).split('^'):
        parts = item.split('~')
        if len(parts) >= 3:
            market, code, name = parts[0], parts[1], parts[2]
            prefix = market.upper()
            results.append({
                'code': f'{prefix}{code}',
                'name': name,
            })

    return results


# ── 东方财富数据源 ────────────────────────────────────────

def _fetch_eastmoney(codes):
    """
    东方财富实时行情 (push2.eastmoney.com)
    返回: [{'code','name','now','percent','high','low','yesterday'}, ...]
    """
    if isinstance(codes, str):
        codes = [codes]

    secids = ','.join(_to_eastmoney_secid(c) for c in codes)
    fields = 'f12,f14,f2,f3,f15,f16,f18,f6,f7,f10,f170,f43,f44,f45,f46,f60'
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids={secids}&fields={fields}"

    headers = {
        'Accept': 'application/json',
        'Referer': 'https://quote.eastmoney.com/',
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        data = r.json()
    except Exception as e:
        return [{'error': f'东方财富接口失败: {e}'}]

    diff = data.get('data', {}).get('diff', {})
    if not diff:
        return []

    items = diff.values() if isinstance(diff, dict) else diff
    results = []

    for item in items:
        try:
            def _v(key):
                val = item.get(key)
                if val is None or val == '-':
                    return 0
                return float(val)

            std_code = _normalize_code(str(item.get('f12', '')))
            results.append({
                'code': std_code,
                'name': str(item.get('f14', '')),
                'now': _v('f43') or _v('f2'),
                'percent': _v('f170') or _v('f3'),
                'high': _v('f44') or _v('f15'),
                'low': _v('f45') or _v('f16'),
                'yesterday': _v('f60') or _v('f18'),
                'change': _v('f6'),
                'amplitude': _v('f7'),
                'turnover_rate': _v('f10'),
            })
        except (ValueError, TypeError):
            continue

    return results


def _search_eastmoney(keyword):
    """东方财富搜索 (searchapi.eastmoney.com)"""
    token = 'D43BF722C8E33BDC906FB84D85E326E8'
    url = f"https://searchapi.eastmoney.com/api/suggest/get?input={keyword}&type=14&token={token}"

    headers = {'Referer': 'https://quote.eastmoney.com/'}

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        data = r.json()
    except Exception:
        return []

    items = data.get('QuotationCodeTable', {}).get('Data', [])
    results = []
    for item in items:
        code = item.get('Code', '')
        mkt = item.get('MktNum', '')
        name = item.get('Name', '')
        if code:
            prefix = 'SH' if mkt == '1' else 'SZ'
            results.append({'code': f'{prefix}{code}', 'name': name})

    return results


# ── 对外接口 ──────────────────────────────────────────────

_SOURCE_MAP = {
    'tencent': (_fetch_tencent, _search_tencent),
    'eastmoney': (_fetch_eastmoney, _search_eastmoney),
}


def get_realtime(codes, source='auto'):
    """
    获取股票实时行情

    Parameters
    ----------
    codes : str | list - 股票代码，如 'sh600519' 或 ['sh600519','sz000858']
    source : str - 数据源 ('auto'|'tencent'|'eastmoney')

    Returns
    -------
    list of dict: [{'code','name','now','percent','high','low','yesterday'}, ...]
    """
    if isinstance(codes, str):
        codes = [c.strip() for c in codes.split(',') if c.strip()]

    # auto: 优先腾讯，失败则降级东方财富
    if source == 'auto':
        results = _fetch_tencent(codes)
        if results and 'error' not in results[0]:
            return results
        results = _fetch_eastmoney(codes)
        return results

    fetch_fn = _SOURCE_MAP.get(source, (_fetch_tencent,))[0]
    return fetch_fn(codes)


def search_stock(keyword, source='auto'):
    """
    搜索股票

    Parameters
    ----------
    keyword : str - 关键词（名称或代码）
    source : str - 数据源 ('auto'|'tencent'|'eastmoney')

    Returns
    -------
    list of dict: [{'code', 'name'}, ...]
    """
    if source == 'auto':
        results = _search_eastmoney(keyword)
        if results:
            return results
        return _search_tencent(keyword)

    search_fn = _SOURCE_MAP.get(source, (None, _search_tencent))[1]
    return search_fn(keyword)


def format_realtime(results):
    """
    格式化实时行情为可读文本
    """
    if not results:
        return "  无数据"

    lines = []
    for r in results:
        if 'error' in r:
            lines.append(f"  ❌ {r['error']}")
            continue

        name = r.get('name', '')
        code = r.get('code', '')
        now = r.get('now', 0)
        pct = r.get('percent', 0)
        high = r.get('high', 0)
        low = r.get('low', 0)
        yesterday = r.get('yesterday', 0)

        arrow = '🔴' if pct < 0 else '🟢' if pct > 0 else '⚪'
        sign = '+' if pct > 0 else ''

        vol_str = ''
        vol = r.get('volume', 0)
        if vol:
            if vol >= 10000:
                vol_str = f"  量:{vol/10000:.0f}万手"
            else:
                vol_str = f"  量:{vol:.0f}手"

        amt_str = ''
        amt = r.get('amount', 0)
        if amt:
            if amt >= 1e8:
                amt_str = f"  额:{amt/1e8:.2f}亿"
            elif amt >= 1e4:
                amt_str = f"  额:{amt/1e4:.0f}万"

        time_str = ''
        t = r.get('time', '')
        if t and ':' in str(t):
            time_str = f"  {t}"

        lines.append(f"  {arrow} {name}({code})  {now:.2f}  {sign}{pct:.2f}%  高:{high:.2f} 低:{low:.2f} 昨:{yesterday:.2f}{vol_str}{amt_str}{time_str}")

    return '\n'.join(lines)
