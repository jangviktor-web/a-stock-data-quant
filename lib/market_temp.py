"""
市场温度计模块 (Market Temperature)

综合多个A股市场指标，计算市场温度分数(0-100)，
用于判断当前市场情绪是偏热(贪婪)还是偏冷(恐惧)。

指标来源:
- 巴菲特指标 (总市值/GDP)
- 股债利差 (风险溢价)
- 创新高/新低统计
- QVIX期权波动率指数 (中国版VIX)
- 市场活跃度

用法:
    from lib.market_temp import get_market_temperature, format_temperature
    result = get_market_temperature()
    print(format_temperature(result))
"""

import sys
import datetime

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

try:
    from lib.akshare_data import get_zt_pool, get_dt_pool
    HAS_ZT_DT = True
except ImportError:
    try:
        from akshare_data import get_zt_pool, get_dt_pool
        HAS_ZT_DT = True
    except ImportError:
        HAS_ZT_DT = False


# ---------------------------------------------------------------------------
# 数据获取函数
# ---------------------------------------------------------------------------

def fetch_buffett_index():
    """
    获取巴菲特指标 (A股总市值/GDP)
    返回: {'value': float, 'percentile': float, 'date': str, 'name': str}
    失败返回 None
    """
    if not HAS_AKSHARE:
        print("[market_temp] akshare not installed, skip buffett_index", file=sys.stderr)
        return None
    try:
        df = ak.stock_buffett_index_lg()
        if df is None or df.empty:
            return None
        # 取最新一行
        latest = df.iloc[-1]
        # 列名可能为: 日期, 总市值, GDP, 巴菲特指标(总市值/GDP)
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "指标" in cl or "gdp" in cl.lower() and "总" in cl:
                value = float(latest[c])
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        # 如果没找到指标列，尝试最后一列数值
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        # 计算历史百分位
        indicator_col = None
        for c in cols:
            cl = str(c).lower()
            if "指标" in cl or ("总" in cl and "gdp" in cl.lower()):
                indicator_col = c
                break
        if indicator_col is None:
            # 尝试倒数第二列
            for c in reversed(cols):
                try:
                    df[c].astype(float)
                    indicator_col = c
                    break
                except (ValueError, TypeError):
                    continue
        percentile = 50.0
        if indicator_col is not None:
            series = df[indicator_col].astype(float).dropna()
            if len(series) > 0:
                percentile = float((series < value).sum() / len(series) * 100)
        return {
            'value': round(value, 2),
            'percentile': round(percentile, 1),
            'date': date_str,
            'name': '巴菲特指标(总市值/GDP)',
        }
    except Exception as e:
        print(f"[market_temp] fetch_buffett_index failed: {e}", file=sys.stderr)
        return None


def fetch_equity_bond_spread():
    """
    获取股债利差 (风险溢价, 万得全A盈利收益率 - 10年期国债收益率)
    返回: {'value': float, 'date': str, 'name': str}
    失败返回 None
    """
    if not HAS_AKSHARE:
        print("[market_temp] akshare not installed, skip equity_bond_spread", file=sys.stderr)
        return None
    try:
        df = ak.stock_ebs_lg()
        if df is None or df.empty:
            return None
        latest = df.iloc[-1]
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "利差" in cl or "spread" in cl or "溢价" in cl:
                value = float(latest[c])
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        return {
            'value': round(value, 4),
            'date': date_str,
            'name': '股债利差(风险溢价)',
        }
    except Exception as e:
        print(f"[market_temp] fetch_equity_bond_spread failed: {e}", file=sys.stderr)
        return None


def fetch_new_high_low():
    """
    获取创新高/创新低股票数量统计
    主源: akshare stock_a_high_low_statistics
    备用源: 涨停池/跌停池数量比 (push2ex)
    返回: {'new_high': int, 'new_low': int, 'ratio': float, 'symbol': str, 'name': str}
    失败返回 None
    """
    # 主源: akshare
    if HAS_AKSHARE:
        symbols = ["sz50", "hs300"]
        for symbol in symbols:
            try:
                df = ak.stock_a_high_low_statistics(symbol=symbol)
                if df is None or df.empty:
                    continue
                latest = df.iloc[-1]
                cols = df.columns.tolist()
                new_high = None
                new_low = None
                for c in cols:
                    cl = str(c).lower()
                    if "新高" in cl or "high" in cl:
                        new_high = int(float(latest[c]))
                    elif "新低" in cl or "low" in cl:
                        new_low = int(float(latest[c]))
                if new_high is None or new_low is None:
                    numeric_cols = []
                    for c in cols:
                        try:
                            int(float(latest[c]))
                            numeric_cols.append(c)
                        except (ValueError, TypeError):
                            continue
                    if len(numeric_cols) >= 2:
                        new_high = int(float(latest[numeric_cols[0]]))
                        new_low = int(float(latest[numeric_cols[1]]))
                if new_high is None or new_low is None:
                    continue
                ratio = float(new_high) / max(float(new_low), 1.0)
                return {
                    'new_high': new_high,
                    'new_low': new_low,
                    'ratio': round(ratio, 2),
                    'symbol': symbol,
                    'name': f'创新高/新低({symbol})',
                }
            except Exception as e:
                print(f"[market_temp] fetch_new_high_low({symbol}) failed: {e}", file=sys.stderr)
                continue

    # 备用源: 涨停池/跌停池数量比
    if HAS_ZT_DT:
        try:
            zt = get_zt_pool()
            dt = get_dt_pool()
            zt_count = len(zt) if zt else 0
            dt_count = len(dt) if dt else 0
            if zt_count > 0 or dt_count > 0:
                ratio = float(zt_count) / max(float(dt_count), 1.0)
                return {
                    'new_high': zt_count,
                    'new_low': dt_count,
                    'ratio': round(ratio, 2),
                    'symbol': 'zt_dt_pool',
                    'name': f'涨停/跌停比({zt_count}/{dt_count})',
                }
        except Exception as e:
            print(f"[market_temp] fetch_new_high_low(zt_dt fallback) failed: {e}", file=sys.stderr)

    return None


def fetch_qvix():
    """
    获取50ETF期权QVIX波动率指数 (中国版VIX)
    返回: {'value': float, 'date': str, 'name': str}
    失败返回 None
    """
    if not HAS_AKSHARE:
        print("[market_temp] akshare not installed, skip qvix", file=sys.stderr)
        return None
    try:
        df = ak.index_option_50etf_qvix()
        if df is None or df.empty:
            return None
        latest = df.iloc[-1]
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "qvix" in cl or "波动" in cl or "close" in cl or "收盘" in cl:
                try:
                    value = float(latest[c])
                except (ValueError, TypeError):
                    pass
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        return {
            'value': round(value, 2),
            'date': date_str,
            'name': 'QVIX期权波动率',
        }
    except Exception as e:
        print(f"[market_temp] fetch_qvix failed: {e}", file=sys.stderr)
        return None


def fetch_market_activity():
    """
    获取市场活跃度
    主源: akshare stock_market_activity_legu (乐咕乐股)
    备用源: 涨停占比 = ZT/(ZT+DT)*100 作为活跃度代理
    返回: {'value': float, 'date': str, 'name': str}
    失败返回 None
    """
    # 主源: akshare
    if HAS_AKSHARE:
        try:
            df = ak.stock_market_activity_legu()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                cols = df.columns.tolist()
                value = None
                date_str = ""
                for c in cols:
                    cl = str(c).lower()
                    if "活跃" in cl or "activity" in cl or "比例" in cl or "percent" in cl:
                        try:
                            value = float(latest[c])
                        except (ValueError, TypeError):
                            pass
                    elif "日期" in cl or "date" in cl:
                        date_str = str(latest[c])
                if value is None:
                    for c in reversed(cols):
                        try:
                            value = float(latest[c])
                            break
                        except (ValueError, TypeError):
                            continue
                if value is not None:
                    if value <= 1.0:
                        value = value * 100
                    return {
                        'value': round(value, 2),
                        'date': date_str,
                        'name': '市场活跃度',
                    }
        except Exception as e:
            print(f"[market_temp] fetch_market_activity(akshare) failed: {e}", file=sys.stderr)

    # 备用源: 涨停占比作为活跃度代理
    if HAS_ZT_DT:
        try:
            zt = get_zt_pool()
            dt = get_dt_pool()
            zt_count = len(zt) if zt else 0
            dt_count = len(dt) if dt else 0
            total = zt_count + dt_count
            if total > 0:
                # 涨停占比: 涨停多=市场活跃偏热, 跌停多=市场恐慌偏冷
                activity = zt_count / total * 100
                return {
                    'value': round(activity, 2),
                    'date': '',
                    'name': f'涨停占比({zt_count}/{total})',
                }
        except Exception as e:
            print(f"[market_temp] fetch_market_activity(zt_dt fallback) failed: {e}", file=sys.stderr)

    return None


# ---------------------------------------------------------------------------
# 温度计算
# ---------------------------------------------------------------------------

def _score_buffett(data):
    """巴菲特指标子评分: 百分位越低越看多"""
    if data is None:
        return None
    pct = data.get('percentile', 50.0)
    if pct < 70:
        # 偏低估 -> 看多, 80-100
        score = 80 + (70 - pct) / 70 * 20
    elif pct <= 90:
        # 中性区间 -> 40-70
        score = 70 - (pct - 70) / 20 * 30
    else:
        # 偏高估 -> 看空, 0-40
        score = max(0, 40 - (pct - 90) / 10 * 40)
    return round(min(100, max(0, score)), 1)


def _score_spread(data):
    """股债利差子评分: 利差越大股票越有吸引力 -> 看多"""
    if data is None:
        return None
    spread = data.get('value', 0)
    # 经验区间: 利差一般在 -2% ~ 6% 之间
    # spread > 4% 非常看多, < 0 看空
    if spread >= 4:
        score = 90 + min(10, (spread - 4) * 5)
    elif spread >= 2:
        score = 60 + (spread - 2) / 2 * 30
    elif spread >= 0:
        score = 40 + spread / 2 * 20
    else:
        score = max(0, 40 + spread * 20)
    return round(min(100, max(0, score)), 1)


def _score_high_low(data):
    """新高/新低比子评分: ratio>2看多, 0.5-2中性, <0.5看空"""
    if data is None:
        return None
    ratio = data.get('ratio', 1.0)
    if ratio > 2:
        score = 70 + min(30, (ratio - 2) * 10)
    elif ratio >= 0.5:
        score = 40 + (ratio - 0.5) / 1.5 * 30
    else:
        score = max(0, ratio / 0.5 * 40)
    return round(min(100, max(0, score)), 1)


def _score_qvix(data):
    """QVIX子评分: 低波动看多, 高波动看空"""
    if data is None:
        return None
    qvix = data.get('value', 20)
    if qvix < 15:
        score = 80 + (15 - qvix) / 15 * 20
    elif qvix <= 25:
        score = 40 + (25 - qvix) / 10 * 40
    else:
        score = max(0, 40 - (qvix - 25) / 15 * 40)
    return round(min(100, max(0, score)), 1)


def _score_activity(data):
    """市场活跃度子评分: >60%看多, 30-60%中性, <30%看空"""
    if data is None:
        return None
    act = data.get('value', 50)
    if act > 60:
        score = 70 + min(30, (act - 60) / 40 * 30)
    elif act >= 30:
        score = 40 + (act - 30) / 30 * 30
    else:
        score = max(0, act / 30 * 40)
    return round(min(100, max(0, score)), 1)


def compute_temperature(results: dict) -> dict:
    """
    根据各指标数据计算综合市场温度

    参数:
        results: dict, 各指标获取结果
            keys: 'buffett', 'spread', 'high_low', 'qvix', 'activity'

    返回:
        {
            'score': float,       # 综合温度 0-100
            'level': str,         # 温度等级
            'details': {...},     # 各指标子评分
            'missing': [...],     # 缺失的指标列表
        }
    """
    weights = {
        'buffett': 0.25,
        'spread': 0.20,
        'high_low': 0.20,
        'qvix': 0.20,
        'activity': 0.15,
    }

    scorers = {
        'buffett': _score_buffett,
        'spread': _score_spread,
        'high_low': _score_high_low,
        'qvix': _score_qvix,
        'activity': _score_activity,
    }

    details = {}
    missing = []
    weighted_sum = 0.0
    weight_total = 0.0

    for key, weight in weights.items():
        data = results.get(key)
        sub_score = scorers[key](data)
        if sub_score is not None:
            details[key] = {
                'data': data,
                'sub_score': sub_score,
                'weight': weight,
            }
            weighted_sum += sub_score * weight
            weight_total += weight
        else:
            missing.append(key)
            details[key] = {
                'data': None,
                'sub_score': None,
                'weight': weight,
            }

    # 归一化 (如果有指标缺失，按可用权重归一化)
    if weight_total > 0:
        score = weighted_sum / weight_total
    else:
        score = 50.0  # 无数据时给中性分

    score = round(min(100, max(0, score)), 1)

    if score >= 70:
        level = "偏热/贪婪"
    elif score >= 40:
        level = "中性"
    else:
        level = "偏冷/恐惧"

    return {
        'score': score,
        'level': level,
        'details': details,
        'missing': missing,
    }


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def get_market_temperature() -> dict:
    """
    获取市场温度: 调用所有数据源，计算综合温度分数

    返回:
        {
            'score': float,
            'level': str,
            'details': {...},
            'missing': [...],
            'timestamp': str,
        }
    """
    if not HAS_AKSHARE:
        print("[market_temp] akshare is not installed, cannot fetch data", file=sys.stderr)
        return {
            'score': 50.0,
            'level': '中性',
            'details': {},
            'missing': ['buffett', 'spread', 'high_low', 'qvix', 'activity'],
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': 'akshare not installed',
        }

    results = {
        'buffett': fetch_buffett_index(),
        'spread': fetch_equity_bond_spread(),
        'high_low': fetch_new_high_low(),
        'qvix': fetch_qvix(),
        'activity': fetch_market_activity(),
    }

    temp = compute_temperature(results)
    temp['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return temp


# ---------------------------------------------------------------------------
# 格式化输出
# ---------------------------------------------------------------------------

def _make_bar(score, width=20):
    """生成ASCII温度条: [=====>    ] 55/100"""
    filled = int(round(score / 100 * width))
    filled = max(0, min(width, filled))
    if filled < width:
        bar = '=' * max(0, filled - 1) + '>' + ' ' * (width - filled)
    else:
        bar = '=' * width
    return f"[{bar}] {score:.0f}/100"


def _level_marker(level):
    """根据温度等级返回ASCII标记"""
    if "热" in level or "贪婪" in level:
        return "[HOT]"
    elif "冷" in level or "恐惧" in level:
        return "[COLD]"
    return "[WARM]"


def format_temperature(result: dict) -> str:
    """
    格式化市场温度结果为可读文本

    参数:
        result: get_market_temperature() 的返回值

    返回:
        格式化的字符串
    """
    lines = []
    lines.append("=" * 50)
    lines.append("        A股市场温度计 (Market Temperature)")
    lines.append("=" * 50)

    score = result.get('score', 50)
    level = result.get('level', '中性')
    marker = _level_marker(level)
    timestamp = result.get('timestamp', '')

    lines.append(f"  综合温度: {score:.1f} / 100  {marker} {level}")
    lines.append(f"  {_make_bar(score)}")
    if timestamp:
        lines.append(f"  时间: {timestamp}")
    lines.append("-" * 50)

    # 各指标详情
    indicator_names = {
        'buffett': '巴菲特指标',
        'spread': '股债利差',
        'high_low': '新高/新低',
        'qvix': 'QVIX波动率',
        'activity': '市场活跃度',
    }

    details = result.get('details', {})
    for key in ['buffett', 'spread', 'high_low', 'qvix', 'activity']:
        info = details.get(key, {})
        name = indicator_names.get(key, key)
        sub_score = info.get('sub_score')
        data = info.get('data')
        weight = info.get('weight', 0)

        if sub_score is not None and data is not None:
            # 提取关键数值
            if key == 'buffett':
                val_str = f"值={data.get('value', '?')}%, 百分位={data.get('percentile', '?')}%"
            elif key == 'spread':
                val_str = f"利差={data.get('value', '?')}%"
            elif key == 'high_low':
                val_str = f"新高={data.get('new_high', '?')}, 新低={data.get('new_low', '?')}, 比值={data.get('ratio', '?')}"
            elif key == 'qvix':
                val_str = f"QVIX={data.get('value', '?')}"
            elif key == 'activity':
                val_str = f"活跃度={data.get('value', '?')}%"
            else:
                val_str = str(data.get('value', '?'))

            sub_marker = _level_marker(
                "偏热/贪婪" if sub_score >= 70 else ("偏冷/恐惧" if sub_score < 40 else "中性")
            )
            lines.append(f"  {name} (权重{weight*100:.0f}%)")
            lines.append(f"    {val_str}")
            lines.append(f"    子评分: {sub_score:.1f}/100 {sub_marker}")
        else:
            lines.append(f"  {name} (权重{weight*100:.0f}%)")
            lines.append(f"    [数据缺失]")

    lines.append("-" * 50)

    missing = result.get('missing', [])
    if missing:
        missing_names = [indicator_names.get(m, m) for m in missing]
        lines.append(f"  缺失指标: {', '.join(missing_names)}")
        lines.append(f"  (已按可用指标归一化计算)")

    error = result.get('error')
    if error:
        lines.append(f"  [ERROR] {error}")

    lines.append("=" * 50)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 直接运行
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    result = get_market_temperature()
    print(format_temperature(result))
