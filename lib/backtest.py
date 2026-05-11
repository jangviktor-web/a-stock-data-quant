"""
回测引擎模块 - 灵感来自 ScottZt/jin-ce-zhi-suan
简化版信号回测：P&L计算、胜率、最大回撤、夏普比率
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Callable, Optional, List, Dict


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float = 0.0          # 总收益率 %
    annual_return: float = 0.0         # 年化收益率 %
    max_drawdown: float = 0.0          # 最大回撤 %
    sharpe_ratio: float = 0.0          # 夏普比率
    calmar_ratio: float = 0.0          # 卡玛比率（年化收益/最大回撤）
    win_rate: float = 0.0              # 胜率 %
    total_trades: int = 0              # 总交易次数
    winning_trades: int = 0            # 盈利次数
    losing_trades: int = 0             # 亏损次数
    avg_win: float = 0.0               # 平均盈利 %
    avg_loss: float = 0.0              # 平均亏损 %
    profit_factor: float = 0.0         # 盈亏比
    max_consecutive_losses: int = 0    # 最大连续亏损次数
    avg_holding_days: float = 0.0      # 平均持仓天数
    final_capital: float = 0.0         # 最终资金
    trades: list = field(default_factory=list)  # 交易记录
    equity_curve: list = field(default_factory=list)  # 权益曲线
    start_date: str = ''               # 回测起始日期
    end_date: str = ''                 # 回测结束日期
    initial_capital: float = 0.0       # 初始资金
    buy_hold_return: float = 0.0       # 长期持有收益率 %
    buy_hold_final: float = 0.0        # 长期持有最终资金

    def to_dict(self):
        return {
            'total_return': round(self.total_return, 2),
            'annual_return': round(self.annual_return, 2),
            'max_drawdown': round(self.max_drawdown, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 4),
            'calmar_ratio': round(self.calmar_ratio, 2),
            'win_rate': round(self.win_rate, 2),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': round(self.avg_win, 2),
            'avg_loss': round(self.avg_loss, 2),
            'profit_factor': round(self.profit_factor, 2),
            'max_consecutive_losses': self.max_consecutive_losses,
            'avg_holding_days': round(self.avg_holding_days, 1),
            'final_capital': round(self.final_capital, 2),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'buy_hold_return': round(self.buy_hold_return, 2),
            'buy_hold_final': round(self.buy_hold_final, 2),
        }


def backtest(df, signal_func, capital=100000, commission=0.001, slippage=0.001,
             position_size=1.0, stop_loss=None, take_profit=None, lot_size=100, **kwargs):
    """
    简化版信号回测引擎

    Parameters
    ----------
    df : DataFrame - 必须包含 close 列，可选 high, low, volume 列，index 为日期
    signal_func : callable - 信号函数，接收 df 返回 numpy array (1=买, -1=卖, 0=无)
    capital : float - 初始资金
    commission : float - 手续费率 (如 0.001 = 0.1%)
    slippage : float - 滑点率
    position_size : float - 仓位比例 (0-1)
    stop_loss : float or None - 止损比例 (如 0.05 = 5%)
    take_profit : float or None - 止盈比例 (如 0.10 = 10%)
    lot_size : int - 最小交易单位 (A股默认100, 设为1允许零股/模拟全额买入)
    **kwargs : 传递给 signal_func 的额外参数

    Returns
    -------
    BacktestResult - 回测结果
    """
    close = df['close'].values
    n = len(close)

    # 获取日期序列
    dates = None
    if hasattr(df.index, 'strftime'):
        dates = df.index
    elif 'date' in df.columns:
        dates = df['date'].values

    def _get_date(i):
        if dates is not None and i < len(dates):
            try:
                return str(dates[i])[:10]
            except:
                return str(dates[i])
        return f"第{i}天"

    # 生成信号
    if kwargs:
        signals = signal_func(df, **kwargs)
    else:
        signals = signal_func(df)

    # 初始化
    cash = capital
    position = 0         # 持仓数量
    entry_price = 0.0    # 入场价格
    trades = []          # 交易记录
    equity_curve = []    # 权益曲线

    for i in range(n):
        price = close[i]

        # 计算当前权益
        equity = cash + position * price
        equity_curve.append(equity)

        # 检查止损止盈
        if position > 0:
            pnl_pct = (price - entry_price) / entry_price

            # 止损
            if stop_loss and pnl_pct <= -stop_loss:
                sell_price = price * (1 - slippage)
                proceeds = position * sell_price * (1 - commission)
                cash += proceeds
                trades.append({
                    'type': 'sell',
                    'reason': 'stop_loss',
                    'price': sell_price,
                    'qty': position,
                    'pnl_pct': pnl_pct * 100,
                    'date': _get_date(i),
                    'cost': 0,
                    'amount': position * sell_price * (1 - commission),
                })
                position = 0
                entry_price = 0.0
                continue

            # 止盈
            if take_profit and pnl_pct >= take_profit:
                sell_price = price * (1 - slippage)
                proceeds = position * sell_price * (1 - commission)
                cash += proceeds
                trades.append({
                    'type': 'sell',
                    'reason': 'take_profit',
                    'price': sell_price,
                    'qty': position,
                    'pnl_pct': pnl_pct * 100,
                    'date': _get_date(i),
                    'cost': 0,
                    'amount': position * sell_price * (1 - commission),
                })
                position = 0
                entry_price = 0.0
                continue

        # 处理信号
        sig = signals[i] if i < len(signals) else 0

        if sig == 1 and position == 0:
            # 买入
            buy_price = price * (1 + slippage)
            max_qty = int((cash * position_size) / (buy_price * (1 + commission)))
            if lot_size > 1:
                max_qty = (max_qty // lot_size) * lot_size
            if max_qty == 0 and cash > buy_price * (1 + commission):
                max_qty = 1  # 资金不足一手时允许零股（回测模拟）
            if max_qty > 0:
                cost = max_qty * buy_price * (1 + commission)
                cash -= cost
                position = max_qty
                entry_price = buy_price
                trades.append({
                    'type': 'buy',
                    'reason': 'signal',
                    'price': buy_price,
                    'qty': max_qty,
                    'pnl_pct': 0,
                    'date': _get_date(i),
                    'cost': cost,
                    'amount': max_qty * buy_price,
                })

        elif sig == -1 and position > 0:
            # 卖出
            sell_price = price * (1 - slippage)
            proceeds = position * sell_price * (1 - commission)
            pnl_pct = (sell_price - entry_price) / entry_price * 100
            cash += proceeds
            trades.append({
                'type': 'sell',
                'reason': 'signal',
                'price': sell_price,
                'qty': position,
                'pnl_pct': pnl_pct,
                'date': _get_date(i),
                'cost': 0,
                'amount': position * sell_price * (1 - commission),
            })
            position = 0
            entry_price = 0.0

    # 如果还有持仓，按最后价格平仓
    if position > 0:
        final_price = close[-1] * (1 - slippage)
        proceeds = position * final_price * (1 - commission)
        pnl_pct = (final_price - entry_price) / entry_price * 100
        cash += proceeds
        trades.append({
            'type': 'sell',
            'reason': 'end_of_data',
            'price': final_price,
            'qty': position,
            'pnl_pct': pnl_pct,
            'date': _get_date(n - 1),
            'cost': 0,
            'amount': position * final_price * (1 - commission),
        })
        position = 0

    # 计算结果
    final_capital = cash
    total_return = (final_capital - capital) / capital * 100

    # 计算年化收益率
    trading_days = n
    if trading_days > 1:
        annual_return = ((final_capital / capital) ** (252 / trading_days) - 1) * 100
    else:
        annual_return = 0.0

    # 计算最大回撤
    equity_arr = np.array(equity_curve)
    max_drawdown = 0.0
    if len(equity_arr) > 0:
        peak = np.maximum.accumulate(equity_arr)
        drawdown = (peak - equity_arr) / peak
        max_drawdown = float(np.max(drawdown)) * 100

    # 计算夏普比率
    if len(equity_arr) > 1:
        returns = np.diff(equity_arr) / equity_arr[:-1]
        if np.std(returns) > 0:
            sharpe_ratio = float(np.mean(returns) / np.std(returns) * np.sqrt(252))
        else:
            sharpe_ratio = 0.0
    else:
        sharpe_ratio = 0.0

    # 计算胜率和盈亏比
    sell_trades = [t for t in trades if t['type'] == 'sell']
    total_trades = len(sell_trades)
    winning_trades = len([t for t in sell_trades if t['pnl_pct'] > 0])
    losing_trades = len([t for t in sell_trades if t['pnl_pct'] <= 0])

    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

    wins = [t['pnl_pct'] for t in sell_trades if t['pnl_pct'] > 0]
    losses = [t['pnl_pct'] for t in sell_trades if t['pnl_pct'] <= 0]
    avg_win = float(np.mean(wins)) if wins else 0.0
    avg_loss = float(np.mean(losses)) if losses else 0.0

    total_win = sum(wins) if wins else 0.0
    total_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = (total_win / total_loss) if total_loss > 0 else float('inf') if total_win > 0 else 0.0

    # 计算最大连续亏损
    max_consecutive_losses = 0
    current_streak = 0
    for t in sell_trades:
        if t['pnl_pct'] <= 0:
            current_streak += 1
            max_consecutive_losses = max(max_consecutive_losses, current_streak)
        else:
            current_streak = 0

    # 计算平均持仓天数（用交易次数近似）
    buy_indices = [i for i, t in enumerate(trades) if t['type'] == 'buy']
    sell_indices = [i for i, t in enumerate(trades) if t['type'] == 'sell']
    holding_periods = []
    for bi, si in zip(buy_indices, sell_indices):
        if si > bi:
            holding_periods.append(si - bi)
    avg_holding_days = float(np.mean(holding_periods)) if holding_periods else 0.0

    # 卡玛比率
    calmar_ratio = (annual_return / max_drawdown) if max_drawdown > 0 else 0.0

    # 日期范围
    start_date = _get_date(0)
    end_date = _get_date(n - 1)

    # 长期持有收益（第一天买入，最后一天卖出）
    bh_buy_price = close[0] * (1 + slippage)
    bh_sell_price = close[-1] * (1 - slippage)
    bh_qty = int(capital / (bh_buy_price * (1 + commission)))
    bh_cost = bh_qty * bh_buy_price * (1 + commission)
    bh_proceeds = bh_qty * bh_sell_price * (1 - commission)
    bh_final = (capital - bh_cost) + bh_proceeds
    bh_return = (bh_final - capital) / capital * 100

    return BacktestResult(
        total_return=total_return,
        annual_return=annual_return,
        max_drawdown=max_drawdown,
        sharpe_ratio=sharpe_ratio,
        calmar_ratio=calmar_ratio,
        win_rate=win_rate,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        avg_win=avg_win,
        avg_loss=avg_loss,
        profit_factor=profit_factor,
        max_consecutive_losses=max_consecutive_losses,
        avg_holding_days=avg_holding_days,
        final_capital=final_capital,
        trades=trades,
        equity_curve=equity_curve,
        start_date=start_date,
        end_date=end_date,
        initial_capital=capital,
        buy_hold_return=bh_return,
        buy_hold_final=bh_final,
    )
