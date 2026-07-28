# a-stock-data-quant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SkillHub](https://img.shields.io/badge/SkillHub-Published-purple?logo=datacamp)](https://skillhub.cn/skills/astockdataquant)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-orange?logo=anthropic)](https://claude.ai/settings/plugins/submit)
[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue?logo=datacamp)](https://clawhub.ai/plugins/a-stock-data-quant)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://python.org)
[![A-Share](https://img.shields.io/badge/A股-量化分析-red)](https://github.com/jangviktor-web/a-stock-data-quant)

A股量化分析工具箱 — 技术指标 · 形态识别 · 策略回测 · 实时行情 · 多数据源备份 · AI金融分析 · 筹码分布 · 板块资金流 · F10财务 · 华尔街见闻 · 研报/公告/互动易

> 版本: `v3.6.0` | 基于 [akshare](https://github.com/akfamily/akshare) + [MyTT](https://github.com/mpquant/MyTT) 构建
>
> 数据源: akshare (主) + 百度财经 + 通达信(mootdx) + 东财数据中心 + 同花顺 + 腾讯 + 东方财富 + 华尔街见闻 + 巨潮资讯
>
> AI能力: 东方财富妙想 (免费) + 东财/财联社/华尔街见闻新闻聚合
>
> 平台: [SkillHub](https://skillhub.cn/skills/astockdataquant) · [ClawHub](https://clawhub.ai) · [Claude Code](https://claude.ai) · [CherryStudio](https://cherry-ai.com) · [GitHub](https://github.com/jangviktor-web/a-stock-data-quant)

---

## 特性亮点

### 多数据源自动降级

当主数据源 (akshare) 失效时，自动切换到备用源，确保分析不中断：

```
akshare 失败 → 百度财经 / 通达信 / 东财数据中心 / 同花顺
实时行情: 腾讯 → 东方财富 → mootdx (三级降级)
K线数据: 新浪 → 腾讯 → mootdx → 百度 (四级降级)
```

降级过程对用户透明，stderr 输出 `[降级]` 提示，不影响正常输出。

### 东方财富妙想 AI

免费使用，基于东方财富专业数据库，支持：
- **AI 诊断**: 基本面+技术面+资金面+估值综合分析
- **AI 选股**: 自然语言条件选股（"白酒板块龙头"）
- **AI 问答**: 任意金融问题
- **AI 资讯**: 实时财经新闻搜索
- **AI 基金**: 基金诊断+持仓分析

### 20+ 技术指标 + 7 种策略

MA/EMA/MACD/RSI/BOLL/KDJ/CCI/ATR/OBV/WR/BIAS/DMI 等 20+ 指标，
支持 buy_hold/ma_cross/macd/rsi/boll/kdj/ensemble 7 种回测策略。

### 筹码分布分析 (v3.5.0)

基于K线+换手率近似计算筹码分布（移植自 [go-stock](https://github.com/ArvinLovegood/go-stock)），采用换手率衰减+高斯核分配算法，输出平均成本/获利比例/集中度，辅助判断套牢盘和获利盘压力。

### 板块资金流 (v3.5.0)

行业/概念板块主力净流入排名（东财 data.eastmoney.com），区分行业资金（持续性）和概念资金（短线炒作），支持个股资金流历史查询。

### F10 财务指标 (v3.5.0)

东财 datacenter 历史财务数据（营收/净利润/ROE/毛利率/资产负债率/EPS），支持多期趋势对比和机构预测数据。

### 华尔街见闻快讯 (v3.5.0)

11个频道全球财经快讯（全球7x24/A股/美股/港股/外汇/商品/黄金/原油/债券/加密货币/新股），实时掌握市场动态。

### 研报/公告/互动易 (v3.5.0)

个股研究报告（东财 reportapi）、上市公司公告（东财 np-anotice-stock）、互动易投资者问答（巨潮 irm.cninfo），基本面研究一站式数据。

### 市场温度计 (v3.3.0)

综合5个维度（巴菲特指标/股债利差/涨跌停比/QVIX波动率/市场活跃度）计算0-100温度分数，判断市场偏热(贪婪)还是偏冷(恐惧)。

### 个股估值分位 (v3.3.0)

获取PE/PB/PS历史数据（约2000+交易日），计算当前估值在历史区间中的百分位，判断低估/合理/偏高。

### PanWatch 数据集成 (v3.4.0)

移植自 [PanWatch](https://github.com/TNT-Likely/PanWatch) 的轻量数据接口，不依赖 akshare，基于东方财富 push2/push2his 和腾讯 qt.gtimg.cn，提供热门股票排行/热门板块/板块成分股/资金流向细分/基本面快照。

### 广发MCP数据矩阵 (v3.6.0)

- ETF排行榜: 13种榜单 (涨幅/跌幅/规模/换手率/资金流等)
- 龙虎榜深度: 上榜排行/指定日期查询/营业部统计/日历视图
- 指数估值分位: PE/PB百分位 + 低估/合理/高估评估 + 关联ETF
- 财务对比: 市值/PE/PB/行业均值/历史百分位

---

## 安装方式

### 方式一：SkillHub（推荐，支持 9+ AI Agent）

**第一步：安装 SkillHub CLI**

```bash
curl -fsSL https://skillhub.cn/install/install.sh | bash
```

**第二步：安装技能**

```bash
skillhub install astockdataquant
```

在线浏览：[skillhub.cn/skills/astockdataquant](https://skillhub.cn/skills/astockdataquant)

### 方式二：ClawHub / OpenClaw

```bash
clawhub package install a-stock-data-quant
```

在线浏览：[clawhub.ai](https://clawhub.ai) 搜索 `a-stock-data-quant`

### 方式三：Claude Code 插件市场

```bash
# 在 Claude Code CLI 中搜索并安装
/install-plugin a-stock-data-quant
```

或手动安装：

```bash
cd ~/.claude/skills
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式四：CherryStudio 技能

1. 打开 CherryStudio → Skills
2. 搜索 `a-stock-data-quant`
3. 点击安装

或手动克隆到 CherryStudio skills 目录：

```bash
cd "C:\Users\<用户名>\AppData\Roaming\CherryStudio\Data\Skills"
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式五：直接克隆（独立使用）

```bash
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
cd a-stock-data-quant
pip install -r requirements.txt
python bin/quant.py list
```

---

## 快速开始

```bash
# 安装依赖
pip install akshare numpy pandas requests mootdx

# 综合分析（推荐入口）
python bin/quant.py analyze sh600519

# 多股对比
python bin/quant.py compare sh600519,sz000858,sh601212

# 实时行情
python bin/quant.py realtime sh600519,sz000858

# 筹码分布
python bin/quant.py chip 600519

# 板块资金流
python bin/quant.py board-flow --type concept

# F10财务指标
python bin/quant.py finance 600519

# 华尔街见闻快讯
python bin/quant.py wscn --channel a-stock-channel

# 个股研报
python bin/quant.py report 600519

# 市场温度计
python bin/quant.py market-temp

# 估值分位
python bin/quant.py valuation 600519

# AI 诊断
python bin/quant.py em-diagnose sh600519

# 新闻资讯
python bin/quant.py news

# 查看所有命令
python bin/quant.py list

# ETF涨幅榜
python bin/quant.py etf-rank --type gainers --top 5

# 龙虎榜排行 (近1月)
python bin/quant.py lhb-gf --mode rank --months m1

# 指数估值分位
python bin/quant.py index-val --top 10

# 广发财务对比
python bin/quant.py gf-quant 600519,000858
```

> Windows 环境用 `python` 代替 `python3`，需要 `PYTHONIOENCODING=utf-8`

---

## 命令一览

### 核心分析

| 命令 | 功能 | 说明 |
|------|------|------|
| `analyze` | 综合分析 | 行情+指标+形态+策略信号+回测，一次出完整报告 |
| `compare` | 多股对比 | 并排对比多只股票技术面，内置实时行情和综合评分 |
| `backtest` | 策略回测 | 7种策略回测，支持止损/资金量/HTML图表输出 |
| `scan` | 市场扫描 | 全市场板块扫描，按策略信号排序 |
| `indicators` | 技术指标 | MA/MACD/RSI/KDJ/BOLL/CCI/ATR/OBV 等 20+ 指标 |
| `pattern` | 形态识别 | W底、V型反转、杯柄、三重底、回踩买入、Zigzag |
| `fund` | 资金面 | 主力资金流向、融资融券、大中小单分析 |
| `diagnose` | 综合诊断 | 技术面+资金面+形态多维度评分 |

### 数据查询

| 命令 | 功能 | 说明 |
|------|------|------|
| `realtime` | 实时行情 | 腾讯/东方财富/mootdx 秒级行情，三级降级 |
| `search` | 股票搜索 | 关键词搜索股票代码 |
| `data` | 原始行情 | K线数据，支持多周期 (1m~1M) |
| `market` | 市场情绪面 | 涨停池/跌停池/龙虎榜/北向资金/融资融券 |
| `market-temp` | 市场温度计 | 5维度加权温度分数(0-100)，判断贪婪/恐惧 |
| `valuation` | 估值分位 | PE/PB/PS历史百分位，判断低估/合理/偏高 |
| `info` | 个股深度 | 限售解禁/股东人数/十大股东/行业PE/大宗交易 |
| `macro` | 宏观数据 | CPI/PPI/GDP/PMI/M2/LPR/进出口 |
| `hotspot` | 市场热点 | 人气榜+概念板块+行业板块涨跌 |
| `news` | 新闻资讯 | 东财7x24快讯+财联社电报+东财搜索 |

### 筹码/资金/财务 (v3.5.0)

| 命令 | 功能 | 说明 |
|------|------|------|
| `chip` | 筹码分布 | 换手率衰减+高斯核算法，输出平均成本/获利比例/集中度 |
| `board-flow` | 板块资金流 | 行业/概念板块主力净流入排名 |
| `finance` | F10财务指标 | 营收/净利润/ROE/毛利率/资产负债率，多期趋势 |

### 资讯/研报/互动 (v3.5.0)

| 命令 | 功能 | 说明 |
|------|------|------|
| `wscn` | 华尔街见闻 | 11频道全球财经快讯 |
| `report` | 个股研报 | 东财reportapi，标题/机构/评级/作者 |
| `notice` | 上市公司公告 | 东财np-anotice-stock，标题/日期/类型 |
| `interactive` | 互动易数据 | 巨潮资讯投资者问答 |

### PanWatch 数据 (v3.4.0)

| 命令 | 功能 | 说明 |
|------|------|------|
| `hot-stocks` | 热门股票排行 | 按成交额/涨幅/换手率排序 |
| `hot-boards` | 热门板块排行 | 行业/概念板块涨跌排名 |
| `board-stocks` | 板块成分股 | 指定板块的成分股列表 |
| `capital-flow` | 资金流向细分 | 主力/超大单/大单/中单/小单净流入 |
| `fundamentals` | 基本面快照 | PE/PB/总市值/流通市值 |

### 广发MCP数据 (v3.6.0)

| 命令 | 说明 | 示例 |
|------|------|------|
| `etf-rank` | ETF排行榜 (13种) | `etf-rank --type gainers` |
| `lhb-gf` | 龙虎榜深度分析 | `lhb-gf --mode rank --months m3` |
| `index-val` | 指数估值分位 | `index-val --top 10` |
| `gf-quant` | 广发财务对比 | `gf-quant 600519,000858` |

### AI 能力 (东方财富妙想)

| 命令 | 功能 | 说明 |
|------|------|------|
| `em-diagnose` | AI 诊断 | 基本面+技术面+资金面+估值综合分析 |
| `em-pick` | AI 选股 | 自然语言条件选股 |
| `em-ask` | AI 问答 | 任意金融问题 |
| `em-news` | AI 资讯 | 实时财经新闻搜索 |
| `em-fund` | AI 基金 | 基金诊断+持仓分析 |

### 辅助工具

| 命令 | 功能 | 说明 |
|------|------|------|
| `cache` | 缓存管理 | 查看/清理数据缓存 |
| `list` | 资源列表 | 查看所有可用指标/策略/形态 |

---

## 详细使用指南

### analyze — 综合分析

一次出完整报告：行情概览 + 技术指标 + 形态识别 + 策略信号 + 策略回测。

```bash
python bin/quant.py analyze sh600519                        # 默认日线
python bin/quant.py analyze sh600519 --period 1w --count 500  # 周线500根
python bin/quant.py analyze sh510500 --capital 200000 --stop-loss 0.05
python bin/quant.py analyze sh600519 --html                  # 生成HTML图表
```

输出包含：
- **行情概览**: 最新价、涨跌幅、区间高低点、均价、成交量
- **技术指标**: MA5/10/20/60、MACD、RSI、KDJ、BOLL、ATR
- **形态识别**: W底、V型反转、杯柄、三重底、回踩买入、Zigzag 转折点
- **策略信号**: 7种策略的最新买卖信号和共振情况
- **策略回测**: 各策略收益率、年化、最大回撤、夏普比率、胜率
- **综合判断**: 多空评分和建议

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
python bin/quant.py compare sh600519,sz000858,sh601212
python bin/quant.py compare sh000001,sz399001,sz399006 --period 1w
```

输出各股指标并排对比 + 综合评分排名 + 实时价格。评分最高 = 技术面最强。

### backtest — 策略回测

```bash
python bin/quant.py backtest sh510500 --strategy ensemble    # 多策略共振（推荐）
python bin/quant.py backtest sh600519 --strategy macd --html # 含HTML图表
python bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
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

### chip — 筹码分布分析

基于K线+换手率近似计算筹码分布（移植自 go-stock），输出平均成本/获利比例/集中度。

```bash
python bin/quant.py chip 600519                # 默认日线120根（裸代码自动补全sh/sz前缀）
python bin/quant.py chip sh600519 --count 250  # 250根K线
python bin/quant.py chip sh600519 --bins 100   # 100个价格分箱
```

```
============================================================
  筹码分布分析 (120个交易日)
============================================================
  当前价格: 1308.00
  平均成本: 1358.63
  获利比例: 31.7%
  价格区间: 1151.01 ~ 1568.00
  筹码集中度(前5): 17.2%
------------------------------------------------------------
  筹码最集中价位:
       1409.02    4.5%  ████
       1403.81    4.4%  ████
       1414.23    3.4%  ███
============================================================
  解读: 筹码分布相对均衡
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
python bin/quant.py board-flow                     # 行业板块(默认)
python bin/quant.py board-flow --type concept      # 概念板块
python bin/quant.py board-flow --top 10            # 前10名
```

```
======================================================================
  行业板块资金流排名 (主力净流入)
======================================================================
  排名 板块名称     代码       主力净流入
----------------------------------------------------------------------
  1    半导体     BK1036     🟢+166.18亿
  2    通信设备   BK0448     🟢+47.04亿
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
python bin/quant.py finance 600519                # 最近5期
python bin/quant.py finance 600519 --periods 8    # 最近8期
python bin/quant.py finance 600519 --forecast     # 含机构预测
```

```
================================================================================
  F10 主要财务指标: 600519
================================================================================
  📅 2026-03-31
    每股收益: 21.76 元 | 扣非: None 元
    每股净资产: 216.32 元
    ROE(加权): 10.57% | 毛利率: 89.76%
    资产负债率: 12.12%
    营收同比: 6.34% | 净利同比: 1.47%
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

多频道全球财经快讯（全球7x24/A股/美股/港股/外汇/商品/黄金/原油/债券/加密货币/新股）。

```bash
python bin/quant.py wscn                              # 全球7x24(默认)
python bin/quant.py wscn --channel a-stock-channel    # A股频道
python bin/quant.py wscn --channel us-stock-channel   # 美股频道
python bin/quant.py wscn --limit 10                   # 10条
```

频道列表：`global-channel` | `a-stock-channel` | `us-stock-channel` | `hk-stock-channel` | `forex-channel` | `commodity-channel` | `goldc-channel` | `oil-channel` | `bond-channel` | `crypto-channel` | `xgb-channel`

### report — 个股研究报告

东财 reportapi 个股研报（标题/机构/评级/作者）。

```bash
python bin/quant.py report 600519              # 最近30天
python bin/quant.py report 600519 --days 90    # 最近90天
python bin/quant.py report 600519 --top 5      # 前5篇
```

### notice — 上市公司公告

东财 np-anotice-stock 公告列表（标题/日期/类型）。

```bash
python bin/quant.py notice 600519             # 茅台公告
python bin/quant.py notice 600519 --top 10    # 前10条
```

### interactive — 互动易数据

巨潮资讯互动易平台（投资者问答）。

```bash
python bin/quant.py interactive 茅台           # 搜索关键词
python bin/quant.py interactive 600519        # 股票代码
python bin/quant.py interactive 新能源 --top 10
```

### market — 市场情绪面

涨停池/跌停池/情绪判断/龙虎榜/板块资金流/北向资金/融资融券，一站式市场情绪全景。

```bash
python bin/quant.py market                      # 默认参数
python bin/quant.py market --limit 10 --days 5  # 显示10条，龙虎榜近5日
```

**情绪周期速查**：

| 状态 | 涨停数 | 跌停数 | 操作建议 |
|------|--------|--------|---------|
| 冰点期 | <30 | >50 | 最好的埋伏时机 |
| 修复期 | 增多 | 减少 | 小仓位试探 |
| 高潮期 | >100 | <10 | 最危险，准备撤退 |
| 退潮期 | 减少 | 增多 | 绝不追高 |

### market-temp — 市场温度计

综合5个维度计算0-100温度分数，判断市场偏热(贪婪)还是偏冷(恐惧)。

```bash
python bin/quant.py market-temp              # 市场温度
python bin/quant.py market-temp --json       # JSON输出
```

**温度解读**：≥70 偏热/贪婪（注意风险）| 40-70 中性 | <40 偏冷/恐惧（关注机会）

### valuation — 个股估值分位

获取PE/PB/PS历史数据（约2000+交易日），计算当前估值在历史区间中的百分位。

```bash
python bin/quant.py valuation 600519         # 茅台估值分位
python bin/quant.py valuation 000858 --json  # JSON输出
```

**分位解读**：<30% 低估（关注）| 30-70% 合理 | >70% 偏高（谨慎）

### PanWatch 数据集成

移植自 PanWatch 的轻量数据接口，不依赖 akshare。

```bash
python bin/quant.py hot-stocks --mode turnover        # 热门股票(成交额)
python bin/quant.py hot-stocks --mode gainers -n 10   # 热门股票(涨幅前10)
python bin/quant.py hot-boards --mode gainers         # 热门板块(涨幅)
python bin/quant.py board-stocks BK0892 -n 10         # 白酒板块成分股
python bin/quant.py capital-flow 600519               # 资金流向细分
python bin/quant.py fundamentals 600519               # 基本面快照
```

### info — 个股深度

```bash
python bin/quant.py info 600519     # 茅台深度信息
python bin/quant.py info 000858     # 五粮液深度信息
```

输出：限售解禁 / 股东人数变化 / 十大流通股东 / 行业PE估值 / 大宗交易。

**解读要点**：
- 股东人数减少 → 筹码集中，主力在吸筹（偏多）
- 股东人数增加 → 散户化趋势（偏空）
- 十大股东增减 → 机构/港资是否在加仓
- 行业PE对比 → 个股PE是否高于行业中位

### news — 新闻资讯

```bash
python bin/quant.py news                    # 快讯列表 (东财7x24+财联社)
python bin/quant.py news 茅台                # 搜索关键词
python bin/quant.py news --top 10           # 显示10条
```

聚合东财7x24快讯 + 财联社电报 + 东财搜索，按时间排序。

### realtime — 实时行情

```bash
python bin/quant.py realtime sh600519,sz000858,sh601212
python bin/quant.py realtime sh600519 --source tencent
```

三级降级：腾讯 → 东方财富 → mootdx，涨🟢跌🔴标识。

### 东方财富妙想 AI

需在 `config.yaml` 设置 `em_api_key`。注册：https://ai.eastmoney.com/mxClaw

```bash
python bin/quant.py em-diagnose sh600519                  # AI综合诊断
python bin/quant.py em-pick "白酒板块龙头"                 # AI自然语言选股
python bin/quant.py em-ask "茅台Q1业绩怎么样"              # AI问答
python bin/quant.py em-news 白酒                           # AI资讯
python bin/quant.py em-fund sh600519                      # AI基金分析
```

### etf-rank — ETF排行榜

```bash
python bin/quant.py etf-rank --type gainers --top 10
python bin/quant.py etf-rank --type losers
python bin/quant.py etf-rank --type volume
```

13种榜单: gainers(涨幅)/losers(跌幅)/volume(成交额)/turnover(换手率)/scale(规模)/premium(溢价)/discount(折价)/flow(资金流)/five_gainers(5日涨幅)/five_losers(5日跌幅)/five_volume(5日成交额)/five_turnover(5日换手)/five_flow(5日资金流)

**解读速查**：
- 涨幅前3 + 换手率>10% → 短期资金博弈激烈
- 规模榜前10 → 市场主流配置方向
- 溢价率高 → 场内情绪过热, 注意套利风险

### lhb-gf — 龙虎榜深度分析

```bash
python bin/quant.py lhb-gf --mode rank --months m1 --top 10
python bin/quant.py lhb-gf --mode date --date 20260728
```

**解读速查**：
- 上榜>10次/月 → 高度活跃游资标的
- 买入额>>卖出额 → 资金净流入, 关注持续性
- 机构席位连续出现 → 机构资金动向

### index-val — 指数估值分位

```bash
python bin/quant.py index-val --top 20
```

**解读速查**：
- PE分位<20% → 历史低估区间, 关注配置机会
- PE分位>80% → 历史高估区间, 注意风险
- 低估 + 关联ETF资金流入 → 左侧布局信号

### gf-quant — 广发财务对比

```bash
python bin/quant.py gf-quant 600519,000858,000568
```

输出: 总市值/PE(TTM)/PB/行业均值/历史百分位

**解读速查**：
- PE低于行业均值 + 百分位<30% → 相对低估
- PB百分位<20% → 历史底部区域

---

## 多数据源架构

### 降级链

| 数据类型 | 主数据源 | 备用源 |
|----------|----------|--------|
| 实时行情 | 腾讯 → 东方财富 | mootdx (通达信TCP 7709) |
| 历史K线 | 新浪 → 腾讯 | mootdx → 百度财经 |
| 资金流向 | akshare | 百度分钟级资金流 |
| 龙虎榜 | akshare | 东财数据中心 (datacenter-web) |
| 融资融券 | akshare | 东财数据中心 |
| 限售解禁 | akshare | 东财数据中心 |
| 股东人数 | akshare | 东财数据中心 |
| 大宗交易 | akshare | 东财数据中心 |
| 北向资金 | akshare | 同花顺 (hexin.cn) |
| 概念板块 | akshare | 百度财经 |
| 新闻资讯 | 东财7x24 + 财联社 | 华尔街见闻 |
| 板块资金流 | 东财 data.eastmoney.com | akshare sector_fund_flow |
| F10财务 | 东财 datacenter | — |
| 估值分位 | 东财 datacenter | 百度估值 |
| 研报 | 东财 reportapi | — |
| 公告 | 东财 np-anotice-stock | — |
| 互动易 | 巨潮 irm.cninfo | — |
| 华尔街见闻 | api-one-wscn.awtmt.com | — |
| 广发MCP | ETF排行/龙虎榜/指数估值/财务对比 | MCP JSON-RPC | Bearer Token |

### 备用数据源说明

- **mootdx**: 通达信 TCP 7709 协议，无认证无IP限制，适合做备用
- **百度财经**: `finance.pae.baidu.com`，纯HTTP，支持K线/资金流/概念板块
- **东财数据中心**: `datacenter-web.eastmoney.com`，6种报告类型
- **东财datacenter**: `datacenter.eastmoney.com`，F10财务/估值历史
- **东财板块资金**: `data.eastmoney.com/dataapi/bkzj`，行业/概念板块资金流
- **东财reportapi**: `reportapi.eastmoney.com`，个股研究报告
- **东财公告**: `np-anotice-stock.eastmoney.com`，上市公司公告
- **同花顺**: `data.hexin.cn`，北向资金数据
- **华尔街见闻**: `api-one-wscn.awtmt.com`，11频道全球快讯
- **巨潮资讯**: `irm.cninfo.com.cn`，互动易投资者问答

### 降级机制

使用 `@_with_fallback` 装饰器包装 akshare 函数：

```python
@_with_fallback(_ak_fund_flow, ('百度', _baidu_fund_flow))
def get_fund_flow(code, market=None):
    ...
```

- 主数据源成功 → 直接返回
- 主数据源失败 → 自动尝试备用源
- 全部失败 → 返回空结果，stderr 输出错误信息
- 降级提示输出到 stderr，不污染 stdout JSON 输出

---

## 配置管理

### config.yaml

```yaml
# 东方财富妙想 AI (免费)
em_api_key: "em_xxxxxxxxxxxxxxxx"

# 广发MCP数据 API Key
gf_api_key: "your-gf-api-key"

# 回测参数
capital: 100000        # 初始资金
commission: 0.001      # 手续费率
slippage: 0.001        # 滑点

# 数据缓存
cache:
  enabled: true
  ttl_hours: 4         # 缓存有效期（小时）
  directory: cache

# HTML 输出
html:
  directory: html
```

### 数据缓存

```bash
python bin/quant.py cache stats         # 查看缓存统计
python bin/quant.py cache clear         # 清理过期缓存
python bin/quant.py cache clear --older-than 7  # 清理7天前的缓存
```

---

## 可用技术指标

```
MA    简单移动平均      EMA   指数移动平均
MACD  指数平滑异同      RSI   相对强弱指标
BOLL  布林带           KDJ   随机指标
CCI   商品通道指数      WR    威廉指标
ATR   真实波动幅度      BIAS  乖离率
OBV   能量潮           DMI   动向指标
TRIX  三重指数平滑      VR    成交量比率
EMV   简易波动指标      BBI   多空指标
MFI   资金流量指标      ASI   累积摆动指标
PSY   心理线           SAR   抛物线指标
```

---

## 形态识别

| 形态 | 参数 | 信号 |
|------|------|------|
| W底 | `w-bottom` | 底部反转 |
| V型反转 | `v-reversal` | 底部反转 |
| 杯柄 | `cup-handle` | 突破买入 |
| 三重底 | `triple-bottom` | 底部确认 |
| 回踩买入 | `dip-buy` | 顺势买入 |
| Zigzag | `zigzag` | 趋势转折点 |

"已确认"比"形成中"更可靠。深度越大，后续反弹空间通常越大。

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
| `--source` | 数据源(tencent/eastmoney/mootdx) | auto |

## K线周期

| 周期 | 代码 | 说明 |
|------|------|------|
| 日线 | `1d` | 默认，适合中长线分析 |
| 周线 | `1w` | 中期趋势 |
| 月线 | `1M` | 长期趋势 |
| 1分钟 | `1m` | 超短线 |
| 5分钟 | `5m` | 短线 |
| 15分钟 | `15m` | 日内波段 |
| 30分钟 | `30m` | 日内波段 |
| 60分钟 | `60m` | 日内波段 |

## 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6位 | `sh600519`(茅台)、`sh000001`(上证指数)、`sh510500`(中证500ETF) |
| 深市 | `sz` + 6位 | `sz000858`(五粮液)、`sz399006`(创业板指) |

不知道代码？→ `python bin/quant.py search 茅台`

> `chip` 和 `finance` 命令支持裸代码（如 `600519`），自动补全 sh/sz 前缀。

---

## 项目结构

```
a-stock-data-quant/
├── bin/
│   ├── quant.py              # CLI 主入口 (2400+ 行)
│   └── stock_full.py         # 综合分析脚本
├── lib/
│   ├── akshare_data.py       # akshare 数据层 + 降级链
│   ├── ashare.py             # 行情数据获取 (含mootdx/百度降级)
│   ├── backtest.py           # 回测引擎
│   ├── board_fund_flow.py    # 板块资金流 (东财data.eastmoney.com)
│   ├── chart.py              # ECharts HTML 图表生成
│   ├── chip_distribution.py  # 筹码分布计算 (移植自 go-stock)
│   ├── data_cache.py         # CSV+JSON 数据缓存 (4档TTL)
│   ├── em_api.py             # 东方财富妙想 AI 接口
│   ├── f10_finance.py        # F10财务指标 (东财datacenter)
│   ├── fallback.py           # 多数据源降级引擎
│   ├── market_temp.py        # 市场温度计 (5指标加权)
│   ├── mytt.py               # 技术指标库 (MyTT V3.4)
│   ├── patterns.py           # 形态识别
│   ├── realtime_data.py      # 实时行情 (腾讯/东方财富/mootdx)
│   ├── settings.py           # 配置管理
│   ├── sources_baidu.py      # 百度财经 API (K线/资金流/概念)
│   ├── sources_datacenter.py # 东财数据中心 (龙虎榜/融资/大宗/股东/解禁)
│   ├── sources_gf.py        # 广发MCP数据适配层
│   ├── sources_hexin.py      # 同花顺北向资金
│   ├── sources_mootdx.py     # 通达信 TCP 7709 (实时/K线)
│   ├── sources_news.py       # 新闻聚合 (东财7x24/财联社/搜索)
│   ├── sources_panwatch.py   # PanWatch 数据接口 (热门榜/板块/资金/基本面)
│   ├── sources_wallstreetcn.py # 华尔街见闻 (全球快讯/财经日历)
│   ├── stock_notice.py       # 研报/公告/互动易 (东财reportapi/np-anotice/巨潮)
│   ├── strategies.py         # 策略模块
│   └── valuation.py          # 个股估值分位 (东财datacenter+百度)
├── config.yaml               # 配置文件
├── SKILL.md                  # AI Agent skill 文档
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
  ├─ em-diagnose/em-pick/em-ask/em-news/em-fund
  │   → em_api.py (东方财富妙想AI) → output
  ├─ etf-rank (ETF排行榜)
  │   → sources_gf.py → MCP etf_rank → 格式化 → output
  ├─ lhb-gf (龙虎榜深度)
  │   → sources_gf.py → MCP lhb → 格式化 → output
  ├─ index-val (指数估值分位)
  │   → sources_gf.py → MCP windmill → 格式化 → output
  ├─ gf-quant (广发财务对比)
  │   → sources_gf.py → MCP quant → 格式化 → output
  └─ macro/hotspot/cache/list
      → akshare_data.py / settings.py / data_cache.py → output
```

---

## 更新日志

### v3.6.0 (2026-07-28)

- 新增: 广发MCP数据矩阵 (etf-rank/lhb-gf/index-val/gf-quant)
- 新增: ETF排行榜13种榜单 (涨幅/跌幅/规模/换手率/资金流等)
- 新增: 龙虎榜深度分析 (上榜排行/指定日期/营业部统计)
- 新增: 指数估值分位 (PE/PB百分位 + 关联ETF)
- 新增: 广发财务对比 (市值/估值/行业均值/历史百分位)
- 修复: hot-stocks 格式化崩溃 (price为float时ValueError)
- 修复: _gf_check() config读取函数名错误
- 修复: index-val NoneType格式化 (pePercent/pbPercent为null)

### v3.5.0 (2026-07-21)

**go-stock P0+P1 集成 — 筹码分布/板块资金流/F10财务/华尔街见闻/研报/公告/互动易**

新增功能：
- **筹码分布** (`chip`): 基于换手率衰减+高斯核分配算法，输出平均成本/获利比例/集中度（移植自 [go-stock](https://github.com/ArvinLovegood/go-stock)）
- **板块资金流** (`board-flow`): 行业/概念板块主力净流入排名（东财 data.eastmoney.com）
- **F10财务指标** (`finance`): 营收/净利润/ROE/毛利率/资产负债率/EPS，多期趋势+机构预测
- **华尔街见闻快讯** (`wscn`): 11频道全球财经快讯（全球/A股/美股/港股/外汇/商品/黄金/原油/债券/加密/新股）
- **个股研报** (`report`): 东财 reportapi 研报列表（标题/机构/评级/作者）
- **上市公司公告** (`notice`): 东财 np-anotice-stock 公告列表
- **互动易数据** (`interactive`): 巨潮资讯投资者问答搜索

新增文件：
- `lib/chip_distribution.py` — 筹码分布计算（换手率衰减+高斯核，纯算法无网络依赖）
- `lib/board_fund_flow.py` — 板块资金流（东财 data.eastmoney.com/dataapi/bkzj）
- `lib/f10_finance.py` — F10财务指标（东财 datacenter RPT_F10_FINANCE_MAINFINADATA）
- `lib/sources_wallstreetcn.py` — 华尔街见闻（api-one-wscn.awtmt.com，11频道）
- `lib/stock_notice.py` — 研报/公告/互动易（东财reportapi/np-anotice/巨潮irm.cninfo）

改进：
- `chip` 命令支持裸代码（600519 自动补全为 sh600519）
- SKILL.md 新增场景 F-I 工作流模板、解读速查表、反例 11-14、异常处理 7 条
- 端到端测试全部通过（7个新命令均验证可用）

### v3.4.0 (2026-07-15)

**PanWatch 数据集成 — 热门榜/板块/资金/基本面**

新增功能：
- **热门股票排行** (`hot-stocks`): 按成交额/涨幅/换手率排序
- **热门板块排行** (`hot-boards`): 行业/概念板块涨跌排名
- **板块成分股** (`board-stocks`): 指定板块的成分股列表
- **资金流向细分** (`capital-flow`): 主力/超大单/大单/中单/小单净流入
- **基本面快照** (`fundamentals`): PE/PB/总市值/流通市值

新增文件：
- `lib/sources_panwatch.py` — PanWatch 数据接口（东财 push2/push2his + 腾讯 qt.gtimg）

改进：
- 不依赖 akshare 的轻量数据接口，东财 push2 限流时自动降级到 akshare

### v3.3.0 (2026-07-10)

**市场温度计 + 估值分位**

新增功能：
- **市场温度计** (`market-temp`): 综合5维度（巴菲特指标/股债利差/涨跌停比/QVIX/活跃度）计算0-100温度分数
- **个股估值分位** (`valuation`): PE/PB/PS历史百分位（约2000+交易日），判断低估/合理/偏高

新增文件：
- `lib/market_temp.py` — 市场温度计（5指标加权）
- `lib/valuation.py` — 个股估值分位（东财datacenter + 百度估值）

改进：
- 涨停池/跌停池/板块资金流增加东财 push2 备用源
- JSON 缓存层（cached_json_fetch，4档TTL）
- 检查点优化（🔴 CHECKPOINT / 🛑 STOP 视觉标记）

### v3.2.0 (2026-05-19)

**多数据源备份系统 + 新闻资讯**

新增功能：
- **多数据源自动降级**: 主数据源失效时自动切换备用源，确保分析不中断
  - 实时行情: 腾讯 → 东方财富 → mootdx (三级降级)
  - K线数据: 新浪 → 腾讯 → mootdx → 百度 (四级降级)
  - 资金流向: akshare → 百度分钟级
  - 龙虎榜/融资融券/限售解禁/股东人数/大宗交易: akshare → 东财数据中心
  - 北向资金: akshare → 同花顺
  - 概念板块: akshare → 百度财经
- **新闻资讯命令** (`news`): 东财7x24快讯 + 财联社电报 + 东财搜索
- **市场情绪面命令** (`market`): 涨停池/跌停池/龙虎榜/北向资金/融资融券一站式分析
- **个股深度命令** (`info`): 限售解禁/股东人数/十大股东/行业PE/大宗交易

新增文件：
- `lib/fallback.py` — 降级引擎 `try_sources()` + `@_with_fallback` 装饰器
- `lib/sources_baidu.py` — 百度财经 K线/资金流/概念板块
- `lib/sources_mootdx.py` — 通达信 TCP 7709 实时行情+K线
- `lib/sources_datacenter.py` — 东财数据中心 6类报告
- `lib/sources_hexin.py` — 同花顺北向资金
- `lib/sources_news.py` — 东财7x24+财联社+东财搜索

改进：
- `akshare_data.py`: 12个函数加 `@_with_fallback` 降级链
- `realtime_data.py`: 加 mootdx 第三级降级
- `ashare.py`: K线加 mootdx + 百度降级
- 修复 akshare API 签名变更导致的多个函数失效
- 修复涨停池/跌停池默认日期错误
- 修复龙虎榜金额单位显示错误
- 修复股东人数/限售解禁列名不匹配

### v3.1.0 (2026-05-15)

**东方财富妙想 AI 集成 + 实时行情**

新增功能：
- **东方财富妙想 AI**: 5个AI命令 (em-diagnose/em-pick/em-ask/em-news/em-fund)
- **实时行情** (`realtime`): 腾讯/东方财富秒级行情
- **股票搜索** (`search`): 关键词搜索股票代码
- **HTML 图表**: ECharts 交互式图表，支持缩放/拖拽/数据点悬停
- **数据缓存**: CSV 缓存，支持 TTL 过期
- **配置管理**: `config.yaml` 集中配置

新增文件：
- `lib/em_api.py` — 东方财富妙想 AI 接口
- `lib/realtime_data.py` — 腾讯/东方财富实时行情
- `lib/chart.py` — ECharts HTML 图表生成
- `lib/data_cache.py` — CSV 数据缓存
- `lib/settings.py` — 配置管理

### v3.0.0 (2026-05-15)

**综合诊断 + 宏观数据**

新增功能：
- **综合诊断** (`diagnose`): 技术面+资金面+形态多维度评分
- **宏观数据** (`macro`): CPI/PPI/GDP/PMI/M2/LPR/进出口
- **市场热点** (`hotspot`): 人气榜+概念板块+行业板块

### v2.0.0 (2026-05-13)

**核心分析功能**

新增功能：
- **综合分析** (`analyze`): 行情+指标+形态+策略信号+回测
- **多股对比** (`compare`): 并排对比多只股票技术面
- **策略回测** (`backtest`): 7种策略回测
- **市场扫描** (`scan`): 全市场板块扫描
- **形态识别** (`pattern`): W底/V型反转/杯柄/三重底/回踩买入

### v1.0.0 (2026-05-12)

**初始版本**

- 基于 akshare + MyTT + Ashare 构建
- 支持 20+ 技术指标
- 支持资金流向分析

---

## 致谢

- [Ashare](https://github.com/mpquant/Ashare) — 行情数据接口
- [akshare](https://github.com/akfamily/akshare) — A股数据
- [MyTT](https://github.com/mpquant/MyTT) — 技术指标库
- [mootdx](https://github.com/mootdx/mootdx) — 通达信行情接口
- [东方财富妙想](https://ai-oss.eastmoney.com) — AI金融分析接口
- [go-stock](https://github.com/ArvinLovegood/go-stock) — 筹码分布算法参考
- [PanWatch](https://github.com/TNT-Likely/PanWatch) — 热门榜/板块/资金数据接口参考
- [华尔街见闻](https://wallstreetcn.com) — 全球财经快讯
- [巨潮资讯](https://www.cninfo.com.cn) — 互动易投资者问答
- [广发证券MCP数据平台](https://mcp.gf.com.cn) — ETF排行/龙虎榜/指数估值/财务对比
- [stock-api](https://github.com/zhangxiangliang/stock-api) — 实时行情协议参考
- [a-stock-data](https://github.com/simonlin1212/a-stock-data) — 备用数据源 API 参考

## License

MIT
