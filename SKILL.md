---
name: a-stock-data-quant
version: "3.6.0"
description: "A-share stock quantitative analysis toolkit with 20+ technical indicators, 7 backtesting strategies, candlestick pattern recognition, multi-source data fallback, real-time quotes, AI financial analysis, 7x24 news, chip distribution, board fund flow, F10 finance, Wallstreetcn news, research reports, and interactive answers. Supports Claude Code, Cursor, Codex, Gemini, and 5+ other AI agents."
keywords: ["stock", "quant", "a-share", "backtest", "technical-analysis", "finance", "akshare", "trading", "investment", "china-stock", "MACD", "RSI", "KDJ", "real-time-quotes", "AI-analysis"]
author: "jangviktor"
license: "MIT"
repository: "https://github.com/jangviktor-web/a-stock-data-quant"
category: "data"
allowedTools:
  - Bash
  - Read
  - Glob
  - Grep
---

# a-stock-data-quant — A股量化分析工具箱

> 技术指标 · 形态识别 · 策略回测 · 实时行情 · 新闻资讯 · AI金融分析（东方财富妙想）

**⚠️ 免责声明**：本工具仅供学习研究，不构成投资建议。技术分析基于历史数据，不预测未来。

**🔄 多数据源**: 主源 akshare 失效时自动降级到备用源（百度/mootdx/datacenter/同花顺），确保数据可用性。

---

## TL;DR

```bash
python3 bin/quant.py analyze sh600519                    # 综合分析
python3 bin/quant.py compare sh600519,sz000858           # 多股对比
python3 bin/quant.py backtest sh510500 --strategy ensemble --html  # 回测+图表
python3 bin/quant.py realtime sh600519,sz000858          # 实时行情
python3 bin/quant.py market-temp                         # 市场温度计
python3 bin/quant.py valuation 600519                  # 估值分位
python3 bin/quant.py hot-stocks --mode turnover          # 热门股票排行
python3 bin/quant.py hot-boards --mode gainers           # 热门板块排行
python3 bin/quant.py board-stocks BK0892                 # 板块成分股
python3 bin/quant.py capital-flow 600519               # 资金流向细分
python3 bin/quant.py fundamentals 600519                 # 基本面快照
python3 bin/quant.py news                                # 新闻快讯
python3 bin/quant.py em-diagnose sh600519                # AI诊断
python3 bin/quant.py search 白银                          # 搜索股票
python3 bin/quant.py chip sh600519                       # 筹码分布
python3 bin/quant.py board-flow --type concept           # 概念板块资金流
python3 bin/quant.py finance 600519                      # F10财务指标
python3 bin/quant.py wscn --channel a-stock-channel      # 华尔街见闻A股快讯
python3 bin/quant.py report 600519                       # 个股研报
python3 bin/quant.py notice 600519                       # 上市公司公告
python3 bin/quant.py interactive 茅台                     # 互动易数据
python3 bin/quant.py etf-rank --type gainers             # ETF排行榜 (GF MCP)
python3 bin/quant.py lhb-gf                              # 龙虎榜深度分析 (GF MCP)
python3 bin/quant.py index-val --top 10                    # 指数估值分位 (GF MCP)
python3 bin/quant.py gf-quant 600519,000858              # 广发财务对比 (GF MCP)
# GF MCP数据源: ETF排行/龙虎榜/指数估值/财务对比
```

---

## 安装

### 方式一：SkillHub (推荐，支持9+ AI Agent)

```bash
# Claude Code
npx @skill-hub/cli install a-stock-data-quant --agent claude

# Cursor
npx @skill-hub/cli install a-stock-data-quant --agent cursor

# 其他 Agent (codex/gemini/copilot/windsurf/cline/roo/opencode)
npx @skill-hub/cli install a-stock-data-quant --agent <agent>
```

### 方式二：ClawHub

```bash
clawhub package install a-stock-data-quant
```

### 方式三：GitHub 直接克隆

```bash
cd ~/.claude/skills   # Claude Code
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 依赖安装

```bash
pip install akshare numpy pandas requests mootdx
# Windows: 用 python 代替 python3
```

---

## 决策树

```
用户问了什么？
│
├─ "分析某只股票" ──────────→ analyze
├─ "哪只股票更强" ──────────→ compare
├─ "回测某个策略" ──────────→ backtest
├─ "今天市场有什么信号" ────→ scan
├─ "RSI/MACD/均线多少" ────→ indicators
├─ "有没有W底/形态" ──────→ pattern
├─ "主力资金怎么样" ──────→ fund
├─ "现在价格多少" ─────────→ realtime
├─ "搜一下XX股票" ─────────→ search
├─ "帮我诊断一下" ─────────→ diagnose
├─ "AI分析/AI选股" ────────→ em-diagnose / em-pick
├─ "AI问答/AI资讯" ────────→ em-ask / em-news
├─ "AI基金分析" ───────────→ em-fund
├─ "宏观数据(CPI/GDP)" ───→ macro
├─ "市场热点" ─────────────→ hotspot
├─ "市场情绪/涨停/跌停" ──→ market
├─ "市场温度/贪婪恐惧" ──→ market-temp
├─ "热门股票/板块排行" ──→ hot-stocks / hot-boards
├─ "板块成分股" ─────────→ board-stocks
├─ "资金流向/主力" ──────→ capital-flow
├─ "基本面/PE/PB" ───────→ fundamentals
├─ "估值分位/PE高低" ────→ valuation
├─ "个股深度/股东/解禁" ──→ info
├─ "筹码分布/成本" ──────→ chip
├─ "板块资金流/概念资金" ─→ board-flow
├─ "财务指标/ROE/营收" ──→ finance
├─ "华尔街见闻/全球快讯" ─→ wscn
├─ "研报/机构评级" ──────→ report
├─ "公告/上市公司公告" ──→ notice
├─ "互动易/投资者问答" ──→ interactive
├─ "ETF排行/涨跌榜" ──→ etf-rank
├─ "龙虎榜/游资/营业部" → lhb-gf
├─ "指数估值/PE分位" ──→ index-val
├─ "财务对比/广发F10" ─→ gf-quant
├─ "缓存管理" ─────────────→ cache
├─ "新闻/快讯/资讯" ────────→ news
└─ "有哪些功能" ───────────→ list
```

---

## 检查点

### 🔴 CHECKPOINT A：执行前确认
- 确认代码（"茅台"→ sh600519）、参数（周期、策略、资金量）
- 🛑 STOP：用户说"不用了"/"只看看" → 展示命令+示例，**不执行**
- 🛑 STOP：回测含 `--capital`/`--stop-loss` → 确认资金量和止损比例后再执行

### 🔴 CHECKPOINT B：结果解读
- 一句话总结 + 关键数值引用 + 后续建议
- 🛑 STOP：数据不足（<30条K线）→ 提示"数据量不足，结论仅供参考"

### 🔴 CHECKPOINT C：投资建议前
- 🛑 STOP：涉及买卖信号 → **必须**声明"技术分析仅供参考，不构成投资建议"
- 🛑 STOP：单指标触发 → 至少2个维度交叉验证后才可给出方向性结论

---

## 股票代码

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6位 | `sh600519`(茅台)、`sh000001`(上证指数)、`sh510500`(中证500ETF) |
| 深市 | `sz` + 6位 | `sz000858`(五粮液)、`sz399006`(创业板指) |

> 不知道代码？→ `python3 bin/quant.py search 茅台`

---

## 核心命令

### analyze — 综合分析（推荐入口）

行情 + 指标 + 形态 + 策略信号 + 回测，一次出完整报告。

```bash
python3 bin/quant.py analyze sh600519                        # 默认日线
python3 bin/quant.py analyze sh600519 --period 1w --count 500  # 周线500根
python3 bin/quant.py analyze sh600519 --html                  # 生成HTML图表
```

**解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| MA5偏离>2% | 短期涨太快 | 注意回调 |
| MACD金叉 | 中期动能向上 | 偏多 |
| RSI>70 | 超买 | 不宜追高 |
| ensemble跑赢buy_hold | 策略有超额收益 | 可参考信号 |
| 最大回撤>15% | 波动大 | 需设止损 |

### compare — 多股对比

```bash
python3 bin/quant.py compare sh600519,sz000858,sh601212      # 自动显示实时行情
python3 bin/quant.py compare sh000001,sz399001,sz399006 --period 1w
```

输出：各股指标并排 + 综合评分排名 + 实时价格。评分最高 = 技术面最强。

### backtest — 策略回测

🔴 CHECKPOINT：执行前确认股票代码、策略名、资金量。含 `--capital`/`--stop-loss` 时须用户确认参数。

```bash
python3 bin/quant.py backtest sh510500 --strategy ensemble    # 多策略共振
python3 bin/quant.py backtest sh600519 --strategy macd --html # 含HTML图表
python3 bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
```

| 策略 | 逻辑 | 适用场景 |
|------|------|---------|
| `buy_hold` | 买入持有（基准） | 对比基准 |
| `ma_cross` | MA5/MA20金叉死叉 | 趋势行情 |
| `macd` | DIF/DEA交叉 | 中期趋势 |
| `rsi` | RSI超买超卖 | 震荡行情 |
| `boll` | 布林带轨道反弹 | 区间震荡 |
| `kdj` | KDJ金叉死叉 | 短线交易 |
| `ensemble` | **多策略共振（推荐）** | 过滤假信号 |

**关键指标**：总收益率 vs 基准、最大回撤<15%较健康、夏普>1较好>2优秀、胜率>50%正期望。

### scan — 市场扫描

🛑 STOP：批量扫描（>20只）前确认范围，加2-3秒间隔避免429限流。

```bash
python3 bin/quant.py scan --strategy macd
python3 bin/quant.py scan --strategy ma_cross --min-volume 1000000
```

输出按信号排序，金叉=潜在买入机会。结合RSI过滤超买（>70不追），成交量<100万流动性差。

### indicators — 技术指标

```bash
python3 bin/quant.py indicators sh600519 --indicators ma5,ma10,ma20,macd,rsi
python3 bin/quant.py indicators sh600519 --indicators boll,kdj,cci,wr,atr,bias,obv
```

多指标交叉验证更可靠（如MACD金叉+RSI中性=较安全的买入信号）。

### pattern — 形态识别

```bash
python3 bin/quant.py pattern sh600519                            # 全部形态
python3 bin/quant.py pattern sh600519 --pattern w-bottom,cup-handle  # 指定形态
```

| 形态 | 信号 |
|------|------|
| W底(`w-bottom`) | 底部反转 |
| V型反转(`v-reversal`) | 底部反转 |
| 杯柄(`cup-handle`) | 突破买入 |
| 三重底(`triple-bottom`) | 底部确认 |
| 回踩买入(`dip-buy`) | 顺势买入 |

"已确认"比"形成中"更可靠。深度越大，后续反弹空间通常越大。

### fund — 资金面分析

```bash
python3 bin/quant.py fund sh600519
```

主力净流入=机构在买（偏多）。连续3日以上主力流入=资金面趋势确认。

### data — 原始行情

```bash
python3 bin/quant.py data sh600519 --count 30               # 日线
python3 bin/quant.py data sh600519 --period 15m --count 50   # 15分钟线
```

---

## 新增命令

### realtime — 实时行情

腾讯/东方财富秒级数据，无需akshare。

```bash
python3 bin/quant.py realtime sh600519,sz000858,sh601212
python3 bin/quant.py realtime sh600519 --source tencent
```

```
📡 实时行情  数据源: auto
  🔴 贵州茅台(SH600519)  1332.95  -0.69%  高:1339.28 低:1327.11 昨:1342.17
  🔴 五 粮 液(SZ000858)  86.87  -2.38%  高:88.08 低:86.62 昨:88.99
```

涨🟢/跌🔴标识，含最高价/最低价/昨收。

### search — 股票搜索

```bash
python3 bin/quant.py search 白银
python3 bin/quant.py search 宁德时代
```

```
🔍 搜索: 白银
  SZBK1616     白银
  共找到 1 条结果
```

### diagnose — 综合诊断

技术面 + 资金面 + 形态，多维度评分。

```bash
python3 bin/quant.py diagnose sh600519
```

```
🏥 股票综合诊断: sh600519
  技术面得分: -3/8
  形态: w-bottom(2) v-reversal(1) cup-handle(1)
  综合诊断: 强烈看空 🔴🔴🔴 (技术-3 + 资金+0 = -3)
```

### macro — 宏观数据

```bash
python3 bin/quant.py macro cpi       # CPI
python3 bin/quant.py macro pmi       # PMI
python3 bin/quant.py macro gdp       # GDP
python3 bin/quant.py macro m2        # M2货币供应
python3 bin/quant.py macro lpr       # LPR利率
python3 bin/quant.py macro trade     # 进出口
```

```
📊 宏观数据: 居民消费价格指数 (CPI)
  2026年04月份  全国-同比增长: 1.20  全国-环比增长: 0.30
  2026年03月份  全国-同比增长: 1.00  全国-环比增长: -0.70
```

### hotspot — 市场热点

```bash
python3 bin/quant.py hotspot
python3 bin/quant.py hotspot --top 30
```

⚠️ hotspot 依赖东方财富网络接口，部分网络环境下可能不可用。

### market — 市场情绪面分析

涨停池/跌停池/情绪判断/龙虎榜/板块资金流/北向资金/融资融券，一站式市场情绪全景。

```bash
python3 bin/quant.py market                      # 默认参数
python3 bin/quant.py market --limit 10 --days 5  # 显示10条，龙虎榜近5日
python3 bin/quant.py market --period 5日          # 板块资金流用5日累计
```

```
🌊 市场情绪面分析
  🔴 涨停池: 54只（利仁科技5连板、蒙娜丽莎6连板）
  🟢 跌停池: 15只（通达股份2连跌停）
  情绪判断: 涨停54只 / 跌停15只 → 🌊 正常
  🐉 龙虎榜: 德明利 +22.1亿、长盈通 +15.0亿
  📋 融资融券: 融资余额 14,408亿
```

**情绪周期速查**：

| 状态 | 涨停数 | 跌停数 | 操作建议 |
|------|--------|--------|---------|
| ❄️ 冰点期 | <30 | >50 | 最好的埋伏时机 |
| 🌡️ 修复期 | 增多 | 减少 | 小仓位试探 |
| 🔥 高潮期 | >100 | <10 | 最危险，准备撤退 |
| 🌊 退潮期 | 减少 | 增多 | 绝不追高 |

### market-temp — 市场温度计

综合5个维度（巴菲特指标/股债利差/涨跌停比/QVIX波动率/市场活跃度）计算0-100温度分数，判断市场偏热(贪婪)还是偏冷(恐惧)。

```bash
python3 bin/quant.py market-temp              # 市场温度
python3 bin/quant.py market-temp --json       # JSON输出
```

```
==================================================
        A股市场温度计 (Market Temperature)
==================================================
  综合温度: 53.4 / 100  [WARM] 中性
  [==========>         ] 53/100
--------------------------------------------------
  股债利差 (权重20%)  利差=0.06%  子评分: 40.6
  新高/新低 (权重20%) 涨停/跌停比(30/21)  子评分: 58.6
  QVIX波动率 (权重20%) QVIX=22.66  子评分: 49.4
  市场活跃度 (权重15%) 涨停占比(30/51)  子评分: 68.8
==================================================
```

**温度解读**：≥70 偏热/贪婪（注意风险）| 40-70 中性 | <40 偏冷/恐惧（关注机会）

### PanWatch 数据集成（热门榜/板块/资金/基本面）

移植自 [PanWatch](https://github.com/TNT-Likely/PanWatch) 的轻量数据接口，不依赖 akshare，基于东方财富 push2/push2his 和腾讯 qt.gtimg.cn。

```bash
python3 bin/quant.py hot-stocks --mode turnover        # 热门股票(成交额)
python3 bin/quant.py hot-stocks --mode gainers -n 10   # 热门股票(涨幅前10)
python3 bin/quant.py hot-boards --mode gainers         # 热门板块(涨幅)
python3 bin/quant.py board-stocks BK0892 -n 10         # 白酒板块成分股
python3 bin/quant.py capital-flow 600519               # 资金流向细分
python3 bin/quant.py fundamentals 600519             # 基本面快照
```

**`capital-flow` 输出示例**：

```
============================================================
  资金流向细分: 600519 贵州茅台
============================================================
  主力净流入: -5.79亿 (-5.69%)  [主力流出]
  超大单: -0.95亿
  大单: -4.84亿
  中单: 5.80亿
  小单: -0.04亿
  5日主力净流入: XX亿
============================================================
```

**`fundamentals` 输出示例**：

```
============================================================
  基本面快照: 600519 贵州茅台
============================================================
  PE(TTM): 19.77
  PE(静态): 15.01
  PB:      7.02
  总市值: 16351.07 亿
  流通市值: 16351.07 亿
============================================================
```

### valuation — 个股估值分位

获取PE/PB/PS历史数据（东财datacenter，约2000+交易日），计算当前估值在历史区间中的百分位。

```bash
python3 bin/quant.py valuation 600519         # 茅台估值分位
python3 bin/quant.py valuation 000858 --json  # JSON输出
```

```
==================================================
  个股估值分析: 600519
==================================================
  PE(市盈率): [LOW]
    当前值: 19.77  分位数: 4% (低估)
    最小: 17.66 | 中位: 32.49 | 最大: 73.29
  PB(市净率): [LOW]
    当前值: 6.04  分位数: 2% (低估)
  综合评估: 低估
==================================================
```

**分位解读**：<30% 低估（关注）| 30-70% 合理 | >70% 偏高（谨慎）

### info — 个股深度信息

限售解禁/股东人数变化/十大流通股东/行业PE估值/大宗交易，个股多维度深度分析。

```bash
python3 bin/quant.py info 600519     # 茅台深度信息
python3 bin/quant.py info 000858     # 五粮液深度信息
```

```
📋 个股深度信息: 600519
  📅 限售解禁: 近期无解禁
  👥 股东人数: 2026Q1 243,159户 (减少12,733户 -4.98%) → 筹码集中 🟢
  🏛️ 十大流通股东: 茅台集团54.07%、港中央6.91%(+609万股)
  📊 行业PE: 制造业 加权PE 37.51 / 中位PE 52.00
  🏷️ 大宗交易: 2026-05-15 成交价1332.96 2笔
```

**解读要点**：
- 股东人数减少 → 筹码集中，主力在吸筹（偏多）
- 股东人数增加 → 散户化趋势（偏空）
- 十大股东增减 → 机构/港资是否在加仓
- 行业PE对比 → 个股PE是否高于行业中位

### chip — 筹码分布分析

基于K线+换手率近似计算筹码分布（移植自 go-stock），输出平均成本/获利比例/集中度。

```bash
python3 bin/quant.py chip sh600519              # 默认日线120根
python3 bin/quant.py chip sh600519 --count 250  # 250根K线
python3 bin/quant.py chip sh600519 --bins 100   # 100个价格分箱
```

```
============================================================
  筹码分布分析 (120个交易日)
============================================================
  当前价格: 1332.95
  平均成本: 1285.42
  获利比例: 68.5%
  价格区间: 1180.00 ~ 1450.00
  筹码集中度(前5): 42.3%
------------------------------------------------------------
  筹码最集中价位:
      1305.50   8.5%  ████████
      1285.25   7.2%  ███████
      1325.75   6.8%  ██████
============================================================
  解读: 获利盘多，注意回调压力
```

**解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| 获利比例>80% | 大部分筹码盈利 | 抛压大，注意回调 |
| 获利比例<20% | 大部分筹码套牢 | 可能接近底部区域 |
| 平均成本≈当前价 | 市场成本一致 | 变盘窗口，关注方向 |
| 集中度(前5)>40% | 筹码高度集中 | 主力控盘，波动可能加大 |
| 集中度(前5)<15% | 筹码分散 | 散户行情，趋势性弱 |

### board-flow — 板块资金流

行业/概念板块主力净流入排名（东财 data.eastmoney.com）。

```bash
python3 bin/quant.py board-flow                     # 行业板块(默认)
python3 bin/quant.py board-flow --type concept      # 概念板块
python3 bin/quant.py board-flow --top 10            # 前10名
```

```
======================================================================
  行业板块资金流排名 (主力净流入)
======================================================================
  排名 板块名称     代码       主力净流入
----------------------------------------------------------------------
  1    半导体     BK0447     🟢+25.36亿
  2    汽车整车   BK0481     🟢+18.92亿
  3    白酒       BK0477     🔴-12.45亿
======================================================================
  统计: 15个流入 / 5个流出
```

**解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| 行业板块连续3日净流入 | 资金持续看好该行业 | 关注行业内龙头个股 |
| 概念板块单日暴增 | 短线热点炒作 | 追高风险大，注意持续性 |
| 流入/流出比>3:1 | 市场资金面偏多 | 可适度参与 |
| 流出板块集中在某行业 | 资金撤退 | 回避该行业个股 |

### finance — F10财务指标

东财 datacenter 历史财务数据（营收/净利润/ROE/毛利率/资产负债率）。

```bash
python3 bin/quant.py finance 600519                # 最近5期
python3 bin/quant.py finance 600519 --periods 8    # 最近8期
python3 bin/quant.py finance 600519 --forecast     # 含机构预测
```

```
================================================================================
  F10 主要财务指标: 600519
================================================================================
  📅 2026-03-31
    每股收益: 21.38 元 | 扣非: 20.95 元
    营业总收入: 539.02亿 | 归属净利润: 272.15亿
    ROE(加权): 8.25% | 毛利率: 91.50%
    营收同比: +6.54% | 净利同比: +1.47%
================================================================================
```

**解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| ROE连续3期>15% | 盈利能力强且稳定 | 优质公司特征 |
| 毛利率同比下降>5% | 成本压力或竞争加剧 | 关注后续趋势 |
| 营收同比+但净利同比- | 增收不增利 | 警惕费用失控 |
| 资产负债率>70% | 高杠杆 | 注意偿债风险（银行/地产除外） |
| 扣非EPS远低于EPS | 非经常损益占比大 | 盈利质量差，不可持续 |

### wscn — 华尔街见闻快讯

多频道全球财经快讯（全球7x24/A股/美股/港股/外汇/商品/黄金/原油/债券）。

```bash
python3 bin/quant.py wscn                              # 全球7x24(默认)
python3 bin/quant.py wscn --channel a-stock-channel    # A股频道
python3 bin/quant.py wscn --channel us-stock-channel   # 美股频道
python3 bin/quant.py wscn --limit 10                   # 10条
```

频道列表：`global-channel` | `a-stock-channel` | `us-stock-channel` | `hk-stock-channel` | `forex-channel` | `commodity-channel` | `goldc-channel` | `oil-channel` | `bond-channel` | `crypto-channel` | `xgb-channel`

### report — 个股研究报告

东财 reportapi 个股研报（标题/机构/评级/作者）。

```bash
python3 bin/quant.py report 600519              # 最近30天
python3 bin/quant.py report 600519 --days 90    # 最近90天
python3 bin/quant.py report 600519 --top 5      # 前5篇
```

### notice — 上市公司公告

东财 np-anotice-stock 公告列表（标题/日期/类型）。

```bash
python3 bin/quant.py notice 600519             # 茅台公告
python3 bin/quant.py notice 600519 --top 10    # 前10条
```

### interactive — 互动易数据

巨潮资讯互动易平台（投资者问答）。

```bash
python3 bin/quant.py interactive 茅台           # 搜索关键词
python3 bin/quant.py interactive 600519        # 股票代码
python3 bin/quant.py interactive 新能源 --top 10
```

### 广发 GF MCP 数据 (etf-rank / lhb-gf / index-val / gf-quant)

基于广发证券 MCP server 的数据适配层，覆盖 ETF 排行、龙虎榜深度分析、指数估值分位、财务对比。需在 `config.yaml` 设置 `gf_api_key`（Bearer token）。

#### etf-rank — ETF排行榜

涨幅/跌幅/规模/换手率等13种榜单。

```bash
python3 bin/quant.py etf-rank --type gainers       # 涨幅榜
python3 bin/quant.py etf-rank --type losers        # 跌幅榜
python3 bin/quant.py etf-rank --type scale         # 规模榜
python3 bin/quant.py etf-rank --type turnover      # 换手率榜
```

#### lhb-gf — 龙虎榜深度分析

上榜排行/指定日期/营业部统计。

```bash
python3 bin/quant.py lhb-gf                        # 上榜排行
python3 bin/quant.py lhb-gf --date 2026-05-19      # 指定日期
python3 bin/quant.py lhb-gf --mode broker          # 营业部统计
```

#### index-val — 指数估值分位

PE/PB百分位 + 关联ETF。

```bash
python3 bin/quant.py index-val --top 10             # 指数估值分位
python3 bin/quant.py index-val --top 20 --json      # JSON输出
```

**分位解读**：<20% 历史低估区间 | 20-80% 合理 | >80% 历史高估区间

#### gf-quant — 广发财务对比

市值/估值/PE百分位/行业均值多维对比。

```bash
python3 bin/quant.py gf-quant 600519,000858       # 茅台 vs 五粮液
python3 bin/quant.py gf-quant 600519 --json       # JSON输出
```

**ETF/指数估值解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| ETF涨幅榜前3 + 换手率>10% | 短期资金博弈 | 注意波动，不追高 |
| 指数PE分位<20% | 历史低估区间 | 关注左侧布局机会 |
| 指数PE分位>80% | 历史高估区间 | 谨慎，注意回调风险 |
| 龙虎榜上榜>10次/月 | 高度活跃游资标的 | 结合机构席位连续性判断 |

### 东方财富妙想 AI (em-*)

需在 `config.yaml` 设置 `em_api_key`。注册：https://ai.eastmoney.com/mxClaw

```bash
python3 bin/quant.py em-diagnose sh600519                  # AI综合诊断
python3 bin/quant.py em-pick "白酒板块龙头"                 # AI自然语言选股
python3 bin/quant.py em-ask "茅台Q1业绩怎么样"              # AI问答
python3 bin/quant.py em-news 白酒                           # AI资讯
python3 bin/quant.py em-fund sh600519                      # AI基金分析
```

```
🤖 东方财富妙想 AI 诊断
  查询: 分析sh600519

  一、基本面：2026Q1营收539亿(+6.54%)，净利润272亿(+1.47%)
  二、技术面：股价1332.95，下行通道，PE历史百分位17.36%
  三、资金面：主力净流出6.52亿，连续10日DDX为负
  总结：基本面稳健，估值历史低位，短期技术面偏弱
```

```
🤖 东方财富妙想 AI 选股
  条件: 白酒板块龙头  符合条件: 57 只
  |600519|贵州茅台|1332.95|-0.69%|1.67万亿|
  |000858|五 粮 液|86.87|-2.38%|3371.95亿|
  ...
```

### news — 新闻资讯

东财7x24快讯 + 财联社电报 + 东财搜索，实时掌握市场动态。

```bash
python3 bin/quant.py news                    # 快讯列表 (东财7x24+财联社)
python3 bin/quant.py news 茅台                # 搜索关键词
python3 bin/quant.py news --top 10           # 显示10条
```

```
📰 新闻资讯
  1. 【水利部针对赣鄂湘粤桂黔琼七省区启动洪水防御Ⅳ级应急响应】
     2026-05-19 13:42  [财联社]
  2. 【三星电子股价转涨，抹去早盘5.3%的跌幅】
     2026-05-19 13:41  [财联社]
```

### cache — 缓存管理

```bash
python3 bin/quant.py cache stats    # 查看缓存
python3 bin/quant.py cache clear    # 清理缓存
```

### list — 可用资源

```bash
python3 bin/quant.py list
```

---

## 行动映射

| 看到什么 | 意味着 | 建议 |
|---------|--------|------|
| MACD金叉 + RSI<70 + 多头排列 | 技术面偏多 | 可关注，逢低布局 |
| MACD死叉 + RSI>70 + 空头排列 | 技术面偏空 | 减仓观望 |
| MA5偏离>3% | 短期涨太快 | 不宜追高 |
| ensemble夏普>1.5且跑赢基准 | 策略有效 | 可参考信号 |
| 最大回撤>20% | 波动大 | 严格止损 |
| compare评分差>20分 | 强弱分明 | 关注最强 |
| 获利比例>80% + 集中度>40% | 筹码高度获利 | 抛压大，不宜追高 |
| 获利比例<20% + 估值分位<30% | 套牢+低估 | 关注底部机会 |
| 行业板块连续3日净流入 | 资金持续看好 | 关注板块内龙头 |
| 概念板块单日暴增 | 短线炒作 | 注意持续性，不追高 |
| ROE连续>15% + 毛利率稳定 | 基本面优质 | 可长期关注 |
| 营收增+净利降 | 增收不增利 | 警惕费用/成本问题 |
| 研报密集发布(>5篇/月) | 机构关注度高 | 结合评级方向判断 |
| 互动易频繁提及某概念 | 市场热点关联 | 交叉验证news/wscn |
| 指数PE分位<10% + 关联ETF资金流入 | 低估+资金共振 | 左侧布局窗口 |
| 龙虎榜机构席位连续买入 | 机构资金持续介入 | 跟踪机构动向 |
| ETF换手率暴增 + 涨幅居前 | 短期资金博弈激烈 | 注意波动，不追高 |

---

## K线周期

`1d`(日线) | `1w`(周线) | `1M`(月线) | `1m` | `5m` | `15m` | `30m` | `60m`

---

## 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--period` | K线周期 | `1d` |
| `--count` | 数据条数 | `120` |
| `--strategy` | 策略名 | `buy_hold` |
| `--capital` | 初始资金 | `100000` |
| `--stop-loss` | 止损比例(如0.05=5%) | 无 |
| `--ensemble N` | 共振阈值 | `3` |
| `--html` | 生成HTML图表 | — |
| `--json` | 输出JSON格式 | — |
| `--source` | 数据源(tencent/eastmoney) | auto |

---

## 工作流模板

### 场景A：分析一只股票
```
用户："茅台技术面怎么样"
→ 🔴 CHECKPOINT A：确认 sh600519
→ python3 bin/quant.py analyze sh600519
→ 🔴 CHECKPOINT B：一句话总结 + 关键数值 + 后续建议
→ 🔴 CHECKPOINT C：如涉及买卖，声明免责
```

### 场景B：选股对比
```
用户："茅台五粮液泸州老窖哪个强"
→ 🔴 CHECKPOINT A：确认代码
→ python3 bin/quant.py compare sh600519,sz000858,sh601212
→ 🔴 CHECKPOINT B：排名 + 对比表 + 一句话结论
```

### 场景C：策略验证
```
用户："ensemble回测中证500"
→ 🔴 CHECKPOINT A：确认 sh510500 + ensemble策略
→ python3 bin/quant.py backtest sh510500 --strategy ensemble
→ 🔴 CHECKPOINT B：收益率/回撤/夏普 vs buy_hold
→ 🔴 CHECKPOINT C：声明回测不代表未来
```

### 场景D：AI诊断
```
用户："帮我全面分析一下茅台"
→ 🔴 CHECKPOINT A：确认 sh600519 + em_api_key已配置
→ python3 bin/quant.py em-diagnose sh600519  (AI基本面+技术面+资金面)
→ python3 bin/quant.py analyze sh600519      (本地技术指标验证)
→ 🔴 CHECKPOINT B：综合AI报告+本地数据，给出结论
```

### 场景E：复合需求
```
用户："茅台和五粮液哪个强，顺便看看MACD回测"
→ 🔴 CHECKPOINT A：确认代码 + 回测参数
→ Step 1: compare sh600519,sz000858
→ Step 2: backtest sh600519 --strategy macd
→ Step 3: backtest sz000858 --strategy macd
→ 🔴 CHECKPOINT B：综合结论
```

### 场景F：筹码与成本分析
```
用户："茅台现在筹码怎么样，套牢盘多不多"
→ 🔴 CHECKPOINT A：确认 sh600519
→ Step 1: chip sh600519              (筹码分布/获利比例/集中度)
→ Step 2: valuation 600519           (估值分位交叉验证)
→ 🔴 CHECKPOINT B：获利比例+平均成本+估值分位，综合判断当前位置
→ 🛑 STOP：获利比例>80% → 提示"获利盘多，注意回调压力"，不给出买入建议
```

### 场景G：板块资金流向
```
用户："今天资金都往哪跑"
→ Step 1: board-flow --type industry --top 10   (行业板块)
→ Step 2: board-flow --type concept --top 10    (概念板块)
→ 🔴 CHECKPOINT B：一句话总结资金主攻方向 + 连续流入板块
→ 🛑 STOP：概念板块单日暴增 → 提示"短线炒作，注意持续性"
```

### 场景H：基本面深度研究
```
用户："茅台基本面怎么样，机构怎么看"
→ 🔴 CHECKPOINT A：确认 600519
→ Step 1: finance 600519 --periods 5   (财务指标趋势)
→ Step 2: report 600519 --days 90      (近期研报/评级)
→ Step 3: notice 600519                (近期公告)
→ Step 4: info 600519                  (股东/解禁/大宗)
→ 🔴 CHECKPOINT B：财务趋势+机构评级+公告要点，综合结论
→ 🔴 CHECKPOINT C：涉及估值判断 → 声明"仅供参考，不构成投资建议"
```

### 场景I：资讯快讯速览
```
用户："最近有什么重要消息"
→ Step 1: wscn --limit 10                       (全球快讯)
→ Step 2: wscn --channel a-stock-channel --limit 5  (A股聚焦)
→ Step 3: news --top 10                          (东财+财联社)
→ 🔴 CHECKPOINT B：按重要性排序摘要，标注影响板块
→ 🛑 STOP：涉及具体买卖建议 → 只转述事实，不加主观判断
```

### 场景J：GF MCP数据交叉验证
```
用户："帮我看看现在哪些板块有机会"
→ 🔴 CHECKPOINT A：确认 gf_api_key 已配置
→ Step 1: index-val --top 10                      (指数估值分位)
→ Step 2: etf-rank --type gainers/turnover      (ETF资金流向)
→ Step 3: lhb-gf                                (龙虎榜游资动向)
→ Step 4: gf-quant <候选股>                      (财务对比验证)
→ 🔴 CHECKPOINT B：低估指数 + ETF资金流入 + 游资关注 = 板块性机会信号
→ 🔴 CHECKPOINT C：涉及买卖 → 声明"仅供参考，不构成投资建议"
```

---

## 反例黑名单（不要做的事）

| # | 反模式 | 为什么不要做 | 正确做法 |
|---|--------|-------------|---------|
| 1 | **单指标下结论** | 仅凭 RSI<30 就说"买入"，忽略趋势/量能/基本面 | 至少2个维度交叉验证（如 MACD金叉 + RSI中性 + 量能放大） |
| 2 | **追超买股** | RSI>70 或 MA5偏离>3% 时推荐买入 | 提示"短期超买，不宜追高"，等回调信号 |
| 3 | **忽略市场环境** | 大盘暴跌时只看个股技术面偏多就推荐 | 先 `market` 看情绪周期，冰点期/退潮期降低仓位建议 |
| 4 | **回测当预测** | "回测年化30%所以未来也能赚" | 必须声明"回测基于历史数据，不代表未来收益" |
| 5 | **跨行业裸比** | 拿银行股和科技股直接比 PE 高低 | 用 `info` 查行业PE中位数，在同行业内比较 |
| 6 | **忽略止损** | 给出买入建议但不提止损位 | 结合 ATR 或最大回撤给出止损参考（如"跌破MA20止损"） |
| 7 | **数据不足强分析** | 只有30根K线就跑周线回测 | 提示数据不足，建议增加 `--count` 或切换日线 |
| 8 | **替用户做决策** | "你应该现在买入XX" | 只输出技术面事实+信号，决策权留给用户 |
| 9 | **忽略免责声明** | 分析完直接结束 | 涉及买卖建议时必须附"技术分析仅供参考，不构成投资建议" |
| 10 | **批量请求不限流** | 一次 scan 200只股票不加间隔 | 批量分析加2-3秒间隔，避免触发数据源限流(429) |
| 11 | **筹码分布当精确数据** | 筹码分布是换手率近似估算，当作真实持仓成本 | 说明"基于换手率近似计算"，结合估值分位交叉验证 |
| 12 | **单日板块资金流下结论** | 仅凭一天板块资金流入就推荐板块 | 至少观察3日趋势，区分行业(持续)和概念(短线)资金 |
| 13 | **单期财务数据定论** | 仅看一期ROE/毛利率就判断公司好坏 | 用 `--periods 5` 看趋势，结合研报(`report`)交叉验证 |
| 14 | **快讯当交易信号** | 看到wscn/news某条消息就建议买卖 | 只转述事实+标注影响板块，不加主观买卖判断 |
| 15 | **仅凭ETF单日涨幅推荐买入** | 短期波动不代表趋势，单日涨幅易反转 | 结合估值分位(`index-val`)+多日资金流向交叉验证 |
| 16 | **龙虎榜数据滞后追高** | 上榜时可能已高位，游资次日可能出货 | 注意上榜日期，结合`lhb-gf`机构席位连续性判断 |

---

## 异常处理（三段式 Fallback）

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|---------|-----------|
| `ImportError: akshare` | `pip install akshare numpy pandas requests` | 使用不依赖akshare的模块（realtime/valuation/fundamentals） |
| 股票代码格式错 | 提示正确格式：`sh600519` / `sz000001` / 纯数字`600519` | 用 `search 关键词` 查找正确代码 |
| akshare 接口返回空/报错 | 自动切换备用源（@_with_fallback 装饰器） | 提示"数据源暂不可用，稍后重试" |
| 网络超时 / ConnectionError | 等待5秒后重试1次 | 提示"网络连接失败"，建议检查代理设置 |
| akshare 429 限流 | 批量分析加2-3秒间隔 | 等30秒后重试；仍失败则跳过该股票继续下一只 |
| push2 clist/fflow 连接重置 | 切换 akshare 同类函数（hot_rank_em/sector_hot） | 提示"东财接口限流"，建议非交易时段重试 |
| 股票停牌 | 提示"已停牌，数据可能不完整" | 仍输出最近交易日数据，标注⚠️ |
| 非交易时段查询 | 正常返回，数据截至上一交易日 | 无需额外处理 |
| 股票退市/不存在 | 提示"未找到该股票数据" | 建议用 `search` 确认代码是否正确 |
| K线数据不足（<30条） | 自动降级：周线→日线，提示用户 | 提示"数据量不足以计算指标，请增加 --count" |
| em-api 返回错误 | 自动降级到 em-ask 通用端点 | 提示"AI接口暂不可用"，建议用本地 analyze 替代 |
| 估值数据为空（新股/次新） | 缩短period到"近一年"重试 | 提示"上市时间过短，无足够历史数据计算分位" |
| 筹码分布获取失败 | 跳过筹码模块，仅输出PE/PB/PS分位 | 综合评估标注"筹码数据缺失" |
| market-temp 指标缺失 | 按可用指标归一化计算（权重自动调整） | 全部缺失时返回50分+错误提示 |
| wscn API 返回非20000 | 重试1次（间隔3秒） | 提示"华尔街见闻接口暂不可用"，建议用 `news` 替代 |
| report 返回空列表 | 扩大 `--days` 到180天重试 | 提示"近期无研报覆盖"，建议用 `em-diagnose` AI分析替代 |
| notice 接口超时 | 重试1次 | 提示"公告接口暂不可用"，建议直接访问巨潮资讯网 |
| interactive 搜索无结果 | 换用更短/更通用的关键词重试 | 提示"未找到相关互动易数据" |
| board-flow 连接重置 | 切换 akshare sector_fund_flow 同类函数 | 提示"东财板块资金接口限流"，建议非交易时段重试 |
| finance 财务数据为空 | 检查代码是否正确（`search`确认） | 提示"未找到财务数据"，新股/次新股可能无历史报告期 |
| GF MCP超时/401 | 检查`gf_api_key`配置，确认Bearer token有效 | 提示"GF MCP认证失败"，建议重新获取token |
| GF MCP返回空数据 | 非交易时间或参数错误，检查market/date参数 | 提示"无数据返回"，确认交易时段及参数格式后重试 |

---

## 项目结构

```
a-stock-data-quant/
├── bin/
│   ├── quant.py              # CLI 主入口
│   └── stock_full.py         # 综合分析脚本
├── lib/
│   ├── akshare_data.py       # akshare 数据层 (含降级链+push2ex备用)
│   ├── ashare.py             # 行情数据获取 (含mootdx/百度降级)
│   ├── backtest.py           # 回测引擎
│   ├── chart.py              # ECharts HTML 图表
│   ├── data_cache.py         # CSV+JSON 数据缓存 (4档TTL)
│   ├── em_api.py             # 东方财富妙想 AI 接口
│   ├── fallback.py           # 多数据源降级引擎
│   ├── market_temp.py        # 市场温度计 (5指标加权)
│   ├── mytt.py               # 技术指标库（MyTT V3.4）
│   ├── patterns.py           # 形态识别
│   ├── realtime_data.py      # 实时行情 (腾讯/东方财富/mootdx)
│   ├── settings.py           # 配置管理
│   ├── sources_baidu.py      # 百度财经 API (K线/资金流/概念)
│   ├── sources_datacenter.py # 东财数据中心 (龙虎榜/融资/大宗/股东/解禁)
│   ├── sources_gf.py         # 广发MCP数据适配层 (ETF/龙虎榜/指数估值/F10)
│   ├── sources_hexin.py      # 同花顺北向资金
│   ├── sources_mootdx.py     # 通达信 TCP 7709 (实时/K线)
│   ├── sources_news.py       # 新闻聚合 (东财7x24/财联社/搜索)
│   ├── sources_panwatch.py   # PanWatch 数据接口 (热门榜/板块/资金/基本面)
│   ├── sources_wallstreetcn.py # 华尔街见闻 (全球快讯/财经日历)
│   ├── stock_notice.py       # 研报/公告/互动易 (东财reportapi/np-anotice/巨潮)
│   ├── chip_distribution.py  # 筹码分布计算 (移植自 go-stock)
│   ├── board_fund_flow.py    # 板块资金流 (东财data.eastmoney.com)
│   ├── f10_finance.py        # F10财务指标 (东财datacenter)
│   ├── strategies.py         # 策略模块
│   └── valuation.py          # 个股估值分位 (东财datacenter+百度)
├── config.yaml               # 配置文件（em_api_key等）
├── requirements.txt          # Python 依赖
└── LICENSE                   # MIT
```

---

## 数据流

```
用户输入 → 意图路由 → quant.py CLI
  ├─ analyze/compare/backtest/scan/indicators/pattern/fund/diagnose
  │   → akshare_data.py → mytt.py (指标) → strategies.py (信号)
  │   → [降级] → sources_baidu.py / sources_datacenter.py / sources_hexin.py
  │   → backtest.py (回测) → chart.py (HTML) → output
  ├─ realtime/search
  │   → realtime_data.py (腾讯→东方财富→mootdx) → output
  ├─ news (新闻资讯)
  │   → sources_news.py (东财7x24/财联社/东财搜索) → output
  ├─ market (市场情绪面)
  │   → akshare_data.py (涨停池/跌停池/龙虎榜/北向/融资融券) → output
  ├─ market-temp (市场温度计)
  │   → market_temp.py (巴菲特/股债利差/涨跌停比/QVIX/活跃度) → output
  ├─ hot-stocks / hot-boards / board-stocks (热门榜/板块成分)
  │   → sources_panwatch.py (东财clist) → output
  ├─ capital-flow (资金流向细分)
  │   → sources_panwatch.py (东财fflow) → output
  ├─ fundamentals (基本面快照)
  │   → sources_panwatch.py (腾讯qt.gtimg) → output
  ├─ valuation (估值分位)
  │   → valuation.py (东财datacenter PE/PB/PS历史 → 分位计算) → output
  ├─ info (个股深度)
  │   → akshare_data.py (限售解禁/股东人数/十大股东/行业PE/大宗交易) → output
  ├─ chip (筹码分布)
  │   → ashare.py (K线) → chip_distribution.py (换手率衰减+高斯核) → output
  ├─ board-flow (板块资金流)
  │   → board_fund_flow.py (东财 data.eastmoney.com/dataapi/bkzj) → output
  ├─ finance (F10财务指标)
  │   → f10_finance.py (东财 datacenter RPT_F10_FINANCE_MAINFINADATA) → output
  ├─ wscn (华尔街见闻)
  │   → sources_wallstreetcn.py (api-one-wscn.awtmt.com) → output
  ├─ report/notice/interactive (研报/公告/互动易)
  │   → stock_notice.py (东财reportapi/np-anotice/巨潮irm.cninfo) → output
  ├─ etf-rank (ETF排行榜)
  │   → sources_gf.get_etf_rank() → MCP etf_rank server → 格式化输出
  ├─ lhb-gf (龙虎榜深度分析)
  │   → sources_gf.get_lhb_rank/by_date() → MCP lhb server → 格式化输出
  ├─ index-val (指数估值分位)
  │   → sources_gf.get_index_valuation() → MCP windmill server → 格式化输出
  ├─ gf-quant (广发财务对比)
  │   → sources_gf.get_gf_basic() → MCP quant server → 格式化输出
  ├─ em-diagnose/em-pick/em-ask/em-news/em-fund
  │   → em_api.py (东方财富妙想AI) → output
  └─ macro/hotspot/cache/list
      → akshare_data.py / settings.py / data_cache.py → output
```

---

## License

MIT
