<div align="center">

# a-stock-data-quant

**A 股量化分析工具箱 · 让 AI 成为你的量化分析师**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://python.org)
[![SkillHub](https://img.shields.io/badge/SkillHub-Published-purple?logo=datacamp)](https://skillhub.cn/skills/astockdataquant)
[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue?logo=datacamp)](https://clawhub.ai/plugins/a-stock-data-quant)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-orange?logo=anthropic)](https://claude.ai/settings/plugins/submit)
[![A-Share](https://img.shields.io/badge/A股-量化分析-red)](https://github.com/jangviktor-web/a-stock-data-quant)

> **v3.2.0** · 技术指标 · 形态识别 · 策略回测 · 实时行情 · 多数据源自动备份 · 东方财富 AI 金融分析<br>
> 基于 [akshare](https://github.com/akfamily/akshare) + [MyTT](https://github.com/mpquant/MyTT) 构建<br>
> 支持平台: [SkillHub](https://skillhub.cn/skills/astockdataquant) · [ClawHub](https://clawhub.ai) · [Claude Code](https://claude.ai) · [CherryStudio](https://cherry-ai.com)

</div>

---

## 目录

- [为什么选择 a-stock-data-quant](#为什么选择-a-stock-data-quant)
- [核心特性](#核心特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
  - [核心分析](#核心分析)
  - [数据查询](#数据查询)
  - [AI 能力 (东方财富妙想)](#ai-能力-东方财富妙想)
  - [辅助工具](#辅助工具)
- [实战工作流](#实战工作流)
- [多数据源降级架构](#多数据源降级架构)
- [技术指标速查](#技术指标速查)
- [形态识别](#形态识别)
- [策略回测详解](#策略回测详解)
- [配置管理](#配置管理)
- [项目结构](#项目结构)
- [数据流](#数据流)
- [最佳实践与常见陷阱](#最佳实践与常见陷阱)
- [FAQ / 疑难排查](#faq--疑难排查)
- [更新日志](#更新日志)
- [参与贡献](#参与贡献)
- [致谢](#致谢)
- [License](#license)

---

## 为什么选择 a-stock-data-quant

| 痛点 | 本项目的解法 |
|------|------------|
| 单一数据源经常抽风，分析到一半报错 | **多数据源自动降级** — akshare 失效时自动切换百度/通达信/东财/同花顺，降级过程对用户透明 |
| 技术指标散落在各个库，用法不统一 | **20+ 指标统一接口** — 基于 MyTT，一套参数风格，`MA(close, 5)` 即可调用 |
| 写策略容易，回测难 | **7 种策略内置回测** — 含止损/手续费/滑点，一行命令出夏普比率和最大回撤 |
| 行情数据有延迟，盘中跟不上 | **三级实时行情降级** — 腾讯 → 东方财富 → 通达信 TCP 直连，秒级更新 |
| AI 分析能力强但门槛高 | **东方财富妙想 AI 免费接入** — 自然语言选股、AI 诊断、AI 问答 |
| 宏观/情绪/资金面数据散落各处 | **一站式命令** — `market` 看情绪、`info` 看个股、`macro` 看宏观、`news` 看快讯 |

---

## 核心特性

### 1. 多数据源自动降级

```
┌─────────────────────────────────────────────────────────┐
│  实时行情:  腾讯 ──失败──▶ 东方财富 ──失败──▶ mootdx    │
│  K 线数据:  新浪 ──失败──▶ 腾讯 ──失败──▶ mootdx ──▶ 百度│
│  资金流向:  akshare ──失败──▶ 百度分钟级资金流           │
│  龙虎榜:   akshare ──失败──▶ 东财数据中心               │
│  融资融券:  akshare ──失败──▶ 东财数据中心               │
│  北向资金:  akshare ──失败──▶ 同花顺                     │
│  概念板块:  akshare ──失败──▶ 百度财经                   │
│  新闻资讯:  东财 7x24 + 财联社 (聚合)                   │
└─────────────────────────────────────────────────────────┘
```

- 降级过程 `stderr` 输出 `[降级]` 提示，不污染 stdout JSON
- 所有备用源经过生产验证，单次请求超时 3-5 秒自动跳过
- 支持自定义 `@_with_fallback` 装饰器扩展新数据源

### 2. 东方财富妙想 AI（免费）

| 能力 | 命令 | 说明 |
|------|------|------|
| AI 诊断 | `em-diagnose` | 基本面 + 技术面 + 资金面 + 估值四维分析 |
| AI 选股 | `em-pick` | 自然语言条件选股，如 "白酒板块龙头" |
| AI 问答 | `em-ask` | 任意金融问题 |
| AI 资讯 | `em-news` | 实时财经新闻搜索 |
| AI 基金 | `em-fund` | 基金诊断 + 持仓分析 |

基于东方财富专业数据库，无需额外付费，注册即可使用。

### 3. 完整的量化分析链路

```
数据获取 → 技术指标 → 形态识别 → 策略信号 → 回测验证 → 综合判断 → HTML 图表
```

一条命令 `analyze` 即可跑通全链路，也可拆开使用每个环节。

---

## 安装

### 方式一：SkillHub（推荐）

支持 9+ AI Agent 平台自动集成：

```bash
# 安装 SkillHub CLI
curl -fsSL https://skillhub.cn/install/install.sh | bash

# 安装本技能
skillhub install astockdataquant
```

在线浏览: [skillhub.cn/skills/astockdataquant](https://skillhub.cn/skills/astockdataquant)

### 方式二：ClawHub / OpenClaw

```bash
clawhub package install a-stock-data-quant
```

在线浏览: [clawhub.ai](https://clawhub.ai) 搜索 `a-stock-data-quant`

### 方式三：Claude Code 插件

```bash
# 在 Claude Code CLI 中
/install-plugin a-stock-data-quant

# 或手动安装到 skills 目录
cd ~/.claude/skills
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式四：CherryStudio 技能

1. CherryStudio → Skills → 搜索 `a-stock-data-quant` → 安装

或手动克隆：

```bash
cd "C:\Users\<用户名>\AppData\Roaming\CherryStudio\Data\Skills"
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式五：直接克隆

```bash
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
cd a-stock-data-quant
pip install -r requirements.txt

# 验证安装
python bin/quant.py list
```

**依赖**: `akshare`, `numpy`, `pandas`, `requests`, `mootdx`

> **注意**: Windows 环境用 `python` 代替 `python3`，建议设置 `PYTHONIOENCODING=utf-8`。

---

## 快速开始

```bash
# 1. 安装依赖
pip install akshare numpy pandas requests mootdx

# 2. 综合分析一只股票（最常用）
python bin/quant.py analyze sh600519

# 3. 多股对比
python bin/quant.py compare sh600519,sz000858,sh601212

# 4. 策略回测
python bin/quant.py backtest sh510500 --strategy ensemble

# 5. 实时行情
python bin/quant.py realtime sh600519,sz000858

# 6. AI 诊断
python bin/quant.py em-diagnose sh600519

# 7. 查看所有命令
python bin/quant.py list
```

### 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6 位 | `sh600519`（贵州茅台）、`sh000001`（上证指数）、`sh510500`（中证 500ETF） |
| 深市 | `sz` + 6 位 | `sz000858`（五粮液）、`sz399006`（创业板指） |

> 不知道代码？用 `python bin/quant.py search 茅台` 搜索。

---

## 命令详解

### 核心分析

#### `analyze` — 一站式综合分析

**这是最常用的命令**，一次出完整报告：行情概览 + 技术指标 + 形态识别 + 策略信号 + 回测结果 + 综合判断。

```bash
python bin/quant.py analyze sh600519                            # 默认日线，120 根 K 线
python bin/quant.py analyze sh600519 --period 1w --count 500    # 周线，500 根
python bin/quant.py analyze sh510500 --capital 200000 --stop-loss 0.05  # 自定义资金+止损
python bin/quant.py analyze sh600519 --html                     # 生成交互式 HTML 图表
python bin/quant.py analyze sh600519 --json                     # JSON 格式输出（适合程序调用）
```

**输出包含 6 大模块**：

| 模块 | 内容 |
|------|------|
| 行情概览 | 最新价、涨跌幅、区间高低点、均价、成交量 |
| 技术指标 | MA5/10/20/60、MACD、RSI、KDJ、BOLL、ATR |
| 形态识别 | W 底、V 型反转、杯柄、三重底、回踩买入、Zigzag 转折点 |
| 策略信号 | 7 种策略最新买卖信号 + 共振情况 |
| 策略回测 | 各策略收益率、年化、最大回撤、夏普比率、胜率 |
| 综合判断 | 多空评分和操作建议 |

**解读速查表**：

| 看到 | 含义 | 建议 |
|------|------|------|
| MA5 偏离 > 2% | 短期涨太快 | 注意回调 |
| MACD 金叉 | 中期动能向上 | 偏多看待 |
| RSI > 70 | 超买区间 | 不宜追高 |
| RSI < 30 | 超卖区间 | 可能有反弹 |
| BOLL 收口 | 即将变盘 | 关注突破方向 |
| ensemble 跑赢 buy_hold | 策略有超额收益 | 可参考信号操作 |
| 最大回撤 > 15% | 波动较大 | 需设止损 |

---

#### `compare` — 多股对比

并排对比多只股票的技术面指标 + 综合评分排名 + 实时价格。

```bash
python bin/quant.py compare sh600519,sz000858,sh601212            # 对比三只白酒股
python bin/quant.py compare sh000001,sz399001,sz399006 --period 1w # 三大指数周线对比
```

评分最高 = 当前技术面最强。适合在同板块多只候选股中快速筛选。

---

#### `backtest` — 策略回测

对指定策略进行历史回测，输出收益率、年化、最大回撤、夏普比率、胜率等关键指标。

```bash
python bin/quant.py backtest sh510500 --strategy ensemble     # 多策略共振（推荐）
python bin/quant.py backtest sh600519 --strategy macd --html  # MACD + HTML 图表
python bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
```

**7 种策略详解**：

| 策略 | 逻辑 | 适用场景 | 特点 |
|------|------|---------|------|
| `buy_hold` | 买入持有 | 作为基准对比 | 最简单，无交易信号 |
| `ma_cross` | MA5/MA20 金叉死叉 | 趋势行情 | 跟踪趋势，滞后性明显 |
| `macd` | DIF/DEA 交叉 | 中期趋势 | 兼顾趋势和动能 |
| `rsi` | RSI 超买超卖 | 震荡行情 | 均值回归思路 |
| `boll` | 布林带轨道反弹 | 区间震荡 | 适合有明确支撑/压力的品种 |
| `kdj` | KDJ 金叉死叉 | 短线交易 | 灵敏但假信号多 |
| `ensemble` | **多策略投票（推荐）** | 通用 | ≥3 个策略同向才出信号，过滤假信号 |

**回测关键指标解读**：

| 指标 | 健康范围 | 说明 |
|------|---------|------|
| 总收益率 | > 基准 (buy_hold) | 策略是否产生超额收益 |
| 最大回撤 | < 15% | 超过 20% 心理压力大 |
| 夏普比率 | > 1 (好) / > 2 (优秀) | 风险调整后收益 |
| 胜率 | > 50% | 盈利交易占比 |
| 年化收益 | > 无风险利率 | 是否值得做 |

---

#### `scan` — 市场扫描

全市场或指定板块扫描，按策略信号排序。

```bash
python bin/quant.py scan                    # 默认扫描
python bin/quant.py scan --strategy macd    # 按 MACD 信号扫描
```

---

#### `indicators` — 技术指标

查看指定股票的全部或指定技术指标原始值。

```bash
python bin/quant.py indicators sh600519              # 全部指标
python bin/quant.py indicators sh600519 --ind MA,MACD,RSI  # 指定指标
```

---

#### `pattern` — 形态识别

自动识别 K 线形态，给出买卖点和确认状态。

```bash
python bin/quant.py pattern sh600519             # 全部形态扫描
python bin/quant.py pattern sh600519 --type w-bottom  # 只看 W 底
```

> "已确认"的形态比"形成中"更可靠。形态深度越大，后续反弹空间通常越大。

---

#### `fund` — 资金面

主力资金流向、融资融券、大中小单分析。

```bash
python bin/quant.py fund sh600519
```

---

#### `diagnose` — 综合诊断

技术面 + 资金面 + 形态多维度评分。

```bash
python bin/quant.py diagnose sh600519
```

---

### 数据查询

#### `realtime` — 实时行情

```bash
python bin/quant.py realtime sh600519,sz000858,sh601212      # 多股行情
python bin/quant.py realtime sh600519 --source tencent        # 指定数据源
```

三级降级: **腾讯 → 东方财富 → mootdx (通达信 TCP 直连)**

涨 🟢 跌 🔴 标识，支持沪深 A 股、ETF、指数。

---

#### `market` — 市场情绪面

一站式查看市场全景：涨停池 / 跌停池 / 情绪判断 / 龙虎榜 / 板块资金流 / 北向资金 / 融资融券。

```bash
python bin/quant.py market                      # 默认参数
python bin/quant.py market --limit 10 --days 5  # 显示 10 条，龙虎榜近 5 日
```

**情绪周期操作指南**：

| 市场状态 | 涨停数 | 跌停数 | 特征 | 操作建议 |
|---------|--------|--------|------|---------|
| 冰点期 | < 30 | > 50 | 市场恐慌，成交量萎缩 | **最好的埋伏时机**，分批建仓 |
| 修复期 | 逐步增多 | 逐步减少 | 亏钱效应减弱，试探性反弹 | 小仓位试探，快进快出 |
| 高潮期 | > 100 | < 10 | 涨停遍地，情绪亢奋 | **最危险的阶段**，准备撤退 |
| 退潮期 | 逐步减少 | 逐步增加 | 高位股开始补跌 | **绝不追高**，持有者考虑减仓 |

---

#### `info` — 个股深度

```bash
python bin/quant.py info 600519     # 贵州茅台深度信息
python bin/quant.py info 000858     # 五粮液深度信息
```

**输出 5 大维度**：限售解禁 / 股东人数变化 / 十大流通股东 / 行业 PE 估值 / 大宗交易。

**解读要点**：

| 信号 | 偏多 | 偏空 |
|------|------|------|
| 股东人数 | 减少（筹码集中，主力吸筹） | 增加（散户化趋势） |
| 十大股东 | 机构/港资加仓 | 机构/港资减持 |
| 行业 PE | 个股 PE 低于行业中位 | 个股 PE 显著高于行业中位 |
| 限售解禁 | 无近期大额解禁 | 3 个月内大额解禁（抛压） |
| 大宗交易 | 溢价成交 | 折价成交 |

---

#### `news` — 新闻资讯

聚合 **东财 7x24 快讯 + 财联社电报 + 东财搜索**，按时间排序。

```bash
python bin/quant.py news                    # 最新快讯列表
python bin/quant.py news 茅台                # 关键词搜索
python bin/quant.py news --top 10           # 只显示 10 条
```

---

#### `search` — 股票搜索

```bash
python bin/quant.py search 茅台
python bin/quant.py search 510500
```

---

#### `data` — 原始行情数据

```bash
python bin/quant.py data sh600519                    # 默认日线
python bin/quant.py data sh600519 --period 15m       # 15 分钟线
python bin/quant.py data sh600519 --period 1w --count 200  # 周线 200 根
```

---

#### `macro` — 宏观经济数据

```bash
python bin/quant.py macro      # CPI/PPI/GDP/PMI/M2/LPR/进出口
```

---

#### `hotspot` — 市场热点

```bash
python bin/quant.py hotspot    # 人气榜 + 概念板块 + 行业板块涨跌
```

---

### AI 能力 (东方财富妙想)

需要先在 `config.yaml` 中配置 `em_api_key`。

**注册地址**: <https://ai.eastmoney.com/mxClaw> (免费)

```bash
python bin/quant.py em-diagnose sh600519           # AI 综合诊断
python bin/quant.py em-pick "白酒板块龙头"          # AI 自然语言选股
python bin/quant.py em-ask "茅台Q1业绩怎么样"       # AI 问答
python bin/quant.py em-news 白酒                    # AI 资讯搜索
python bin/quant.py em-fund sh600519               # AI 基金分析
```

---

### 辅助工具

| 命令 | 功能 | 示例 |
|------|------|------|
| `cache stats` | 查看缓存统计 | `python bin/quant.py cache stats` |
| `cache clear` | 清理过期缓存 | `python bin/quant.py cache clear --older-than 7` |
| `list` | 查看所有可用指标/策略/形态 | `python bin/quant.py list` |

---

## 实战工作流

### 场景一：早盘快速决策（3 分钟）

```bash
# 1. 看市场整体情绪
python bin/quant.py market

# 2. 看持仓股实时行情
python bin/quant.py realtime sh600519,sz000858

# 3. 看最新快讯，有没有影响持仓的消息
python bin/quant.py news --top 5
```

### 场景二：深度研究一只股票（10 分钟）

```bash
# 1. 综合技术分析
python bin/quant.py analyze sh600519 --html

# 2. 个股深度信息（解禁/股东/估值）
python bin/quant.py info 600519

# 3. 资金面
python bin/quant.py fund sh600519

# 4. AI 辅助诊断
python bin/quant.py em-diagnose sh600519
```

### 场景三：在几只候选股中做选择

```bash
# 1. 并排对比技术面
python bin/quant.py compare sh600519,sz000858,sh601212

# 2. 回测看哪只更适合当前策略
python bin/quant.py backtest sh600519 --strategy ensemble
python bin/quant.py backtest sz000858 --strategy ensemble
```

### 场景四：验证策略有效性

```bash
# 1. 先用 buy_hold 看基准表现
python bin/quant.py backtest sh510500 --strategy buy_hold

# 2. 用 ensemble 看是否有超额收益
python bin/quant.py backtest sh510500 --strategy ensemble --html

# 3. 与 MACD 单策略对比
python bin/quant.py backtest sh510500 --strategy macd --html
```

---

## 多数据源降级架构

### 设计原则

1. **主备分离**: akshare 作为主数据源（覆盖最广），其他作为备用
2. **透明降级**: 失败时 stderr 提示，stdout 始终输出有效 JSON
3. **超时控制**: 单源超时 3-5 秒自动跳过，不阻塞用户
4. **零配置**: 开箱即用，无需手动切换数据源

### 降级链详情

| 数据类型 | L1 (主) | L2 (备) | L3 (备) | L4 (备) |
|----------|---------|---------|---------|---------|
| 实时行情 | 腾讯 | 东方财富 | mootdx (TCP 7709) | — |
| 历史 K 线 | 新浪 | 腾讯 | mootdx | 百度财经 |
| 资金流向 | akshare | 百度分钟级 | — | — |
| 龙虎榜 | akshare | 东财数据中心 | — | — |
| 融资融券 | akshare | 东财数据中心 | — | — |
| 限售解禁 | akshare | 东财数据中心 | — | — |
| 股东人数 | akshare | 东财数据中心 | — | — |
| 大宗交易 | akshare | 东财数据中心 | — | — |
| 北向资金 | akshare | 同花顺 (hexin.cn) | — | — |
| 概念板块 | akshare | 百度财经 | — | — |
| 新闻资讯 | 东财 7x24 + 财联社 | — | — | — |

### 备用数据源技术说明

| 数据源 | 协议 | 说明 |
|--------|------|------|
| **mootdx** | TCP 7709 | 通达信协议，无认证无 IP 限制，延迟低 |
| **百度财经** | HTTP | `finance.pae.baidu.com`，纯 HTTP，支持 K 线/资金流/概念 |
| **东财数据中心** | HTTP | `datacenter-web.eastmoney.com`，6 种报告类型 |
| **同花顺** | HTTP | `data.hexin.cn`，北向资金专用 |

### 降级实现

使用 `@_with_fallback` 装饰器：

```python
# lib/fallback.py 核心逻辑
@_with_fallback(_ak_fund_flow, ('百度', _baidu_fund_flow))
def get_fund_flow(code, market=None):
    """资金流向 — akshare 为主，百度为备"""
    ...
```

- 主源成功 → 直接返回
- 主源失败 → 自动尝试备用源
- 全部失败 → 返回空结果，stderr 输出错误

---

## 技术指标速查

| 指标 | 全称 | 类别 | 用途 |
|------|------|------|------|
| **MA** | Simple Moving Average | 趋势 | 判断方向和支撑/压力 |
| **EMA** | Exponential Moving Average | 趋势 | 更灵敏的趋势跟踪 |
| **MACD** | Moving Average Convergence Divergence | 趋势+动能 | 金叉/死叉，顶/底背离 |
| **RSI** | Relative Strength Index | 震荡 | 超买(>70)/超卖(<30) |
| **BOLL** | Bollinger Bands | 波动 | 轨道突破/回归 |
| **KDJ** | Stochastic Oscillator | 震荡 | 短线买卖点 |
| **CCI** | Commodity Channel Index | 震荡 | 异常偏离检测 |
| **WR** | Williams %R | 震荡 | 超买超卖 |
| **ATR** | Average True Range | 波动 | 止损设置参考 |
| **BIAS** | Bias Ratio | 震荡 | 乖离程度 |
| **OBV** | On Balance Volume | 量价 | 量价配合验证 |
| **DMI** | Directional Movement Index | 趋势 | 多空力量对比 |
| **TRIX** | Triple Exponential Average | 趋势 | 长期趋势 |
| **VR** | Volume Ratio | 量价 | 成交量异动 |
| **EMV** | Ease of Movement | 量价 | 价格变动的难易度 |
| **BBI** | Bull and Bear Index | 趋势 | 多空分界 |
| **MFI** | Money Flow Index | 量价+震荡 | 资金流向的 RSI |
| **ASI** | Accumulative Swing Index | 趋势 | 累积摆动 |
| **PSY** | Psychological Line | 情绪 | 市场心理 |
| **SAR** | Parabolic SAR | 趋势 | 止损转向点 |

---

## 形态识别

| 形态 | 参数 | 类型 | 信号 | 说明 |
|------|------|------|------|------|
| W 底 | `w-bottom` | 底部反转 | 看多 | 经典双底，突破颈线确认 |
| V 型反转 | `v-reversal` | 底部反转 | 看多 | 急跌后快速反弹 |
| 杯柄形态 | `cup-handle` | 突破买入 | 看多 | 长期整理后突破 |
| 三重底 | `triple-bottom` | 底部确认 | 看多 | 三次探底不破，支撑强 |
| 回踩买入 | `dip-buy` | 顺势买入 | 看多 | 上升趋势中的回调买入 |
| Zigzag | `zigzag` | 趋势转折 | 参考 | 过滤噪音，标记转折点 |

**使用建议**：
- "已确认"的信号比"形成中"更可靠，不要过早入场
- 形态深度越大，后续空间通常越大
- 多个形态同时出现时信号更可靠
- 结合成交量确认：突破时放量更可信

---

## 策略回测详解

### 关键指标说明

| 指标 | 计算方式 | 解读 |
|------|---------|------|
| **总收益率** | (期末资金 - 期初资金) / 期初资金 | 必须与 buy_hold 对比 |
| **年化收益** | 总收益率折算为年 | 消除持仓时间差异 |
| **最大回撤** | 峰值到谷底的最大跌幅 | 最坏情况的亏损幅度 |
| **夏普比率** | (策略收益 - 无风险收益) / 波动率 | > 1 好，> 2 优秀 |
| **胜率** | 盈利次数 / 总交易次数 | > 50% 为正期望 |
| **交易次数** | 开仓次数 | 过少可能过拟合 |

### 参数调优

| 参数 | 说明 | 建议 |
|------|------|------|
| `--capital 100000` | 初始资金 | 与实际资金一致更有参考价值 |
| `--stop-loss 0.05` | 止损比例 | 5%-8% 较常用，太小容易被洗出 |
| `--ensemble 3` | 共振阈值 | 3 = 保守，2 = 激进 |

### 注意事项

- 回测不等于未来收益，仅作为策略验证参考
- 关注回测期间是否覆盖牛熊周期
- 手续费和滑点会影响高频策略表现
- 过度优化参数容易过拟合

---

## 配置管理

### config.yaml

```yaml
# ============================================
# a-stock-data-quant 配置文件
# ============================================

# 东方财富妙想 AI（免费）
# 注册: https://ai.eastmoney.com/mxClaw
em_api_key: "em_xxxxxxxxxxxxxxxx"

# 回测参数
capital: 100000        # 初始资金（元）
commission: 0.001      # 手续费率（万分之十）
slippage: 0.001        # 滑点（千分之一）

# 数据缓存
cache:
  enabled: true        # 是否启用缓存
  ttl_hours: 4         # 缓存有效期（小时）
  directory: cache     # 缓存目录

# HTML 图表输出
html:
  directory: html      # 输出目录
```

### K 线周期

| 周期 | 代码 | 适用场景 |
|------|------|---------|
| 日线 | `1d` | 中长线分析（默认） |
| 周线 | `1w` | 中期趋势 |
| 月线 | `1M` | 长期趋势 |
| 1 分钟 | `1m` | 超短线 / 高频 |
| 5 分钟 | `5m` | 短线 |
| 15 分钟 | `15m` | 日内波段 |
| 30 分钟 | `30m` | 日内波段 |
| 60 分钟 | `60m` | 日内波段 |

---

## 项目结构

```
a-stock-data-quant/
│
├── bin/                          # 入口
│   ├── quant.py                  #   CLI 主入口 (2000+ 行)
│   └── stock_full.py             #   综合分析脚本
│
├── lib/                          # 核心库
│   ├── akshare_data.py           #   akshare 数据层 + 降级链
│   ├── ashare.py                 #   行情数据获取 (含 mootdx/百度降级)
│   ├── backtest.py               #   回测引擎
│   ├── chart.py                  #   ECharts HTML 图表生成
│   ├── data_cache.py             #   CSV 数据缓存
│   ├── em_api.py                 #   东方财富妙想 AI 接口
│   ├── fallback.py               #   多数据源降级引擎
│   ├── mytt.py                   #   技术指标库 (MyTT)
│   ├── patterns.py               #   形态识别
│   ├── realtime_data.py          #   实时行情 (腾讯/东方财富/mootdx)
│   ├── settings.py               #   配置管理
│   ├── strategies.py             #   策略模块
│   │
│   ├── sources_baidu.py          #   [备用] 百度财经 API
│   ├── sources_datacenter.py     #   [备用] 东财数据中心
│   ├── sources_hexin.py          #   [备用] 同花顺北向资金
│   ├── sources_mootdx.py         #   [备用] 通达信 TCP 7709
│   └── sources_news.py           #   [聚合] 东财 7x24 + 财联社 + 东财搜索
│
├── config.yaml                   # 配置文件
├── SKILL.md                      # Claude Code skill 文档
├── requirements.txt              # Python 依赖
└── LICENSE                       # MIT
```

---

## 数据流

```
用户输入
  │
  ▼
quant.py CLI (意图路由)
  │
  ├─ analyze / compare / backtest / scan / indicators / pattern / fund / diagnose
  │     │
  │     ▼
  │   akshare_data.py  ──失败──▶  sources_baidu.py
  │     │                        sources_datacenter.py
  │     │                        sources_hexin.py
  │     ▼
  │   mytt.py (计算技术指标)
  │     │
  │     ├──▶ strategies.py (策略信号)
  │     │       │
  │     │       ▼
  │     │     backtest.py (回测)
  │     │
  │     ├──▶ patterns.py (形态识别)
  │     │
  │     └──▶ chart.py (HTML 图表)
  │             │
  │             ▼
  │          output (stdout / HTML file)
  │
  ├─ realtime / search
  │     │
  │     ▼
  │   realtime_data.py: 腾讯 → 东方财富 → mootdx
  │
  ├─ news
  │     │
  │     ▼
  │   sources_news.py (东财 7x24 + 财联社 + 东财搜索)
  │
  ├─ market / info / macro / hotspot
  │     │
  │     ▼
  │   akshare_data.py (+ 备用源降级)
  │
  └─ em-diagnose / em-pick / em-ask / em-news / em-fund
        │
        ▼
      em_api.py (东方财富妙想 AI)
```

---

## 最佳实践与常见陷阱

### 最佳实践

1. **先看大盘再看个股**: 用 `market` 判断整体情绪，系统性风险比个股技术面更重要
2. **多指标交叉验证**: 单一指标容易误判，至少 3 个指标方向一致再做决策
3. **回测要做样本外验证**: 不要只看近期表现，至少覆盖一轮牛熊
4. **止损纪律**: `--stop-loss` 一定要设，5%-8% 是常见区间
5. **关注最大回撤**: 比收益率更重要，超过 20% 的策略要谨慎
6. **日线为主**: 短周期 (1m/5m/15m) 噪音大，初学者建议从日线开始
7. **定期清理缓存**: `cache clear --older-than 3`，避免使用过期数据

### 常见陷阱

| 陷阱 | 说明 | 避免方法 |
|------|------|---------|
| 过度拟合 | 参数调得过于精准，在历史数据上表现完美但未来失效 | 用 ensemble 多策略投票降低单一策略风险 |
| 只看收益不看回撤 | 收益 50% 但回撤 40%，心理上难以坚持 | 重点关注夏普比率和最大回撤 |
| 忽视交易成本 | 频繁交易的手续费和滑点侵蚀利润 | 用 `--commission` 和 `--slippage` 设置真实值 |
| 追涨杀跌 | RSI > 70 还在追，RSI < 30 恐慌卖 | 参考情绪周期表操作 |
| 在高潮期满仓 | 涨停 > 100 时最危险 | 参考 `market` 命令的情绪判断 |

---

## FAQ / 疑难排查

<details>
<summary><b>Q: 安装后运行报错 ModuleNotFoundError</b></summary>

```bash
pip install -r requirements.txt
```

如果仍有问题，尝试：

```bash
pip install --upgrade akshare numpy pandas requests mootdx
```

</details>

<details>
<summary><b>Q: 数据获取失败 / 返回空数据</b></summary>

1. 确认股票代码格式正确（`sh600519`，不是 `600519`）
2. 非交易时间部分数据可能为空
3. 网络问题会触发自动降级，查看 stderr 是否有 `[降级]` 提示
4. 尝试指定数据源: `--source tencent`

</details>

<details>
<summary><b>Q: Windows 下中文输出乱码</b></summary>

设置环境变量：

```cmd
set PYTHONIOENCODING=utf-8
python bin/quant.py analyze sh600519
```

</details>

<details>
<summary><b>Q: akshare 版本不兼容</b></summary>

akshare API 签名经常变更。如果某个命令报错，先升级：

```bash
pip install --upgrade akshare
```

本项目已内置多数据源降级，即使 akshare 某个接口失效也会自动切换。

</details>

<details>
<summary><b>Q: 东方财富妙想 AI 命令报错</b></summary>

1. 确认已在 `config.yaml` 中配置 `em_api_key`
2. 注册地址: <https://ai.eastmoney.com/mxClaw>
3. 检查 API Key 格式: `em_xxxxxxxxxxxxxxxx`

</details>

<details>
<summary><b>Q: 回测结果和实盘差距大</b></summary>

回测是历史回放，存在以下偏差：

- **滑点**: 回测按收盘价成交，实盘可能买高卖低
- **流动性**: 小盘股实盘可能无法以目标价成交
- **心理因素**: 回测无情绪，实盘受恐惧/贪婪影响
- **未来函数**: 确保策略没有用到当时未知的数据

建议：将回测结果视为 "策略上限"，实盘预期打 6-7 折。

</details>

---

## 参数速查

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--period` | K 线周期 | `1d` | `1d` `1w` `1M` `1m` `5m` `15m` `30m` `60m` |
| `--count` | 数据条数 | `120` | `--count 500` |
| `--strategy` | 策略名 | `buy_hold` | `ma_cross` `macd` `rsi` `boll` `kdj` `ensemble` |
| `--capital` | 初始资金 | `100000` | `--capital 200000` |
| `--stop-loss` | 止损比例 | 无 | `--stop-loss 0.05` (5%) |
| `--ensemble N` | 共振阈值 | `3` | `--ensemble 2` |
| `--html` | 生成 HTML 图表 | — | `--html` |
| `--json` | JSON 格式输出 | — | `--json` |
| `--source` | 指定数据源 | auto | `tencent` `eastmoney` `mootdx` |
| `--ind` | 指定指标 | 全部 | `--ind MA,MACD,RSI` |
| `--type` | 指定形态 | 全部 | `--type w-bottom` |
| `--top` | 显示条数 | 默认 | `--top 10` |
| `--limit` | 限制条数 | 默认 | `--limit 10` |
| `--days` | 天数 | 默认 | `--days 5` |

---

## 更新日志

<details>
<summary><b>v3.2.0</b> — 2026-05-19 — 多数据源备份系统 + 新闻资讯</summary>

**新功能**
- 多数据源自动降级: 实时行情三级降级、K 线四级降级、资金面/龙虎榜/融资融券/北向等二级降级
- `news` 命令: 东财 7x24 快讯 + 财联社电报 + 东财搜索
- `market` 命令: 涨停池/跌停池/龙虎榜/北向资金/融资融券一站式
- `info` 命令: 限售解禁/股东人数/十大股东/行业 PE/大宗交易

**新增模块**
- `lib/fallback.py` — 降级引擎
- `lib/sources_baidu.py` — 百度财经
- `lib/sources_mootdx.py` — 通达信 TCP
- `lib/sources_datacenter.py` — 东财数据中心
- `lib/sources_hexin.py` — 同花顺
- `lib/sources_news.py` — 新闻聚合

**修复**
- akshare API 签名变更导致的多个函数失效
- 涨停池/跌停池默认日期错误
- 龙虎榜金额单位显示错误
- 股东人数/限售解禁列名不匹配

</details>

<details>
<summary><b>v3.1.0</b> — 2026-05-15 — 东方财富 AI + 实时行情</summary>

- 东方财富妙想 AI 5 个命令
- 实时行情: 腾讯/东方财富秒级行情
- `search` 股票搜索
- ECharts HTML 交互式图表
- 数据缓存 + config.yaml 配置

</details>

<details>
<summary><b>v3.0.0</b> — 2026-05-15 — 综合诊断 + 宏观数据</summary>

- `diagnose` 综合诊断
- `macro` 宏观经济数据
- `hotspot` 市场热点

</details>

<details>
<summary><b>v2.0.0</b> — 2026-05-13 — 核心分析功能</summary>

- `analyze` / `compare` / `backtest` / `scan` / `pattern` 核心命令
- 7 种回测策略

</details>

<details>
<summary><b>v1.0.0</b> — 2026-05-12 — 初始版本</summary>

- akshare + MyTT + Ashare 构建
- 20+ 技术指标
- 资金流向分析

</details>

---

## 参与贡献

欢迎提交 Issue 和 Pull Request。

### 开发环境

```bash
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
cd a-stock-data-quant
pip install -r requirements.txt
```

### 提交规范

- 新增数据源: 在 `lib/sources_*.py` 中实现，并在 `akshare_data.py` 中添加降级链
- 新增策略: 在 `lib/strategies.py` 中实现，并注册到策略列表
- Bug 修复: 说明复现步骤和修复方案

### 版本策略

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 新增功能，向后兼容
- **PATCH**: Bug 修复

---

## 致谢

| 项目 | 说明 |
|------|------|
| [Ashare](https://github.com/mpquant/Ashare) | 行情数据接口 |
| [akshare](https://github.com/akfamily/akshare) | A 股综合数据 |
| [MyTT](https://github.com/mpquant/MyTT) | 技术指标库 |
| [mootdx](https://github.com/mootdx/mootdx) | 通达信行情接口 |
| [东方财富妙想](https://ai.eastmoney.com/mxClaw) | AI 金融分析 |
| [stock-api](https://github.com/zhangxiangliang/stock-api) | 实时行情协议参考 |
| [a-stock-data](https://github.com/simonlin1212/a-stock-data) | 备用数据源参考 |

---

## License

[MIT](LICENSE)

---

<div align="center">

如果觉得有用，点个 Star 支持一下

[![Star History Chart](https://api.star-history.com/svg?repos=jangviktor-web/a-stock-data-quant&type=Date)](https://star-history.com/#jangviktor-web/a-stock-data-quant&Date)

</div>
