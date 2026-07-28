"""
东方财富妙想 (MXClaw) API 封装 — 免费 AI 金融数据接口

依赖：requests
配置：config.yaml 中设置 em_api_key，或设置环境变量 EM_API_KEY
注册：https://ai.eastmoney.com/mxClaw
"""

import json
import os
import requests

API_BASE = "https://ai-saas.eastmoney.com/proxy"

# 各功能的 API 端点
ENDPOINTS = {
    'stock_analysis': '/app-robo-advisor-api/assistant/stock-analysis',
    'fund_analysis': '/app-robo-advisor-api/assistant/fund-analysis',
    'search_data': '/b/mcp/tool/searchData',
    'select_security': '/b/mcp/tool/selectSecurity',
    'search_news': '/b/mcp/tool/searchNews',
    'write_report': '/app-robo-advisor-api/assistant/write/tracking/report',
    'ask': '/app-robo-advisor-api/assistant/ask',
    'comparable': '/app-robo-advisor-api/assistant/comparable-company-analysis',
}

TIMEOUT = 60


def _get_api_key():
    """获取 API Key：环境变量 > config.yaml"""
    key = os.environ.get('EM_API_KEY', '')
    if key:
        return key
    try:
        from lib.settings import get
        key = get('em_api_key', '')
        if key:
            return key
    except Exception:
        pass
    return ''


def is_configured():
    """是否已配置 API Key"""
    return bool(_get_api_key())


def _fix_gbk(text):
    """
    修复 API 返回的 GBK 编码中文。
    东方财富 API 的 displayData 有时返回 GBK 编码的字节序列，
    被错误解码为 latin-1/utf-8 导致乱码。
    """
    if not isinstance(text, str):
        return text

    # 检测是否是 GBK 乱码（包含大量无法显示的字符）
    garbled_count = sum(1 for c in text if ord(c) > 127 and ord(c) < 0x2E80)
    if garbled_count > len(text) * 0.1:
        try:
            # 尝试将乱码字符串按 latin-1 编码回字节，再用 GBK 解码
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            return decoded
        except Exception:
            pass

    # 检测是否包含 GBK 特征乱码模式
    if '\ufffd' in text or any(ord(c) > 0xE000 for c in text[:100]):
        try:
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            if decoded != text:
                return decoded
        except Exception:
            pass

    return text


def _call(endpoint_key, payload, extra_headers=None):
    """
    通用 API 调用

    Parameters
    ----------
    endpoint_key : str - ENDPOINTS 中的 key
    payload : dict - 请求体
    extra_headers : dict - 额外请求头

    Returns
    -------
    dict - API 响应
    """
    api_key = _get_api_key()
    if not api_key:
        return {'error': '未配置 EM_API_KEY，请在 config.yaml 中设置 em_api_key 或设置环境变量 EM_API_KEY。注册地址：https://ai.eastmoney.com/mxClaw'}

    url = API_BASE + ENDPOINTS.get(endpoint_key, '')
    headers = {
        'Content-Type': 'application/json',
        'em_api_key': api_key,
    }
    if extra_headers:
        headers.update(extra_headers)

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT,
                         proxies={'http': None, 'https': None})
        result = r.json()
        # 检查 API 层面错误
        if result.get('code') == 401 or result.get('status', 0) < 0:
            msg = result.get('message', '未知错误')
            # 修复消息中的 GBK 编码
            msg = _fix_gbk(msg)
            return {'error': f'API错误: {msg}'}
        return result
    except requests.exceptions.ConnectionError:
        return {'error': '网络连接失败，无法访问东方财富妙想 API'}
    except requests.exceptions.Timeout:
        return {'error': '请求超时，请稍后重试'}
    except Exception as e:
        return {'error': f'请求失败: {str(e)}'}


def _extract_content(result):
    """从 API 响应中提取可读内容（通用）"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    # 1. 优先提取 displayData（AI 文本回复）
    display_data = data.get('displayData', '')
    if isinstance(display_data, str) and display_data.strip():
        content = _fix_gbk(display_data.strip())
        return content, None

    if isinstance(display_data, (list, dict)):
        return json.dumps(display_data, ensure_ascii=False, indent=2), None

    # 2. 兜底字段
    for key in ('content', 'answer', 'summary'):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return _fix_gbk(val.strip()), None

    return None, 'API 返回空内容'


def _extract_ai_content(result):
    """提取 AI 文本类回复（股票诊断、问答等）— 修复 GBK"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    display_data = data.get('displayData', '')
    if isinstance(display_data, str) and display_data.strip():
        return _fix_gbk(display_data.strip()), None

    return None, 'API 返回空内容'


def _extract_select_stock(result):
    """提取选股结果（partialResults 中的 markdown 表格）"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    # partialResults 包含 markdown 表格
    partial = data.get('partialResults', '')
    if isinstance(partial, str) and partial.strip():
        content = _fix_gbk(partial.strip())
        # 补充选股条件摘要
        conditions = data.get('totalCondition', '')
        count = data.get('securityCount', 0)
        header = f"选股条件: {_fix_gbk(conditions)}\n符合条件: {count} 只\n\n"
        return header + content, None

    return None, '选股返回空结果'


def _extract_news(result):
    """提取资讯搜索结果"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    llm_resp = data.get('llmSearchResponse', {})
    news_list = llm_resp.get('data', [])

    if not news_list:
        return None, '未找到相关资讯'

    lines = []
    for i, item in enumerate(news_list[:15], 1):
        title = _fix_gbk(item.get('title', ''))
        date = item.get('date', '')
        source = item.get('source', '')
        url = item.get('jumpUrl', '')
        content = _fix_gbk(item.get('content', '')[:200])

        lines.append(f"{i}. 【{title}】")
        lines.append(f"   时间: {date}  来源: {source}")
        if content:
            lines.append(f"   摘要: {content}")
        if url:
            lines.append(f"   链接: {url}")
        lines.append('')

    return '\n'.join(lines), None


def _extract_search_data(result):
    """提取金融数据查询结果"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    sdr = data.get('searchDataResultDTO', {})
    tables = sdr.get('dataTableDTOList', [])

    if not tables:
        return None, '未查到相关数据'

    lines = []
    for table_obj in tables:
        entity = _fix_gbk(table_obj.get('entityName', ''))
        table = table_obj.get('table', {})
        head_names = table.get('headName', [])

        lines.append(f"📊 {entity}")
        lines.append(f"   期间: {', '.join(head_names)}")
        lines.append('')

        # 提取数据行（跳过 headName）
        data_keys = [k for k in table.keys() if k != 'headName']
        for key in data_keys:
            vals = table[key]
            # key 是指标 ID，无法直接显示名称
            val_str = ', '.join(str(v) for v in vals)
            val_str = _fix_gbk(val_str)
            lines.append(f"   {key}: {val_str}")

        lines.append('')

    return '\n'.join(lines), None


# ── 股票诊断 ──────────────────────────────────────────────

def stock_diagnosis(question):
    """
    股票综合诊断（自然语言）
    优先用 stock-analysis 端点，若 API 不支持则降级到 ask 端点

    Parameters
    ----------
    question : str - 如 "分析贵州茅台"、"贵州茅台怎么样"

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    result = _call('stock_analysis', {'question': question})
    content, error = _extract_ai_content(result)

    # 降级到通用问答
    if error and ('不支持' in error or '空内容' in error):
        fallback_q = f"请从基本面、技术面、资金面、估值、风险五个维度，综合分析{question.replace('分析','').replace('怎么样','').strip()}这只股票，给出详细诊断报告"
        result2 = _call('ask', {'question': fallback_q})
        content, error = _extract_ai_content(result2)

    return {'content': content, 'error': error}


# ── 基金诊断 ──────────────────────────────────────────────

def fund_diagnosis(question):
    """
    基金综合诊断（自然语言）
    优先用 fund-analysis 端点，若 API 不支持则降级到 ask 端点

    Parameters
    ----------
    question : str - 如 "分析招商中证白酒"、"这只基金怎么样"

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    result = _call('fund_analysis', {'question': question})
    content, error = _extract_ai_content(result)

    # 降级到通用问答
    if error and ('不支持' in error or '空内容' in error):
        fallback_q = f"请从基金类型、业绩表现、持仓结构、基金经理、费率、风险收益特征六个维度，综合分析{question.replace('分析','').replace('怎么样','').strip()}这只基金"
        result2 = _call('ask', {'question': fallback_q})
        content, error = _extract_ai_content(result2)

    return {'content': content, 'error': error}


# ── 金融数据查询 ──────────────────────────────────────────

def search_data(query, entity='', indicator='', data_type='quant'):
    """
    金融数据自然语言查询

    Parameters
    ----------
    query : str - 自然语言查询，如 "贵州茅台最近一年的营收和净利润"
    entity : str - 实体名称（可选）
    indicator : str - 指标名称（可选）
    data_type : str - 数据类型 ('quant'|' realtime'|'finance')

    Returns
    -------
    dict: {'content': str, 'data': list, 'error': str or None}
    """
    payload = {
        'query': query,
        'entity': entity,
        'indicator': indicator,
        'type': data_type,
    }
    result = _call('search_data', payload)

    if 'error' in result:
        return {'content': None, 'data': [], 'error': result['error']}

    content, error = _extract_search_data(result)
    raw_data = result.get('data', {})

    return {'content': content, 'data': raw_data, 'error': error}


# ── 选股 ──────────────────────────────────────────────────

def select_security(query, market='a_share', category='stock', top_n=10):
    """
    自然语言选股

    Parameters
    ----------
    query : str - 自然语言，如 "市盈率最低的50只股票"、"连续上涨的创业板股票"
    market : str - 市场 ('a_share'|'hk'|'us')
    category : str - 品类 ('stock'|'fund'|'etf'|'bond'|'convertible_bond'|'sector'|'concept')
    top_n : int - 返回数量

    Returns
    -------
    dict: {'content': str, 'data': list, 'error': str or None}
    """
    payload = {
        'query': query,
        'market': market,
        'category': category,
        'count': top_n,
    }
    result = _call('select_security', payload)

    if 'error' in result:
        return {'content': None, 'data': [], 'error': result['error']}

    content, error = _extract_select_stock(result)
    raw_data = result.get('data', {})

    return {'content': content, 'data': raw_data, 'error': error}


# ── 资讯搜索 ──────────────────────────────────────────────

def search_news(query, market='', count=10):
    """
    金融资讯搜索

    Parameters
    ----------
    query : str - 搜索关键词
    market : str - 市场筛选 (''|'cn'|'hk'|'us')
    count : int - 返回数量

    Returns
    -------
    dict: {'content': str, 'data': list, 'error': str or None}
    """
    payload = {
        'query': query,
        'market': market,
        'count': count,
    }
    result = _call('search_news', payload)

    if 'error' in result:
        return {'content': None, 'data': [], 'error': result['error']}

    content, error = _extract_news(result)
    raw_data = result.get('data', {})

    return {'content': content, 'data': raw_data, 'error': error}


# ── AI 问答 ──────────────────────────────────────────────

def ask(question, deep_think=False):
    """
    金融 AI 问答

    Parameters
    ----------
    question : str - 问题
    deep_think : bool - 是否启用深度思考

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    payload = {
        'question': question,
        'deepThink': deep_think,
    }
    result = _call('ask', payload)
    content, error = _extract_ai_content(result)
    return {'content': content, 'error': error}


# ── 可比公司分析 ──────────────────────────────────────────

def comparable_analysis(question):
    """
    可比公司分析

    Parameters
    ----------
    question : str - 如 "对比贵州茅台和五粮液的估值"

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    result = _call('comparable', {'question': question})
    content, error = _extract_ai_content(result)
    return {'content': content, 'error': error}
