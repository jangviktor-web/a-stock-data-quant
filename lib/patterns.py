"""
形态识别模块 - 提取自 KlangAlpha/Klang
包含: zigzag转折点、W底、V型反转、杯柄形态
"""

import numpy as np
import pandas as pd

PEAK, VALLEY = 1, -1


def peak_valley_pivots_np(X, step=3):
    """
    使用滑动窗口法识别序列中的峰和谷。
    提取自 KlangAlpha/Klang zigzag_lib.py

    Parameters
    ----------
    X : numpy array - 价格序列
    step : int - 滑动窗口半径

    Returns
    -------
    numpy array - 1表示峰(PEAK), -1表示谷(VALLEY), 0表示无转折
    """
    pivots = np.zeros(len(X), dtype='i1')
    if len(X) < 2:
        return pivots

    preindex = 0
    # 获取第一个趋势
    if X[0] < X[1]:
        trend = -1
    else:
        trend = 1
    
    for i in range(0, len(X)):
        l = i - step
        r = i + step
        if l < 0:
            l = 0
        if l < preindex:
            l = preindex

        x1 = X[l:r]
        if trend == 1:
            if X[i] == np.amin(x1):
                trend = -1
                pivots[preindex] = 1
                preindex = i
            if X[i] == np.amax(x1) and X[i] > X[preindex]:
                preindex = i
        else:
            if X[i] == np.amax(x1):
                trend = 1
                pivots[preindex] = -1
                preindex = i
            if X[i] == np.amin(x1) and X[i] < X[preindex]:
                preindex = i
    # 补充最后一个
    if trend == 1:
        pivots[preindex] = 1
    else:
        pivots[preindex] = -1

    return pivots


def _create_index(pivots):
    """从pivots数组中提取非零元素的索引列表"""
    index_list = []
    for i in range(0, len(pivots)):
        if pivots[i] != 0:
            index_list.append(i)
    return index_list


def _approx(a, b, tolerance=0.05):
    """判断两个值是否近似相等（容差内）"""
    if b == 0:
        return False
    return abs(a - b) / abs(b) < tolerance


def zigzag(close, step=3):
    """
    计算zigzag转折点

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - 滑动窗口半径，默认3

    Returns
    -------
    dict: {
        'pivots': numpy array (1=峰, -1=谷, 0=无),
        'indices': list of pivot indices,
        'values': list of pivot prices,
        'types': list of pivot types (1 or -1)
    }
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    indices = _create_index(pivots)
    values = [close[i] for i in indices]
    types = [int(pivots[i]) for i in indices]
    
    return {
        'pivots': pivots,
        'indices': indices,
        'values': values,
        'types': types
    }


def detect_w_bottom(close, step=3, min_depth_pct=0.05):
    """
    检测W底形态（双重底）
    提取自 KlangAlpha/Klang patterns.py

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - zigzag窗口半径
    min_depth_pct : float - 最小深度百分比

    Returns
    -------
    list of dict: 每个检测到的W底包含位置和价格信息
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    pv_index = _create_index(pivots)
    
    results = []
    if len(pv_index) < 5:
        return results
    
    for i in range(0, len(pv_index) - 4):
        a = pv_index[i]
        b = pv_index[i + 1]
        c = pv_index[i + 2]
        d = pv_index[i + 3]
        e = pv_index[i + 4]
        ab = close[a] - close[b]
        ad = close[a] - close[d]

        # b,d 为双底，a,e为顶
        if pivots[a] == 1 and _approx(ab, ad, 0.05) and ab / close[b] > min_depth_pct:
            results.append({
                'type': 'w-bottom',
                'left_peak': int(a),
                'first_bottom': int(b),
                'middle_peak': int(c),
                'second_bottom': int(d),
                'right_peak': int(e),
                'bottom_price': float((close[b] + close[d]) / 2),
                'peak_price': float(close[a]),
                'depth_pct': float(ab / close[b] * 100)
            })
    
    return results


def detect_v_reversal(close, step=3, min_drop_pct=0.03, max_recovery_ratio=0.8):
    """
    检测V型反转形态
    特征：急跌后快速反弹，跌幅大但恢复快

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - zigzag窗口半径
    min_drop_pct : float - 最小跌幅百分比
    max_recovery_ratio : float - 最大恢复周期比（恢复周期/下跌周期）

    Returns
    -------
    list of dict: 每个检测到的V型反转包含位置和价格信息
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    pv_index = _create_index(pivots)
    
    results = []
    if len(pv_index) < 3:
        return results
    
    for i in range(0, len(pv_index) - 2):
        a = pv_index[i]      # 起始高点
        b = pv_index[i + 1]  # 最低点（谷）
        c = pv_index[i + 2]  # 反弹高点
        
        if pivots[a] != 1 or pivots[b] != -1 or pivots[c] != 1:
            continue
        
        drop = close[a] - close[b]
        recovery = close[c] - close[b]
        drop_pct = drop / close[a]
        
        # 跌幅足够大
        if drop_pct < min_drop_pct:
            continue
        
        # 反弹幅度要大（至少恢复跌幅的60%）
        if recovery / drop < 0.6:
            continue
        
        # 反弹速度快（周期比小）
        down_bars = b - a
        up_bars = c - b
        if down_bars <= 0:
            continue
        
        recovery_ratio = up_bars / down_bars
        if recovery_ratio > max_recovery_ratio:
            continue
        
        results.append({
            'type': 'v-reversal',
            'peak': int(a),
            'bottom': int(b),
            'recovery_peak': int(c),
            'drop_pct': float(drop_pct * 100),
            'recovery_pct': float(recovery / drop * 100),
            'speed_ratio': float(recovery_ratio)
        })
    
    return results


def detect_cup_handle(close, step=3, max_cup_depth_pct=0.30):
    """
    检测杯柄形态（Cup and Handle）
    提取自 KlangAlpha/Klang patterns.py

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - zigzag窗口半径
    max_cup_depth_pct : float - 最大杯深度百分比

    Returns
    -------
    list of dict: 每个检测到的杯柄形态包含位置和价格信息
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    pv_index = _create_index(pivots)
    
    results = []
    if len(pv_index) < 6:
        return results
    
    for i in range(0, len(pv_index) - 5):
        x1 = pv_index[i]
        a = pv_index[i + 1]
        b = pv_index[i + 2]
        c = pv_index[i + 3]
        d = pv_index[i + 4]
        e = pv_index[i + 5]
        
        # a,c 杯沿差不多高，杯底b，比杯柄低，回调不能超过杯底部1/3
        ab = close[a] - close[b]
        cb = close[c] - close[b]
        cd = close[c] - close[d]
        
        if pivots[x1] == -1 and cb > 0 and abs(ab - cb) / cb < 0.15 and \
            close[b] < close[d] and cb / 3 > cd:
            results.append({
                'type': 'cup-handle',
                'cup_left_rim': int(a),
                'cup_bottom': int(b),
                'cup_right_rim': int(c),
                'handle_dip': int(d),
                'handle_end': int(e),
                'cup_depth': float(cb),
                'handle_depth': float(cd),
                'depth_pct': float(cb / close[b] * 100)
            })
    
    return results


def detect_triple_bottom(close, step=3, min_depth_pct=0.05):
    """
    检测三重底形态
    提取自 KlangAlpha/Klang patterns.py

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - zigzag窗口半径
    min_depth_pct : float - 最小深度百分比

    Returns
    -------
    list of dict: 每个检测到的三重底包含位置和价格信息
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    pv_index = _create_index(pivots)
    
    results = []
    if len(pv_index) < 6:
        return results
    
    for i in range(0, len(pv_index) - 5):
        a = pv_index[i]
        b = pv_index[i + 1]
        c = pv_index[i + 2]
        d = pv_index[i + 3]
        e = pv_index[i + 4]
        f = pv_index[i + 5]
        ab = close[a] - close[b]
        ad = close[a] - close[d]
        af = close[a] - close[f]

        # b,d,f 为三底，a，e为顶
        if pivots[a] == 1 and _approx(ab, ad, 0.05) and \
            _approx(ab, af, 0.05) and ab / close[b] > min_depth_pct:
            results.append({
                'type': 'triple-bottom',
                'peak': int(a),
                'bottom1': int(b),
                'bottom2': int(d),
                'bottom3': int(f),
                'bottom_price': float((close[b] + close[d] + close[f]) / 3),
                'depth_pct': float(ab / close[b] * 100)
            })
    
    return results


def detect_dip_buy(close, step=3, min_rise_pct=0.10, max_retrace_ratio=0.50):
    """
    检测上攻回调买入形态
    提取自 KlangAlpha/Klang patterns.py

    Parameters
    ----------
    close : array-like - 收盘价序列
    step : int - zigzag窗口半径
    min_rise_pct : float - 最小上涨幅度百分比
    max_retrace_ratio : float - 最大回撤比例

    Returns
    -------
    list of dict: 每个检测到的回调买入包含位置和价格信息
    """
    close = np.array(close, dtype=float)
    pivots = peak_valley_pivots_np(close, step=step)
    pv_index = _create_index(pivots)
    
    results = []
    if len(pivots) < 3:
        return results
    
    # 取最后5个转折点
    last_index = pv_index[-5:] if len(pv_index) >= 5 else pv_index
    for i in range(0, len(last_index) - 2):
        a = last_index[i]
        b = last_index[i + 1]
        c = last_index[i + 2]
        ba = close[b] - close[a]
        bc = close[b] - close[c]
        
        # a 为起涨点，b为高点，c为回调点, 跌幅不能超过50%
        if pivots[a] == -1 and ba / close[b] > min_rise_pct and bc / ba < max_retrace_ratio:
            results.append({
                'type': 'dip-buy',
                'start': int(a),
                'peak': int(b),
                'dip': int(c),
                'rise_pct': float(ba / close[a] * 100),
                'retrace_pct': float(bc / ba * 100),
            })
    
    return results


# 模式名称到检测函数的映射
PATTERN_MAP = {
    'zigzag': zigzag,
    'w-bottom': detect_w_bottom,
    'v-reversal': detect_v_reversal,
    'cup-handle': detect_cup_handle,
    'triple-bottom': detect_triple_bottom,
    'dip-buy': detect_dip_buy,
}
