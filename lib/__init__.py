"""
a-stock-data-quant: A股量化分析工具箱
整合行情数据、技术指标、形态识别、策略回测
"""

from .mytt import *
from .ashare import get_price
from .patterns import zigzag, detect_w_bottom, detect_v_reversal, detect_cup_handle, detect_triple_bottom, detect_dip_buy, PATTERN_MAP
from .strategies import STRATEGY_MAP, STRATEGY_DESC
from .backtest import backtest, BacktestResult

__version__ = "1.0.0"
__all__ = [
    # 行情数据
    "get_price",
    # 形态识别
    "zigzag", "detect_w_bottom", "detect_v_reversal", "detect_cup_handle",
    "detect_triple_bottom", "PATTERN_MAP",
    # 策略
    "STRATEGY_MAP", "STRATEGY_DESC",
    # 回测
    "backtest", "BacktestResult",
]
