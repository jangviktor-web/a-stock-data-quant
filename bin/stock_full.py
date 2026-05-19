#!/usr/bin/env python3
"""
老六综合选股系统 v1.0
融合 a-stock-data-quant + ths-sdk + 新闻分析
四维评分：资金面(40%) + 板块面(25%) + 技术面(20%) + 消息面(15%)
"""

import sys, os, time, warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.ashare import get_price
from lib import mytt

# ── 检查依赖 ──────────────────────────────────────────

HAS_AKSHARE = False
HAS_THS = False

try:
    from lib.akshare_data import get_fund_flow, get_sector_hot, get_margin_data
    HAS_AKSHARE = True
except ImportError:
    pass

try:
    from thsdk import THS
    HAS_THS = True
except ImportError:
    pass


# ── 资金面分析 (a-stock-data-quant + akshare) ─────────────────

def analyze_fund(code):
    """资金面：主力流向 + 融资融券"""
    result = {"score": 0, "max": 3, "detail": [], "tag": ""}
    pure_code = code.replace('sh', '').replace('sz', '')

    if not HAS_AKSHARE:
        result["detail"].append("  ⚠️ akshare 未安装，跳过资金面")
        return result

    # 主力资金
    try:
        fund = get_fund_flow(pure_code)
        rows = fund.get('rows', [])
        summary = fund.get('summary', {})
        m1 = summary.get('main_net_1d', 0)
        m3 = summary.get('main_net_3d', 0)
        s1 = summary.get('super_large_1d', 0)

        result["detail"].append(f"  主力1日: {m1/1e8:+.2f}亿 | 3日: {m3/1e8:+.2f}亿 | 超大单: {s1/1e8:+.2f}亿")

        if m1 > 0 and m3 > 0:
            result["score"] += 2
            result["detail"].append("  → 资金持续流入 🟢 (+2)")
        elif m1 < 0 and m3 < 0:
            result["score"] -= 1
            result["detail"].append("  → 资金持续流出 🔴 (-1)")
        elif m1 > 0 and m3 < 0:
            result["score"] += 1
            result["detail"].append("  → 短期回流，中期仍弱 🟡 (+1)")
        else:
            result["detail"].append("  → 资金面分歧 🟡 (0)")
    except Exception as e:
        result["detail"].append(f"  ⚠️ 主力资金获取失败: {e}")

    # 融资融券
    try:
        margin = get_margin_data(days=30)
        if margin:
            latest = margin[-1]
            result["detail"].append(f"  融资余额: {latest['margin_balance']/1e8:,.0f}亿 | 融资买入: {latest['margin_buy']/1e8:,.0f}亿")
            if len(margin) >= 2:
                prev = margin[-2]
                if latest['margin_balance'] > prev['margin_balance']:
                    result["score"] += 1
                    result["detail"].append("  → 融资余额增长 🟢 (+1)")
                elif latest['margin_balance'] < prev['margin_balance']:
                    result["detail"].append("  → 融资余额下降 🟡 (0)")
    except Exception as e:
        result["detail"].append(f"  ⚠️ 融资融券获取失败: {e}")

    result["tag"] = f"{result['score']}/{result['max']}"
    return result


# ── 技术面分析 (a-stock-data-quant) ──────────────────────────

def analyze_tech(code):
    """技术面：MACD + KDJ + RSI + 均线 + 量价"""
    result = {"score": 0, "max": 2, "detail": [], "tag": ""}

    try:
        df = get_price(code, count=60)
        if df is None or len(df) < 20:
            result["detail"].append("  ⚠️ 数据不足")
            return result

        close = df['close'].values
        vol = df['volume'].values

        # MACD
        dif, dea, macd = mytt.MACD(close)
        macd_signal = "金叉" if dif[-1] > dea[-1] else "死叉"
        macd_ok = dif[-1] > dea[-1]

        # KDJ
        k, d, j = mytt.KDJ(df['high'].values, df['low'].values, close)
        kdj_signal = f"K={k[-1]:.1f} D={d[-1]:.1f} J={j[-1]:.1f}"
        kdj_oversold = j[-1] < 20
        kdj_overbought = j[-1] > 80

        # RSI
        rsi = mytt.RSI(close, 14)
        rsi_val = rsi[-1]
        rsi_oversold = rsi_val < 30
        rsi_overbought = rsi_val > 70

        # 均线
        ma5 = close[-5:].mean()
        ma20 = close[-20:].mean()
        price = close[-1]
        above_ma5 = price > ma5
        above_ma20 = price > ma20

        # 量比
        vol_ratio = vol[-1] / vol[-6:-1].mean() if vol[-6:-1].mean() > 0 else 1

        result["detail"].append(f"  MACD: {macd_signal} | KDJ: {kdj_signal} | RSI: {rsi_val:.1f}")
        result["detail"].append(f"  价格: {price:.2f} | MA5: {ma5:.2f} | MA20: {ma20:.2f} | 量比: {vol_ratio:.2f}")

        signals = 0
        if macd_ok: signals += 1
        if kdj_oversold or (k[-1] > d[-1] and k[-2] < d[-2]): signals += 1
        if rsi_oversold or (40 < rsi_val < 60): signals += 1
        if above_ma5: signals += 1
        if above_ma20: signals += 1

        if signals >= 3:
            result["score"] = 2
            result["detail"].append(f"  → 多头信号 ({signals}/5) 🟢 (+2)")
        elif signals >= 2:
            result["score"] = 1
            result["detail"].append(f"  → 信号中性 ({signals}/5) 🟡 (+1)")
        else:
            result["score"] = 0
            result["detail"].append(f"  → 空头信号 ({signals}/5) 🔴 (0)")

        # 量价警告
        chg = (price - close[-2]) / close[-2] * 100
        if chg > 0 and vol_ratio < 0.7:
            result["detail"].append("  ⚠️ 缩量上涨，警惕诱多")
        elif chg < -2 and vol_ratio > 1.5:
            result["detail"].append("  ⚠️ 放量下跌，注意风险")

    except Exception as e:
        result["detail"].append(f"  ⚠️ 技术分析失败: {e}")

    result["tag"] = f"{result['score']}/{result['max']}"
    return result


# ── 板块面分析 (ths-sdk 问财) ──────────────────────────

def analyze_sector(stock_name=""):
    """板块面：问财查板块热度"""
    result = {"score": 0, "max": 2, "detail": [], "tag": ""}

    if not HAS_THS:
        # fallback: 用 akshare
        if HAS_AKSHARE:
            try:
                data = get_sector_hot(5)
                hot = data.get('hot', [])
                if hot:
                    result["detail"].append("  热门板块 Top 5:")
                    for s in hot[:5]:
                        result["detail"].append(f"    {s['name']:<12} {s['chg_pct']:>+6.2f}%")
                    result["score"] = 1
                    result["detail"].append("  → 用 akshare 板块数据 (+1)")
            except Exception as e:
                result["detail"].append(f"  ⚠️ 板块数据获取失败: {e}")
        else:
            result["detail"].append("  ⚠️ 无板块数据源")
        result["tag"] = f"{result['score']}/{result['max']}"
        return result

    try:
        with THS() as ths:
            time.sleep(0.3)
            # 查行业排名
            resp = ths.wencai_nlp("今日申万行业涨跌幅排名")
            df = resp.df
            if not df.empty and '行业简称' in df.columns:
                sectors = df.groupby('行业简称').first().reset_index()
                sectors = sectors.sort_values(list(sectors.columns)[1], ascending=False)
                top5 = sectors.head(5)
                result["detail"].append("  热门行业 Top 5:")
                for _, row in top5.iterrows():
                    name = row['行业简称']
                    chg_col = [c for c in row.index if '涨跌' in c]
                    chg = row[chg_col[0]] if chg_col else 'N/A'
                    result["detail"].append(f"    {name:<12} {chg}")
                result["score"] = 1
                result["detail"].append("  → 行业数据获取成功 (+1)")
    except Exception as e:
        result["detail"].append(f"  ⚠️ 问财板块查询失败: {e}")

    result["tag"] = f"{result['score']}/{result['max']}"
    return result


# ── 消息面分析 ──────────────────────────────────────

def analyze_news(stock_name=""):
    """消息面：标记为需要人工/LLM补充"""
    result = {"score": 0, "max": 1, "detail": [], "tag": ""}
    result["detail"].append("  📰 消息面需结合实时新闻分析")
    result["detail"].append("  (由 LLM 在对话中补充)")
    result["tag"] = f"待评/{result['max']}"
    return result


# ── 综合分析入口 ──────────────────────────────────────

def full_analysis(code, name=""):
    """四维综合分析"""
    if not name:
        name = code

    print(f"\n{'='*60}")
    print(f"  🧠 老六综合分析: {name} ({code})")
    print(f"{'='*60}")

    # 资金面
    print(f"\n💰 资金面 (权重40%)")
    fund = analyze_fund(code)
    for line in fund["detail"]:
        print(line)
    print(f"  评分: {fund['tag']}")

    # 技术面
    print(f"\n📉 技术面 (权重20%)")
    tech = analyze_tech(code)
    for line in tech["detail"]:
        print(line)
    print(f"  评分: {tech['tag']}")

    # 板块面
    print(f"\n📈 板块面 (权重25%)")
    sector = analyze_sector(name)
    for line in sector["detail"]:
        print(line)
    print(f"  评分: {sector['tag']}")

    # 消息面
    print(f"\n📰 消息面 (权重15%)")
    news = analyze_news(name)
    for line in news["detail"]:
        print(line)
    print(f"  评分: {news['tag']}")

    # 综合评分
    total_score = fund["score"] + tech["score"] + sector["score"]
    total_max = fund["max"] + tech["max"] + sector["max"]
    pct = total_score / total_max * 100 if total_max > 0 else 0

    print(f"\n{'='*60}")
    print(f"  🎯 综合评分: {total_score}/{total_max} ({pct:.0f}%)")

    if pct >= 70:
        verdict = "🟢 强烈关注 — 多维度共振，可考虑建仓"
    elif pct >= 50:
        verdict = "🟡 适度关注 — 有看点但需确认，观察为主"
    elif pct >= 30:
        verdict = "🟠 谨慎 — 信号偏弱，不建议追入"
    else:
        verdict = "🔴 回避 — 多维度走弱，风险较大"

    print(f"  → {verdict}")
    print(f"{'='*60}")

    # 风险提示
    print(f"\n⚠️ 以上分析仅供参考，不构成投资建议")
    print(f"   投资有风险，入市需谨慎")
    print(f"   空仓不丢人，亏钱才丢人")


# ── CLI ──────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 stock_full.py <股票代码> [名称]")
        print("示例: python3 stock_full.py sh600519 贵州茅台")
        print("      python3 stock_full.py sz002594 比亚迪")
        sys.exit(1)

    code = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    full_analysis(code, name)
