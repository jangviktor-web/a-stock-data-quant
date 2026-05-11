"""
内置策略模块 - 灵感来自 ScottZt/jin-ce-zhi-suan
包含: MA交叉、MACD信号、RSI超买超卖、布林带、KDJ交叉
"""

import numpy as np
import pandas as pd
from . import mytt


def strategy_ma_cross(df, short=5, long=20):
    """
    均线交叉策略（金叉/死叉）
    金叉买入，死叉卖出

    Parameters
    ----------
    df : DataFrame - 包含 close 列
    short : int - 短期均线周期
    long : int - 长期均线周期

    Returns
    -------
    numpy array - 1=买入信号, -1=卖出信号, 0=无信号
    """
    close = df['close'].values
    ma_short = mytt.MA(close, short)
    ma_long = mytt.MA(close, long)
    
    # 金叉: 短均线上穿长均线
    golden_cross = mytt.CROSS(ma_short, ma_long)
    # 死叉: 短均线下穿长均线
    death_cross = mytt.CROSS(ma_long, ma_short)
    
    signals = np.zeros(len(close))
    signals[golden_cross] = 1
    signals[death_cross] = -1
    return signals


def strategy_macd(df, short=12, long=26, m=9):
    """
    MACD策略
    DIF上穿DEA买入，DIF下穿DEA卖出

    Parameters
    ----------
    df : DataFrame - 包含 close 列
    short : int - 短期EMA周期
    long : int - 长期EMA周期
    m : int - 信号线周期

    Returns
    -------
    numpy array - 1=买入信号, -1=卖出信号, 0=无信号
    """
    close = df['close'].values
    dif, dea, macd = mytt.MACD(close, short, long, m)
    
    golden_cross = mytt.CROSS(dif, dea)
    death_cross = mytt.CROSS(dea, dif)
    
    signals = np.zeros(len(close))
    signals[golden_cross] = 1
    signals[death_cross] = -1
    return signals


def strategy_rsi(df, n=14, oversold=30, overbought=70):
    """
    RSI超买超卖策略
    RSI低于oversold买入，高于overbought卖出

    Parameters
    ----------
    df : DataFrame - 包含 close 列
    n : int - RSI周期
    oversold : float - 超卖阈值
    overbought : float - 超买阈值

    Returns
    -------
    numpy array - 1=买入信号, -1=卖出信号, 0=无信号
    """
    close = df['close'].values
    rsi = mytt.RSI(close, n)
    
    signals = np.zeros(len(close))
    # 从超卖区域上穿
    buy_cond = (rsi > oversold) & (np.roll(rsi, 1) <= oversold)
    # 从超买区域下穿
    sell_cond = (rsi < overbought) & (np.roll(rsi, 1) >= overbought)
    
    buy_cond[0] = False
    sell_cond[0] = False
    
    signals[buy_cond] = 1
    signals[sell_cond] = -1
    return signals


def strategy_boll(df, n=20, p=2):
    """
    布林带策略
    价格触及下轨买入，触及上轨卖出

    Parameters
    ----------
    df : DataFrame - 包含 close 列
    n : int - 布林带周期
    p : int - 标准差倍数

    Returns
    -------
    numpy array - 1=买入信号, -1=卖出信号, 0=无信号
    """
    close = df['close'].values
    upper, mid, lower = mytt.BOLL(close, n, p)
    
    signals = np.zeros(len(close))
    # 价格从下方触及下轨后回升
    buy_cond = (close > lower) & (np.roll(close, 1) <= np.roll(lower, 1))
    # 价格从上方触及上轨后回落
    sell_cond = (close < upper) & (np.roll(close, 1) >= np.roll(upper, 1))
    
    buy_cond[0] = False
    sell_cond[0] = False
    
    signals[buy_cond] = 1
    signals[sell_cond] = -1
    return signals


def strategy_buy_hold(df):
    """
    长期持有策略（Buy & Hold）
    第一天买入信号，之后无操作，最后一天平仓由回测引擎自动处理

    Returns
    -------
    numpy array - 第一个元素=1(买入), 其余=0(持有不动)
    """
    close = df['close'].values
    signals = np.zeros(len(close))
    signals[0] = 1  # 第一天买入
    return signals


def strategy_kdj(df, n=9, m1=3, m2=3):
    """
    KDJ金叉死叉策略
    K上穿D买入，K下穿D卖出

    Parameters
    ----------
    df : DataFrame - 包含 close, high, low 列
    n : int - KDJ的N周期
    m1 : int - K的平滑参数
    m2 : int - D的平滑参数

    Returns
    -------
    numpy array - 1=买入信号, -1=卖出信号, 0=无信号
    """
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    k, d, j = mytt.KDJ(close, high, low, n, m1, m2)
    
    golden_cross = mytt.CROSS(k, d)
    death_cross = mytt.CROSS(d, k)
    
    signals = np.zeros(len(close))
    signals[golden_cross] = 1
    signals[death_cross] = -1
    return signals


def strategy_ensemble(df, strategies=None, min_agree=3, **kwargs):
    """
    多策略组合（共振）策略
    N个策略中至少min_agree个同时看多才出买入信号，反之出卖出信号

    Parameters
    ----------
    df : DataFrame
    strategies : list - 参与组合的策略名列表，默认全部（不含buy_hold）
    min_agree : int - 最少同意数，默认3

    Returns
    -------
    numpy array - 1=买入, -1=卖出, 0=无信号
    """
    if strategies is None:
        strategies = ['ma_cross', 'macd', 'rsi', 'boll', 'kdj']

    all_signals = {}
    for name in strategies:
        if name in STRATEGY_MAP and name != 'buy_hold':
            all_signals[name] = STRATEGY_MAP[name](df)

    n = len(df['close'].values)
    buy_votes = np.zeros(n)
    sell_votes = np.zeros(n)

    for name, sigs in all_signals.items():
        buy_votes[sigs == 1] += 1
        sell_votes[sigs == -1] += 1

    signals = np.zeros(n)
    signals[buy_votes >= min_agree] = 1
    signals[sell_votes >= min_agree] = -1

    # 避免同一天买卖冲突（取多数）
    conflict = (signals == 1) & (sell_votes > buy_votes)
    signals[conflict] = -1
    conflict2 = (signals == -1) & (buy_votes > sell_votes)
    signals[conflict2] = 1

    return signals


# 策略名称到函数的映射
STRATEGY_MAP = {
    'buy_hold': strategy_buy_hold,
    'ma_cross': strategy_ma_cross,
    'macd': strategy_macd,
    'rsi': strategy_rsi,
    'boll': strategy_boll,
    'kdj': strategy_kdj,
    'ensemble': strategy_ensemble,
}

# 策略描述（中文）
STRATEGY_DESC = {
    'buy_hold': '长期持有策略 (买入不动)',
    'ma_cross': '均线金叉/死叉策略',
    'macd': 'MACD DIF/DEA交叉策略',
    'rsi': 'RSI超买超卖策略',
    'boll': '布林带轨道反弹策略',
    'kdj': 'KDJ金叉/死叉策略',
    'ensemble': '多策略共振组合 (≥N个策略同时看多)',
}
