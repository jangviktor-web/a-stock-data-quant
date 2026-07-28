"""
筹码分布计算模块
移植自 go-stock (github.com/ArvinLovegood/go-stock) chip_distribution.go
基于K线+换手率近似计算筹码分布，不依赖第三方私有接口。

算法：
1. 用换手率对历史筹码做衰减（保留比例 = 1 - turnover）
2. 将当日成交量按以「成本中枢」为中心的高斯核落在 [low, high] 与各 bin 的交集上
3. 成本中枢优先为日 VWAP（成交额/成交量），否则典型价 (H+L+C)/3
"""

import math
from typing import List, Dict, Optional


def _safe_float(val, default=0.0) -> float:
    """安全转换为float"""
    if val is None:
        return default
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (ValueError, TypeError):
        return default


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _cost_center(low: float, high: float, open_p: float, close: float,
                 vol: float, amount: float) -> float:
    """计算单根K线的成本中枢"""
    if low <= 0 or high <= 0 or high < low:
        if low > 0 and high > 0:
            return (low + high) / 2
        return 0.0

    # 优先 VWAP
    if amount > 0 and vol > 0:
        vwap = amount / vol
        if math.isfinite(vwap) and vwap > 0:
            return _clamp(vwap, low, high)

    # 典型价 (H+L+C)/3
    if close > 0 and math.isfinite(close):
        tp = (high + low + close) / 3
        if math.isfinite(tp):
            return _clamp(tp, low, high)

    # (H+L+O+C)/4
    if open_p > 0 and close > 0:
        tp = (high + low + open_p + close) / 4
        if math.isfinite(tp):
            return _clamp(tp, low, high)

    return (high + low) / 2


def _add_chip_kernel(dist: List[float], bins: int, min_p: float, width: float,
                     low: float, high: float, vol: float, center: float):
    """将当日成交量按高斯核分配到各bin"""
    if vol <= 0 or width <= 0:
        return

    # 高斯核标准差 = 当日振幅的 1/4（经验值）
    sigma = max((high - low) / 4, width / 2)
    if sigma <= 0:
        sigma = width

    total_weight = 0.0
    weights = []

    for i in range(bins):
        bin_center = min_p + (i + 0.5) * width
        # 检查bin与[low, high]是否有交集
        bin_lo = min_p + i * width
        bin_hi = bin_lo + width
        if bin_hi < low or bin_lo > high:
            weights.append(0.0)
            continue

        # 高斯权重
        dx = bin_center - center
        w = math.exp(-0.5 * (dx / sigma) ** 2)
        weights.append(w)
        total_weight += w

    if total_weight <= 0:
        return

    for i in range(bins):
        if weights[i] > 0:
            dist[i] += vol * weights[i] / total_weight


def calculate_chip_distribution(klines: List[Dict], bins: int = 80) -> Optional[Dict]:
    """
    计算筹码分布

    参数:
        klines: K线数据列表，每项需包含:
            - open, high, low, close: 价格
            - volume: 成交量
            - amount: 成交额（可选，用于计算VWAP）
            - turnover: 换手率（百分比，如 2.5 表示 2.5%）
        bins: 价格分箱数量（默认80，最大300）

    返回:
        {
            'days': K线天数,
            'bins': 分箱数,
            'current': 最新收盘价,
            'avg_cost': 平均成本,
            'profit_ratio': 获利筹码占比,
            'min_price': 最低价,
            'max_price': 最高价,
            'items': [{'price': 价位, 'vol': 筹码量, 'ratio': 占比}, ...],
            'top_concentration': 筹码最集中的前5个价位
        }
    """
    if not klines or len(klines) == 0:
        return None

    bins = max(10, min(bins, 300))

    # 提取价格范围
    prices = []
    for k in klines:
        h = _safe_float(k.get('high'))
        l = _safe_float(k.get('low'))
        if h > 0 and l > 0:
            prices.extend([h, l])

    if not prices:
        return None

    min_p = min(prices)
    max_p = max(prices)

    if min_p <= 0 or max_p <= 0 or max_p < min_p:
        return None

    if max_p == min_p:
        max_p = min_p * 1.001

    width = (max_p - min_p) / bins
    if width <= 0:
        return None

    dist = [0.0] * bins

    for k in klines:
        turnover = _safe_float(k.get('turnover')) / 100.0  # 百分比转小数
        turnover = _clamp(turnover, 0, 0.98)

        # 衰减历史筹码
        remain = 1.0 - turnover
        for i in range(bins):
            dist[i] *= remain

        low = _safe_float(k.get('low'))
        high = _safe_float(k.get('high'))
        vol = _safe_float(k.get('volume'))
        open_p = _safe_float(k.get('open'))
        close = _safe_float(k.get('close'))
        amount = _safe_float(k.get('amount'))

        if vol <= 0 or low <= 0 or high <= 0:
            continue

        if high < low:
            low, high = high, low

        center = _cost_center(low, high, open_p, close, vol, amount)
        _add_chip_kernel(dist, bins, min_p, width, low, high, vol, center)

    # 计算统计量
    total_vol = sum(dist)
    if total_vol <= 0:
        return None

    last_close = _safe_float(klines[-1].get('close'))
    if last_close <= 0:
        last_close = _safe_float(klines[-1].get('high'))

    items = []
    avg_cost = 0.0
    profit_vol = 0.0

    for i in range(bins):
        center = min_p + (i + 0.5) * width
        vol = dist[i]
        ratio = vol / total_vol if total_vol > 0 else 0
        items.append({
            'price': round(center, 4),
            'vol': round(vol, 4),
            'ratio': round(ratio, 6)
        })
        avg_cost += vol * center
        if center <= last_close:
            profit_vol += vol

    avg_cost = avg_cost / total_vol if total_vol > 0 else 0
    profit_ratio = profit_vol / total_vol if total_vol > 0 else 0

    # 筹码集中度：前5大bin的占比之和
    sorted_items = sorted(items, key=lambda x: x['ratio'], reverse=True)
    top5 = sorted_items[:5]
    concentration = sum(x['ratio'] for x in top5)

    return {
        'days': len(klines),
        'bins': bins,
        'current': round(last_close, 4),
        'avg_cost': round(avg_cost, 4),
        'profit_ratio': round(profit_ratio, 6),
        'min_price': round(min_p, 4),
        'max_price': round(max_p, 4),
        'sum_vol': round(total_vol, 4),
        'items': items,
        'top_concentration': round(concentration, 6),
        'top_bins': top5
    }


def format_chip_distribution(result: Dict) -> str:
    """格式化筹码分布输出"""
    if not result:
        return "筹码分布计算失败：数据不足"

    lines = [
        "=" * 60,
        f"  筹码分布分析 ({result['days']}个交易日)",
        "=" * 60,
        f"  当前价格: {result['current']:.2f}",
        f"  平均成本: {result['avg_cost']:.2f}",
        f"  获利比例: {result['profit_ratio']*100:.1f}%",
        f"  价格区间: {result['min_price']:.2f} ~ {result['max_price']:.2f}",
        f"  筹码集中度(前5): {result['top_concentration']*100:.1f}%",
        "-" * 60,
        "  筹码最集中价位:",
    ]

    for item in result.get('top_bins', [])[:5]:
        bar_len = int(item['ratio'] * 100)
        bar = "█" * bar_len
        lines.append(f"    {item['price']:>10.2f}  {item['ratio']*100:>5.1f}%  {bar}")

    lines.append("=" * 60)

    # 解读
    if result['profit_ratio'] > 0.8:
        lines.append("  解读: 获利盘多，注意回调压力")
    elif result['profit_ratio'] < 0.2:
        lines.append("  解读: 套牢盘多，反弹阻力大")
    else:
        lines.append("  解读: 筹码分布相对均衡")

    if result['top_concentration'] > 0.5:
        lines.append("  解读: 筹码高度集中，主力控盘迹象")

    return "\n".join(lines)
