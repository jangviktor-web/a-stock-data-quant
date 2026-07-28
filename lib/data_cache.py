"""
数据缓存模块 - 参考 stock-quant 的 CSV 数据管理
将行情数据缓存到本地 CSV，支持离线回测
"""

import os
import time
import hashlib
import json
import pandas as pd


# TTL 常量 (单位: 分钟)
TTL_REALTIME = 5      # 实时行情 5分钟
TTL_INTRADAY = 30     # 盘中数据(涨停池/资金流) 30分钟
TTL_DAILY = 240       # 日级数据(宏观/估值) 4小时
TTL_WEEKLY = 1440     # 周级数据 24小时


def _get_cache_dir():
    """获取缓存目录"""
    from lib.settings import get
    cache_dir = get('cache_dir', 'cache')
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _cache_key(code, count, period, end=''):
    """生成缓存文件名"""
    raw = f"{code}_{count}_{period}_{end}"
    h = hashlib.md5(raw.encode()).hexdigest()[:12]
    safe_code = code.replace('.', '_').replace('/', '_')
    return f"{safe_code}_{period}_{h}.csv"


def get_cached(code, count, period, end=''):
    """
    尝试从缓存获取数据

    Returns
    -------
    DataFrame or None - 缓存命中返回 DataFrame，否则返回 None
    """
    from lib.settings import get

    if not get('cache_enabled', True):
        return None

    cache_dir = _get_cache_dir()
    filename = _cache_key(code, count, period, end)
    filepath = os.path.join(cache_dir, filename)

    if not os.path.exists(filepath):
        return None

    # 检查缓存是否过期
    ttl_hours = get('cache_ttl_hours', 4)
    file_age = time.time() - os.path.getmtime(filepath)
    if file_age > ttl_hours * 3600:
        return None

    try:
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def save_cache(code, count, period, end, df):
    """保存数据到缓存"""
    from lib.settings import get

    if not get('cache_enabled', True):
        return

    if df is None or df.empty:
        return

    cache_dir = _get_cache_dir()
    filename = _cache_key(code, count, period, end)
    filepath = os.path.join(cache_dir, filename)

    try:
        df.to_csv(filepath)
    except Exception:
        pass  # 缓存失败不影响主流程


def cached_fetch(code, count, period, end='', fetch_func=None):
    """
    带缓存的数据获取

    Parameters
    ----------
    code : str - 股票代码
    count : int - 数据条数
    period : str - 周期
    end : str - 结束日期
    fetch_func : callable - 实际获取数据的函数 (code, count, period, end) -> DataFrame

    Returns
    -------
    DataFrame
    """
    # 先查缓存
    df = get_cached(code, count, period, end)
    if df is not None:
        return df

    # 缓存未命中，调用实际获取函数
    if fetch_func is None:
        from lib.ashare import get_price
        fetch_func = lambda c, n, p, e: get_price(c, end_date=e or '', count=n, frequency=p)

    df = fetch_func(code, count, period, end)

    # 保存缓存
    if df is not None and not df.empty:
        save_cache(code, count, period, end, df)

    return df


# ============================================================
# JSON 通用缓存层 (资金流/涨停池/宏观数据/北向资金等非DataFrame数据)
# ============================================================

def _json_cache_key(category: str, key: str) -> str:
    """生成 JSON 缓存文件名"""
    h = hashlib.md5(key.encode()).hexdigest()[:10]
    return f"{category}_{h}.json"


def get_json_cached(category: str, key: str, ttl_minutes: int = 60):
    """
    尝试从 JSON 缓存获取数据

    Parameters
    ----------
    category : str - 数据类别 (如 'fund_flow', 'zt_pool', 'macro', 'north_flow')
    key : str - 缓存键 (如股票代码、日期等)
    ttl_minutes : int - 缓存有效期(分钟)

    Returns
    -------
    dict/list or None - 缓存命中返回反序列化数据，否则返回 None
    """
    from lib.settings import get

    if not get('cache_enabled', True):
        return None

    cache_dir = _get_cache_dir()
    filename = _json_cache_key(category, key)
    filepath = os.path.join(cache_dir, filename)

    if not os.path.exists(filepath):
        return None

    # 检查缓存是否过期
    file_age = time.time() - os.path.getmtime(filepath)
    if file_age > ttl_minutes * 60:
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def save_json_cache(category: str, key: str, data):
    """
    保存数据到 JSON 缓存

    Parameters
    ----------
    category : str - 数据类别
    key : str - 缓存键
    data : dict/list - 可 JSON 序列化的数据
    """
    from lib.settings import get

    if not get('cache_enabled', True):
        return

    if data is None:
        return

    cache_dir = _get_cache_dir()
    filename = _json_cache_key(category, key)
    filepath = os.path.join(cache_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass  # 缓存失败不影响主流程


def cached_json_fetch(category: str, key: str, fetch_func, ttl_minutes: int = 60):
    """
    带 JSON 缓存的数据获取 (主入口)

    Parameters
    ----------
    category : str - 数据类别 (如 'fund_flow', 'zt_pool', 'macro', 'north_flow')
    key : str - 缓存键
    fetch_func : callable - 实际获取数据的函数 () -> dict/list
    ttl_minutes : int - 缓存有效期(分钟)

    Returns
    -------
    dict/list or None
    """
    # 先查缓存
    data = get_json_cached(category, key, ttl_minutes)
    if data is not None:
        return data

    # 缓存未命中，调用实际获取函数
    data = fetch_func()

    # 保存缓存
    if data is not None:
        save_json_cache(category, key, data)

    return data


def clear_cache(older_than_hours=None):
    """
    清理缓存文件

    Parameters
    ----------
    older_than_hours : int or None - 只清理超过指定小时的文件，None 则清全部
    """
    cache_dir = _get_cache_dir()
    if not os.path.exists(cache_dir):
        return 0

    count = 0
    now = time.time()
    for f in os.listdir(cache_dir):
        if not (f.endswith('.csv') or f.endswith('.json')):
            continue
        fp = os.path.join(cache_dir, f)
        if older_than_hours is not None:
            age = now - os.path.getmtime(fp)
            if age < older_than_hours * 3600:
                continue
        os.remove(fp)
        count += 1

    return count


def cache_stats():
    """缓存统计信息"""
    cache_dir = _get_cache_dir()
    if not os.path.exists(cache_dir):
        return {'files': 0, 'size_kb': 0, 'json_files': 0, 'json_size_kb': 0}

    csv_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
    csv_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in csv_files)

    json_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    json_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in json_files)

    return {
        'files': len(csv_files),
        'size_kb': round(csv_size / 1024, 1),
        'json_files': len(json_files),
        'json_size_kb': round(json_size / 1024, 1),
    }
