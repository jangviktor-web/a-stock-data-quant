#!/usr/bin/env python3
"""
quant-china CLI 入口
A股量化分析工具箱 - 行情数据、技术指标、形态识别、策略回测
"""

import sys
import os

# 修复 Windows 编码问题（参考 stock-quant 的编码处理）
if sys.platform == 'win32':
    os.environ['PYTHONUTF8'] = '1'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json

# 添加上级目录到路径，以便导入lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.ashare import get_price
from lib import mytt
from lib.patterns import PATTERN_MAP, zigzag
from lib.strategies import STRATEGY_MAP, STRATEGY_DESC, strategy_ensemble
from lib.backtest import backtest
from lib.data_cache import cached_fetch
from lib.settings import get as cfg

try:
    from lib.akshare_data import get_fund_flow, get_sector_hot, get_margin_data, get_sector_list
    HAS_AKSHARE_DATA = True
except ImportError:
    HAS_AKSHARE_DATA = False

try:
    from lib import em_api
    HAS_EM_API = True
except ImportError:
    HAS_EM_API = False

try:
    from lib.realtime_data import get_realtime, search_stock, format_realtime
    HAS_REALTIME = True
except ImportError:
    HAS_REALTIME = False


# ── 工具函数 ──────────────────────────────────────────────

def _fetch(code, count, period, end='', use_cache=True):
    """获取行情数据，带缓存和网络错误处理"""
    try:
        if use_cache:
            df = cached_fetch(code, count, period, end,
                              fetch_func=lambda c, n, p, e: get_price(c, end_date=e or '', count=n, frequency=p))
        else:
            df = get_price(code, end_date=end or '', count=count, frequency=period)
        if df is None or df.empty:
            print(f"  错误: 未获取到 {code} 的数据，请检查股票代码是否正确")
            print(f"  提示: 沪市用 sh 前缀 (如 sh600519)，深市用 sz 前缀 (如 sz000001)")
            sys.exit(1)
        return df
    except Exception as e:
        print(f"  错误: 获取数据失败 - {e}")
        print(f"  提示: 请检查网络连接和股票代码")
        sys.exit(1)


def fmt_table(df, max_rows=30):
    """格式化DataFrame为文本表格"""
    if df is None or df.empty:
        return "无数据"
    show = df.tail(max_rows)
    lines = []
    cols = list(show.index.names) + list(show.columns)
    lines.append("  ".join(f"{c:>12s}" for c in cols if c))
    lines.append("-" * (14 * len(cols)))
    for idx, row in show.iterrows():
        vals = []
        if show.index.name:
            vals.append(str(idx)[:12])
        elif hasattr(idx, '__iter__'):
            for v in idx:
                vals.append(str(v)[:12])
        else:
            vals.append(str(idx)[:12])
        for v in row:
            if isinstance(v, float):
                vals.append(f"{v:>12.2f}")
            else:
                vals.append(f"{str(v):>12s}")
        lines.append("  ".join(vals))
    return "\n".join(lines)


def to_json(obj):
    """将numpy类型转为JSON可序列化的Python类型"""
    import numpy as np
    def _convert(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, dict):
            return {k: _convert(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_convert(v) for v in o]
        return o
    return _convert(obj)


# ── 子命令 ────────────────────────────────────────────────

def cmd_data(args):
    """获取行情数据"""
    df = _fetch(args.code, args.count, args.period, args.end)

    if args.json:
        print(json.dumps(to_json(json.loads(df.to_json(orient='records', date_format='iso'))), ensure_ascii=False, indent=2))
    else:
        close = df['close'].values
        print(f"\n{'='*60}")
        print(f"  股票代码: {args.code}  周期: {args.period}  数量: {len(df)}")
        print(f"{'='*60}")
        print(fmt_table(df))
        # 摘要统计
        if len(close) >= 2:
            change = (close[-1] - close[-2]) / close[-2] * 100
            high_val = max(close)
            low_val = min(close)
            avg_val = sum(close) / len(close)
            print(f"\n  最新: {close[-1]:.2f}  涨跌: {change:+.2f}%  最高: {high_val:.2f}  最低: {low_val:.2f}  均价: {avg_val:.2f}")
        print(f"  共 {len(df)} 条数据")


def cmd_indicators(args):
    """计算技术指标"""
    df = _fetch(args.code, args.count, args.period, args.end)

    close = df['close'].values
    high = df['high'].values if 'high' in df.columns else close
    low = df['low'].values if 'low' in df.columns else close
    volume = df['volume'].values if 'volume' in df.columns else None

    indicators = [s.strip().lower() for s in args.indicators.split(',')]
    result = df.copy()

    for ind in indicators:
        if ind == 'macd':
            dif, dea, macd = mytt.MACD(close)
            result['DIF'] = dif
            result['DEA'] = dea
            result['MACD'] = macd
        elif ind == 'boll':
            upper, mid, lower = mytt.BOLL(close)
            result['BOLL_U'] = upper
            result['BOLL_M'] = mid
            result['BOLL_L'] = lower
        elif ind == 'kdj':
            k, d, j = mytt.KDJ(close, high, low)
            result['K'] = k
            result['D'] = d
            result['J'] = j
        elif ind == 'cci':
            result['CCI'] = mytt.CCI(close, high, low)
        elif ind == 'wr':
            wr, wr1 = mytt.WR(close, high, low)
            result['WR'] = wr
            result['WR1'] = wr1
        elif ind == 'bias':
            b1, b2, b3 = mytt.BIAS(close)
            result['BIAS6'] = b1
            result['BIAS12'] = b2
            result['BIAS24'] = b3
        elif ind == 'obv' and volume is not None:
            result['OBV'] = mytt.OBV(close, volume)
        elif ind.startswith('atr'):
            n = int(ind[3:]) if len(ind) > 3 else 20
            result[f'ATR{n}'] = mytt.ATR(close, high, low, n)
        elif ind.startswith('ema'):
            n = int(ind[3:])
            result[f'EMA{n}'] = mytt.EMA(close, n)
        elif ind.startswith('rsi'):
            n = int(ind[3:]) if len(ind) > 3 else 14
            result[f'RSI{n}'] = mytt.RSI(close, n)
        elif ind.startswith('ma'):
            n = int(ind[2:])
            result[f'MA{n}'] = mytt.MA(close, n)
        else:
            print(f"  [警告] 未识别的指标: {ind}  (可用: maN, emaN, macd, rsi, boll, kdj, atr, cci, wr, bias, obv)")

    if args.json:
        print(json.dumps(to_json(json.loads(result.to_json(orient='records', date_format='iso'))), ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  股票代码: {args.code}  周期: {args.period}  指标: {args.indicators}")
        print(f"{'='*60}")
        print(fmt_table(result))
        print(f"\n  共 {len(result)} 条数据")


def cmd_pattern(args):
    """形态识别"""
    df = _fetch(args.code, args.count, args.period, args.end)

    close = df['close'].values
    patterns = [s.strip().lower() for s in args.pattern.split(',')]

    results_all = {}
    for pat in patterns:
        if pat in PATTERN_MAP:
            results_all[pat] = PATTERN_MAP[pat](close)
        else:
            print(f"  [警告] 未识别的形态: {pat}")
            print(f"  可用形态: {', '.join(PATTERN_MAP.keys())}")

    if args.json:
        print(json.dumps(to_json(results_all), ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  股票代码: {args.code}  周期: {args.period}  数据: {len(close)} 条")
        print(f"{'='*60}")
        for pat, result in results_all.items():
            print(f"\n  [{pat}]")
            if pat == 'zigzag':
                zz = result
                print(f"    转折点数: {len(zz['indices'])}")
                for j, (idx, val, typ) in enumerate(zip(zz['indices'][-10:], zz['values'][-10:], zz['types'][-10:])):
                    t = "峰▲" if typ == 1 else "谷▼"
                    print(f"    [{idx:>4d}] {t} {val:.2f}")
            elif isinstance(result, list):
                if not result:
                    print(f"    未检测到该形态")
                else:
                    print(f"    检测到 {len(result)} 个形态:")
                    for r in result:
                        print(f"    {json.dumps(r, ensure_ascii=False)}")
            else:
                print(f"    {result}")


def cmd_backtest(args):
    """策略回测"""
    df = _fetch(args.code, args.count, args.period, args.end)

    if args.strategy not in STRATEGY_MAP:
        print(f"未知策略: {args.strategy}")
        print(f"可用策略: {', '.join(STRATEGY_MAP.keys())}")
        return

    # 长期持有策略用 lot_size=1 允许全额买入
    lot = 1 if args.strategy == 'buy_hold' else 100

    # 生成信号（用于图表标注）
    signals = STRATEGY_MAP[args.strategy](df)

    result = backtest(
        df,
        STRATEGY_MAP[args.strategy],
        capital=args.capital,
        commission=cfg('commission', 0.001),
        slippage=cfg('slippage', 0.001),
        position_size=cfg('position_size', 1.0),
        stop_loss=args.stop_loss,
        take_profit=args.take_profit,
        lot_size=lot,
    )

    # HTML 图表输出（参考 stock-quant 的 html 目录设计）
    if hasattr(args, 'html') and args.html:
        from lib.chart import save_backtest_chart
        filepath = save_backtest_chart(args.code, df, result, args.strategy, signals)
        print(f"\n  HTML 图表已保存: {filepath}")

    if args.json:
        output = result.to_dict()
        output['trades'] = result.trades[-20:]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        d = result.to_dict()

        # ── 回测概览 ──
        print(f"\n{'='*64}")
        print(f"  🧪 回测报告: {args.code}  策略: {args.strategy} ({STRATEGY_DESC.get(args.strategy, '')})")
        print(f"{'='*64}")
        print(f"  回测区间: {d['start_date']}  →  {d['end_date']}")
        print(f"  数据周期: {args.period}  K线数: {len(df)}")
        print(f"  初始资金: {d['initial_capital']:,.0f} 元")

        # ── 核心指标 ──
        print(f"\n{'─'*64}")
        print(f"  📊 核心指标")
        print(f"{'─'*64}")
        labels = [
            ('total_return', '策略总收益'),
            ('annual_return', '策略年化'),
            ('buy_hold_return', '长期持有收益'),
            ('max_drawdown', '最大回撤'),
            ('sharpe_ratio', '夏普比率'),
            ('calmar_ratio', '卡玛比率'),
            ('win_rate', '胜率'),
            ('profit_factor', '盈亏比'),
        ]
        for k, label in labels:
            v = d[k]
            suffix = '%' if 'return' in k or 'drawdown' in k or 'rate' in k else ''
            print(f"  {label:<14s} {v:>10.2f}{suffix}")

        print(f"\n  策略最终资金: {d['final_capital']:>12,.0f} 元")
        print(f"  长期持有资金: {d['buy_hold_final']:>12,.0f} 元")
        diff = d['final_capital'] - d['buy_hold_final']
        if diff > 0:
            print(f"  → 策略跑赢长期持有 {diff:+,.0f} 元 ✅")
        else:
            print(f"  → 策略跑输长期持有 {diff:+,.0f} 元 ❌")

        # ── 交易统计 ──
        print(f"\n{'─'*64}")
        print(f"  📈 交易统计")
        print(f"{'─'*64}")
        print(f"  总交易次数:   {d['total_trades']}")
        print(f"  盈利次数:     {d['winning_trades']}")
        print(f"  亏损次数:     {d['losing_trades']}")
        print(f"  平均盈利:     {d['avg_win']:+.2f}%")
        print(f"  平均亏损:     {d['avg_loss']:+.2f}%")
        print(f"  最大连亏:     {d['max_consecutive_losses']} 次")
        print(f"  平均持仓:     {d['avg_holding_days']:.1f} 天")

        # ── 交易明细 ──
        if result.trades:
            print(f"\n{'─'*80}")
            print(f"  📋 交易明细 (共 {len(result.trades)} 笔)")
            print(f"{'─'*80}")
            print(f"  {'日期':<12s} {'方向':>4s} {'价格':>10s} {'数量':>8s} {'金额':>12s} {'剩余资金':>12s} {'盈亏%':>8s} {'原因':>10s}")
            print(f"  {'-'*82}")
            running_cash = d['initial_capital']
            for t in result.trades:
                direction = "买入" if t['type'] == 'buy' else "卖出"
                date_str = t.get('date', '—')
                amount = t.get('amount', 0)
                cost = t.get('cost', 0)
                if t['type'] == 'buy':
                    running_cash -= cost
                else:
                    running_cash += amount
                print(f"  {date_str:<12s} {direction:>4s} {t['price']:>10.2f} {t['qty']:>8d} {amount:>12,.0f} {running_cash:>12,.0f} {t['pnl_pct']:>+8.2f} {t['reason']:>10s}")


def cmd_scan(args):
    """市场扫描"""
    scan_codes = [
        ('sh000001', '上证指数'),
        ('sz399001', '深证成指'),
        ('sz399006', '创业板指'),
        ('sh000300', '沪深300'),
        ('sh000016', '上证50'),
        ('sz399673', '创业板50'),
    ]

    if args.strategy not in STRATEGY_MAP:
        print(f"未知策略: {args.strategy}")
        print(f"可用策略: {', '.join(STRATEGY_MAP.keys())}")
        return

    print(f"\n{'='*70}")
    print(f"  市场扫描  策略: {args.strategy} ({STRATEGY_DESC.get(args.strategy, '')})")
    print(f"{'='*70}")
    print(f"  {'代码':<12s}  {'名称':<10s}  {'最新价':>10s}  {'涨跌%':>8s}  {'信号':>8s}")
    print(f"  {'-'*55}")

    buy_count = 0
    sell_count = 0

    for code, name in scan_codes:
        try:
            df = get_price(code, count=120, frequency='1d')
            if df is None or df.empty:
                continue

            if args.min_volume and 'volume' in df.columns:
                avg_vol = df['volume'].tail(5).mean()
                if avg_vol < args.min_volume:
                    continue

            signals = STRATEGY_MAP[args.strategy](df)
            last_signal = int(signals[-1]) if len(signals) > 0 else 0
            close = df['close'].values
            last_price = float(close[-1])
            change = (close[-1] - close[-2]) / close[-2] * 100 if len(close) >= 2 else 0

            if last_signal == 1:
                sig_str = "▲ 买入"
                buy_count += 1
            elif last_signal == -1:
                sig_str = "▼ 卖出"
                sell_count += 1
            else:
                sig_str = "  —"

            print(f"  {code:<12s}  {name:<10s}  {last_price:>10.2f}  {change:>+7.2f}%  {sig_str}")
        except Exception as e:
            print(f"  {code:<12s}  {name:<10s}  {'获取失败':>10s}  {'':>8s}  {str(e)[:20]}")

    print(f"\n  买入信号: {buy_count}  卖出信号: {sell_count}  无信号: {len(scan_codes)-buy_count-sell_count}")


def cmd_analyze(args):
    """综合分析 — 数据+指标+形态+策略信号+回测，一次出完整报告"""
    import numpy as np

    df = _fetch(args.code, args.count, args.period, args.end)
    close = df['close'].values
    high = df['high'].values if 'high' in df.columns else close
    low = df['low'].values if 'low' in df.columns else close
    volume = df['volume'].values if 'volume' in df.columns else None

    # ── 1. 行情概览 ──────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  📊 综合分析: {args.code}")
    print(f"{'='*60}")
    if len(close) >= 2:
        change = (close[-1] - close[-2]) / close[-2] * 100
    else:
        change = 0
    print(f"  最新价: {close[-1]:.2f}  涨跌: {change:+.2f}%")
    print(f"  区间高: {max(close):.2f}  区间低: {min(close):.2f}  均价: {np.mean(close):.2f}")
    if volume is not None:
        avg_vol = np.mean(volume[-5:])
        print(f"  近5日均量: {avg_vol:,.0f}")
    print(f"  数据: {len(df)} 条  周期: {args.period}")

    # ── 2. 技术指标 ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  📈 技术指标")
    print(f"{'─'*60}")

    # 均线系统
    for n in [5, 10, 20, 60]:
        ma = mytt.MA(close, n)
        val = ma[-1] if not np.isnan(ma[-1]) else 0
        diff = (close[-1] - val) / val * 100 if val else 0
        pos = "↑" if close[-1] > val else "↓"
        print(f"  MA{n:<3d}: {val:>10.2f}  {pos} 偏离 {diff:+.2f}%")

    # MACD
    dif, dea, macd_val = mytt.MACD(close)
    macd_signal = "金叉看多" if dif[-1] > dea[-1] else "死叉看空"
    print(f"  MACD:  DIF={dif[-1]:.3f}  DEA={dea[-1]:.3f}  MACD={macd_val[-1]:.3f}  → {macd_signal}")

    # RSI
    rsi14 = mytt.RSI(close, 14)
    rsi_val = rsi14[-1]
    if rsi_val > 70:
        rsi_signal = "超买 ⚠️"
    elif rsi_val < 30:
        rsi_signal = "超卖 ⚠️"
    else:
        rsi_signal = "中性"
    print(f"  RSI14: {rsi_val:.2f}  → {rsi_signal}")

    # KDJ
    k, d, j = mytt.KDJ(close, high, low)
    kdj_signal = "金叉看多" if k[-1] > d[-1] else "死叉看空"
    print(f"  KDJ:   K={k[-1]:.2f}  D={d[-1]:.2f}  J={j[-1]:.2f}  → {kdj_signal}")

    # 布林带
    boll_u, boll_m, boll_l = mytt.BOLL(close)
    boll_width = (boll_u[-1] - boll_l[-1]) / boll_m[-1] * 100
    if close[-1] > boll_u[-1]:
        boll_pos = "突破上轨 ⚠️"
    elif close[-1] < boll_l[-1]:
        boll_pos = "跌破下轨 ⚠️"
    else:
        boll_pos = f"轨道内 (带宽{boll_width:.1f}%)"
    print(f"  BOLL:  上={boll_u[-1]:.2f}  中={boll_m[-1]:.2f}  下={boll_l[-1]:.2f}  → {boll_pos}")

    # ATR 波动率
    atr20 = mytt.ATR(close, high, low, 20)
    atr_pct = atr20[-1] / close[-1] * 100
    print(f"  ATR20: {atr20[-1]:.2f}  波动率: {atr_pct:.2f}%")

    # ── 3. 形态识别 ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  🔍 形态识别")
    print(f"{'─'*60}")

    # 用足够的数据做形态检测
    pattern_count = max(len(close), 250)
    if pattern_count > len(close):
        pat_df = _fetch(args.code, pattern_count, args.period, args.end)
        pat_close = pat_df['close'].values
    else:
        pat_close = close

    for pat_name, pat_func in PATTERN_MAP.items():
        if pat_name == 'zigzag':
            continue  # zigzag 单独处理
        result = pat_func(pat_close)
        if isinstance(result, list) and result:
            print(f"  {pat_name}: 检测到 {len(result)} 个形态")
            for r in result[-3:]:  # 只显示最近3个
                if 'depth_pct' in r:
                    print(f"    · 位置[{r.get('first_bottom', r.get('bottom', '?'))}] 深度 {r['depth_pct']:.1f}%")
                elif 'drop_pct' in r:
                    print(f"    · 跌幅 {r['drop_pct']:.1f}%  恢复 {r.get('recovery_pct', 0):.1f}%")
                elif 'rise_pct' in r:
                    print(f"    · 涨幅 {r['rise_pct']:.1f}%  回撤 {r.get('retrace_pct', 0):.1f}%")
        else:
            print(f"  {pat_name}: 未检测到")

    # Zigzag 最近转折点
    zz = zigzag(pat_close, step=3)
    if zz['indices']:
        print(f"  zigzag: {len(zz['indices'])} 个转折点, 最近5个:")
        for idx, val, typ in zip(zz['indices'][-5:], zz['values'][-5:], zz['types'][-5:]):
            t = "峰▲" if typ == 1 else "谷▼"
            print(f"    [{idx:>4d}] {t} {val:.2f}")

    # ── 4. 策略信号 ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  🎯 策略信号 (最新)")
    print(f"{'─'*60}")

    active_signals = []
    for strat_name, strat_func in STRATEGY_MAP.items():
        signals = strat_func(df)
        last_sig = int(signals[-1]) if len(signals) > 0 else 0
        desc = STRATEGY_DESC.get(strat_name, '')
        if last_sig == 1:
            sig_str = "▲ 买入信号"
            active_signals.append((strat_name, 'buy'))
        elif last_sig == -1:
            sig_str = "▼ 卖出信号"
            active_signals.append((strat_name, 'sell'))
        else:
            sig_str = "  无信号"
        print(f"  {strat_name:<12s} {sig_str}  ({desc})")

    # 信号共振
    buy_count = sum(1 for _, s in active_signals if s == 'buy')
    sell_count = sum(1 for _, s in active_signals if s == 'sell')
    print(f"\n  共振: {buy_count} 个买入 / {sell_count} 个卖出", end="")
    if buy_count >= 3:
        print(f"  → 多头共振 🔥")
    elif sell_count >= 3:
        print(f"  → 空头共振 🔥")
    elif buy_count > sell_count:
        print(f"  → 偏多")
    elif sell_count > buy_count:
        print(f"  → 偏空")
    else:
        print(f"  → 多空平衡")

    # ── 5. 策略回测 ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  🧪 策略回测 (初始资金 {args.capital:,.0f})")
    print(f"{'─'*60}")

    # 获取日期范围
    first_date = str(df.index[0])[:10] if hasattr(df.index, 'strftime') else str(df['date'].iloc[0])[:10] if 'date' in df.columns else '?'
    last_date = str(df.index[-1])[:10] if hasattr(df.index, 'strftime') else str(df['date'].iloc[-1])[:10] if 'date' in df.columns else '?'
    print(f"  回测区间: {first_date}  →  {last_date}")

    print(f"  {'策略':<12s} {'收益率':>8s} {'年化':>8s} {'回撤':>8s} {'夏普':>8s} {'胜率':>8s} {'交易':>6s}")
    print(f"  {'-'*62}")

    best_strategy = None
    best_sharpe = -999

    for strat_name, strat_func in STRATEGY_MAP.items():
        lot = 1 if strat_name == 'buy_hold' else 100
        result = backtest(
            df, strat_func,
            capital=args.capital,
            commission=0.001,
            slippage=0.001,
            position_size=1.0,
            stop_loss=args.stop_loss,
            take_profit=args.take_profit,
            lot_size=lot,
        )
        d = result.to_dict()
        print(f"  {strat_name:<12s} {d['total_return']:>+7.2f}% {d['annual_return']:>+7.2f}% "
              f"{d['max_drawdown']:>7.2f}% {d['sharpe_ratio']:>8.4f} {d['win_rate']:>7.1f}% {d['total_trades']:>5d}")

        if d['sharpe_ratio'] > best_sharpe and d['total_trades'] > 0 and strat_name != 'ensemble':
            best_sharpe = d['sharpe_ratio']
            best_strategy = strat_name

    if best_strategy:
        print(f"\n  🏆 单一最优: {best_strategy} (夏普比率 {best_sharpe:.4f})")

    # ensemble 也回测了，看看是否跑赢
    if 'ensemble' in STRATEGY_MAP:
        ens_result = backtest(df, STRATEGY_MAP['ensemble'], capital=args.capital,
                              commission=0.001, slippage=0.001, lot_size=100)
        ens_d = ens_result.to_dict()
        if ens_d['sharpe_ratio'] > best_sharpe:
            print(f"  🏆 组合最优: ensemble (夏普比率 {ens_d['sharpe_ratio']:.4f} > 单一 {best_sharpe:.4f}) ✅")

    # ── HTML 图表输出 ──
    if hasattr(args, 'html') and args.html:
        from lib.chart import save_analyze_chart
        # 收集所有回测结果
        all_bt_results = {}
        for strat_name, strat_func in STRATEGY_MAP.items():
            lot = 1 if strat_name == 'buy_hold' else 100
            bt = backtest(df, strat_func, capital=args.capital, commission=0.001, slippage=0.001, lot_size=lot)
            all_bt_results[strat_name] = bt
        filepath = save_analyze_chart(args.code, df, all_bt_results, signals_map=None)
        print(f"\n  HTML 图表已保存: {filepath}")

    # ── 6. 综合判断 ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  📋 综合判断")
    print(f"{'─'*60}")

    score = 0
    reasons = []

    # 均线多空
    if close[-1] > mytt.MA(close, 20)[-1]:
        score += 1
        reasons.append("价格在MA20上方 (+1)")
    else:
        score -= 1
        reasons.append("价格在MA20下方 (-1)")

    # MACD
    if dif[-1] > dea[-1]:
        score += 1
        reasons.append("MACD金叉 (+1)")
    else:
        score -= 1
        reasons.append("MACD死叉 (-1)")

    # RSI
    if rsi_val < 30:
        score += 1
        reasons.append("RSI超卖 (+1)")
    elif rsi_val > 70:
        score -= 1
        reasons.append("RSI超买 (-1)")

    # 策略共振
    if buy_count > sell_count:
        score += 1
        reasons.append(f"策略偏多 {buy_count}:{sell_count} (+1)")
    elif sell_count > buy_count:
        score -= 1
        reasons.append(f"策略偏空 {buy_count}:{sell_count} (-1)")

    # 形态
    for pat_name, pat_func in PATTERN_MAP.items():
        if pat_name == 'zigzag':
            continue
        r = pat_func(pat_close)
        if isinstance(r, list) and r:
            reasons.append(f"检测到 {pat_name} 形态 (关注)")

    if score >= 3:
        verdict = "强烈看多 🟢🟢🟢"
    elif score >= 1:
        verdict = "偏多 🟢"
    elif score <= -3:
        verdict = "强烈看空 🔴🔴🔴"
    elif score <= -1:
        verdict = "偏空 🔴"
    else:
        verdict = "中性 ⚪"

    print(f"  综合评分: {score:+d}  → {verdict}")
    for r in reasons:
        print(f"    · {r}")

    print(f"\n{'='*60}")
    print(f"  ⚠️  以上分析仅供参考，不构成投资建议")
    print(f"{'='*60}")


def cmd_fund(args):
    """资金面分析 — 主力资金、融资融券"""
    code = args.code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')

    if not HAS_AKSHARE_DATA:
        print("❌ akshare 未安装，请运行: pip3 install akshare")
        return

    print(f"\n{'='*60}")
    print(f"  💰 资金面分析: {code}")
    print(f"{'='*60}")

    # 资金流向
    try:
        fund = get_fund_flow(code)
        rows = fund.get('rows', [])
        summary = fund.get('summary', {})
        if rows:
            print(f"\n  📊 主力资金流向 (近5日)")
            print(f"  {'日期':<12} {'收盘':>8} {'涨跌%':>7} {'主力净额':>12} {'主力占比':>8} {'超大单':>12}")
            print(f"  {'-'*65}")
            for r in rows:
                main_str = f"{r['main_net']/1e4:+,.0f}万"
                sl_str = f"{r['super_large_net']/1e4:+,.0f}万"
                print(f"  {r['date']:<12} {r['close']:>8.2f} {r['chg_pct']:>+6.2f}% {main_str:>12} {r['main_pct']:>+7.2f}% {sl_str:>12}")

            m1 = summary.get('main_net_1d', 0)
            m3 = summary.get('main_net_3d', 0)
            s1 = summary.get('super_large_1d', 0)
            print(f"\n  📈 汇总")
            print(f"    主力1日净流入: {m1/1e8:+.2f}亿")
            print(f"    主力3日净流入: {m3/1e8:+.2f}亿")
            print(f"    超大单1日净流入: {s1/1e8:+.2f}亿")
            if m1 > 0 and m3 > 0:
                print(f"    → 资金持续流入 🟢")
            elif m1 < 0 and m3 < 0:
                print(f"    → 资金持续流出 🔴")
            else:
                print(f"    → 资金面分歧 🟡")
    except Exception as e:
        print(f"  ❌ 资金流向获取失败: {e}")

    # 融资融券
    try:
        print(f"\n  📋 融资融券 (上交所近10日)")
        margin = get_margin_data(days=30)
        if margin:
            for r in margin[-10:]:
                print(f"    {r['date']}  融资余额: {r['margin_balance']/1e8:,.0f}亿  融资买入: {r['margin_buy']/1e8:,.0f}亿")
        else:
            print("    无数据")
    except Exception as e:
        print(f"  ❌ 融资融券获取失败: {e}")

    print(f"\n{'='*60}")


def cmd_compare(args):
    """多股票对比分析"""
    import numpy as np

    codes = [c.strip() for c in args.codes.split(',') if c.strip()]
    if len(codes) < 2:
        print("  至少需要2个股票代码，用逗号分隔")
        sys.exit(1)
    if len(codes) > 8:
        print("  最多支持8个股票对比")
        codes = codes[:8]

    # 收集每只股票的数据
    results = []
    for code in codes:
        try:
            df = _fetch(code, args.count, args.period)
            close = df['close'].values
            high = df['high'].values if 'high' in df.columns else close
            low = df['low'].values if 'low' in df.columns else close
            volume = df['volume'].values if 'volume' in df.columns else None

            # 基本信息
            last_price = close[-1]
            change = (close[-1] - close[-2]) / close[-2] * 100 if len(close) >= 2 else 0
            chg_5d = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
            chg_20d = (close[-1] - close[-20]) / close[-20] * 100 if len(close) >= 20 else 0

            # 技术指标
            ma5 = mytt.MA(close, 5)[-1]
            ma20 = mytt.MA(close, 20)[-1]
            dif, dea, _ = mytt.MACD(close)
            rsi14 = mytt.RSI(close, 14)[-1]

            # 信号统计
            buy_count = 0
            sell_count = 0
            signal_names = []
            for strat_name, strat_func in STRATEGY_MAP.items():
                if strat_name in ('buy_hold', 'ensemble'):
                    continue
                sigs = strat_func(df)
                last_sig = int(sigs[-1]) if len(sigs) > 0 else 0
                if last_sig == 1:
                    buy_count += 1
                    signal_names.append(f"{strat_name}▲")
                elif last_sig == -1:
                    sell_count += 1
                    signal_names.append(f"{strat_name}▼")

            # 均线位置
            if close[-1] > ma5 > ma20:
                ma_pos = "多头排列"
            elif close[-1] > ma20:
                ma_pos = "MA20上"
            elif close[-1] > ma5:
                ma_pos = "MA5上"
            else:
                ma_pos = "均线下"

            # MACD状态
            macd_state = "金叉" if dif[-1] > dea[-1] else "死叉"

            # RSI状态
            if rsi14 > 70:
                rsi_state = f"{rsi14:.0f}超买"
            elif rsi14 < 30:
                rsi_state = f"{rsi14:.0f}超卖"
            else:
                rsi_state = f"{rsi14:.0f}"

            # 综合评分
            score = 0
            if close[-1] > ma20:
                score += 1
            if dif[-1] > dea[-1]:
                score += 1
            if rsi14 < 70:
                score += 1
            if rsi14 > 30:
                score -= 0  # 不扣分
            score += (buy_count - sell_count) * 0.5

            # 波动率
            atr20 = mytt.ATR(close, high, low, 20)[-1]
            vol_pct = atr20 / close[-1] * 100

            results.append({
                'code': code,
                'price': last_price,
                'chg_1d': change,
                'chg_5d': chg_5d,
                'chg_20d': chg_20d,
                'ma_pos': ma_pos,
                'macd': macd_state,
                'rsi': rsi_state,
                'vol_pct': vol_pct,
                'buy_count': buy_count,
                'sell_count': sell_count,
                'signals': signal_names,
                'score': score,
            })
        except Exception as e:
            results.append({
                'code': code,
                'price': 0,
                'error': str(e)[:30],
            })

    # 输出
    print(f"\n{'='*90}")
    print(f"  📊 多股对比  周期: {args.period}  数量: {args.count}")
    print(f"{'='*90}")

    # 表头
    print(f"  {'代码':<10s} {'现价':>8s} {'今涨%':>7s} {'5日%':>7s} {'20日%':>7s} {'均线':>8s} {'MACD':>5s} {'RSI':>8s} {'波动%':>6s} {'买/卖':>6s} {'评分':>5s}")
    print(f"  {'-'*88}")

    # 按评分排序
    results.sort(key=lambda x: x.get('score', -99), reverse=True)

    for r in results:
        if 'error' in r:
            print(f"  {r['code']:<10s} {'获取失败':>8s}  {r['error']}")
            continue
        print(f"  {r['code']:<10s} {r['price']:>8.2f} {r['chg_1d']:>+6.2f}% {r['chg_5d']:>+6.2f}% {r['chg_20d']:>+6.2f}% "
              f"{r['ma_pos']:>8s} {r['macd']:>5s} {r['rsi']:>8s} {r['vol_pct']:>5.1f}% "
              f"{r['buy_count']}/{r['sell_count']:>4d} {r['score']:>+5.1f}")

    # 信号详情
    print(f"\n  📋 信号详情:")
    for r in results:
        if 'error' in r or not r.get('signals'):
            continue
        sigs = ' '.join(r['signals'])
        print(f"    {r['code']:<10s} → {sigs}")

    # 推荐
    valid = [r for r in results if 'error' not in r]
    if valid:
        best = valid[0]
        print(f"\n  🏆 综合最优: {best['code']} (评分 {best['score']:+.1f}, {best['ma_pos']}, {best['macd']}, 买{best['buy_count']}/卖{best['sell_count']})")

    # 实时价格
    if HAS_REALTIME:
        try:
            rt_results = get_realtime(codes)
            rt_map = {r['code']: r for r in rt_results if 'code' in r}
            print(f"\n  📡 实时行情:")
            for r in rt_results:
                if 'error' in r:
                    continue
                name = r.get('name', '')
                pct = r.get('percent', 0)
                now = r.get('now', 0)
                sign = '+' if pct > 0 else ''
                arrow = '🔴' if pct < 0 else '🟢' if pct > 0 else '⚪'
                print(f"    {arrow} {name}({r['code']})  {now:.2f}  {sign}{pct:.2f}%")
        except Exception:
            pass

    # ensemble 回测对比
    if args.ensemble:
        print(f"\n{'─'*90}")
        print(f"  🧪 策略组合回测对比 (ensemble min_agree={args.ensemble})")
        print(f"{'─'*90}")
        print(f"  {'代码':<10s} {'单一最优':>10s} {'单一夏普':>8s} {'组合收益':>8s} {'组合夏普':>8s} {'组合回撤':>8s} {'组合交易':>6s}")
        print(f"  {'-'*68}")

        for r in results:
            if 'error' in r:
                continue
            code = r['code']
            try:
                df = _fetch(code, args.count, args.period)
                # 单一最优策略
                best_sharpe = -999
                best_name = ''
                for sn, sf in STRATEGY_MAP.items():
                    if sn in ('buy_hold', 'ensemble'):
                        continue
                    bt = backtest(df, sf, capital=args.capital, commission=0.001, slippage=0.001, lot_size=100)
                    d = bt.to_dict()
                    if d['sharpe_ratio'] > best_sharpe and d['total_trades'] > 0:
                        best_sharpe = d['sharpe_ratio']
                        best_name = sn
                # ensemble 回测
                ens_func = lambda df: strategy_ensemble(df, min_agree=args.ensemble)
                bt_ens = backtest(df, ens_func, capital=args.capital, commission=0.001, slippage=0.001, lot_size=100)
                d_ens = bt_ens.to_dict()
                print(f"  {code:<10s} {best_name:>10s} {best_sharpe:>8.2f} {d_ens['total_return']:>+7.2f}% {d_ens['sharpe_ratio']:>8.2f} {d_ens['max_drawdown']:>7.2f}% {d_ens['total_trades']:>5d}")
            except Exception as e:
                print(f"  {code:<10s} 回测失败: {str(e)[:30]}")

    print(f"\n{'='*90}")
    print(f"  ⚠️  以上分析仅供参考，不构成投资建议")
    print(f"{'='*90}")


def cmd_search(args):
    """搜索股票代码/名称"""
    if not HAS_REALTIME:
        print("  ❌ realtime_data 模块未加载")
        return

    keyword = args.keyword

    print(f"\n{'='*50}")
    print(f"  🔍 搜索: {keyword}")
    print(f"{'='*50}")

    results = search_stock(keyword, source=args.source)
    if results:
        for r in results:
            print(f"  {r['code']:<12s} {r['name']}")
        print(f"\n  共找到 {len(results)} 条结果")
    else:
        print("  未找到匹配结果")


def cmd_cache(args):
    """数据缓存管理"""
    from lib.data_cache import cache_stats, clear_cache

    if args.action == 'stats':
        stats = cache_stats()
        print(f"\n{'='*40}")
        print(f"  📦 数据缓存统计")
        print(f"{'='*40}")
        print(f"  缓存文件数: {stats['files']}")
        print(f"  缓存大小:   {stats['size_kb']} KB")
        print(f"  缓存目录:   {cfg('cache_dir', 'cache')}")
        print(f"  缓存TTL:    {cfg('cache_ttl_hours', 4)} 小时")
        print(f"{'='*40}")
    elif args.action == 'clear':
        count = clear_cache(older_than_hours=args.older_than)
        print(f"  已清理 {count} 个缓存文件")


def cmd_diagnose(args):
    """股票综合诊断 — 借鉴 Aeolus stock-diagnosis"""
    if not HAS_AKSHARE_DATA:
        print("❌ akshare 未安装")
        return
        print("❌ akshare 未安装")
        return

    code = args.code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')
    print(f"\n{'='*60}")
    print(f"  🏥 股票综合诊断: {args.code}")
    print(f"{'='*60}")

    # 1. 技术面
    df = _fetch(args.code, args.count, args.period)
    close = df['close'].values
    high = df['high'].values if 'high' in df.columns else close
    low = df['low'].values if 'low' in df.columns else close

    import numpy as np
    last = close[-1]
    change = (close[-1] - close[-2]) / close[-2] * 100 if len(close) >= 2 else 0

    print(f"\n  📈 技术面评分")
    print(f"  {'─'*50}")
    tech_score = 0
    tech_reasons = []

    # 均线
    for n in [5, 20, 60]:
        ma = mytt.MA(close, n)
        val = ma[-1] if not np.isnan(ma[-1]) else 0
        if val > 0:
            if last > val:
                tech_score += 1
                tech_reasons.append(f"  价格 > MA{n} ({val:.2f})  +1")
            else:
                tech_score -= 1
                tech_reasons.append(f"  价格 < MA{n} ({val:.2f})  -1")

    # MACD
    dif, dea, macd_v = mytt.MACD(close)
    if dif[-1] > dea[-1]:
        tech_score += 1
        tech_reasons.append(f"  MACD 金叉  +1")
    else:
        tech_score -= 1
        tech_reasons.append(f"  MACD 死叉  -1")

    # RSI
    rsi = mytt.RSI(close, 14)[-1]
    if rsi < 30:
        tech_score += 1
        tech_reasons.append(f"  RSI={rsi:.1f} 超卖  +1")
    elif rsi > 70:
        tech_score -= 1
        tech_reasons.append(f"  RSI={rsi:.1f} 超买  -1")
    else:
        tech_reasons.append(f"  RSI={rsi:.1f} 中性   0")

    # 成交量趋势
    vol = df['volume'].values if 'volume' in df.columns else None
    if vol is not None and len(vol) >= 10:
        vol_recent = np.mean(vol[-3:])
        vol_prev = np.mean(vol[-10:-3])
        if vol_recent > vol_prev * 1.5:
            tech_reasons.append(f"  近3日放量 (均量 {vol_recent/1e4:.0f}万)   0")
        elif vol_recent < vol_prev * 0.7:
            tech_reasons.append(f"  近3日缩量 (均量 {vol_recent/1e4:.0f}万)   0")

    for r in tech_reasons:
        print(r)
    print(f"\n  技术面得分: {tech_score:+d}/8")

    # 2. 资金面
    print(f"\n  💰 资金面")
    print(f"  {'─'*50}")
    try:
        from lib.akshare_data import get_fund_flow
        flow = get_fund_flow(code)
        rows = flow.get('rows', [])
        summary = flow.get('summary', {})
        if rows:
            m1 = summary.get('main_net_1d', 0)
            m3 = summary.get('main_net_3d', 0)
            direction_1d = '🟢 流入' if m1 > 0 else '🔴 流出'
            direction_3d = '🟢 流入' if m3 > 0 else '🔴 流出'
            print(f"  主力1日: {m1/1e4:+,.0f}万 {direction_1d}")
            print(f"  主力3日: {m3/1e4:+,.0f}万 {direction_3d}")
            for r in rows:
                print(f"    {r['date']}  主力 {r['main_net']/1e4:+,.0f}万  超大单 {r['super_large_net']/1e4:+,.0f}万")
        else:
            print(f"  无资金流向数据")
    except Exception as e:
        print(f"  数据获取失败: {e}")

    # 3. 基本面
    print(f"\n  📊 基本面")
    print(f"  {'─'*50}")
    try:
        from lib.akshare_data import get_stock_diagnosis_data
        diag = get_stock_diagnosis_data(code)
        fin = diag.get('financial', {})
        val = diag.get('valuation', {})
        if fin:
            rev = fin.get('营业总收入', fin.get('revenue', 0))
            np_ = fin.get('净利润', fin.get('net_profit', 0))
            roe_ = fin.get('净资产收益率', fin.get('roe', 0))
            gm = fin.get('毛利率', fin.get('gross_margin', 0))
            if rev:
                print(f"  营业总收入: {rev/1e8:.2f}亿" if abs(rev) > 1e4 else f"  营业总收入: {rev}")
            if np_:
                print(f"  净利润:     {np_/1e8:.2f}亿" if abs(np_) > 1e4 else f"  净利润: {np_}")
            if roe_:
                print(f"  ROE:        {roe_:.2f}%")
            if gm:
                print(f"  毛利率:     {gm:.2f}%")
        if val:
            pe = val.get('市盈率(TTM)', val.get('pe_ttm', 0))
            pb = val.get('市净率', val.get('pb', 0))
            dv = val.get('股息率%', val.get('dv_ratio', 0))
            if pe: print(f"  市盈率TTM:  {pe:.2f}")
            if pb: print(f"  市净率:     {pb:.2f}")
            if dv: print(f"  股息率:     {dv:.2f}%")
        if not fin and not val:
            print(f"  无基本面数据")
    except Exception as e:
        print(f"  数据获取失败: {e}")

    # 4. 形态
    print(f"\n  🔍 形态识别")
    print(f"  {'─'*50}")
    for pat_name, pat_func in PATTERN_MAP.items():
        if pat_name == 'zigzag':
            continue
        r = pat_func(close)
        if isinstance(r, list) and r:
            print(f"  {pat_name}: {len(r)} 个 ✅")
        else:
            print(f"  {pat_name}: 无")

    # 5. 综合评分
    fund_score = 0
    try:
        m3 = summary.get('main_net_3d', 0) if 'summary' in dir() else 0
        if m3 > 0: fund_score = 1
        elif m3 < 0: fund_score = -1
    except:
        pass

    total = tech_score + fund_score
    if total >= 3: verdict = "强烈看多 🟢🟢🟢"
    elif total >= 1: verdict = "偏多 🟢"
    elif total <= -3: verdict = "强烈看空 🔴🔴🔴"
    elif total <= -1: verdict = "偏空 🔴"
    else: verdict = "中性 ⚪"

    print(f"\n{'─'*60}")
    print(f"  🏆 综合诊断: {verdict} (技术{tech_score:+d} + 资金{fund_score:+d} = 总分{total:+d})")
    print(f"{'─'*60}")
    print(f"\n  ⚠️ 以上分析仅供参考，不构成投资建议")


def cmd_macro(args):
    """宏观经济数据查询 — 借鉴 Aeolus MX_MacroData"""
    from lib.akshare_data import get_macro_data

    result = get_macro_data(args.indicator)

    if 'error' in result:
        print(f"  ❌ {result['error']}")
        return

    indicator_names = {
        'cpi': '居民消费价格指数 (CPI)',
        'ppi': '工业生产者出厂价格指数 (PPI)',
        'gdp': '国内生产总值 (GDP)',
        'pmi': '制造业采购经理指数 (PMI)',
        'm2': 'M2 货币供应量',
        'lpr': '贷款市场报价利率 (LPR)',
        'unemployment': '城镇调查失业率',
        'trade': '进出口贸易数据',
        'industrial': '工业增加值',
    }

    name = indicator_names.get(args.indicator, args.indicator)
    data = result.get('data', [])
    columns = result.get('columns', [])

    print(f"\n{'='*70}")
    print(f"  📊 宏观数据: {name}")
    print(f"{'='*70}")

    if not data:
        print(f"  无数据")
        return

    # 取关键列显示
    key_cols = [c for c in columns if any(k in c for k in ['日期', '时间', '月份', '季度', '年份', '公布日期', '今值', '前值', '数值', '同比', '环比', 'GDP', 'CPI', 'PPI', 'PMI', 'M2', '失业率'])]

    if not key_cols:
        key_cols = columns[:6]  # 取前6列

    # 打印表头
    header = f"  "
    for c in key_cols:
        header += f"{str(c):>14s}"
    print(header)
    print(f"  {'─' * (14 * len(key_cols))}")

    for row in data[:12]:
        line = f"  "
        for c in key_cols:
            val = row.get(c, '')
            if val is None:
                val = '-'
            elif isinstance(val, float):
                val = f"{val:.2f}"
            else:
                val = str(val)[:12]
            line += f"{str(val):>14s}"
        print(line)

    print(f"\n  共 {len(data)} 条数据")


def cmd_hotspot(args):
    """市场热点发现 — 借鉴 Aeolus stock-market-hotspot-discovery"""
    from lib.akshare_data import get_market_hotspot

    print(f"\n{'='*70}")
    print(f"  🔥 市场热点扫描")
    print(f"{'='*70}")

    result = get_market_hotspot(top_n=args.top)

    # 1. 人气榜
    hot_ranks = result.get('hot_ranks', [])
    if hot_ranks:
        print(f"\n  📢 A股人气榜 Top {min(10, len(hot_ranks))}")
        print(f"  {'排名':>4s} {'代码':>8s} {'名称':<10s} {'现价':>8s} {'涨跌%':>7s} {'人气':>8s}")
        print(f"  {'─'*55}")
        for r in hot_ranks[:10]:
            cls = '↑' if r['chg_pct'] > 0 else '↓' if r['chg_pct'] < 0 else '-'
            print(f"  {int(r.get('rank', 0)):>4d} {r['code']:>8s} {r['name']:<10s} {r['price']:>8.2f} {r['chg_pct']:>+6.2f}% {cls} {r.get('heat', 0):>8.0f}")
    else:
        print(f"\n  📢 人气榜: 数据暂不可用 (东方财富接口连接失败)")

    # 2. 概念板块
    concepts = result.get('concept_hot', [])
    if concepts:
        print(f"\n  🏷️  概念板块涨幅榜 Top {min(10, len(concepts))}")
        print(f"  {'板块名称':<16s} {'涨跌%':>7s} {'领涨股':<10s}")
        print(f"  {'─'*40}")
        for r in concepts[:10]:
            print(f"  {r['name']:<16s} {r['chg_pct']:>+6.2f}% {r.get('leader', ''):<10s}")
    else:
        print(f"\n  🏷️  概念板块: 数据暂不可用")

    # 3. 行业板块（已有接口，用 get_sector_hot）
    try:
        from lib.akshare_data import get_sector_hot
        hot_data = get_sector_hot(top_n=10)
        hot_list = hot_data.get('hot', [])
        if hot_list:
            print(f"\n  🏭 行业板块涨幅榜 Top {len(hot_list)}")
            print(f"  {'板块名称':<16s} {'涨跌%':>7s} {'领涨股':<10s}")
            print(f"  {'─'*40}")
            for r in hot_list:
                print(f"  {r['name']:<16s} {r['chg_pct']:>+6.2f}% {r.get('leader', ''):<10s}")
    except Exception:
        print(f"\n  🏭 行业板块: 数据暂不可用")

    print(f"\n{'='*70}")
    print(f"  ⚠️ 数据仅供参考，不构成投资建议")


def cmd_realtime(args):
    """实时行情 — 腾讯/东方财富多数据源"""
    if not HAS_REALTIME:
        print("  ❌ realtime_data 模块未加载")
        return

    codes = [c.strip() for c in args.codes.split(',') if c.strip()]

    results = get_realtime(codes, source=args.source)

    print(f"\n{'='*60}")
    print(f"  📡 实时行情  数据源: {args.source}")
    print(f"{'='*60}")
    print(format_realtime(results))
    print(f"\n{'='*60}")


def _check_em_api():
    """检查东方财富妙想 API 是否配置"""
    if not HAS_EM_API:
        print("  ❌ em_api 模块未加载")
        return False
    if not em_api.is_configured():
        print("  ❌ 未配置东方财富妙想 API Key")
        print("  💡 请在 config.yaml 中设置 em_api_key 或设置环境变量 EM_API_KEY")
        print("  💡 注册地址: https://ai.eastmoney.com/mxClaw")
        return False
    return True


def cmd_em_diagnose(args):
    """东方财富妙想 AI 股票诊断"""
    if not _check_em_api():
        return

    question = args.question or f"分析{args.code}"
    # 转换代码格式: sh600519 → 贵州茅台
    code = args.code

    print(f"\n{'='*60}")
    print(f"  🤖 东方财富妙想 AI 诊断")
    print(f"{'='*60}")
    print(f"  查询: {question}")
    print(f"  {'─'*56}")

    result = em_api.stock_diagnosis(question)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
    elif result.get('content'):
        print(f"\n{result['content']}")
    else:
        print("  未返回有效内容")


def cmd_em_pick(args):
    """东方财富妙想 AI 选股"""
    if not _check_em_api():
        return

    query = args.query
    market = args.market
    category = args.category

    print(f"\n{'='*60}")
    print(f"  🤖 东方财富妙想 AI 选股")
    print(f"{'='*60}")
    print(f"  条件: {query}")
    print(f"  市场: {market}  品类: {category}")
    print(f"  {'─'*56}")

    result = em_api.select_security(query, market=market, category=category, top_n=args.top)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
    elif result.get('content'):
        print(f"\n{result['content']}")
    else:
        print("  未返回有效内容")


def cmd_em_ask(args):
    """东方财富妙想 AI 金融问答"""
    if not _check_em_api():
        return

    question = args.question

    print(f"\n{'='*60}")
    print(f"  🤖 东方财富妙想 AI 问答")
    print(f"{'='*60}")
    print(f"  问题: {question}")
    print(f"  {'─'*56}")

    result = em_api.ask(question, deep_think=args.deep)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
    elif result.get('content'):
        print(f"\n{result['content']}")
    else:
        print("  未返回有效内容")


def cmd_em_news(args):
    """东方财富妙想 AI 资讯搜索"""
    if not _check_em_api():
        return

    query = args.query

    print(f"\n{'='*60}")
    print(f"  🤖 东方财富妙想 AI 资讯")
    print(f"{'='*60}")
    print(f"  搜索: {query}")
    print(f"  {'─'*56}")

    result = em_api.search_news(query, market=args.market, count=args.top)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
    elif result.get('content'):
        print(f"\n{result['content']}")
    else:
        print("  未返回有效内容")


def cmd_em_fund(args):
    """东方财富妙想 AI 基金诊断"""
    if not _check_em_api():
        return

    question = args.question or f"分析{args.code}"

    print(f"\n{'='*60}")
    print(f"  🤖 东方财富妙想 AI 基金诊断")
    print(f"{'='*60}")
    print(f"  查询: {question}")
    print(f"  {'─'*56}")

    result = em_api.fund_diagnosis(question)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
    elif result.get('content'):
        print(f"\n{result['content']}")
    else:
        print("  未返回有效内容")


def cmd_list(args):
    """列出可用资源"""
    print(f"\n{'='*60}")
    print(f"  可用指标")
    print(f"{'='*60}")
    indicators = [
        ('maN', '简单移动平均', '如 ma5, ma10, ma20'),
        ('emaN', '指数移动平均', '如 ema12, ema26'),
        ('macd', 'MACD', '返回 DIF, DEA, MACD'),
        ('rsi / rsiN', 'RSI', '默认14，可指定 rsi6, rsi24'),
        ('boll', '布林带', '返回 上轨/中轨/下轨'),
        ('kdj', 'KDJ', '返回 K, D, J'),
        ('atr / atrN', '真实波动幅度', '默认20周期'),
        ('cci', 'CCI', '商品通道指数'),
        ('wr', '威廉指标', '返回 WR, WR1'),
        ('bias', '乖离率', '返回 BIAS6/12/24'),
        ('obv', '能量潮', '需成交量数据'),
    ]
    for code, name, desc in indicators:
        print(f"  {code:<14s}  {name:<10s}  {desc}")

    print(f"\n{'='*60}")
    print(f"  可用策略")
    print(f"{'='*60}")
    for name, desc in STRATEGY_DESC.items():
        print(f"  {name:<14s}  {desc}")

    print(f"\n{'='*60}")
    print(f"  可用形态")
    print(f"{'='*60}")
    for name in PATTERN_MAP:
        print(f"  {name:<14s}")

    print(f"\n{'='*60}")
    print(f"  K线周期")
    print(f"{'='*60}")
    periods = [('1d', '日线'), ('1w', '周线'), ('1M', '月线'), ('1m', '1分钟'), ('5m', '5分钟'), ('15m', '15分钟'), ('30m', '30分钟'), ('60m', '60分钟')]
    for p, desc in periods:
        print(f"  {p:<6s}  {desc}")


# ── 主入口 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='quant.py',
        description='quant-china: A股量化分析工具箱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  quant.py data sh000001 --count 30
  quant.py indicators sh000001 --indicators ma5,ma10,macd,rsi
  quant.py pattern sh000001 --pattern w-bottom,v-reversal
  quant.py backtest sh000001 --strategy ma_cross --capital 100000
  quant.py analyze sh000001          # 综合分析 (一次出完整报告)
  quant.py scan --strategy macd
  quant.py list
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # data
    p_data = subparsers.add_parser('data', help='获取行情数据')
    p_data.add_argument('code', help='股票代码 (如 sh000001, sz000001)')
    p_data.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M', '1m', '5m', '15m', '30m', '60m'], help='K线周期')
    p_data.add_argument('--count', '-n', type=int, default=30, help='数据条数')
    p_data.add_argument('--end', '-e', default='', help='结束日期 (YYYY-MM-DD)')
    p_data.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    # indicators
    p_ind = subparsers.add_parser('indicators', help='计算技术指标')
    p_ind.add_argument('code', help='股票代码')
    p_ind.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M', '1m', '5m', '15m', '30m', '60m'], help='K线周期')
    p_ind.add_argument('--count', '-n', type=int, default=120, help='数据条数')
    p_ind.add_argument('--end', '-e', default='', help='结束日期')
    p_ind.add_argument('--indicators', '-i', default='ma5,ma10,ma20,macd,rsi', help='指标列表 (逗号分隔)')
    p_ind.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    # pattern
    p_pat = subparsers.add_parser('pattern', help='形态识别')
    p_pat.add_argument('code', help='股票代码')
    p_pat.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M'], help='K线周期')
    p_pat.add_argument('--count', '-n', type=int, default=250, help='数据条数')
    p_pat.add_argument('--end', '-e', default='', help='结束日期')
    p_pat.add_argument('--pattern', default='zigzag,w-bottom,v-reversal,cup-handle', help='形态类型 (逗号分隔)')
    p_pat.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    # backtest
    p_bt = subparsers.add_parser('backtest', help='策略回测')
    p_bt.add_argument('code', help='股票代码')
    p_bt.add_argument('--strategy', '-s', default='ma_cross', choices=list(STRATEGY_MAP.keys()), help='策略名称')
    p_bt.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M'], help='K线周期')
    p_bt.add_argument('--count', '-n', type=int, default=500, help='数据条数')
    p_bt.add_argument('--end', '-e', default='', help='结束日期')
    p_bt.add_argument('--capital', '-c', type=float, default=100000, help='初始资金')
    p_bt.add_argument('--stop-loss', type=float, default=None, help='止损比例 (如 0.05)')
    p_bt.add_argument('--take-profit', type=float, default=None, help='止盈比例 (如 0.10)')
    p_bt.add_argument('--json', '-j', action='store_true', help='JSON格式输出')
    p_bt.add_argument('--html', action='store_true', help='输出HTML图表文件 (参考 stock-quant)')

    # scan
    p_scan = subparsers.add_parser('scan', help='市场扫描')
    p_scan.add_argument('--market', default='a-shares', help='市场')
    p_scan.add_argument('--strategy', '-s', default='ma_cross', choices=list(STRATEGY_MAP.keys()), help='策略名称')
    p_scan.add_argument('--min-volume', type=float, default=None, help='最小成交量过滤')

    # analyze
    p_analyze = subparsers.add_parser('analyze', help='综合分析 (数据+指标+形态+策略+回测)')
    p_analyze.add_argument('code', help='股票代码 (如 sh000001, sz000001)')
    p_analyze.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M'], help='K线周期')
    p_analyze.add_argument('--count', '-n', type=int, default=500, help='数据条数')
    p_analyze.add_argument('--end', '-e', default='', help='结束日期 (YYYY-MM-DD)')
    p_analyze.add_argument('--capital', '-c', type=float, default=100000, help='初始资金')
    p_analyze.add_argument('--stop-loss', type=float, default=None, help='止损比例 (如 0.05)')
    p_analyze.add_argument('--take-profit', type=float, default=None, help='止盈比例 (如 0.10)')
    p_analyze.add_argument('--html', action='store_true', help='输出HTML图表文件 (参考 stock-quant)')

    # compare
    p_compare = subparsers.add_parser('compare', help='多股票对比分析')
    p_compare.add_argument('codes', help='股票代码，逗号分隔 (如 sh600519,sz000858,sh601212)')
    p_compare.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M'], help='K线周期')
    p_compare.add_argument('--count', '-n', type=int, default=500, help='数据条数')
    p_compare.add_argument('--capital', '-c', type=float, default=100000, help='回测初始资金')
    p_compare.add_argument('--ensemble', type=int, default=0, metavar='N', help='同时跑ensemble回测，N为最少同意策略数')

    # list
    p_fund = subparsers.add_parser('fund', help='资金面分析 (主力/融资融券)')
    p_fund.add_argument('code', help='股票代码，如 sh600519 或 sz000001')

    subparsers.add_parser('list', help='列出可用指标/策略/形态')

    # cache
    p_cache = subparsers.add_parser('cache', help='数据缓存管理')
    p_cache.add_argument('action', choices=['stats', 'clear'], help='stats=查看统计, clear=清理缓存')
    p_cache.add_argument('--older-than', type=int, default=None, help='只清理超过N小时的缓存')

    # diagnose
    p_diag = subparsers.add_parser('diagnose', help='股票综合诊断 (技术+资金+基本面+形态)')
    p_diag.add_argument('code', help='股票代码')
    p_diag.add_argument('--period', '-p', default='1d', choices=['1d', '1w', '1M'], help='K线周期')
    p_diag.add_argument('--count', '-n', type=int, default=250, help='数据条数')

    # macro
    p_macro = subparsers.add_parser('macro', help='宏观经济数据查询')
    p_macro.add_argument('indicator', nargs='?', default='cpi',
                         choices=['cpi', 'ppi', 'gdp', 'pmi', 'm2', 'lpr', 'unemployment', 'trade', 'industrial'],
                         help='指标类型 (默认cpi)')

    # hotspot
    p_hot = subparsers.add_parser('hotspot', help='市场热点扫描 (人气榜+概念+行业)')
    p_hot.add_argument('--top', '-n', type=int, default=20, help='返回前N名 (默认20)')

    # realtime
    p_rt = subparsers.add_parser('realtime', help='实时行情 (腾讯/东方财富)')
    p_rt.add_argument('codes', help='股票代码，逗号分隔 (如 sh600519,sz000858)')
    p_rt.add_argument('--source', '-s', default='auto', choices=['auto', 'tencent', 'eastmoney'], help='数据源')

    # search
    p_search = subparsers.add_parser('search', help='搜索股票代码/名称')
    p_search.add_argument('keyword', help='搜索关键词')
    p_search.add_argument('--source', '-s', default='auto', choices=['auto', 'tencent', 'eastmoney'], help='数据源')

    # em-diagnose (东方财富妙想 AI 诊断)
    p_emd = subparsers.add_parser('em-diagnose', help='东方财富妙想 AI 股票诊断')
    p_emd.add_argument('code', help='股票代码 (如 sh600519) 或基金代码')
    p_emd.add_argument('--question', '-q', default='', help='自定义问题 (默认: 分析XX)')

    # em-pick (东方财富妙想 AI 选股)
    p_emp = subparsers.add_parser('em-pick', help='东方财富妙想 AI 自然语言选股')
    p_emp.add_argument('query', help='选股条件 (如 "市盈率最低的20只股票")')
    p_emp.add_argument('--market', '-m', default='a_share', choices=['a_share', 'hk', 'us'], help='市场')
    p_emp.add_argument('--category', '-c', default='stock', choices=['stock', 'fund', 'etf', 'bond', 'convertible_bond', 'sector', 'concept'], help='品类')
    p_emp.add_argument('--top', '-n', type=int, default=10, help='返回数量')

    # em-ask (东方财富妙想 AI 问答)
    p_ema = subparsers.add_parser('em-ask', help='东方财富妙想 AI 金融问答')
    p_ema.add_argument('question', help='金融问题')
    p_ema.add_argument('--deep', '-d', action='store_true', help='启用深度思考')

    # em-news (东方财富妙想 AI 资讯)
    p_emn = subparsers.add_parser('em-news', help='东方财富妙想 AI 资讯搜索')
    p_emn.add_argument('query', help='搜索关键词')
    p_emn.add_argument('--market', '-m', default='', choices=['', 'cn', 'hk', 'us'], help='市场筛选')
    p_emn.add_argument('--top', '-n', type=int, default=10, help='返回数量')

    # em-fund (东方财富妙想 AI 基金诊断)
    p_emf = subparsers.add_parser('em-fund', help='东方财富妙想 AI 基金诊断')
    p_emf.add_argument('code', help='基金代码或名称')
    p_emf.add_argument('--question', '-q', default='', help='自定义问题')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        'data': cmd_data,
        'indicators': cmd_indicators,
        'pattern': cmd_pattern,
        'backtest': cmd_backtest,
        'scan': cmd_scan,
        'analyze': cmd_analyze,
        'compare': cmd_compare,
        'fund': cmd_fund,
        'list': cmd_list,
        'cache': cmd_cache,
        'diagnose': cmd_diagnose,
        'macro': cmd_macro,
        'hotspot': cmd_hotspot,
        'realtime': cmd_realtime,
        'search': cmd_search,
        'em-diagnose': cmd_em_diagnose,
        'em-pick': cmd_em_pick,
        'em-ask': cmd_em_ask,
        'em-news': cmd_em_news,
        'em-fund': cmd_em_fund,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n已中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
