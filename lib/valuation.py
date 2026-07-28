"""
个股估值分位分析模块

获取历史 PE/PB/PS 估值数据，计算当前估值在历史区间中的分位数，
结合筹码分布判断个股估值水平（低估/合理/偏高）。

依赖 akshare >= 1.18.x
"""

import sys
import warnings

warnings.filterwarnings("ignore")

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


def _warn(msg):
    """输出警告到 stderr"""
    print(f"[valuation] WARNING: {msg}", file=sys.stderr)


def get_valuation_baidu(code: str, indicator: str = "pe", period: str = "all") -> dict:
    """
    获取个股估值指标及历史分位

    主源: 东方财富 datacenter (RPT_VALUEANALYSIS_DET)
    备用源: akshare stock_zh_valuation_baidu (百度)

    Parameters
    ----------
    code : str - 股票代码，纯数字如 "600519"
    indicator : str - 估值指标: "pe", "pb", "ps"
    period : str - 时间范围: "近一年", "近三年", "近五年", "近十年", "全部"
                   也接受英文 "all" 映射为 "全部"

    Returns
    -------
    dict or None
        {'current': float, 'percentile': float, 'min': float,
         'max': float, 'median': float, 'history': list}
        失败时返回 None
    """
    # 主源: 东方财富 datacenter
    result = _fetch_valuation_eastmoney(code, indicator, period)
    if result is not None:
        return result

    # 备用源: akshare 百度
    if not HAS_AKSHARE:
        return None

    period_map = {
        "all": "全部", "1y": "近一年", "3y": "近三年",
        "5y": "近五年", "10y": "近十年",
    }
    period_cn = period_map.get(period, period)

    try:
        df = ak.stock_zh_valuation_baidu(
            symbol=code, indicator=indicator, period=period_cn
        )
        if df is None or df.empty:
            return None

        value_col = df.columns[-1]
        values = df[value_col].dropna().astype(float)
        if values.empty:
            return None

        current = float(values.iloc[-1])
        vmin = float(values.min())
        vmax = float(values.max())
        vmedian = float(values.median())

        if vmax - vmin > 0:
            percentile = (current - vmin) / (vmax - vmin) * 100
        else:
            percentile = 50.0
        percentile = max(0.0, min(100.0, percentile))

        history = []
        for _, row in df.tail(10).iterrows():
            history.append({
                'date': str(row.iloc[0]),
                'value': float(row[value_col]) if str(row[value_col]) != 'nan' else None,
            })

        return {
            'current': round(current, 2),
            'percentile': round(percentile, 2),
            'min': round(vmin, 2),
            'max': round(vmax, 2),
            'median': round(vmedian, 2),
            'history': history,
        }
    except Exception as e:
        _warn(f"获取 {code} {indicator} 估值失败(百度): {e}")
        return None


def _fetch_valuation_eastmoney(code: str, indicator: str = "pe", period: str = "all") -> dict:
    """
    东方财富 datacenter 估值数据 (RPT_VALUEANALYSIS_DET)
    返回与 get_valuation_baidu 相同格式
    """
    import requests

    # indicator -> 东财字段映射
    field_map = {
        'pe': 'PE_TTM',
        'pb': 'PB_MRQ',
        'ps': 'PS_TTM',
    }
    field = field_map.get(indicator.lower())
    if not field:
        _warn(f"不支持的指标: {indicator} (可用: pe/pb/ps)")
        return None

    # period -> pageSize 映射 (交易日约250天/年)
    period_pages = {
        'all': 2500, '全部': 2500,
        '10y': 2500, '近十年': 2500,
        '5y': 1250, '近五年': 1250,
        '3y': 750, '近三年': 750,
        '1y': 250, '近一年': 250,
    }
    page_size = period_pages.get(period, 2500)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://data.eastmoney.com/',
    }

    try:
        url = (
            f"https://datacenter-web.eastmoney.com/api/data/v1/get"
            f"?reportName=RPT_VALUEANALYSIS_DET"
            f"&columns=TRADE_DATE,{field},CLOSE_PRICE"
            f"&filter=(SECURITY_CODE=%22{code}%22)"
            f"&pageNumber=1&pageSize={page_size}"
            f"&sortColumns=TRADE_DATE&sortTypes=-1"
        )
        r = requests.get(url, headers=headers, timeout=15, proxies={'http': None, 'https': None})
        data = r.json()

        if not data.get('result') or not data['result'].get('data'):
            _warn(f"{code} {indicator} 东财估值数据为空")
            return None

        rows = data['result']['data']
        # 提取有效数值 (按时间正序)
        values = []
        dates = []
        for row in reversed(rows):
            v = row.get(field)
            if v is not None:
                values.append(float(v))
                dates.append(str(row.get('TRADE_DATE', ''))[:10])

        if not values:
            return None

        current = values[-1]
        vmin = min(values)
        vmax = max(values)
        import statistics
        vmedian = statistics.median(values)

        # 分位数: 当前值在历史中的位置
        below = sum(1 for v in values if v < current)
        percentile = below / len(values) * 100
        percentile = max(0.0, min(100.0, percentile))

        # 最近10个数据点
        history = [{'date': dates[i], 'value': values[i]} for i in range(max(0, len(values)-10), len(values))]

        return {
            'current': round(current, 2),
            'percentile': round(percentile, 2),
            'min': round(vmin, 2),
            'max': round(vmax, 2),
            'median': round(vmedian, 2),
            'history': history,
        }
    except Exception as e:
        _warn(f"获取 {code} {indicator} 估值失败(东财): {e}")
        return None


def get_chip_distribution(code: str) -> dict:
    """
    获取个股筹码分布数据

    Parameters
    ----------
    code : str - 股票代码，纯数字如 "600519"

    Returns
    -------
    dict or None
        {'avg_cost': float, 'profit_ratio': float,
         'concentration_90': str, 'concentration_70': str,
         'upper_bound': float, 'lower_bound': float}
        失败时返回 None
    """
    if not HAS_AKSHARE:
        _warn("akshare 未安装，无法获取筹码分布")
        return None

    try:
        df = ak.stock_cyq_em(symbol=code, adjust="qfq")
        if df is None or df.empty:
            _warn(f"{code} 筹码分布数据为空")
            return None

        # 东方财富筹码接口返回列可能包含:
        # 均价、获利比例、90%集中度、70%集中度、上限、下限等
        # 根据实际返回列名做兼容解析
        cols = list(df.columns)
        row = df.iloc[-1]  # 取最新一行

        def _find_col(keywords):
            """按关键词模糊匹配列名"""
            for c in cols:
                for kw in keywords:
                    if kw in str(c):
                        return c
            return None

        col_avg = _find_col(['均价', '平均成本', 'avg'])
        col_profit = _find_col(['获利', '盈利', 'profit'])
        col_90 = _find_col(['90'])
        col_70 = _find_col(['70'])
        col_upper = _find_col(['上限', 'upper'])
        col_lower = _find_col(['下限', 'lower'])

        def _safe_float(val):
            try:
                return round(float(val), 2)
            except (TypeError, ValueError):
                return 0.0

        return {
            'avg_cost': _safe_float(row[col_avg]) if col_avg else 0.0,
            'profit_ratio': _safe_float(row[col_profit]) if col_profit else 0.0,
            'concentration_90': str(row[col_90]) if col_90 else "N/A",
            'concentration_70': str(row[col_70]) if col_70 else "N/A",
            'upper_bound': _safe_float(row[col_upper]) if col_upper else 0.0,
            'lower_bound': _safe_float(row[col_lower]) if col_lower else 0.0,
        }

    except Exception as e:
        _warn(f"获取 {code} 筹码分布失败: {e}")
        return None


def _assess_percentile(percentile):
    """根据分位数给出评估标签"""
    if percentile is None:
        return "未知"
    if percentile < 30:
        return "低估"
    elif percentile <= 70:
        return "合理"
    else:
        return "偏高"


def get_stock_valuation(code: str) -> dict:
    """
    综合估值分析：PE/PB/PS 分位 + 筹码分布

    Parameters
    ----------
    code : str - 股票代码，纯数字如 "600519"

    Returns
    -------
    dict
        {'code': str, 'pe': dict|None, 'pb': dict|None,
         'ps': dict|None, 'chip': dict|None, 'assessment': str}
    """
    pe_data = get_valuation_baidu(code, indicator="pe")
    pb_data = get_valuation_baidu(code, indicator="pb")
    ps_data = get_valuation_baidu(code, indicator="ps")
    chip_data = get_chip_distribution(code)

    # 综合评估：以 PE 分位为主，PB 分位为辅
    pe_pct = pe_data['percentile'] if pe_data else None
    pb_pct = pb_data['percentile'] if pb_data else None

    if pe_pct is not None and pb_pct is not None:
        avg_pct = (pe_pct + pb_pct) / 2
        assessment = _assess_percentile(avg_pct)
        # 如果 PE 和 PB 判断不一致，给出更细致的描述
        pe_label = _assess_percentile(pe_pct)
        pb_label = _assess_percentile(pb_pct)
        if pe_label != pb_label:
            assessment = f"{assessment}(PE{pe_label}/PB{pb_label})"
    elif pe_pct is not None:
        assessment = _assess_percentile(pe_pct)
    elif pb_pct is not None:
        assessment = _assess_percentile(pb_pct)
    else:
        assessment = "数据不足，无法评估"

    return {
        'code': code,
        'pe': pe_data,
        'pb': pb_data,
        'ps': ps_data,
        'chip': chip_data,
        'assessment': assessment,
    }


def _percentile_bar(percentile, label=""):
    """
    生成分位数进度条

    示例: [===>      ] 32% (低估)
    """
    if percentile is None:
        return "[N/A]"
    filled = int(percentile / 10)
    filled = max(0, min(10, filled))
    bar = "=" * filled + ">" if filled < 10 else "=" * 10
    bar = bar.ljust(10)
    text = f"[{bar}] {percentile:.0f}%"
    if label:
        text += f" ({label})"
    return text


def _marker(percentile):
    """根据分位数返回 ASCII 标记"""
    if percentile is None:
        return "[N/A]"
    if percentile < 30:
        return "[LOW]"
    elif percentile <= 70:
        return "[FAIR]"
    else:
        return "[HIGH]"


def format_valuation(result: dict) -> str:
    """
    格式化估值分析结果为纯文本

    Parameters
    ----------
    result : dict - get_stock_valuation() 的返回值

    Returns
    -------
    str - 格式化的文本报告
    """
    if not result:
        return "估值数据获取失败"

    lines = []
    code = result.get('code', '------')
    lines.append(f"{'=' * 50}")
    lines.append(f"  个股估值分析: {code}")
    lines.append(f"{'=' * 50}")
    lines.append("")

    # PE / PB / PS 估值
    for key, name in [('pe', 'PE(市盈率)'), ('pb', 'PB(市净率)'), ('ps', 'PS(市销率)')]:
        data = result.get(key)
        if data:
            pct = data['percentile']
            label = _assess_percentile(pct)
            marker = _marker(pct)
            lines.append(f"  {name}: {marker}")
            lines.append(f"    当前值: {data['current']}")
            lines.append(f"    分位数: {_percentile_bar(pct, label)}")
            lines.append(f"    最小值: {data['min']}  |  中位数: {data['median']}  |  最大值: {data['max']}")
            lines.append("")
        else:
            lines.append(f"  {name}: 数据获取失败")
            lines.append("")

    # 筹码分布
    chip = result.get('chip')
    lines.append(f"  {'─' * 44}")
    lines.append("  筹码分布:")
    if chip:
        lines.append(f"    平均成本: {chip['avg_cost']}")
        lines.append(f"    获利比例: {chip['profit_ratio']}%")
        lines.append(f"    90%筹码集中区间: {chip['concentration_90']}")
        lines.append(f"    70%筹码集中区间: {chip['concentration_70']}")
        lines.append(f"    成本上界: {chip['upper_bound']}  |  成本下界: {chip['lower_bound']}")
    else:
        lines.append("    筹码数据获取失败")
    lines.append("")

    # 综合评估
    assessment = result.get('assessment', '未知')
    lines.append(f"  {'─' * 44}")
    lines.append(f"  综合评估: {assessment}")
    lines.append(f"{'=' * 50}")

    return "\n".join(lines)


if __name__ == '__main__':
    # 测试: 贵州茅台
    test_code = "600519"
    print(f"正在获取 {test_code} 估值数据...\n")

    result = get_stock_valuation(test_code)
    print(format_valuation(result))
