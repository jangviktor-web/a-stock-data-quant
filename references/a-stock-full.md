---
name: a-stock-data-quant
description: 当任务需要实际获取A股数据时使用——行情/K线(腾讯/通达信/百度)、研报(东财+巨潮)、信号(热点/北向/龙虎榜/解禁/行业)、资金面(融资融券/大宗/股东户数/资金流)、新闻(东财7x24/财联社/华尔街见闻)、F10财务三表(东财datacenter)、公告(东财)、互动易(巨潮)、筹码分布、板块资金流、市场温度(5维度)、估值分位(PE/PB/PS)、ETF排行/龙虎榜/指数估值/财务对比(广发MCP)、AI金融分析(东财妙想)等。十二层数据源·40+端点·内嵌全部可运行代码，自包含零依赖外部文件；多源自动降级(主源失效切备用)；东财接口内置限流防封。仅在需要调用数据接口取数时使用。
version: 3.6.0
---

> 项目主页：https://github.com/jangviktor-web/a-stock-data-quant
> 
> 基于 [akshare](https://github.com/akfamily/akshare) + [MyTT](https://github.com/mpquant/MyTT) 构建

# A股量化分析工具箱 V3.6.0

十二层数据架构，40+ 端点，覆盖主板/中小板/科创板/ST。每类数据在路由表中标有独立备胎，主源被封时可降级。

```
行情层（实时，不封IP）
├── 腾讯财经 API   → 实时价/PE/PB/市值/换手率/涨跌停 (HTTP)
├── 东方财富 push2 → 实时行情/热门排行 (HTTP)
├── mootdx         → K线 + 五档盘口 (TCP 7709)
└── 百度股市通     → K线带MA5/10/20 + 资金流 (HTTP)

研报/公告层
├── 东财 reportapi → 个股研报 + PDF下载 + 评级
├── 东财 anotice   → 上市公司公告
└── 巨潮 cninfo    → 互动易投资者问答

信号层
├── 东财 push2     → 个股资金流(分钟级) + 热门股/板块排行
├── 东财 datacenter→ 龙虎榜/融资融券/大宗交易/股东人数/限售解禁
├── 同花顺 hexin   → 北向资金日度流向
└── 东财 dataapi   → 板块资金流(行业/概念/地域)

财务层
├── 东财 datacenter→ F10主要财务指标(营收/净利/ROE/毛利率/EPS)
├── 广发 MCP quant → 市值/PE/PB/行业均值/历史百分位
└── 百度财经       → 概念板块关联

筹码/估值层
├── 纯算法         → 筹码分布(换手率衰减+高斯核，移植自go-stock)
├── 东财 datacenter→ PE/PB/PS历史百分位
└── akshare        → 筹码分布(东财cyq)

新闻层
├── 新浪财经       → 7x24快讯
├── 东财 weblist   → 7x24快讯(备用)
├── 东财 search    → 关键词搜索
└── 华尔街见闻     → 11频道全球快讯 + 财经日历

市场温度层
├── akshare        → 巴菲特指标/股债利差/QVIX/活跃度/新高新低
└── 综合5维度加权   → 0-100温度分数

广发MCP层
├── ETF排行        → 13种榜单(涨幅/跌幅/规模/换手率/资金流等)
├── 龙虎榜深度     → 上榜排行/指定日期/营业部统计/日历
├── 指数估值分位   → PE/PB百分位 + 关联ETF
└── 财务对比       → 市值/估值/行业均值/历史百分位

AI层
└── 东财妙想       → AI诊断/选股/问答/资讯/基金(需API Key)
```

## 端点路由速查（按需定位，不必通读全文）

| § | 函数 | 拿什么 | 源 |
|---|------|--------|----|
| 1.1 | `load_config()` / `get(key)` | 配置读取 | config.yaml |
| 1.2 | `cached_fetch()` / `cached_json_fetch()` | 数据缓存 | 本地CSV/JSON |
| 1.3 | `try_sources()` | 多源降级引擎 | 通用 |
| 2.1 | `fetch_tencent(codes)` | 实时行情(腾讯) | qt.gtimg.cn |
| 2.2 | `fetch_eastmoney(codes)` | 实时行情(东财) | push2.eastmoney.com |
| 2.3 | `get_realtime(codes)` | 统一实时行情(含降级) | 腾讯→东财→mootdx |
| 2.4 | `search_stock(keyword)` | 股票搜索 | 腾讯/东财 |
| 2.5 | `mootdx_realtime(codes)` / `mootdx_kline(code)` | 通达信行情/K线 | TCP 7709 |
| 3.1 | `baidu_kline(code)` | 百度K线 | finance.pae.baidu.com |
| 3.2 | `baidu_fund_flow(code)` | 百度资金流 | finance.pae.baidu.com |
| 3.3 | `get_north_flow(symbol)` | 北向资金 | data.hexin.cn |
| 4.1 | `calculate_chip_distribution(klines)` | 筹码分布(纯算法) | 无网络依赖 |
| 5.1 | `get_board_fund_flow(board_type)` | 板块资金流排名 | data.eastmoney.com |
| 5.2 | `get_stock_fund_flow_history(code)` | 个股资金流历史 | push2his.eastmoney.com |
| 6.1 | `get_main_finance(code)` | F10主要财务指标 | datacenter.eastmoney.com |
| 6.2 | `get_forecast(code)` | 机构盈利预测 | datacenter.eastmoney.com |
| 7.1 | `get_market_temperature()` | 市场温度(0-100) | akshare(5指标) |
| 7.2 | `get_stock_valuation(code)` | 个股估值分位 | datacenter.eastmoney.com |
| 8.1 | `get_sina_finance()` | 新浪7x24 | feed.mix.sina.com.cn |
| 8.2 | `get_eastmoney_7x24()` | 东财7x24 | np-weblist.eastmoney.com |
| 8.3 | `get_eastmoney_search(keyword)` | 东财搜索 | search-api-web.eastmoney.com |
| 8.5 | `get_lives(channel)` | 华尔街见闻快讯 | api-one-wscn.awtmt.com |
| 8.6 | `get_calendar(channel)` | 财经日历 | api-one-wscn.awtmt.com |
| 9.1 | `get_research_reports(code)` | 个股研报 | reportapi.eastmoney.com |
| 9.2 | `get_stock_notices(code)` | 上市公司公告 | np-anotice-stock.eastmoney.com |
| 9.3 | `get_interactive_answers(keyword)` | 互动易问答 | irm.cninfo.com.cn |
| 10.1 | `get_hot_stocks(mode)` | 热门股票排行 | push2.eastmoney.com |
| 10.2 | `get_hot_boards(mode)` | 热门板块排行 | push2.eastmoney.com |
| 10.3 | `get_board_stocks(board_code)` | 板块成分股 | push2.eastmoney.com |
| 10.4 | `get_capital_flow_detail(code)` | 资金流向细分 | push2his.eastmoney.com |
| 10.5 | `get_fundamentals_snapshot(code)` | 基本面快照 | qt.gtimg.cn |
| 10.6 | `get_lhb_data()` / `get_margin_data()` / `get_block_trade()` / `get_holder_num()` / `get_locked_shares()` | 龙虎榜/融资/大宗/股东/解禁 | datacenter-web.eastmoney.com |
| 11.1 | `_mcp_call(server, tool, args)` | 广发MCP通用调用 | mcp-api.gf.com.cn |
| 11.2 | `get_etf_rank(rank_type)` | ETF排行榜(13种) | MCP etf_rank |
| 11.3 | `get_lhb_rank()` / `get_lhb_by_date()` | 龙虎榜排行/日期 | MCP lhb |
| 11.4 | `get_index_valuation()` | 指数估值分位 | MCP windmill |
| 11.5 | `get_gf_basic(codes)` | 广发财务对比 | MCP quant |
| 12.1 | `stock_diagnosis(question)` | AI综合诊断 | ai-saas.eastmoney.com |
| 12.2 | `select_security(query)` / `search_news(query)` / `ask(question)` | AI选股/资讯/问答 | ai-saas.eastmoney.com |

## 数据源优先级 & 防封（重要，先读）

| 优先级 | 数据源 | 协议 | 封IP风险 | 覆盖 |
|--------|--------|------|----------|------|
| **1（首选）** | **腾讯财经** | HTTP GBK | **不封** | 实时价/PE/PB/市值/换手/基本面 |
| **2** | **mootdx（通达信）** | TCP 7709 | **不封** | K线/五档盘口/逐笔成交 |
| **3** | 百度/新浪/巨潮/同花顺 | HTTP | 低 | K线/财报/公告/北向 |
| **4（仅独有数据）** | **东财 eastmoney** | HTTP | **有风控** | 龙虎榜/融资融券/大宗/研报/资金流 |
| **5** | **广发MCP** | HTTPS JSON-RPC | 低(需Bearer) | ETF/龙虎榜/指数估值/财务对比 |

**东财风控阈值**：>5次/秒 或 ≥10并发 或 ≥200次/分钟 可能触发封禁。被封表现：403/429/空数据。临时封禁几分钟到几小时。

**原则**：行情/市值/基本面能从腾讯/通达信拿到的，一律走它们。东财仅用于其独有数据（龙虎榜/融资融券/大宗/研报/资金流等）。

## 依赖安装

```bash
pip install requests pandas akshare
# 可选：通达信行情
pip install mootdx
# 可选：yaml配置
pip install pyyaml
```

## 使用方式

将本文件放入 `~/.claude/skills/a-stock-data-quant/SKILL.md`（Claude Code）或对应 AI Agent 的 skills 目录。AI 会自动识别并在 A 股相关对话中激活，按路由表定位到对应章节，复制代码块直接执行。

---

## §1 公共工具

### §1.1 配置管理

集中化配置管理：加载 `config.yaml`，支持 ENC: 前缀加密值自动解密，环境变量覆盖，全局单例缓存。

```python
import os
import base64
import yaml  # 需要: pip install pyyaml

# ── 密钥混淆 ──────────────────────────────────────────────
_XK = b'aSq7x!2026'

def _decrypt(val: str) -> str:
    """解密 ENC: 前缀的混淆值"""
    raw = base64.b64decode(val[4:])
    return bytes([b ^ _XK[i % len(_XK)] for i, b in enumerate(raw)]).decode()

def encrypt(plain: str) -> str:
    """加密为 ENC: 格式 (用于生成配置)"""
    data = plain.encode()
    xored = bytes([b ^ _XK[i % len(_XK)] for i, b in enumerate(data)])
    return 'ENC:' + base64.b64encode(xored).decode()

def _deobfuscate(config: dict):
    """自动解密配置中所有 ENC: 前缀的值"""
    for k, v in config.items():
        if isinstance(v, str) and v.startswith('ENC:'):
            try:
                config[k] = _decrypt(v)
            except Exception:
                pass

# ── 默认配置 ──────────────────────────────────────────────

DEFAULTS = {
    # 回测参数
    'capital': 100000,
    'commission': 0.001,
    'slippage': 0.001,
    'position_size': 1.0,
    'stop_loss': None,
    'take_profit': None,

    # 数据参数
    'default_count': 120,
    'analyze_count': 500,
    'pattern_count': 250,
    'backtest_count': 500,
    'default_period': '1d',

    # 输出
    'html_output_dir': 'html',
    'log_dir': 'logs',

    # 市场扫描
    'scan_min_volume': None,
    'scan_codes': [
        ('sh000001', '上证指数'),
        ('sz399001', '深证成指'),
        ('sz399006', '创业板指'),
        ('sh000300', '沪深300'),
        ('sh000016', '上证50'),
        ('sz399673', '创业板50'),
    ],

    # 数据缓存
    'cache_enabled': True,
    'cache_dir': 'cache',
    'cache_ttl_hours': 4,
}

# ── 配置加载 ──────────────────────────────────────────────

_config = None

def _get_project_root():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_config():
    """加载配置，config.yaml 优先，缺省用 DEFAULTS"""
    global _config
    if _config is not None:
        return _config

    config = dict(DEFAULTS)
    config_path = os.path.join(_get_project_root(), 'config.yaml')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f) or {}
            config.update(yaml_config)
            _deobfuscate(config)
        except Exception as e:
            print(f"[警告] 读取 config.yaml 失败: {e}，使用默认配置")

    # 环境变量覆盖
    if os.environ.get('QUANT_CAPITAL'):
        config['capital'] = float(os.environ['QUANT_CAPITAL'])
    if os.environ.get('QUANT_HTML_DIR'):
        config['html_output_dir'] = os.environ['QUANT_HTML_DIR']
    if os.environ.get('WECHAT_WEBHOOK_QUANT'):
        config['wechat_webhook'] = os.environ['WECHAT_WEBHOOK_QUANT']

    _config = config
    return config

def get(key, default=None):
    """获取配置项"""
    cfg = load_config()
    return cfg.get(key, default if default is not None else DEFAULTS.get(key))

def reload():
    """重新加载配置（修改 config.yaml 后调用）"""
    global _config
    _config = None
    return load_config()
```

### §1.2 数据缓存

双层缓存：CSV 缓存用于 DataFrame 行情数据，JSON 缓存用于资金流/涨停池等非结构化数据。支持 TTL 过期检查和批量清理。

```python
import os
import time
import hashlib
import json
import pandas as pd  # 需要: pip install pandas

# TTL 常量 (单位: 分钟)
TTL_REALTIME = 5      # 实时行情 5分钟
TTL_INTRADAY = 30     # 盘中数据(涨停池/资金流) 30分钟
TTL_DAILY = 240       # 日级数据(宏观/估值) 4小时
TTL_WEEKLY = 1440     # 周级数据 24小时

# 依赖: settings.get('cache_dir', 'cache') 和 settings.get('cache_enabled', True)
# 以下为独立运行版本，使用默认值

_CACHE_DIR = 'cache'
_CACHE_ENABLED = True
_CACHE_TTL_HOURS = 4

def _get_cache_dir():
    """获取缓存目录"""
    cache_dir = _CACHE_DIR
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def _cache_key(code, count, period, end=''):
    """生成缓存文件名"""
    raw = f"{code}_{count}_{period}_{end}"
    h = hashlib.md5(raw.encode()).hexdigest()[:12]
    safe_code = code.replace('.', '_').replace('/', '_')
    return f"{safe_code}_{period}_{h}.csv"

def get_cached(code, count, period, end=''):
    """尝试从缓存获取 DataFrame，过期或不存在返回 None"""
    if not _CACHE_ENABLED:
        return None
    cache_dir = _get_cache_dir()
    filename = _cache_key(code, count, period, end)
    filepath = os.path.join(cache_dir, filename)
    if not os.path.exists(filepath):
        return None
    ttl_hours = _CACHE_TTL_HOURS
    file_age = time.time() - os.path.getmtime(filepath)
    if file_age > ttl_hours * 3600:
        return None
    try:
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        if df.empty:
            return None
        return df
    except Exception:
        return None

def save_cache(code, count, period, end, df):
    """保存 DataFrame 到 CSV 缓存"""
    if df is None or df.empty:
        return
    cache_dir = _get_cache_dir()
    filename = _cache_key(code, count, period, end)
    filepath = os.path.join(cache_dir, filename)
    try:
        df.to_csv(filepath)
    except Exception:
        pass

def cached_fetch(code, count, period, end='', fetch_func=None):
    """
    带缓存的 DataFrame 数据获取

    Parameters
    ----------
    code : str - 股票代码
    count : int - 数据条数
    period : str - 周期
    end : str - 结束日期
    fetch_func : callable - 实际获取数据的函数 (code, count, period, end) -> DataFrame

    Returns
    -------
    DataFrame
    """
    df = get_cached(code, count, period, end)
    if df is not None:
        return df
    if fetch_func is None:
        raise ValueError("fetch_func is required when cache miss")
    df = fetch_func(code, count, period, end)
    if df is not None and not df.empty:
        save_cache(code, count, period, end, df)
    return df

# ── JSON 通用缓存层 ──────────────────────────────────────

def _json_cache_key(category: str, key: str) -> str:
    """生成 JSON 缓存文件名"""
    h = hashlib.md5(key.encode()).hexdigest()[:10]
    return f"{category}_{h}.json"

def get_json_cached(category: str, key: str, ttl_minutes: int = 60):
    """尝试从 JSON 缓存获取数据，过期或不存在返回 None"""
    if not _CACHE_ENABLED:
        return None
    cache_dir = _get_cache_dir()
    filename = _json_cache_key(category, key)
    filepath = os.path.join(cache_dir, filename)
    if not os.path.exists(filepath):
        return None
    file_age = time.time() - os.path.getmtime(filepath)
    if file_age > ttl_minutes * 60:
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception:
        return None

def save_json_cache(category: str, key: str, data):
    """保存数据到 JSON 缓存"""
    if data is None:
        return
    cache_dir = _get_cache_dir()
    filename = _json_cache_key(category, key)
    filepath = os.path.join(cache_dir, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

def cached_json_fetch(category: str, key: str, fetch_func, ttl_minutes: int = 60):
    """
    带 JSON 缓存的数据获取 (主入口)

    Parameters
    ----------
    category : str - 数据类别 (如 'fund_flow', 'zt_pool', 'macro', 'north_flow')
    key : str - 缓存键
    fetch_func : callable - 实际获取数据的函数 () -> dict/list
    ttl_minutes : int - 缓存有效期(分钟)

    Returns
    -------
    dict/list or None
    """
    data = get_json_cached(category, key, ttl_minutes)
    if data is not None:
        return data
    data = fetch_func()
    if data is not None:
        save_json_cache(category, key, data)
    return data

def clear_cache(older_than_hours=None):
    """
    清理缓存文件

    Parameters
    ----------
    older_than_hours : int or None - 只清理超过指定小时的文件，None 则清全部
    """
    cache_dir = _get_cache_dir()
    if not os.path.exists(cache_dir):
        return 0
    count = 0
    now = time.time()
    for f in os.listdir(cache_dir):
        if not (f.endswith('.csv') or f.endswith('.json')):
            continue
        fp = os.path.join(cache_dir, f)
        if older_than_hours is not None:
            age = now - os.path.getmtime(fp)
            if age < older_than_hours * 3600:
                continue
        os.remove(fp)
        count += 1
    return count
```

### §1.3 降级引擎

多数据源降级调度器：按优先级依次尝试数据源，失败时自动降级到下一个源并打印提示。

```python
import sys

def try_sources(sources, is_valid=None):
    """
    按顺序尝试数据源，返回第一个有效结果。

    Parameters
    ----------
    sources : list of (name: str, callable)
        数据源列表，按优先级排列。例如:
        [('百度', lambda: fetch_baidu()), ('通达信', lambda: fetch_mootdx())]
    is_valid : callable(result) -> bool
        自定义有效性检查，默认检查非空

    Returns
    -------
    result from first valid source, or None if all fail
    """
    if is_valid is None:
        is_valid = _default_is_valid

    errors = []
    for i, (name, fn) in enumerate(sources):
        try:
            result = fn()
            if is_valid(result):
                if i > 0:
                    prev_name = sources[i - 1][0]
                    _log_fallback(prev_name, name, errors[-1] if errors else "")
                return result
            errors.append(f"{name}: 返回空结果")
        except Exception as e:
            errors.append(f"{name}: {e}")

    if errors:
        print(f"  [降级] 所有数据源均失败: {'; '.join(errors)}", file=sys.stderr)
    return None

def _default_is_valid(result):
    """默认有效性检查：非 None、非空列表、无 error 键"""
    if result is None:
        return False
    if isinstance(result, list):
        if len(result) == 0:
            return False
        if len(result) > 0 and isinstance(result[0], dict) and 'error' in result[0]:
            return False
        return True
    if isinstance(result, dict):
        if 'error' in result:
            return False
        if 'rows' in result:
            return len(result.get('rows', [])) > 0
        if 'data' in result:
            return len(result.get('data', [])) > 0
        return True
    return True

def _log_fallback(from_source, to_source, error_msg):
    """打印降级日志"""
    short_err = error_msg.split(': ', 1)[-1] if ': ' in error_msg else error_msg
    print(f"  [降级] {from_source} 不可用({short_err[:40]})，尝试备用源 {to_source}", file=sys.stderr)
```

---

## §2 实时行情

### §2.1 腾讯实时行情

腾讯财经实时行情接口（qt.gtimg.cn），GBK 编码，`~` 分隔字段。无需认证，纯 HTTP GET 请求。

```python
import re
import requests  # 需要: pip install requests

def _decode_gbk(content):
    """GBK 字节解码，依次尝试 gbk/gb2312/utf-8/latin-1"""
    if isinstance(content, bytes):
        for enc in ('gbk', 'gb2312', 'utf-8', 'latin-1'):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    return content

def _normalize_code(code):
    """
    标准化股票代码 -> SH/SZ + 6位数字
    支持: sh600519, SH600519, 600519, 1.600519
    """
    code = str(code).upper().strip()
    if re.match(r'^(SH|SZ)\d{6}$', code):
        return code
    m = re.match(r'^([01])\.(\d{6})$', code)
    if m:
        prefix = 'SH' if m.group(1) == '1' else 'SZ'
        return prefix + m.group(2)
    if re.match(r'^\d{6}$', code):
        prefix = 'SH' if code.startswith(('6', '9')) else 'SZ'
        return prefix + code
    return code

def _to_tencent_code(code):
    """转腾讯格式: sh600519"""
    std = _normalize_code(code)
    return std.lower()

def _fetch_tencent(codes):
    """
    腾讯实时行情 (qt.gtimg.cn)

    Parameters
    ----------
    codes : str | list - 股票代码

    Returns
    -------
    list of dict: [{'code','name','now','percent','high','low','yesterday','time'}, ...]
    """
    if isinstance(codes, str):
        codes = [codes]

    tencent_codes = [_to_tencent_code(c) for c in codes]
    url = f"https://qt.gtimg.cn/q={','.join(tencent_codes)}"

    try:
        r = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        text = _decode_gbk(r.content)
    except Exception as e:
        return [{'error': f'腾讯接口失败: {e}'}]

    results = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or '=' not in line:
            continue

        # 格式: v_sh600519="1~贵州茅台~600519~1332.95~..."
        parts = line.split('"')
        if len(parts) < 2:
            continue

        code_key = parts[0].split('_')[-1].replace('v_', '').rstrip('=')
        fields = parts[1].split('~')

        if len(fields) < 35:
            continue

        try:
            name = fields[1]
            now = float(fields[3]) if fields[3] else 0
            yesterday = float(fields[4]) if fields[4] else 0
            high = float(fields[33]) if fields[33] else 0
            low = float(fields[34]) if fields[34] else 0
            change = (now - yesterday) / yesterday * 100 if yesterday else 0
            time_str = fields[30] if len(fields) > 30 else ''

            std_code = _normalize_code(code_key)

            results.append({
                'code': std_code,
                'name': name,
                'now': now,
                'percent': round(change, 2),
                'high': high,
                'low': low,
                'yesterday': yesterday,
                'time': time_str,
            })
        except (ValueError, IndexError):
            continue

    return results
```

### §2.2 东财实时行情

东方财富实时行情接口（push2.eastmoney.com），返回 JSON。字段映射：f2=现价, f3=涨跌幅, f15=最高, f16=最低, f18=昨收。

```python
import re
import requests  # 需要: pip install requests

def _normalize_code(code):
    """标准化股票代码 -> SH/SZ + 6位数字"""
    code = str(code).upper().strip()
    if re.match(r'^(SH|SZ)\d{6}$', code):
        return code
    m = re.match(r'^([01])\.(\d{6})$', code)
    if m:
        prefix = 'SH' if m.group(1) == '1' else 'SZ'
        return prefix + m.group(2)
    if re.match(r'^\d{6}$', code):
        prefix = 'SH' if code.startswith(('6', '9')) else 'SZ'
        return prefix + code
    return code

def _to_eastmoney_secid(code):
    """转东方财富格式: 1.600519 (1=上海, 0=深圳)"""
    std = _normalize_code(code)
    if std.startswith('SH'):
        return '1.' + std[2:]
    return '0.' + std[2:]

def _fetch_eastmoney(codes):
    """
    东方财富实时行情 (push2.eastmoney.com)

    Parameters
    ----------
    codes : str | list - 股票代码

    Returns
    -------
    list of dict: [{'code','name','now','percent','high','low','yesterday',
                    'change','amplitude','turnover_rate'}, ...]
    """
    if isinstance(codes, str):
        codes = [codes]

    secids = ','.join(_to_eastmoney_secid(c) for c in codes)
    fields = 'f12,f14,f2,f3,f15,f16,f18,f6,f7,f10,f170,f43,f44,f45,f46,f60'
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids={secids}&fields={fields}"

    headers = {
        'Accept': 'application/json',
        'Referer': 'https://quote.eastmoney.com/',
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        data = r.json()
    except Exception as e:
        return [{'error': f'东方财富接口失败: {e}'}]

    diff = data.get('data', {}).get('diff', {})
    if not diff:
        return []

    items = diff.values() if isinstance(diff, dict) else diff
    results = []

    for item in items:
        try:
            def _v(key):
                val = item.get(key)
                if val is None or val == '-':
                    return 0
                return float(val)

            std_code = _normalize_code(str(item.get('f12', '')))
            results.append({
                'code': std_code,
                'name': str(item.get('f14', '')),
                'now': _v('f2') or _v('f43'),
                'percent': _v('f3') or _v('f170'),
                'high': _v('f15') or _v('f44'),
                'low': _v('f16') or _v('f45'),
                'yesterday': _v('f18') or _v('f60'),
                'change': _v('f6'),
                'amplitude': _v('f7'),
                'turnover_rate': _v('f10'),
            })
        except (ValueError, TypeError):
            continue

    return results
```

### §2.3 统一实时行情（含降级）

统一入口 `get_realtime()`：自动模式按 腾讯 -> 东方财富 -> 通达信 顺序降级。`format_realtime()` 将结果格式化为可读文本。

```python
import re
import requests  # 需要: pip install requests

# ── 编码工具 ──────────────────────────────────────────────

def _decode_gbk(content):
    """GBK 字节解码"""
    if isinstance(content, bytes):
        for enc in ('gbk', 'gb2312', 'utf-8', 'latin-1'):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    return content

def _normalize_code(code):
    """标准化股票代码 -> SH/SZ + 6位数字"""
    code = str(code).upper().strip()
    if re.match(r'^(SH|SZ)\d{6}$', code):
        return code
    m = re.match(r'^([01])\.(\d{6})$', code)
    if m:
        prefix = 'SH' if m.group(1) == '1' else 'SZ'
        return prefix + m.group(2)
    if re.match(r'^\d{6}$', code):
        prefix = 'SH' if code.startswith(('6', '9')) else 'SZ'
        return prefix + code
    return code

def _to_tencent_code(code):
    """转腾讯格式: sh600519"""
    return _normalize_code(code).lower()

def _to_eastmoney_secid(code):
    """转东方财富格式: 1.600519"""
    std = _normalize_code(code)
    return ('1.' if std.startswith('SH') else '0.') + std[2:]

# ── 数据源函数 (参见 §2.1 和 §2.2) ──────────────────────

def _fetch_tencent(codes):
    """腾讯实时行情 — 完整实现见 §2.1"""
    # ... (同上 §2.1 的 _fetch_tencent)
    pass  # 实际使用时替换为 §2.1 完整实现

def _fetch_eastmoney(codes):
    """东方财富实时行情 — 完整实现见 §2.2"""
    # ... (同上 §2.2 的 _fetch_eastmoney)
    pass  # 实际使用时替换为 §2.2 完整实现

# ── 通达信备用 (可选, 需要 pip install mootdx) ────────────

_HAS_MOOTDX = None

def _check_mootdx():
    global _HAS_MOOTDX
    if _HAS_MOOTDX is None:
        try:
            from mootdx.quotes import Quotes  # 需要: pip install mootdx
            _HAS_MOOTDX = True
        except ImportError:
            _HAS_MOOTDX = False
    return _HAS_MOOTDX

def _fetch_mootdx(codes):
    """mootdx 实时行情备用源 — 完整实现见 §2.5"""
    # 依赖: sources_mootdx.get_realtime()
    pass  # 实际使用时替换为 §2.5 完整实现

# ── 对外接口 ──────────────────────────────────────────────

def get_realtime(codes, source='auto'):
    """
    获取股票实时行情 (含自动降级)

    Parameters
    ----------
    codes : str | list - 股票代码，如 'sh600519' 或 ['sh600519','sz000858']
    source : str - 数据源 ('auto'|'tencent'|'eastmoney'|'mootdx')

    Returns
    -------
    list of dict: [{'code','name','now','percent','high','low','yesterday'}, ...]
    """
    if isinstance(codes, str):
        codes = [c.strip() for c in codes.split(',') if c.strip()]

    if source == 'auto':
        # 降级顺序: 腾讯 -> 东方财富 -> mootdx
        results = _fetch_tencent(codes)
        if results and 'error' not in results[0]:
            return results
        results = _fetch_eastmoney(codes)
        if results and 'error' not in results[0]:
            return results
        if _check_mootdx():
            results = _fetch_mootdx(codes)
            if results and 'error' not in results[0]:
                return results
        return results

    source_map = {
        'tencent': _fetch_tencent,
        'eastmoney': _fetch_eastmoney,
        'mootdx': _fetch_mootdx,
    }
    fetch_fn = source_map.get(source, _fetch_tencent)
    return fetch_fn(codes)


def format_realtime(results):
    """
    格式化实时行情为可读文本

    Parameters
    ----------
    results : list of dict - get_realtime() 的返回值

    Returns
    -------
    str - 格式化后的多行文本
    """
    if not results:
        return "  无数据"

    lines = []
    for r in results:
        if 'error' in r:
            lines.append(f"  ❌ {r['error']}")
            continue

        name = r.get('name', '')
        code = r.get('code', '')
        now = r.get('now', 0)
        pct = r.get('percent', 0)
        high = r.get('high', 0)
        low = r.get('low', 0)
        yesterday = r.get('yesterday', 0)

        arrow = '🔴' if pct < 0 else '🟢' if pct > 0 else '⚪'
        sign = '+' if pct > 0 else ''

        vol_str = ''
        vol = r.get('volume', 0)
        if vol:
            if vol >= 10000:
                vol_str = f"  量:{vol/10000:.0f}万手"
            else:
                vol_str = f"  量:{vol:.0f}手"

        amt_str = ''
        amt = r.get('amount', 0)
        if amt:
            if amt >= 1e8:
                amt_str = f"  额:{amt/1e8:.2f}亿"
            elif amt >= 1e4:
                amt_str = f"  额:{amt/1e4:.0f}万"

        time_str = ''
        t = r.get('time', '')
        if t and ':' in str(t):
            time_str = f"  {t}"

        lines.append(f"  {arrow} {name}({code})  {now:.2f}  {sign}{pct:.2f}%  高:{high:.2f} 低:{low:.2f} 昨:{yesterday:.2f}{vol_str}{amt_str}{time_str}")

    return '\n'.join(lines)
```

### §2.4 股票搜索

支持腾讯和东方财富两个搜索源，自动模式优先东方财富（结果更全），失败降级到腾讯。

```python
import re
import requests  # 需要: pip install requests

def _decode_gbk(content):
    """GBK 字节解码"""
    if isinstance(content, bytes):
        for enc in ('gbk', 'gb2312', 'utf-8', 'latin-1'):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    return content

def _search_tencent(keyword):
    """
    腾讯股票搜索 (smartbox.gtimg.cn)

    Parameters
    ----------
    keyword : str - 关键词（名称或代码）

    Returns
    -------
    list of dict: [{'code': 'SH600519', 'name': '贵州茅台'}, ...]
    """
    url = f"https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={keyword}"
    try:
        r = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        text = _decode_gbk(r.content)
    except Exception:
        return []

    # 格式: v_hint="sz~000858~五粮液^sh~600519~贵州茅台"
    m = re.search(r'v_hint="([^"]*)"', text)
    if not m:
        return []

    results = []
    for item in m.group(1).split('^'):
        parts = item.split('~')
        if len(parts) >= 3:
            market, code, name = parts[0], parts[1], parts[2]
            prefix = market.upper()
            results.append({
                'code': f'{prefix}{code}',
                'name': name,
            })
    return results


def _search_eastmoney(keyword):
    """
    东方财富搜索 (searchapi.eastmoney.com)

    Parameters
    ----------
    keyword : str - 关键词（名称或代码）

    Returns
    -------
    list of dict: [{'code': 'SH600519', 'name': '贵州茅台'}, ...]
    """
    token = 'D43BF722C8E33BDC906FB84D85E326E8'
    url = f"https://searchapi.eastmoney.com/api/suggest/get?input={keyword}&type=14&token={token}"
    headers = {'Referer': 'https://quote.eastmoney.com/'}

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        data = r.json()
    except Exception:
        return []

    items = data.get('QuotationCodeTable', {}).get('Data', [])
    results = []
    for item in items:
        code = item.get('Code', '')
        mkt = item.get('MktNum', '')
        name = item.get('Name', '')
        if code:
            prefix = 'SH' if mkt == '1' else 'SZ'
            results.append({'code': f'{prefix}{code}', 'name': name})
    return results


def search_stock(keyword, source='auto'):
    """
    搜索股票 (统一入口)

    Parameters
    ----------
    keyword : str - 关键词（名称或代码）
    source : str - 数据源 ('auto'|'tencent'|'eastmoney')

    Returns
    -------
    list of dict: [{'code', 'name'}, ...]
    """
    if source == 'auto':
        # 优先东方财富（结果更全），失败降级腾讯
        results = _search_eastmoney(keyword)
        if results:
            return results
        return _search_tencent(keyword)

    search_fns = {
        'tencent': _search_tencent,
        'eastmoney': _search_eastmoney,
    }
    search_fn = search_fns.get(source, _search_tencent)
    return search_fn(keyword)
```

### §2.5 通达信备用

通达信 TCP 7709 协议，通过 mootdx 库连接。无认证、无 IP 限制，适合做离线备用数据源。支持实时行情和 K 线数据。

```python
import pandas as pd  # 需要: pip install pandas mootdx

_client = None

def _get_client():
    """获取通达信连接客户端 (单例)"""
    global _client
    if _client is None:
        from mootdx.quotes import Quotes  # 需要: pip install mootdx
        _client = Quotes.factory(market='std')
    return _client

def _to_pure_code(code):
    """sh600519 -> 600519"""
    return code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')

def _to_market(code):
    """判断市场: 0=深圳, 1=上海"""
    pure = _to_pure_code(code)
    if pure.startswith(('6', '9', '5')):
        return 1  # 上海
    return 0  # 深圳

def get_realtime(codes):
    """
    mootdx 实时行情 (通达信 TCP 协议)

    Parameters
    ----------
    codes : list of str - 股票代码列表

    Returns
    -------
    list of dict: [{'code','name','now','open','high','low','close',
                    'volume','amount','change','change_pct'}, ...]
    """
    client = _get_client()
    pure_codes = [_to_pure_code(c) for c in codes]

    results = []
    for code in pure_codes:
        market = _to_market(code)
        df = client.quotes(symbol=[code], market=market)
        if df is not None and len(df) > 0:
            row = df.iloc[0]
            results.append({
                'code': ('SH' if market == 1 else 'SZ') + code,
                'name': str(row.get('name', '')),
                'now': float(row.get('price', 0) or 0),
                'open': float(row.get('open', 0) or 0),
                'high': float(row.get('high', 0) or 0),
                'low': float(row.get('low', 0) or 0),
                'close': float(row.get('last_close', 0) or 0),
                'volume': float(row.get('vol', 0) or 0),
                'amount': float(row.get('amount', 0) or 0),
                'change': float(row.get('price', 0) or 0) - float(row.get('last_close', 0) or 0),
                'change_pct': round(
                    (float(row.get('price', 0) or 0) / float(row.get('last_close', 1) or 1) - 1) * 100, 2
                ) if float(row.get('last_close', 0) or 0) > 0 else 0,
            })

    return results


def get_kline(code, frequency=9, offset=100):
    """
    mootdx K线数据 (通达信 TCP 协议)

    Parameters
    ----------
    code : str - 股票代码
    frequency : int - 0=5m, 1=15m, 2=30m, 3=60m, 9=日线
    offset : int - 数据条数

    Returns
    -------
    DataFrame with columns: open, close, high, low, volume
    """
    client = _get_client()
    pure_code = _to_pure_code(code)
    market = _to_market(code)

    df = client.bars(symbol=pure_code, frequency=frequency, offset=offset, market=market)
    if df is None or len(df) == 0:
        raise RuntimeError(f"mootdx K线: 无数据 ({code})")

    result = pd.DataFrame()
    result['open'] = df['open'].astype(float)
    result['close'] = df['close'].astype(float)
    result['high'] = df['high'].astype(float)
    result['low'] = df['low'].astype(float)
    result['volume'] = df['vol'].astype(float)

    if 'datetime' in df.columns:
        result['time'] = pd.to_datetime(df['datetime'])
        result.set_index('time', inplace=True)
        result.index.name = ''

    return result
```

---

## §3 K线数据

### §3.1 百度K线

百度财经 K 线数据接口，无认证，纯 HTTP 请求。支持前/后复权和不复权。返回分号分隔的 OHLCV 数据。

```python
import requests  # 需要: pip install requests
import pandas as pd  # 需要: pip install pandas

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gushitong.baidu.com/',
}

def _to_pure_code(code):
    """sh600519 -> 600519"""
    return code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')

def get_kline(code, count=100, fqtype=1):
    """
    百度财经K线数据

    Parameters
    ----------
    code : str - 股票代码 (sh600519 或 600519)
    count : int - 数据条数
    fqtype : int - 1=前复权, 2=后复权, 3=不复权

    Returns
    -------
    DataFrame with columns: open, close, high, low, volume
    索引为 datetime
    """
    pure_code = _to_pure_code(code)
    url = (
        f"https://finance.pae.baidu.com/selfselect/getstockquotation"
        f"?code={pure_code}&market=ab&is498=1&isBk=false&isBlock=false"
        f"&isFutures=false&isStock=true&newFormat=1&count={count}&fqtype={fqtype}"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10,
                     proxies={'http': None, 'https': None})
    data = r.json()

    result = data.get('Result', []) or data.get('result', []) or []
    if not result:
        raise RuntimeError("百度K线: 无数据")

    # 解析分号分隔数据
    # 格式: 日期;开;收;高;低;成交量;成交额;振幅;涨跌幅;涨跌额;换手率;ma5;ma10;ma20
    rows = []
    for item in result:
        parts = item.split(';') if isinstance(item, str) else []
        if len(parts) >= 6:
            rows.append({
                'time': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': float(parts[5]),
            })

    if not rows:
        raise RuntimeError("百度K线: 解析失败")

    df = pd.DataFrame(rows)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.index.name = ''
    return df
```

### §3.2 百度资金流

百度分钟级资金流向数据，按时间段（如分钟级别）返回主力/超大单/大单/中单/小单的流入流出。

```python
import requests  # 需要: pip install requests
from datetime import datetime

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gushitong.baidu.com/',
}

def _to_pure_code(code):
    """sh600519 -> 600519"""
    return code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')

def get_fund_flow(code, market='ab'):
    """
    百度分钟级资金流向

    Parameters
    ----------
    code : str - 股票代码
    market : str - 市场 ('ab'=A股)

    Returns
    -------
    dict: {
        'rows': [{'name','chg_pct','main_in','main_out','main_net'}, ...],
        'summary': {'total_in','total_out','total_net'}
    }
    """
    pure_code = _to_pure_code(code)
    today = datetime.now().strftime('%Y-%m-%d')
    url = (
        f"https://finance.pae.baidu.com/vapi/v1/fundflow"
        f"?code={pure_code}&market={market}&date={today}&finClientType=pc"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10,
                     proxies={'http': None, 'https': None})
    data = r.json()

    result = data.get('result', {}) or {}
    stock_list = result.get('stockList', []) or []

    rows = []
    total_in = 0
    total_out = 0

    for item in stock_list:
        name = item.get('name', '')
        chg_pct = float(item.get('rate', 0) or 0)
        main_in = float(item.get('superLargeIncome', 0) or 0)
        main_out = float(item.get('superLargePay', 0) or 0)
        main_net = main_in - main_out
        total_in += main_in
        total_out += main_out

        rows.append({
            'name': name,
            'chg_pct': chg_pct,
            'main_in': main_in,
            'main_out': main_out,
            'main_net': main_net,
        })

    summary = {
        'total_in': total_in,
        'total_out': total_out,
        'total_net': total_in - total_out,
    }

    return {'rows': rows, 'summary': summary}
```

### §3.3 北向资金

同花顺北向资金数据接口（data.hexin.cn），无认证，返回 JSON 格式。支持沪股通和深股通。

```python
import requests  # 需要: pip install requests
from datetime import datetime, timedelta

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.10jqka.com.cn/',
}

def get_north_flow(symbol='沪股通', days=10):
    """
    同花顺北向资金

    Parameters
    ----------
    symbol : str - '沪股通' 或 '深股通'
    days : int - 获取天数

    Returns
    -------
    list of dict: [{'date': '2025-01-15', 'net_buy': 1234567890.0,
                    'fund_flow': 0, 'leader': ''}, ...]
    """
    symbol_map = {'沪股通': 'hgt', '深股通': 'sgt'}
    code = symbol_map.get(symbol, 'hgt')

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days + 10)).strftime('%Y-%m-%d')

    url = (
        f"https://data.hexin.cn/market/hsgtApi/method/dayChart/"
        f"?token=&param={code}&start={start_date}&end={end_date}"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=15)
    data = r.json()

    items = data.get(code, []) or []
    rows = []
    for item in items[-days:]:
        rows.append({
            'date': item.get('date', ''),
            'net_buy': float(item.get('value', 0) or 0),
            'fund_flow': 0,
            'leader': '',
        })

    return rows
```
## §4 筹码分布

### §4.1 筹码分布计算

纯算法实现，无网络依赖，移植自 go-stock。基于K线+换手率近似计算筹码分布：用换手率对历史筹码做衰减，将当日成交量按高斯核落在各价格bin上。

```python
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
    sigma = max((high - low) / 4, width / 2)
    if sigma <= 0:
        sigma = width
    total_weight = 0.0
    weights = []
    for i in range(bins):
        bin_center = min_p + (i + 0.5) * width
        bin_lo = min_p + i * width
        bin_hi = bin_lo + width
        if bin_hi < low or bin_lo > high:
            weights.append(0.0)
            continue
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
```


## §5 板块资金流

### §5.1 板块资金流排名

获取行业/概念板块资金流排名（实时），数据源为东方财富 data.eastmoney.com/dataapi/bkzj。

```python
import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

_BK_INDUSTRY_URL = "https://data.eastmoney.com/dataapi/bkzj/getbkzj"


def _safe_float(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_board_fund_flow(board_type: str = 'industry', top_n: int = 20) -> List[Dict]:
    """
    获取板块资金流排名

    参数:
        board_type: 'industry'(行业板块) 或 'concept'(概念板块)
        top_n: 返回前N名

    返回:
        [{'code': 板块代码, 'name': 板块名称, 'net_inflow': 主力净流入(元)}, ...]
    """
    # code参数: m:90+s:4 = 行业板块, m:90+t:3 = 概念板块
    code_param = "m:90+s:4" if board_type == 'industry' else "m:90+t:3"

    params = {
        'key': 'f62',
        'code': code_param,
    }

    try:
        resp = requests.get(_BK_INDUSTRY_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取板块资金流失败: {e}")
        return []

    if data.get('rc') != 0:
        print(f"  [WARN] 接口返回异常: rc={data.get('rc')}")
        return []

    diff = data.get('data', {}).get('diff', [])
    if not diff:
        return []

    results = []
    for item in diff:
        results.append({
            'code': item.get('f12', ''),
            'name': item.get('f14', ''),
            'net_inflow': _safe_float(item.get('f62')),
            'market': item.get('f13', 0),
        })

    # 按主力净流入排序
    results.sort(key=lambda x: x['net_inflow'], reverse=True)
    return results[:top_n]


def format_board_fund_flow(results: List[Dict], board_type: str = 'industry') -> str:
    """格式化板块资金流输出"""
    if not results:
        return "未获取到板块资金流数据"

    title = "行业板块" if board_type == 'industry' else "概念板块"
    lines = [
        "=" * 70,
        f"  {title}资金流排名 (主力净流入)",
        "=" * 70,
        f"  {'排名':<4} {'板块名称':<12} {'代码':<10} {'主力净流入':>14}",
        "-" * 70,
    ]

    for i, item in enumerate(results, 1):
        inflow = item['net_inflow']
        inflow_yi = inflow / 1e8
        sign = "+" if inflow_yi >= 0 else ""
        arrow = "🟢" if inflow_yi >= 0 else "🔴"
        lines.append(f"  {i:<4} {item['name']:<12} {item['code']:<10} {arrow}{sign}{inflow_yi:>10.2f}亿")

    lines.append("=" * 70)

    # 统计
    inflow_count = sum(1 for r in results if r['net_inflow'] > 0)
    outflow_count = len(results) - inflow_count
    total_inflow = sum(r['net_inflow'] for r in results if r['net_inflow'] > 0) / 1e8
    total_outflow = sum(r['net_inflow'] for r in results if r['net_inflow'] < 0) / 1e8

    lines.append(f"  统计: {inflow_count}个流入 / {outflow_count}个流出")
    lines.append(f"  总流入: +{total_inflow:.2f}亿 | 总流出: {total_outflow:.2f}亿")

    return "\n".join(lines)
```

### §5.2 个股资金流历史

获取个股资金流历史（日线级别），使用东方财富 push2his fflow 接口，返回每日主力/超大单/大单/中单/小单净额。

```python
import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://data.eastmoney.com/',
}


def _safe_float(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_stock_fund_flow_history(stock_code: str, days: int = 30) -> List[Dict]:
    """
    获取个股资金流历史（日线级别）
    使用东方财富 push2his fflow 接口

    参数:
        stock_code: 股票代码（纯数字，如 '600519'）
        days: 获取天数

    返回:
        [{'date': 日期, 'main_net': 主力净额, 'super_large': 超大单, 'large': 大单,
          'medium': 中单, 'small': 小单}, ...]
    """
    # 确定 secid
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    if code.startswith(('6', '9')):
        secid = f"1.{code}"
    elif code.startswith(('0', '3')):
        secid = f"0.{code}"
    elif code.startswith(('4', '8')):
        secid = f"0.{code}"
    else:
        secid = f"1.{code}"

    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        'lmt': str(days),
        'klt': '101',
        'secid': secid,
        'fields1': 'f1,f2,f3,f7',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65',
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取资金流历史失败: {e}")
        return []

    klines = data.get('data', {}).get('klines', [])
    if not klines:
        return []

    results = []
    for line in klines:
        parts = line.split(',')
        if len(parts) < 7:
            continue
        results.append({
            'date': parts[0],
            'main_net': _safe_float(parts[1]),       # 主力净额
            'small': _safe_float(parts[2]),          # 小单净额
            'medium': _safe_float(parts[3]),         # 中单净额
            'large': _safe_float(parts[4]),          # 大单净额
            'super_large': _safe_float(parts[5]),    # 超大单净额
        })

    return results


def format_stock_fund_flow_history(results: List[Dict], stock_code: str) -> str:
    """格式化个股资金流历史输出"""
    if not results:
        return f"未获取到 {stock_code} 的资金流历史数据"

    lines = [
        "=" * 75,
        f"  个股资金流历史: {stock_code} (最近{len(results)}个交易日)",
        "=" * 75,
        f"  {'日期':<12} {'主力净额':>12} {'超大单':>12} {'大单':>12} {'中单':>12} {'小单':>12}",
        "-" * 75,
    ]

    total_main = 0
    for item in results:
        main = item['main_net'] / 1e8
        total_main += item['main_net']
        sign = "+" if main >= 0 else ""
        arrow = "🟢" if main >= 0 else "🔴"
        lines.append(
            f"  {item['date']:<12} {arrow}{sign}{main:>9.2f}亿 "
            f"{item['super_large']/1e8:>10.2f}亿 "
            f"{item['large']/1e8:>10.2f}亿 "
            f"{item['medium']/1e8:>10.2f}亿 "
            f"{item['small']/1e8:>10.2f}亿"
        )

    lines.append("-" * 75)
    total_yi = total_main / 1e8
    sign = "+" if total_yi >= 0 else ""
    lines.append(f"  累计主力净流入: {sign}{total_yi:.2f}亿")
    lines.append("=" * 75)

    return "\n".join(lines)
```


## §6 F10财务指标

### §6.1 主要财务指标

获取个股主要财务指标（营收/净利润/ROE/毛利率等），数据源为东方财富 datacenter。

```python
import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0',
    'Referer': 'https://emweb.securities.eastmoney.com/',
    'Origin': 'https://emweb.securities.eastmoney.com',
    'Host': 'datacenter.eastmoney.com',
}

_BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"


def _safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _normalize_code(stock_code: str) -> str:
    """转换为东财datacenter格式: 600519.SH"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    if '.' in code:
        return code
    if code.startswith(('6', '9')):
        return f"{code}.SH"
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"
    elif code.startswith(('4', '8')):
        return f"{code}.BJ"
    elif code.startswith('5'):
        return f"{code}.SH"
    return f"{code}.SZ"


def _f10_request(report_name: str, secucode: str, page_size: int = 5,
                 columns: str = 'ALL', sort_columns: str = 'REPORT_DATE',
                 sort_types: str = '-1') -> List[Dict]:
    """通用F10请求"""
    params = {
        'reportName': report_name,
        'columns': columns,
        'filter': f'(SECUCODE="{secucode}")',
        'pageSize': str(page_size),
        'sortColumns': sort_columns,
        'sortTypes': sort_types,
        'source': 'HSF10',
        'client': 'PC',
    }

    try:
        resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] F10请求失败: {e}")
        return []

    if not data.get('success'):
        return []

    result = data.get('result', {})
    return result.get('data', []) or []


def get_main_finance(stock_code: str, periods: int = 5) -> List[Dict]:
    """
    获取主要财务指标

    参数:
        stock_code: 股票代码（如 '600519' 或 'sh600519'）
        periods: 获取最近几期

    返回:
        [{'report_date': 报告日期, 'eps': 每股收益, 'bps': 每股净资产,
          'revenue': 营业总收入, 'net_profit': 归属净利润, 'roe': ROE,
          'gross_margin': 毛利率, 'debt_ratio': 资产负债率,
          'revenue_yoy': 营收同比增长, 'profit_yoy': 净利同比增长}, ...]
    """
    secucode = _normalize_code(stock_code)
    data = _f10_request('RPT_F10_FINANCE_MAINFINADATA', secucode, page_size=periods)

    results = []
    for item in data:
        results.append({
            'report_date': item.get('REPORT_DATE', '')[:10],
            'eps': _safe_float(item.get('EPSJB')),
            'eps_deducted': _safe_float(item.get('EPSKCJB')),
            'bps': _safe_float(item.get('BPS')),
            'revenue': _safe_float(item.get('TOTALOPERATEREVE')),
            'net_profit': _safe_float(item.get('PARENTNETPROFIT')),
            'net_profit_deducted': _safe_float(item.get('KCFJCXSYJLR')),
            'roe': _safe_float(item.get('ROEJQ')),
            'gross_margin': _safe_float(item.get('XSMLL')),
            'debt_ratio': _safe_float(item.get('ZCFZL')),
            'revenue_yoy': _safe_float(item.get('TOTALOPERATEREVETZ')),
            'profit_yoy': _safe_float(item.get('PARENTNETPROFITTZ')),
            'profit_yoy_deducted': _safe_float(item.get('KCFJCXSYJLRTZ')),
            'total_shares': _safe_float(item.get('TOTAL_SHARE')),
            'free_shares': _safe_float(item.get('FREE_SHARE')),
        })

    return results


def format_main_finance(results: List[Dict], stock_code: str) -> str:
    """格式化主要财务指标输出"""
    if not results:
        return f"未获取到 {stock_code} 的财务数据"

    lines = [
        "=" * 80,
        f"  F10 主要财务指标: {stock_code}",
        "=" * 80,
    ]

    for item in results:
        rev = item.get('revenue')
        profit = item.get('net_profit')
        rev_str = f"{rev/1e8:.2f}亿" if rev is not None else "N/A"
        profit_str = f"{profit/1e8:.2f}亿" if profit is not None else "N/A"

        def _r(v, nd=2):
            return round(v, nd) if v is not None else 'N/A'

        lines.append(f"\n  📅 {item.get('report_date', 'N/A')}")
        lines.append(f"    每股收益: {_r(item.get('eps'))} 元 | 扣非: {_r(item.get('eps_deducted'))} 元")
        lines.append(f"    每股净资产: {_r(item.get('bps'))} 元")
        lines.append(f"    营业总收入: {rev_str} | 归属净利润: {profit_str}")
        lines.append(f"    ROE(加权): {_r(item.get('roe'))}% | 毛利率: {_r(item.get('gross_margin'))}%")
        lines.append(f"    资产负债率: {_r(item.get('debt_ratio'))}%")
        lines.append(f"    营收同比: {_r(item.get('revenue_yoy'))}% | 净利同比: {_r(item.get('profit_yoy'))}%")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)
```

### §6.2 机构盈利预测

获取机构对个股的盈利预测数据，包含未来1-3年的预测EPS和预测PE。

```python
import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0',
    'Referer': 'https://emweb.securities.eastmoney.com/',
    'Origin': 'https://emweb.securities.eastmoney.com',
    'Host': 'datacenter.eastmoney.com',
}

_BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"


def _safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _normalize_code(stock_code: str) -> str:
    """转换为东财datacenter格式: 600519.SH"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    if '.' in code:
        return code
    if code.startswith(('6', '9')):
        return f"{code}.SH"
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"
    elif code.startswith(('4', '8')):
        return f"{code}.BJ"
    elif code.startswith('5'):
        return f"{code}.SH"
    return f"{code}.SZ"


def _f10_request(report_name: str, secucode: str, page_size: int = 5,
                 columns: str = 'ALL', sort_columns: str = 'REPORT_DATE',
                 sort_types: str = '-1') -> List[Dict]:
    """通用F10请求"""
    params = {
        'reportName': report_name,
        'columns': columns,
        'filter': f'(SECUCODE="{secucode}")',
        'pageSize': str(page_size),
        'sortColumns': sort_columns,
        'sortTypes': sort_types,
        'source': 'HSF10',
        'client': 'PC',
    }

    try:
        resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] F10请求失败: {e}")
        return []

    if not data.get('success'):
        return []

    result = data.get('result', {})
    return result.get('data', []) or []


def get_forecast(stock_code: str) -> List[Dict]:
    """
    获取机构盈利预测

    返回:
        [{'year': 预测年份, 'eps': 预测每股收益, 'pe': 预测市盈率}, ...]
    """
    secucode = _normalize_code(stock_code)
    data = _f10_request('RPT_F10_FINANCE_FORECAST', secucode, page_size=3,
                        sort_columns='REPORT_DATE', sort_types='-1')

    results = []
    for item in data:
        results.append({
            'report_date': item.get('REPORT_DATE', '')[:10],
            'year1': item.get('YEAR1'),
            'eps1': _safe_float(item.get('EPS1')),
            'pe1': _safe_float(item.get('PE1')),
            'year2': item.get('YEAR2'),
            'eps2': _safe_float(item.get('EPS2')),
            'pe2': _safe_float(item.get('PE2')),
            'year3': item.get('YEAR3'),
            'eps3': _safe_float(item.get('EPS3')),
            'pe3': _safe_float(item.get('PE3')),
        })

    return results


def format_forecast(results: List[Dict], stock_code: str) -> str:
    """格式化机构预测输出"""
    if not results:
        return f"未获取到 {stock_code} 的机构预测数据"

    lines = [
        "=" * 60,
        f"  机构盈利预测: {stock_code}",
        "=" * 60,
    ]

    for item in results:
        lines.append(f"\n  📅 预测日期: {item.get('report_date', 'N/A')}")
        for i in [1, 2, 3]:
            year = item.get(f'year{i}')
            eps = item.get(f'eps{i}')
            pe = item.get(f'pe{i}')
            if year and eps:
                lines.append(
                    f"    {year}年: 预测EPS {eps:.2f}元, 预测PE {pe:.1f}"
                    if pe else
                    f"    {year}年: 预测EPS {eps:.2f}元"
                )

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
```


## §7 市场温度与估值

### §7.1 市场温度计

综合多个A股市场指标（巴菲特指标、股债利差、创新高/新低、QVIX波动率、市场活跃度），计算市场温度分数(0-100)，判断市场情绪偏热(贪婪)还是偏冷(恐惧)。

需要: pip install akshare

```python
import sys
import datetime

# 需要: pip install akshare
import akshare as ak


def fetch_buffett_index():
    """
    获取巴菲特指标 (A股总市值/GDP)
    返回: {'value': float, 'percentile': float, 'date': str, 'name': str}
    """
    try:
        df = ak.stock_buffett_index_lg()
        if df is None or df.empty:
            return None
        latest = df.iloc[-1]
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "指标" in cl or "gdp" in cl.lower() and "总" in cl:
                value = float(latest[c])
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        # 计算历史百分位
        indicator_col = None
        for c in cols:
            cl = str(c).lower()
            if "指标" in cl or ("总" in cl and "gdp" in cl.lower()):
                indicator_col = c
                break
        if indicator_col is None:
            for c in reversed(cols):
                try:
                    df[c].astype(float)
                    indicator_col = c
                    break
                except (ValueError, TypeError):
                    continue
        percentile = 50.0
        if indicator_col is not None:
            series = df[indicator_col].astype(float).dropna()
            if len(series) > 0:
                percentile = float((series < value).sum() / len(series) * 100)
        return {
            'value': round(value, 2),
            'percentile': round(percentile, 1),
            'date': date_str,
            'name': '巴菲特指标(总市值/GDP)',
        }
    except Exception as e:
        print(f"[market_temp] fetch_buffett_index failed: {e}", file=sys.stderr)
        return None


def fetch_equity_bond_spread():
    """
    获取股债利差 (风险溢价, 万得全A盈利收益率 - 10年期国债收益率)
    返回: {'value': float, 'date': str, 'name': str}
    """
    try:
        df = ak.stock_ebs_lg()
        if df is None or df.empty:
            return None
        latest = df.iloc[-1]
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "利差" in cl or "spread" in cl or "溢价" in cl:
                value = float(latest[c])
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        return {
            'value': round(value, 4),
            'date': date_str,
            'name': '股债利差(风险溢价)',
        }
    except Exception as e:
        print(f"[market_temp] fetch_equity_bond_spread failed: {e}", file=sys.stderr)
        return None


def fetch_new_high_low():
    """
    获取创新高/创新低股票数量统计
    返回: {'new_high': int, 'new_low': int, 'ratio': float, 'symbol': str, 'name': str}
    """
    symbols = ["sz50", "hs300"]
    for symbol in symbols:
        try:
            df = ak.stock_a_high_low_statistics(symbol=symbol)
            if df is None or df.empty:
                continue
            latest = df.iloc[-1]
            cols = df.columns.tolist()
            new_high = None
            new_low = None
            for c in cols:
                cl = str(c).lower()
                if "新高" in cl or "high" in cl:
                    new_high = int(float(latest[c]))
                elif "新低" in cl or "low" in cl:
                    new_low = int(float(latest[c]))
            if new_high is None or new_low is None:
                numeric_cols = []
                for c in cols:
                    try:
                        int(float(latest[c]))
                        numeric_cols.append(c)
                    except (ValueError, TypeError):
                        continue
                if len(numeric_cols) >= 2:
                    new_high = int(float(latest[numeric_cols[0]]))
                    new_low = int(float(latest[numeric_cols[1]]))
            if new_high is None or new_low is None:
                continue
            ratio = float(new_high) / max(float(new_low), 1.0)
            return {
                'new_high': new_high,
                'new_low': new_low,
                'ratio': round(ratio, 2),
                'symbol': symbol,
                'name': f'创新高/新低({symbol})',
            }
        except Exception as e:
            print(f"[market_temp] fetch_new_high_low({symbol}) failed: {e}", file=sys.stderr)
            continue
    return None


def fetch_qvix():
    """
    获取50ETF期权QVIX波动率指数 (中国版VIX)
    返回: {'value': float, 'date': str, 'name': str}
    """
    try:
        df = ak.index_option_50etf_qvix()
        if df is None or df.empty:
            return None
        latest = df.iloc[-1]
        cols = df.columns.tolist()
        value = None
        date_str = ""
        for c in cols:
            cl = str(c).lower()
            if "qvix" in cl or "波动" in cl or "close" in cl or "收盘" in cl:
                try:
                    value = float(latest[c])
                except (ValueError, TypeError):
                    pass
            elif "日期" in cl or "date" in cl:
                date_str = str(latest[c])
        if value is None:
            for c in reversed(cols):
                try:
                    value = float(latest[c])
                    break
                except (ValueError, TypeError):
                    continue
        if value is None:
            return None
        return {
            'value': round(value, 2),
            'date': date_str,
            'name': 'QVIX期权波动率',
        }
    except Exception as e:
        print(f"[market_temp] fetch_qvix failed: {e}", file=sys.stderr)
        return None


def fetch_market_activity():
    """
    获取市场活跃度
    返回: {'value': float, 'date': str, 'name': str}
    """
    try:
        df = ak.stock_market_activity_legu()
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            cols = df.columns.tolist()
            value = None
            date_str = ""
            for c in cols:
                cl = str(c).lower()
                if "活跃" in cl or "activity" in cl or "比例" in cl or "percent" in cl:
                    try:
                        value = float(latest[c])
                    except (ValueError, TypeError):
                        pass
                elif "日期" in cl or "date" in cl:
                    date_str = str(latest[c])
            if value is None:
                for c in reversed(cols):
                    try:
                        value = float(latest[c])
                        break
                    except (ValueError, TypeError):
                        continue
            if value is not None:
                if value <= 1.0:
                    value = value * 100
                return {
                    'value': round(value, 2),
                    'date': date_str,
                    'name': '市场活跃度',
                }
    except Exception as e:
        print(f"[market_temp] fetch_market_activity failed: {e}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# 温度计算
# ---------------------------------------------------------------------------

def _score_buffett(data):
    """巴菲特指标子评分: 百分位越低越看多"""
    if data is None:
        return None
    pct = data.get('percentile', 50.0)
    if pct < 70:
        score = 80 + (70 - pct) / 70 * 20
    elif pct <= 90:
        score = 70 - (pct - 70) / 20 * 30
    else:
        score = max(0, 40 - (pct - 90) / 10 * 40)
    return round(min(100, max(0, score)), 1)


def _score_spread(data):
    """股债利差子评分: 利差越大股票越有吸引力 -> 看多"""
    if data is None:
        return None
    spread = data.get('value', 0)
    if spread >= 4:
        score = 90 + min(10, (spread - 4) * 5)
    elif spread >= 2:
        score = 60 + (spread - 2) / 2 * 30
    elif spread >= 0:
        score = 40 + spread / 2 * 20
    else:
        score = max(0, 40 + spread * 20)
    return round(min(100, max(0, score)), 1)


def _score_high_low(data):
    """新高/新低比子评分: ratio>2看多, 0.5-2中性, <0.5看空"""
    if data is None:
        return None
    ratio = data.get('ratio', 1.0)
    if ratio > 2:
        score = 70 + min(30, (ratio - 2) * 10)
    elif ratio >= 0.5:
        score = 40 + (ratio - 0.5) / 1.5 * 30
    else:
        score = max(0, ratio / 0.5 * 40)
    return round(min(100, max(0, score)), 1)


def _score_qvix(data):
    """QVIX子评分: 低波动看多, 高波动看空"""
    if data is None:
        return None
    qvix = data.get('value', 20)
    if qvix < 15:
        score = 80 + (15 - qvix) / 15 * 20
    elif qvix <= 25:
        score = 40 + (25 - qvix) / 10 * 40
    else:
        score = max(0, 40 - (qvix - 25) / 15 * 40)
    return round(min(100, max(0, score)), 1)


def _score_activity(data):
    """市场活跃度子评分: >60%看多, 30-60%中性, <30%看空"""
    if data is None:
        return None
    act = data.get('value', 50)
    if act > 60:
        score = 70 + min(30, (act - 60) / 40 * 30)
    elif act >= 30:
        score = 40 + (act - 30) / 30 * 30
    else:
        score = max(0, act / 30 * 40)
    return round(min(100, max(0, score)), 1)


def compute_temperature(results: dict) -> dict:
    """
    根据各指标数据计算综合市场温度

    参数:
        results: dict, 各指标获取结果
            keys: 'buffett', 'spread', 'high_low', 'qvix', 'activity'

    返回:
        {
            'score': float,       # 综合温度 0-100
            'level': str,         # 温度等级
            'details': {...},     # 各指标子评分
            'missing': [...],     # 缺失的指标列表
        }
    """
    weights = {
        'buffett': 0.25,
        'spread': 0.20,
        'high_low': 0.20,
        'qvix': 0.20,
        'activity': 0.15,
    }

    scorers = {
        'buffett': _score_buffett,
        'spread': _score_spread,
        'high_low': _score_high_low,
        'qvix': _score_qvix,
        'activity': _score_activity,
    }

    details = {}
    missing = []
    weighted_sum = 0.0
    weight_total = 0.0

    for key, weight in weights.items():
        data = results.get(key)
        sub_score = scorers[key](data)
        if sub_score is not None:
            details[key] = {
                'data': data,
                'sub_score': sub_score,
                'weight': weight,
            }
            weighted_sum += sub_score * weight
            weight_total += weight
        else:
            missing.append(key)
            details[key] = {
                'data': None,
                'sub_score': None,
                'weight': weight,
            }

    # 归一化 (如果有指标缺失，按可用权重归一化)
    if weight_total > 0:
        score = weighted_sum / weight_total
    else:
        score = 50.0  # 无数据时给中性分

    score = round(min(100, max(0, score)), 1)

    if score >= 70:
        level = "偏热/贪婪"
    elif score >= 40:
        level = "中性"
    else:
        level = "偏冷/恐惧"

    return {
        'score': score,
        'level': level,
        'details': details,
        'missing': missing,
    }


def get_market_temperature() -> dict:
    """
    获取市场温度: 调用所有数据源，计算综合温度分数

    返回:
        {
            'score': float,
            'level': str,
            'details': {...},
            'missing': [...],
            'timestamp': str,
        }
    """
    results = {
        'buffett': fetch_buffett_index(),
        'spread': fetch_equity_bond_spread(),
        'high_low': fetch_new_high_low(),
        'qvix': fetch_qvix(),
        'activity': fetch_market_activity(),
    }

    temp = compute_temperature(results)
    temp['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return temp


def _make_bar(score, width=20):
    """生成ASCII温度条: [=====>    ] 55/100"""
    filled = int(round(score / 100 * width))
    filled = max(0, min(width, filled))
    if filled < width:
        bar = '=' * max(0, filled - 1) + '>' + ' ' * (width - filled)
    else:
        bar = '=' * width
    return f"[{bar}] {score:.0f}/100"


def _level_marker(level):
    """根据温度等级返回ASCII标记"""
    if "热" in level or "贪婪" in level:
        return "[HOT]"
    elif "冷" in level or "恐惧" in level:
        return "[COLD]"
    return "[WARM]"


def format_temperature(result: dict) -> str:
    """
    格式化市场温度结果为可读文本

    参数:
        result: get_market_temperature() 的返回值

    返回:
        格式化的字符串
    """
    lines = []
    lines.append("=" * 50)
    lines.append("        A股市场温度计 (Market Temperature)")
    lines.append("=" * 50)

    score = result.get('score', 50)
    level = result.get('level', '中性')
    marker = _level_marker(level)
    timestamp = result.get('timestamp', '')

    lines.append(f"  综合温度: {score:.1f} / 100  {marker} {level}")
    lines.append(f"  {_make_bar(score)}")
    if timestamp:
        lines.append(f"  时间: {timestamp}")
    lines.append("-" * 50)

    # 各指标详情
    indicator_names = {
        'buffett': '巴菲特指标',
        'spread': '股债利差',
        'high_low': '新高/新低',
        'qvix': 'QVIX波动率',
        'activity': '市场活跃度',
    }

    details = result.get('details', {})
    for key in ['buffett', 'spread', 'high_low', 'qvix', 'activity']:
        info = details.get(key, {})
        name = indicator_names.get(key, key)
        sub_score = info.get('sub_score')
        data = info.get('data')
        weight = info.get('weight', 0)

        if sub_score is not None and data is not None:
            if key == 'buffett':
                val_str = f"值={data.get('value', '?')}%, 百分位={data.get('percentile', '?')}%"
            elif key == 'spread':
                val_str = f"利差={data.get('value', '?')}%"
            elif key == 'high_low':
                val_str = f"新高={data.get('new_high', '?')}, 新低={data.get('new_low', '?')}, 比值={data.get('ratio', '?')}"
            elif key == 'qvix':
                val_str = f"QVIX={data.get('value', '?')}"
            elif key == 'activity':
                val_str = f"活跃度={data.get('value', '?')}%"
            else:
                val_str = str(data.get('value', '?'))

            sub_marker = _level_marker(
                "偏热/贪婪" if sub_score >= 70 else ("偏冷/恐惧" if sub_score < 40 else "中性")
            )
            lines.append(f"  {name} (权重{weight*100:.0f}%)")
            lines.append(f"    {val_str}")
            lines.append(f"    子评分: {sub_score:.1f}/100 {sub_marker}")
        else:
            lines.append(f"  {name} (权重{weight*100:.0f}%)")
            lines.append(f"    [数据缺失]")

    lines.append("-" * 50)

    missing = result.get('missing', [])
    if missing:
        missing_names = [indicator_names.get(m, m) for m in missing]
        lines.append(f"  缺失指标: {', '.join(missing_names)}")
        lines.append(f"  (已按可用指标归一化计算)")

    error = result.get('error')
    if error:
        lines.append(f"  [ERROR] {error}")

    lines.append("=" * 50)
    return "\n".join(lines)
```

### §7.2 个股估值分位

获取个股历史 PE/PB/PS 估值数据，计算当前估值在历史区间中的分位数，判断个股估值水平（低估/合理/偏高）。主源为东方财富 datacenter，备用源为 akshare 百度估值。

需要: pip install akshare

```python
import sys
import warnings
import requests
import statistics

warnings.filterwarnings("ignore")

# 需要: pip install akshare
import akshare as ak


def _warn(msg):
    """输出警告到 stderr"""
    print(f"[valuation] WARNING: {msg}", file=sys.stderr)


def _fetch_valuation_eastmoney(code: str, indicator: str = "pe", period: str = "all") -> dict:
    """
    东方财富 datacenter 估值数据 (RPT_VALUEANALYSIS_DET)
    """
    field_map = {
        'pe': 'PE_TTM',
        'pb': 'PB_MRQ',
        'ps': 'PS_TTM',
    }
    field = field_map.get(indicator.lower())
    if not field:
        _warn(f"不支持的指标: {indicator} (可用: pe/pb/ps)")
        return None

    period_pages = {
        'all': 2500, '全部': 2500,
        '10y': 2500, '近十年': 2500,
        '5y': 1250, '近五年': 1250,
        '3y': 750, '近三年': 750,
        '1y': 250, '近一年': 250,
    }
    page_size = period_pages.get(period, 2500)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://data.eastmoney.com/',
    }

    try:
        url = (
            f"https://datacenter-web.eastmoney.com/api/data/v1/get"
            f"?reportName=RPT_VALUEANALYSIS_DET"
            f"&columns=TRADE_DATE,{field},CLOSE_PRICE"
            f"&filter=(SECURITY_CODE=%22{code}%22)"
            f"&pageNumber=1&pageSize={page_size}"
            f"&sortColumns=TRADE_DATE&sortTypes=-1"
        )
        r = requests.get(url, headers=headers, timeout=15, proxies={'http': None, 'https': None})
        data = r.json()

        if not data.get('result') or not data['result'].get('data'):
            _warn(f"{code} {indicator} 东财估值数据为空")
            return None

        rows = data['result']['data']
        # 提取有效数值 (按时间正序)
        values = []
        dates = []
        for row in reversed(rows):
            v = row.get(field)
            if v is not None:
                values.append(float(v))
                dates.append(str(row.get('TRADE_DATE', ''))[:10])

        if not values:
            return None

        current = values[-1]
        vmin = min(values)
        vmax = max(values)
        vmedian = statistics.median(values)

        # 分位数: 当前值在历史中的位置
        below = sum(1 for v in values if v < current)
        percentile = below / len(values) * 100
        percentile = max(0.0, min(100.0, percentile))

        # 最近10个数据点
        history = [{'date': dates[i], 'value': values[i]}
                   for i in range(max(0, len(values)-10), len(values))]

        return {
            'current': round(current, 2),
            'percentile': round(percentile, 2),
            'min': round(vmin, 2),
            'max': round(vmax, 2),
            'median': round(vmedian, 2),
            'history': history,
        }
    except Exception as e:
        _warn(f"获取 {code} {indicator} 估值失败(东财): {e}")
        return None


def get_valuation_baidu(code: str, indicator: str = "pe", period: str = "all") -> dict:
    """
    获取个股估值指标及历史分位

    主源: 东方财富 datacenter (RPT_VALUEANALYSIS_DET)
    备用源: akshare stock_zh_valuation_baidu (百度)

    Parameters
    ----------
    code : str - 股票代码，纯数字如 "600519"
    indicator : str - 估值指标: "pe", "pb", "ps"
    period : str - 时间范围: "近一年", "近三年", "近五年", "近十年", "全部"

    Returns
    -------
    dict or None
        {'current': float, 'percentile': float, 'min': float,
         'max': float, 'median': float, 'history': list}
    """
    # 主源: 东方财富 datacenter
    result = _fetch_valuation_eastmoney(code, indicator, period)
    if result is not None:
        return result

    # 备用源: akshare 百度
    period_map = {
        "all": "全部", "1y": "近一年", "3y": "近三年",
        "5y": "近五年", "10y": "近十年",
    }
    period_cn = period_map.get(period, period)

    try:
        df = ak.stock_zh_valuation_baidu(
            symbol=code, indicator=indicator, period=period_cn
        )
        if df is None or df.empty:
            return None

        value_col = df.columns[-1]
        values = df[value_col].dropna().astype(float)
        if values.empty:
            return None

        current = float(values.iloc[-1])
        vmin = float(values.min())
        vmax = float(values.max())
        vmedian = float(values.median())

        if vmax - vmin > 0:
            percentile = (current - vmin) / (vmax - vmin) * 100
        else:
            percentile = 50.0
        percentile = max(0.0, min(100.0, percentile))

        history = []
        for _, row in df.tail(10).iterrows():
            history.append({
                'date': str(row.iloc[0]),
                'value': float(row[value_col]) if str(row[value_col]) != 'nan' else None,
            })

        return {
            'current': round(current, 2),
            'percentile': round(percentile, 2),
            'min': round(vmin, 2),
            'max': round(vmax, 2),
            'median': round(vmedian, 2),
            'history': history,
        }
    except Exception as e:
        _warn(f"获取 {code} {indicator} 估值失败(百度): {e}")
        return None


def _assess_percentile(percentile):
    """根据分位数给出评估标签"""
    if percentile is None:
        return "未知"
    if percentile < 30:
        return "低估"
    elif percentile <= 70:
        return "合理"
    else:
        return "偏高"


def get_stock_valuation(code: str) -> dict:
    """
    综合估值分析：PE/PB/PS 分位 + 筹码分布

    Parameters
    ----------
    code : str - 股票代码，纯数字如 "600519"

    Returns
    -------
    dict
        {'code': str, 'pe': dict|None, 'pb': dict|None,
         'ps': dict|None, 'chip': dict|None, 'assessment': str}
    """
    pe_data = get_valuation_baidu(code, indicator="pe")
    pb_data = get_valuation_baidu(code, indicator="pb")
    ps_data = get_valuation_baidu(code, indicator="ps")

    # 综合评估：以 PE 分位为主，PB 分位为辅
    pe_pct = pe_data['percentile'] if pe_data else None
    pb_pct = pb_data['percentile'] if pb_data else None

    if pe_pct is not None and pb_pct is not None:
        avg_pct = (pe_pct + pb_pct) / 2
        assessment = _assess_percentile(avg_pct)
        pe_label = _assess_percentile(pe_pct)
        pb_label = _assess_percentile(pb_pct)
        if pe_label != pb_label:
            assessment = f"{assessment}(PE{pe_label}/PB{pb_label})"
    elif pe_pct is not None:
        assessment = _assess_percentile(pe_pct)
    elif pb_pct is not None:
        assessment = _assess_percentile(pb_pct)
    else:
        assessment = "数据不足，无法评估"

    return {
        'code': code,
        'pe': pe_data,
        'pb': pb_data,
        'ps': ps_data,
        'chip': None,  # 筹码数据需额外获取
        'assessment': assessment,
    }


def _percentile_bar(percentile, label=""):
    """生成分位数进度条 示例: [===>      ] 32% (低估)"""
    if percentile is None:
        return "[N/A]"
    filled = int(percentile / 10)
    filled = max(0, min(10, filled))
    bar = "=" * filled + ">" if filled < 10 else "=" * 10
    bar = bar.ljust(10)
    text = f"[{bar}] {percentile:.0f}%"
    if label:
        text += f" ({label})"
    return text


def _marker(percentile):
    """根据分位数返回 ASCII 标记"""
    if percentile is None:
        return "[N/A]"
    if percentile < 30:
        return "[LOW]"
    elif percentile <= 70:
        return "[FAIR]"
    else:
        return "[HIGH]"


def format_valuation(result: dict) -> str:
    """
    格式化估值分析结果为纯文本

    Parameters
    ----------
    result : dict - get_stock_valuation() 的返回值

    Returns
    -------
    str - 格式化的文本报告
    """
    if not result:
        return "估值数据获取失败"

    lines = []
    code = result.get('code', '------')
    lines.append(f"{'=' * 50}")
    lines.append(f"  个股估值分析: {code}")
    lines.append(f"{'=' * 50}")
    lines.append("")

    # PE / PB / PS 估值
    for key, name in [('pe', 'PE(市盈率)'), ('pb', 'PB(市净率)'), ('ps', 'PS(市销率)')]:
        data = result.get(key)
        if data:
            pct = data['percentile']
            label = _assess_percentile(pct)
            marker = _marker(pct)
            lines.append(f"  {name}: {marker}")
            lines.append(f"    当前值: {data['current']}")
            lines.append(f"    分位数: {_percentile_bar(pct, label)}")
            lines.append(f"    最小值: {data['min']}  |  中位数: {data['median']}  |  最大值: {data['max']}")
            lines.append("")
        else:
            lines.append(f"  {name}: 数据获取失败")
            lines.append("")

    # 筹码分布
    chip = result.get('chip')
    lines.append(f"  {'─' * 44}")
    lines.append("  筹码分布:")
    if chip:
        lines.append(f"    平均成本: {chip['avg_cost']}")
        lines.append(f"    获利比例: {chip['profit_ratio']}%")
        lines.append(f"    90%筹码集中区间: {chip['concentration_90']}")
        lines.append(f"    70%筹码集中区间: {chip['concentration_70']}")
        lines.append(f"    成本上界: {chip['upper_bound']}  |  成本下界: {chip['lower_bound']}")
    else:
        lines.append("    筹码数据获取失败")
    lines.append("")

    # 综合评估
    assessment = result.get('assessment', '未知')
    lines.append(f"  {'─' * 44}")
    lines.append(f"  综合评估: {assessment}")
    lines.append(f"{'=' * 50}")

    return "\n".join(lines)
```
## §8 新闻资讯

### §8.1 新浪财经7x24

新浪财经 7x24 快讯接口，无需认证，直接 HTTP GET 请求。返回按时间排列的新闻列表，每条包含时间、标题、内容和来源。

```python
import requests
import re
from datetime import datetime

def get_sina_finance(page_size=30):
    """
    新浪财经 7x24 快讯

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '新浪财经'}]
    """
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    url = (
        f"https://feed.mix.sina.com.cn/api/roll/get"
        f"?pageid=153&lid=2516&k=&num={page_size}&page=1"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=10)
    data = r.json()

    items = data.get('result', {}).get('data', []) or []
    rows = []
    for item in items:
        ts = int(item.get('ctime', 0) or 0)
        time_str = ''
        if ts:
            time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

        title = item.get('title', '') or ''
        content = item.get('intro', '') or item.get('summary', '') or title
        content = re.sub(r'<[^>]+>', '', content)

        rows.append({
            'time': time_str,
            'title': re.sub(r'<[^>]+>', '', title),
            'content': content[:300],
            'source': '新浪财经',
        })

    return rows
```

### §8.2 东财7x24

东方财富 7x24 快讯备用接口。当新浪接口不稳定时可使用此源。

```python
import requests

def get_eastmoney_7x24(page_size=50):
    """
    东方财富 7x24 快讯 (备用，可能不稳定)

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': '东财7x24'}]
    """
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    url = (
        f"https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
        f"?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize={page_size}"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=10)
    data = r.json()

    items = data.get('data', []) or []
    rows = []
    for item in items:
        rows.append({
            'time': item.get('showTime', '') or item.get('pubTime', ''),
            'title': item.get('title', ''),
            'content': item.get('digest', '') or item.get('content', ''),
            'source': '东财7x24',
        })

    return rows
```

### §8.3 东财搜索

东方财富文章搜索接口，使用 JSONP 格式返回。支持关键词搜索财经文章，返回标题、内容摘要和链接。

```python
import requests
import json
import re
import urllib.parse

def get_eastmoney_search(keyword, count=10):
    """
    东方财富搜索 (JSONP 格式)

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'url': ..., 'source': '东方财富'}]
    """
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    param = json.dumps({
        "uid": "",
        "keyword": keyword,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": "default",
                "pageIndex": 1,
                "pageSize": count,
                "preTag": "",
                "postTag": "",
            }
        }
    })
    url = f"https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param={urllib.parse.quote(param)}"

    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=10)
    text = r.text

    # 解析 JSONP: jQuery({...})
    m = re.search(r'jQuery\((.*)\)', text, re.DOTALL)
    if not m:
        return []

    data = json.loads(m.group(1))
    result = data.get('result', None)
    if result is None or not isinstance(result, dict):
        return []
    cms = result.get('cmsArticleWebOld', None)
    if cms is None or not isinstance(cms, dict):
        return []
    articles = cms.get('list', []) or []

    rows = []
    for item in articles:
        title = item.get('title', '')
        title = re.sub(r'<[^>]+>', '', title)
        content = item.get('content', '') or item.get('mediaName', '')
        content = re.sub(r'<[^>]+>', '', content)

        rows.append({
            'time': item.get('date', ''),
            'title': title,
            'content': content[:200],
            'url': item.get('url', ''),
            'source': '东方财富',
        })

    return rows
```

### §8.4 新闻聚合

聚合新浪财经和东财7x24两个新闻源，按时间降序排序后统一返回。

```python
import requests
import re
from datetime import datetime

def get_sina_finance(page_size=30):
    """新浪财经 7x24 快讯（同上 §8.1）"""
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    url = (
        f"https://feed.mix.sina.com.cn/api/roll/get"
        f"?pageid=153&lid=2516&k=&num={page_size}&page=1"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=10)
    data = r.json()
    items = data.get('result', {}).get('data', []) or []
    rows = []
    for item in items:
        ts = int(item.get('ctime', 0) or 0)
        time_str = ''
        if ts:
            time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        title = item.get('title', '') or ''
        content = item.get('intro', '') or item.get('summary', '') or title
        content = re.sub(r'<[^>]+>', '', content)
        rows.append({
            'time': time_str,
            'title': re.sub(r'<[^>]+>', '', title),
            'content': content[:300],
            'source': '新浪财经',
        })
    return rows

def get_eastmoney_7x24(page_size=50):
    """东财 7x24 快讯（同上 §8.2）"""
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    url = (
        f"https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
        f"?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize={page_size}"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=10)
    data = r.json()
    items = data.get('data', []) or []
    rows = []
    for item in items:
        rows.append({
            'time': item.get('showTime', '') or item.get('pubTime', ''),
            'title': item.get('title', ''),
            'content': item.get('digest', '') or item.get('content', ''),
            'source': '东财7x24',
        })
    return rows

def get_all_news(keyword=None, page_size=30):
    """
    聚合所有新闻源

    Returns
    -------
    list of dict: [{'time': ..., 'title': ..., 'content': ..., 'source': ...}]
    按时间降序排序
    """
    results = []

    for name, fn in [('新浪财经', get_sina_finance), ('东财7x24', get_eastmoney_7x24)]:
        try:
            items = fn(page_size=page_size)
            results.extend(items)
        except Exception:
            pass

    results.sort(key=lambda x: x.get('time', ''), reverse=True)
    return results
```

### §8.5 华尔街见闻快讯

华尔街见闻全球 7x24 快讯，支持多频道（A股/美股/港股/外汇/商品/黄金/原油/债券/加密货币）。数据源 `api-one-wscn.awtmt.com`。

```python
import requests
import re
from typing import List, Dict
from datetime import datetime

_BASE_URL = "https://api-one-wscn.awtmt.com/apiv1"

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Referer': 'https://wallstreetcn.com/',
    'Accept': 'application/json',
    'x-client-type': 'pc',
    'x-ivanka-app': 'wscn|web|0.40.40|0.0|0',
}

# 频道映射
CHANNELS = {
    'global-channel': '全球7x24',
    'a-stock-channel': 'A股',
    'us-stock-channel': '美股',
    'hk-stock-channel': '港股',
    'forex-channel': '外汇',
    'commodity-channel': '商品',
    'goldc-channel': '黄金',
    'oil-channel': '原油',
    'bond-channel': '债券',
    'crypto-channel': '加密货币',
    'xgb-channel': '新股',
}

def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()

def get_lives(channel: str = 'global-channel', limit: int = 20) -> List[Dict]:
    """
    获取华尔街见闻快讯

    参数:
        channel: 频道名（见 CHANNELS）
        limit: 获取条数（最大50）

    返回:
        [{'title': 标题, 'content': 内容, 'time': 时间戳, 'uri': 链接,
          'source': 来源, 'is_important': 是否重要}, ...]
    """
    if channel not in CHANNELS:
        channel = 'global-channel'

    limit = max(1, min(limit, 50))

    url = f"{_BASE_URL}/content/lives"
    params = {
        'channel': channel,
        'client': 'pc',
        'limit': str(limit),
        'first_page': 'true',
        'accept': 'live,vip-live',
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取华尔街见闻快讯失败: {e}")
        return []

    if data.get('code') != 20000:
        print(f"  [WARN] 接口返回异常: code={data.get('code')}, msg={data.get('message')}")
        return []

    items = data.get('data', {}).get('items', [])
    results = []

    for item in items:
        content = _safe_str(item.get('content_text'))
        if not content:
            content = _safe_str(item.get('content'))
            content = re.sub(r'<[^>]+>', '', content).strip()

        if not content:
            continue

        display_time = item.get('display_time', 0)
        time_str = datetime.fromtimestamp(display_time).strftime('%Y-%m-%d %H:%M:%S') if display_time else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'content': content,
            'time': display_time,
            'time_str': time_str,
            'uri': _safe_str(item.get('uri')),
            'source': f"华尔街见闻-{CHANNELS.get(channel, '全球')}",
            'is_important': item.get('score', 0) > 1 or item.get('is_calendar', False),
            'author': _safe_str((item.get('author') or {}).get('display_name')),
        })

    return results

def format_lives(results: List[Dict], channel: str = 'global-channel') -> str:
    """格式化快讯输出"""
    if not results:
        return "未获取到华尔街见闻快讯"

    channel_name = CHANNELS.get(channel, '全球')
    lines = [
        "=" * 70,
        f"  华尔街见闻快讯 - {channel_name}",
        "=" * 70,
    ]

    for i, item in enumerate(results, 1):
        marker = "🔴" if item.get('is_important') else "  "
        title = item.get('title', '')
        content = item.get('content', '')

        if title:
            lines.append(f"\n{marker} [{item.get('time_str', '')}] {title}")
        if content:
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"   {content}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
```

### §8.6 华尔街见闻财经日历

财经日历接口，获取全球经济数据发布时间表，包含实际值、预测值、前值对比。

```python
import requests
from typing import List, Dict
from datetime import datetime

_BASE_URL = "https://api-one-wscn.awtmt.com/apiv1"

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Referer': 'https://wallstreetcn.com/',
    'Accept': 'application/json',
    'x-client-type': 'pc',
    'x-ivanka-app': 'wscn|web|0.40.40|0.0|0',
}

CHANNELS = {
    'global-channel': '全球7x24',
    'a-stock-channel': 'A股',
    'us-stock-channel': '美股',
    'hk-stock-channel': '港股',
    'forex-channel': '外汇',
    'commodity-channel': '商品',
    'goldc-channel': '黄金',
    'oil-channel': '原油',
    'bond-channel': '债券',
    'crypto-channel': '加密货币',
    'xgb-channel': '新股',
}

def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()

def get_calendar(channel: str = 'global-channel', limit: int = 20) -> List[Dict]:
    """
    获取财经日历

    参数:
        channel: 频道名
        limit: 获取条数

    返回:
        [{'title': 事件, 'country': 国家, 'time': 时间, 'importance': 重要性,
          'actual': 实际值, 'forecast': 预测值, 'previous': 前值}, ...]
    """
    if channel not in CHANNELS:
        channel = 'global-channel'

    url = f"{_BASE_URL}/calendar"
    params = {
        'channel': channel,
        'client': 'pc',
        'limit': str(limit),
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取财经日历失败: {e}")
        return []

    if data.get('code') != 20000:
        return []

    items = data.get('data', {}).get('items', [])
    results = []

    for item in items:
        pub_date = item.get('public_date', 0)
        time_str = datetime.fromtimestamp(pub_date).strftime('%Y-%m-%d %H:%M') if pub_date else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'event': _safe_str(item.get('event')),
            'country': _safe_str(item.get('country')),
            'time': pub_date,
            'time_str': time_str,
            'importance': item.get('importance', 0),
            'actual': _safe_str(item.get('actual')),
            'forecast': _safe_str(item.get('forecast')),
            'previous': _safe_str(item.get('previous')),
            'period': _safe_str(item.get('period')),
        })

    return results

def format_calendar(results: List[Dict]) -> str:
    """格式化财经日历输出"""
    if not results:
        return "未获取到财经日历数据"

    lines = [
        "=" * 80,
        "  财经日历",
        "=" * 80,
        f"  {'时间':<16} {'国家':<6} {'事件':<20} {'重要性':<6} {'实际':<10} {'预测':<10} {'前值':<10}",
        "-" * 80,
    ]

    for item in results:
        imp = "⭐" * item.get('importance', 0)
        lines.append(
            f"  {item.get('time_str', ''):<16} "
            f"{item.get('country', ''):<6} "
            f"{item.get('title', '')[:18]:<20} "
            f"{imp:<6} "
            f"{item.get('actual', '-'):<10} "
            f"{item.get('forecast', '-'):<10} "
            f"{item.get('previous', '-'):<10}"
        )

    lines.append("=" * 80)
    return "\n".join(lines)
```

---

## §9 研报/公告/互动易

### §9.1 个股研报

从东财 `reportapi.eastmoney.com` 获取个股研究报告，支持指定时间范围和数量。返回研报标题、机构、评级、作者等信息。

```python
import requests
from typing import List, Dict
from datetime import datetime, timedelta

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
}

def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()

def _normalize_code(stock_code: str) -> str:
    """提取纯数字代码"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    code = code.replace('gb_', '').replace('us', '').replace('us_', '')
    if '.' in code:
        code = code.split('.')[0]
    return code

def get_research_reports(stock_code: str, days: int = 30, page_size: int = 10) -> List[Dict]:
    """
    获取个股研究报告

    参数:
        stock_code: 股票代码
        days: 最近N天
        page_size: 每页条数

    返回:
        [{'title': 研报标题, 'org': 机构, 'date': 日期, 'rating': 评级,
          'author': 作者, 'info_code': 研报编码}, ...]
    """
    code = _normalize_code(stock_code)
    begin_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    url = "https://reportapi.eastmoney.com/report/list2"
    headers = {
        **_HEADERS,
        'Host': 'reportapi.eastmoney.com',
        'Origin': 'https://data.eastmoney.com',
        'Referer': 'https://data.eastmoney.com/report/stock.jshtml',
        'Content-Type': 'application/json',
    }

    payload = {
        'code': code,
        'industryCode': '*',
        'beginTime': begin_date,
        'endTime': end_date,
        'pageNo': 1,
        'pageSize': page_size,
        'p': 1,
        'pageNum': 1,
        'pageNumber': 1,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取研报失败: {e}")
        return []

    hits = data.get('data', [])
    results = []

    for item in hits:
        results.append({
            'title': _safe_str(item.get('title')),
            'org': _safe_str(item.get('orgSName')),
            'date': _safe_str(item.get('publishDate'))[:10],
            'rating': _safe_str(item.get('ratingName')),
            'author': _safe_str(item.get('researcher')),
            'info_code': _safe_str(item.get('infoCode')),
            'industry': _safe_str(item.get('industryName')),
        })

    return results

def format_research_reports(results: List[Dict], stock_code: str) -> str:
    """格式化研报输出"""
    if not results:
        return f"未获取到 {stock_code} 的研究报告"

    lines = [
        "=" * 75,
        f"  个股研究报告: {stock_code} (最近{len(results)}篇)",
        "=" * 75,
    ]

    for i, item in enumerate(results, 1):
        rating = item.get('rating', '')
        rating_str = f" [{rating}]" if rating else ""
        lines.append(f"\n  {i}. {item.get('title', 'N/A')}{rating_str}")
        lines.append(f"     {item.get('org', 'N/A')} | {item.get('author', 'N/A')} | {item.get('date', 'N/A')}")

    lines.append("\n" + "=" * 75)
    return "\n".join(lines)
```

### §9.2 上市公司公告

从东财公告接口 `np-anotice-stock.eastmoney.com` 获取上市公司公告，支持多只股票同时查询。

```python
import requests
from typing import List, Dict

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
}

def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()

def _normalize_code(stock_code: str) -> str:
    """提取纯数字代码"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    code = code.replace('gb_', '').replace('us', '').replace('us_', '')
    if '.' in code:
        code = code.split('.')[0]
    return code

def get_stock_notices(stock_code: str, page_size: int = 20) -> List[Dict]:
    """
    获取上市公司公告

    参数:
        stock_code: 股票代码（支持多只，逗号分隔）
        page_size: 每页条数

    返回:
        [{'title': 公告标题, 'date': 公告日期, 'type': 公告类型}, ...]
    """
    codes = [_normalize_code(c) for c in stock_code.split(',')]
    stock_list = ','.join(codes)

    url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    params = {
        'page_size': str(page_size),
        'page_index': '1',
        'ann_type': 'SHA,CYB,SZA,BJA,INV',
        'client_source': 'web',
        'f_node': '0',
        'stock_list': stock_list,
    }
    headers = {
        **_HEADERS,
        'Host': 'np-anotice-stock.eastmoney.com',
        'Referer': 'https://data.eastmoney.com/notices/hsa/5.html',
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取公告失败: {e}")
        return []

    items = data.get('data', {}).get('list', [])
    results = []

    for item in items:
        columns = item.get('columns', [{}])
        col_name = columns[0].get('column_name', '') if columns else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'date': _safe_str(item.get('notice_date'))[:10],
            'type': col_name,
            'art_code': _safe_str(item.get('art_code')),
        })

    return results

def format_stock_notices(results: List[Dict], stock_code: str) -> str:
    """格式化公告输出"""
    if not results:
        return f"未获取到 {stock_code} 的公告"

    lines = [
        "=" * 75,
        f"  上市公司公告: {stock_code}",
        "=" * 75,
        f"  {'日期':<12} {'类型':<10} {'公告标题'}",
        "-" * 75,
    ]

    for item in results:
        lines.append(f"  {item.get('date', 'N/A'):<12} {item.get('type', 'N/A'):<10} {item.get('title', 'N/A')}")

    lines.append("=" * 75)
    return "\n".join(lines)
```

### §9.3 互动易问答

从巨潮资讯网互动易平台 `irm.cninfo.com.cn` 获取投资者问答数据，支持关键词搜索。

```python
import requests
import time
from typing import List, Dict

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
}

def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()

def get_interactive_answers(keyword: str = '', page: int = 1, page_size: int = 20) -> List[Dict]:
    """
    获取互动易数据（投资者互动平台）

    参数:
        keyword: 搜索关键词（股票代码或公司名）
        page: 页码
        page_size: 每页条数

    返回:
        [{'question': 问题, 'answer': 回答, 'company': 公司, 'date': 日期}, ...]
    """
    url = f"https://irm.cninfo.com.cn/newircs/index/search?_t={int(time.time())}"
    headers = {
        **_HEADERS,
        'Host': 'irm.cninfo.com.cn',
        'Origin': 'https://irm.cninfo.com.cn',
        'Referer': 'https://irm.cninfo.com.cn/views/interactiveAnswer',
        'handleError': 'true',
    }
    form_data = {
        'pageNo': str(page),
        'pageSize': str(page_size),
        'searchTypes': '11',
        'highLight': 'true',
        'keyWord': keyword,
    }

    try:
        resp = requests.post(url, data=form_data, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取互动易数据失败: {e}")
        return []

    rows = data.get('results', [])
    results = []

    for item in rows:
        results.append({
            'question': _safe_str(item.get('mainContent')),
            'answer': _safe_str(item.get('attachedContent')),
            'company': _safe_str(item.get('companyShortName')),
            'code': _safe_str(item.get('stockCode')),
            'date': _safe_str(item.get('pubDate'))[:10],
            'answer_date': _safe_str(item.get('attachedPubDate'))[:10],
        })

    return results

def format_interactive_answers(results: List[Dict], keyword: str) -> str:
    """格式化互动易输出"""
    if not results:
        return f"未获取到互动易数据 (关键词: {keyword})"

    lines = [
        "=" * 75,
        f"  互动易数据 (关键词: {keyword})",
        "=" * 75,
    ]

    for i, item in enumerate(results, 1):
        q = item.get('question', '')
        a = item.get('answer', '')
        if len(q) > 100:
            q = q[:100] + "..."
        if len(a) > 150:
            a = a[:150] + "..."

        lines.append(f"\n  {i}. [{item.get('company', 'N/A')}] {item.get('date', 'N/A')}")
        lines.append(f"     问: {q}")
        lines.append(f"     答: {a}")

    lines.append("\n" + "=" * 75)
    return "\n".join(lines)
```

---

## §10 PanWatch数据

### §10.1 热门股票

东财 push2 clist 热门股票排行，支持按成交额、涨幅、跌幅排序。

```python
import requests
import sys

def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _normalize_diff(data):
    """东财 clist diff 可能是 dict(index 为 key) 或 list。统一成 list。"""
    diff = ((data or {}).get("data") or {}).get("diff") or []
    if isinstance(diff, dict):
        return list(diff.values())
    return diff

def get_hot_stocks(mode: str = "turnover", limit: int = 20) -> list:
    """
    A股热门股票排行 (东财 push2 clist)

    Parameters
    ----------
    mode : str - 'turnover' 按成交额, 'gainers' 按涨幅, 'losers' 按跌幅
    limit : int - 返回数量 (最大 100)
    """
    fid = "f6" if mode == "turnover" else "f3"
    if mode == "losers":
        fid = "f3"

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "volume": _safe_float(it.get("f5"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "amplitude": _safe_float(it.get("f7"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_hot_stocks failed: {e}", file=sys.stderr)
        return []
```

### §10.2 热门板块

东财 push2 clist 板块排行，支持涨幅榜、成交额榜、跌幅榜。

```python
import requests
import sys

def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _normalize_diff(data):
    diff = ((data or {}).get("data") or {}).get("diff") or []
    if isinstance(diff, dict):
        return list(diff.values())
    return diff

def get_hot_boards(mode: str = "gainers", limit: int = 12) -> list:
    """
    A股热门板块排行 (东财 push2 clist)

    Parameters
    ----------
    mode : str - 'gainers' 涨幅榜, 'turnover' 成交额榜, 'losers' 跌幅榜
    limit : int - 返回数量
    """
    fid = "f3" if mode in ("gainers", "losers") else "f6"
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": "m:90+t:2",
        "fields": "f12,f14,f2,f3,f4,f6,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_hot_boards failed: {e}", file=sys.stderr)
        return []
```

### §10.3 板块成分股

查询某个东财板块的成分股数据，使用板块代码（如 `BK0892`）查询。

```python
import requests
import sys

def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _normalize_diff(data):
    diff = ((data or {}).get("data") or {}).get("diff") or []
    if isinstance(diff, dict):
        return list(diff.values())
    return diff

def get_board_stocks(board_code: str, mode: str = "gainers", limit: int = 20) -> list:
    """
    查询某个东财板块的成分股 (东财 push2 clist)

    Parameters
    ----------
    board_code : str - 东财板块代码, 如 'BK0892'
    mode : str - 'gainers' 涨幅, 'turnover' 成交额
    limit : int - 返回数量
    """
    fid = "f3" if mode in ("gainers", "losers") else "f6"
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": f"b:{board_code}",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "volume": _safe_float(it.get("f5"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "amplitude": _safe_float(it.get("f7"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_board_stocks failed: {e}", file=sys.stderr)
        return []
```

### §10.4 资金流向细分

东财 push2his 个股资金流向细分，获取超大单/大单/中单/小单净流入数据，以及5日主力净流入汇总。

```python
import requests
import time

def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _cn_exchange_prefix(code: str) -> str:
    """sh / sz / bj"""
    if code.startswith("920") or code.startswith(("83", "87", "88")):
        return "bj"
    if code.startswith(("5", "6")) or code.startswith("900"):
        return "sh"
    return "sz"

def get_capital_flow_detail(code: str) -> dict:
    """
    获取个股资金流向细分 (东财 push2his fflow)

    Returns
    -------
    {
        'code': '600519',
        'name': '贵州茅台',
        'main_net_inflow': 123456789.0,    # 主力净流入 (超大+大单)
        'main_net_inflow_pct': 5.2,        # 主力净流入占比 (%)
        'super_net_inflow': 98765432.0,    # 超大单净流入
        'big_net_inflow': 24691357.0,      # 大单净流入
        'mid_net_inflow': -12345678.0,     # 中单净流入
        'small_net_inflow': -111111111.0,  # 小单净流入
        'main_net_5d': 999999999.0,        # 5日主力净流入
    }
    """
    code = code.replace("sh", "").replace("sz", "").replace(".", "")
    prefix = _cn_exchange_prefix(code)
    secid = f"{1 if prefix == 'sh' else 0}.{code}"

    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "lmt": "0",
        "klt": "101",
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "_": int(time.time() * 1000),
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        d = data.get("data")
        if not d:
            return None
        klines = d.get("klines", [])
        if not klines:
            return None

        # 最新一天
        last = str(klines[-1]).split(",")
        if len(last) < 13:
            return None

        # 最近5日主力净流入求和
        main_net_5d = 0.0
        for line in klines[-5:]:
            parts = str(line).split(",")
            if len(parts) >= 2:
                main_net_5d += _safe_float(parts[1])

        return {
            "code": str(d.get("code") or code),
            "name": str(d.get("name") or ""),
            "main_net_inflow": _safe_float(last[1]),
            "main_net_inflow_pct": _safe_float(last[6]),
            "super_net_inflow": _safe_float(last[5]),
            "big_net_inflow": _safe_float(last[4]),
            "mid_net_inflow": _safe_float(last[3]),
            "small_net_inflow": _safe_float(last[2]),
            "main_net_5d": main_net_5d,
        }
    except Exception:
        return None

def format_capital_flow(data: dict) -> str:
    """资金流向细分格式化"""
    if not data:
        return "资金流向数据获取失败"

    def _fmt_money(v: float) -> str:
        if abs(v) >= 1e8:
            return f"{v/1e8:.2f}亿"
        return f"{v/1e4:.2f}万"

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  资金流向细分: {data.get('code', '')} {data.get('name', '')}")
    lines.append(f"{'='*60}")
    main = data.get("main_net_inflow", 0)
    main_pct = data.get("main_net_inflow_pct", 0)
    status = "主力流入" if main > 0 else "主力流出"
    lines.append(f"  主力净流入: {_fmt_money(main)} ({main_pct:+.2f}%)  [{status}]")
    lines.append(f"  超大单: {_fmt_money(data.get('super_net_inflow', 0))}")
    lines.append(f"  大单:   {_fmt_money(data.get('big_net_inflow', 0))}")
    lines.append(f"  中单:   {_fmt_money(data.get('mid_net_inflow', 0))}")
    lines.append(f"  小单:   {_fmt_money(data.get('small_net_inflow', 0))}")
    lines.append(f"  5日主力净流入: {_fmt_money(data.get('main_net_5d', 0))}")
    lines.append(f"{'='*60}")
    return "\n".join(lines)
```

### §10.5 基本面快照

腾讯 `qt.gtimg.cn` 个股基本面快照，获取 PE/PB/市值等核心估值指标。

```python
import requests

def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _cn_exchange_prefix(code: str) -> str:
    """sh / sz / bj"""
    if code.startswith("920") or code.startswith(("83", "87", "88")):
        return "bj"
    if code.startswith(("5", "6")) or code.startswith("900"):
        return "sh"
    return "sz"

def get_fundamentals_snapshot(code: str) -> dict:
    """
    腾讯 qt.gtimg.cn 个股基本面快照 (PE/PB/市值)

    Returns
    -------
    {
        'code': '600519',
        'name': '贵州茅台',
        'pe_ttm': 19.77,
        'pe_static': 21.34,
        'pb': 6.04,
        'total_market_value': 16351.07,       # 亿元
        'circulating_market_value': 16351.07,  # 亿元
    }
    """
    code = code.replace("sh", "").replace("sz", "").replace(".", "")
    prefix = _cn_exchange_prefix(code)
    tencent_code = f"{prefix}{code}"
    url = f"https://qt.gtimg.cn/q={tencent_code}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10,
                         proxies={"http": None, "https": None})
        r.encoding = "gbk"
        text = r.text
        if '=""' in text or not text.strip():
            return None

        # 解析 ~ 分隔数组
        _, value = text.split('="', 1)
        parts = value.rstrip('";\n').split("~")
        if len(parts) < 3:
            return None

        symbol = parts[2]
        if "." in symbol and not symbol.startswith("."):
            symbol = symbol.split(".")[0]

        name = parts[1] if len(parts) > 1 else ""
        pe_ttm = _safe_float(parts[39]) if len(parts) > 39 else None
        circ_mv = _safe_float(parts[44]) if len(parts) > 45 else None
        total_mv = _safe_float(parts[45]) if len(parts) > 45 else None
        pb = _safe_float(parts[46]) if len(parts) > 46 else None
        pe_static = _safe_float(parts[52]) if len(parts) > 52 else None

        return {
            "code": symbol,
            "name": name,
            "pe_ttm": pe_ttm,
            "pe_static": pe_static,
            "pb": pb,
            "total_market_value": total_mv,
            "circulating_market_value": circ_mv,
        }
    except Exception:
        return None

def format_fundamentals(data: dict) -> str:
    """基本面快照格式化"""
    if not data:
        return "基本面数据获取失败"
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  基本面快照: {data.get('code', '')} {data.get('name', '')}")
    lines.append(f"{'='*60}")
    lines.append(f"  PE(TTM): {data.get('pe_ttm')}")
    lines.append(f"  PE(静态): {data.get('pe_static')}")
    lines.append(f"  PB:      {data.get('pb')}")
    total = data.get('total_market_value')
    circ = data.get('circulating_market_value')
    if total is not None:
        lines.append(f"  总市值: {total:.2f} 亿")
    if circ is not None:
        lines.append(f"  流通市值: {circ:.2f} 亿")
    lines.append(f"{'='*60}")
    return "\n".join(lines)
```

---

## §10.6 东财数据中心（龙虎榜/融资融券/大宗/股东/解禁）

通用 datacenter-web 查询基础函数，所有数据中心接口共用。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []
```

### §10.6.1 龙虎榜

龙虎榜每日明细，包含营业部买卖金额、涨跌幅、上榜原因等。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []

def get_lhb_data(days=5, limit=30):
    """
    龙虎榜

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'close': ..., 'chg_pct': ...,
                    'reason': ..., 'net_buy': ..., 'buy_total': ..., 'sell_total': ...}]
    """
    records = _dc_get('RPT_DAILYBILLBOARD_DETAILSNEW',
                      page_size=limit, sort_columns='TRADE_DATE')

    rows = []
    for r in records:
        rows.append({
            'date': (r.get('TRADE_DATE', '') or '')[:10],
            'code': r.get('SECURITY_CODE', ''),
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'close': float(r.get('CLOSE_PRICE', 0) or 0),
            'chg_pct': float(r.get('CHANGE_RATE', 0) or 0),
            'reason': r.get('EXPLANATION', ''),
            'net_buy': float(r.get('BILLBOARD_NET_AMT', 0) or 0) / 10000,
            'buy_total': float(r.get('BILLBOARD_BUY_AMT', 0) or 0) / 10000,
            'sell_total': float(r.get('BILLBOARD_SELL_AMT', 0) or 0) / 10000,
        })

    return rows
```

### §10.6.2 融资融券

融资融券每日汇总，按日期聚合全市场融资余额、融券余额等数据。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []

def get_margin_data(days=30):
    """
    融资融券汇总

    Returns
    -------
    list of dict: [{'date': ..., 'rzye': 融资余额, 'rzmre': 融资买入额,
                    'rzche': 融资偿还额, 'rqye': 融券余额, 'rqmcl': 融券卖出量,
                    'rzrqye': 融资融券余额}, ...]
    """
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    records = _dc_get('RPTA_WEB_RZRQ_GGMX',
                      filter_str=f"(TRADE_DATE>='{start}')(TRADE_DATE<='{end}')",
                      page_size=days, sort_columns='TRADE_DATE')

    # 按日期汇总
    date_map = {}
    for r in records:
        date = (r.get('TRADE_DATE', '') or '')[:10]
        if date not in date_map:
            date_map[date] = {
                'date': date,
                'rzye': 0, 'rzmre': 0, 'rzche': 0,
                'rqye': 0, 'rqmcl': 0, 'rzrqye': 0,
            }
        d = date_map[date]
        d['rzye'] += float(r.get('RZYE', 0) or 0)
        d['rzmre'] += float(r.get('RZMRE', 0) or 0)
        d['rzche'] += float(r.get('RZCHE', 0) or 0)
        d['rqye'] += float(r.get('RQYE', 0) or 0)
        d['rqmcl'] += float(r.get('RQMCL', 0) or 0)
        d['rzrqye'] += float(r.get('RZRQYE', 0) or 0)

    return list(date_map.values())
```

### §10.6.3 大宗交易

大宗交易明细，包含成交价格、成交量、买方/卖方营业部信息。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []

def get_block_trade(code='', limit=20):
    """
    大宗交易

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'price': ...,
                    'vol': ..., 'amount': ..., 'buyer': ..., 'seller': ...}]
    """
    records = _dc_get('RPT_DATA_OCCURTRADE', page_size=limit, sort_columns='TRADE_DATE')

    rows = []
    for r in records:
        stock_code = r.get('SECURITY_CODE', '')
        if code and stock_code != code:
            continue
        rows.append({
            'date': (r.get('TRADE_DATE', '') or '')[:10],
            'code': stock_code,
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'price': float(r.get('DEAL_PRICE', 0) or 0),
            'vol': float(r.get('DEAL_VOLUME', 0) or 0),
            'amount': float(r.get('DEAL_AMOUNT', 0) or 0),
            'buyer': r.get('BUYER_NAME', ''),
            'seller': r.get('SELLER_NAME', ''),
        })

    return rows
```

### §10.6.4 股东人数

查询个股股东人数变化趋势，自动计算环比变动和变动百分比。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []

def get_holder_num(code):
    """
    股东人数

    Returns
    -------
    list of dict: [{'date': ..., 'holder_num': ..., 'change': ..., 'change_pct': ...}]
    """
    records = _dc_get('RPT_HOLDERNUMLATEST',
                      filter_str=f'(SECURITY_CODE="{code}")',
                      page_size=10, sort_columns='END_DATE')

    rows = []
    prev_num = None
    for r in records:
        num = float(r.get('HOLDER_NUM', 0) or 0)
        change = num - prev_num if prev_num else 0
        change_pct = round(change / prev_num * 100, 2) if prev_num else 0
        rows.append({
            'date': (r.get('END_DATE', '') or '')[:10],
            'holder_num': int(num),
            'change': int(change),
            'change_pct': change_pct,
        })
        prev_num = num

    return rows
```

### §10.6.5 限售解禁

限售股解禁明细，包含解禁日期、解禁数量、解禁市值。

```python
import requests
from datetime import datetime, timedelta

_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}

def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []

def get_locked_shares(code='', limit=20):
    """
    限售解禁

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'count': ..., 'market_value': ...}]
    """
    records = _dc_get('RPT_LIFT_STAGE', page_size=limit, sort_columns='FREE_DATE')

    rows = []
    for r in records:
        stock_code = r.get('SECURITY_CODE', '')
        if code and stock_code != code:
            continue
        rows.append({
            'date': (r.get('FREE_DATE', '') or '')[:10],
            'code': stock_code,
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'count': float(r.get('FREE_NUM', 0) or 0),
            'market_value': float(r.get('MARKET_CAP', 0) or 0),
        })

    return rows
```
## §11 广发MCP数据

### §11.1 MCP通用调用

广发证券 MCP 端点 (`mcp-api.gf.com.cn`) 采用 **JSON-RPC 2.0** 协议，通过 **Bearer Token** 鉴权。所有数据接口（ETF排行、龙虎榜、指数估值、财务对比等）均通过 `_mcp_call()` 统一调度，F10 扩展信息则走独立的 REST 接口 `_f10_call()`。

```python
"""
广发证券 MCP 数据接口适配层
端点: mcp-api.gf.com.cn (streamableHttp, JSON-RPC 2.0)
鉴权: Bearer token (GF_SKILLS_APIKEY)
"""

import json
import os
from typing import Dict, Optional

try:
    import requests
except ImportError:
    requests = None

# ── 配置 ──────────────────────────────────────────────────────

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_F10_URL = "https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call"
_TIMEOUT = 30

# 从环境变量或 config.yaml 读取
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def set_api_key(key: str):
    """运行时设置 API Key"""
    global _API_KEY
    _API_KEY = key


# ── MCP 通用调用 ──────────────────────────────────────────────

def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """
    调用广发 MCP 端点

    参数:
        server: 服务名 (etf_rank / lhb / quant / windmill)
        tool: 工具名
        arguments: 参数字典

    返回:
        解析后的内层 JSON (result.content[0].text 二次解析)
    """
    if not _API_KEY:
        print("  [ERROR] 未设置 GF_SKILLS_APIKEY，请配置广发API密钥")
        return None

    if requests is None:
        print("  [ERROR] requests 库未安装")
        return None

    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }

    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()

        result = outer.get("result")
        if result is None:
            err = outer.get("error", {})
            print(f"  [ERROR] MCP返回错误: {err}")
            return None

        content = result.get("content", [])
        if not content:
            return None

        inner_text = content[0].get("text", "")
        if not inner_text:
            return None

        return json.loads(inner_text)

    except requests.exceptions.Timeout:
        print(f"  [ERROR] 广发MCP超时 ({server}/{tool})")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] 广发MCP连接失败 ({server}/{tool})")
        return None
    except json.JSONDecodeError as e:
        print(f"  [ERROR] 广发MCP响应解析失败: {e}")
        return None
    except Exception as e:
        print(f"  [ERROR] 广发MCP调用异常: {e}")
        return None


def _f10_call(service_name: str, tool_name: str, args: Dict) -> Optional[Dict]:
    """调用广发 F10 REST API (非MCP协议)"""
    if not _API_KEY:
        print("  [ERROR] 未设置 GF_SKILLS_APIKEY")
        return None

    if requests is None:
        print("  [ERROR] requests 库未安装")
        return None

    payload = {
        "service_name": service_name,
        "tool_name": tool_name,
        "args": args,
    }

    try:
        resp = requests.post(_F10_URL, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        d = resp.json()
        if d.get("retcode") != 0:
            print(f"  [ERROR] F10 API错误: {d.get('msg', 'unknown')}")
            return None
        return d.get("data", {}).get("data")
    except Exception as e:
        print(f"  [ERROR] F10 API异常: {e}")
        return None


def _normalize_gf_code(stock_code: str) -> str:
    """转换为广发格式 SH600519 / SZ000858"""
    code = stock_code.strip()
    if code.startswith(("sh", "SH")):
        return "SH" + code[2:]
    if code.startswith(("sz", "SZ")):
        return "SZ" + code[2:]
    if code.isdigit() and len(code) == 6:
        return ("SH" if code.startswith(("6", "9")) else "SZ") + code
    return code
```

---

### §11.2 ETF排行榜

支持 **13 种榜单**：涨幅/跌幅/换手/主力资金/搜索/关注/5日涨幅/5日跌幅/连涨/连跌/5日主力资金/净申购/溢价率。

```python
"""ETF排行榜 — 广发MCP数据"""

import json
import os
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_TIMEOUT = 30
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """MCP JSON-RPC 2.0 通用调用（参见§11.1）"""
    if not _API_KEY or requests is None:
        return None
    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()
        result = outer.get("result")
        if result is None:
            return None
        content = result.get("content", [])
        if not content:
            return None
        inner_text = content[0].get("text", "")
        if not inner_text:
            return None
        return json.loads(inner_text)
    except Exception:
        return None


# 13种榜单类型映射
ETF_RANK_TYPES = {
    "gainers":      ("1",  "涨幅榜"),
    "losers":       ("2",  "跌幅榜"),
    "turnover":     ("3",  "换手榜"),
    "capital":      ("4",  "主力资金榜"),
    "search":       ("5",  "搜索榜"),
    "focus":        ("6",  "关注榜"),
    "5d-gainers":   ("7",  "5日涨幅榜"),
    "5d-losers":    ("8",  "5日跌幅榜"),
    "streak-up":    ("9",  "连涨榜"),
    "streak-down":  ("10", "连跌榜"),
    "5d-capital":   ("11", "5日主力资金榜"),
    "subscription": ("12", "净申购榜"),
    "premium":      ("13", "溢价率榜"),
}


def get_etf_rank(rank_type: str = "gainers", size: int = 10, page: int = 0,
                 same_index_filter: int = 0) -> List[Dict]:
    """
    获取ETF排行榜

    参数:
        rank_type: 榜单类型 (gainers/losers/turnover/capital/search/focus/
                   5d-gainers/5d-losers/streak-up/streak-down/5d-capital/subscription/premium)
        size: 返回条数
        page: 页码(从0开始)
        same_index_filter: 同指数ETF去重 1=开
    """
    type_info = ETF_RANK_TYPES.get(rank_type)
    if not type_info:
        print(f"  [ERROR] 未知榜单类型: {rank_type}")
        print(f"  可用: {', '.join(ETF_RANK_TYPES.keys())}")
        return []

    type_code, type_name = type_info
    args = {"type": type_code, "size": size, "page": page}
    if same_index_filter:
        args["sameIndexFilter"] = same_index_filter

    data = _mcp_call("etf_rank", "finance-api_product_etf_rank_get", args)
    if not data or data.get("retcode") != 0:
        return []

    return data.get("data", [])


def format_etf_rank(results: List[Dict], rank_type: str = "gainers") -> str:
    """格式化ETF排行输出"""
    if not results:
        return "未获取到ETF排行数据"

    _, type_name = ETF_RANK_TYPES.get(rank_type, ("", rank_type))

    lines = [
        "=" * 78,
        f"  ETF {type_name}",
        "=" * 78,
        f"  {'排名':<4} {'代码':<8} {'名称':<12} {'涨跌幅':>8} {'成交额':>10} {'换手率':>8} {'主力资金':>10} {'规模':>10}",
        "-" * 78,
    ]

    for i, item in enumerate(results, 1):
        code = item.get("code", "")
        name = item.get("name", "")
        roc = item.get("roc", 0)
        volume = item.get("volume", "-")
        turnover = item.get("turnover_rate", 0)
        cash_flow = item.get("cashFlow", "-")
        fund_size = item.get("fundSize", "-")

        roc_str = f"{roc:+.2f}%" if roc else "-"
        turn_str = f"{turnover:.2f}%" if turnover else "-"

        lines.append(f"  {i:<4} {code:<8} {name:<12} {roc_str:>8} {volume:>10} {turn_str:>8} {cash_flow:>10} {fund_size:>10}")

    lines.append("=" * 78)
    return "\n".join(lines)
```

---

### §11.3 龙虎榜深度

龙虎榜模块提供多维度数据：按日期查上榜个股、按时间区间查排行、个股历史上榜记录、买卖席位明细、营业部统计、整体概况、日历等。

```python
"""龙虎榜深度数据 — 广发MCP"""

import json
import os
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_TIMEOUT = 30
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """MCP JSON-RPC 2.0 通用调用（参见§11.1）"""
    if not _API_KEY or requests is None:
        return None
    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()
        result = outer.get("result")
        if result is None:
            return None
        content = result.get("content", [])
        if not content:
            return None
        inner_text = content[0].get("text", "")
        if not inner_text:
            return None
        return json.loads(inner_text)
    except Exception:
        return None


def get_lhb_rank(market: str = "sh", months: str = "m1") -> List[Dict]:
    """获取时间区间内上榜个股排行"""
    data = _mcp_call("lhb", "lhb_stat_stock_months_get", {
        "market": market, "months": months,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_by_date(market: str = "sh", date: int = 20260724) -> List[Dict]:
    """获取指定日期+市场的龙虎榜上榜个股"""
    data = _mcp_call("lhb", "lhb_aborttrade_market_date_get", {
        "market": market, "date": date,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def format_lhb_rank(results: List[Dict], months: str = "m1") -> str:
    """格式化龙虎榜排行"""
    if not results:
        return "未获取到龙虎榜数据"

    period_map = {"m1": "近1月", "m3": "近3月", "m6": "近6月", "m12": "近12月"}
    period = period_map.get(months, months)

    lines = [
        "=" * 75,
        f"  龙虎榜上榜排行 ({period})",
        "=" * 75,
        f"  {'排名':<4} {'代码':<8} {'名称':<10} {'市场':<4} {'上榜次数':>8} {'买入额':>14} {'卖出额':>14}",
        "-" * 75,
    ]

    for i, item in enumerate(results, 1):
        code = item.get("trdCode", "")
        name = item.get("secuSht", "")
        market = item.get("market", "")
        cnt = item.get("abortCnt", 0)
        buy_val = item.get("buyVal", 0)
        sell_val = item.get("sellVal", 0)

        buy_str = f"{buy_val/1e8:.2f}亿" if buy_val else "-"
        sell_str = f"{sell_val/1e8:.2f}亿" if sell_val else "-"

        lines.append(f"  {i:<4} {code:<8} {name:<10} {market:<4} {cnt:>8} {buy_str:>14} {sell_str:>14}")

    lines.append("=" * 75)
    return "\n".join(lines)


def format_lhb_by_date(results: List[Dict], date: int) -> str:
    """格式化指定日期龙虎榜"""
    if not results:
        return f"{date} 无龙虎榜数据"

    lines = [
        "=" * 75,
        f"  龙虎榜上榜个股 ({date})",
        "=" * 75,
    ]

    for item in results:
        code = item.get("trdCode", "")
        name = item.get("secuSht", "")
        reason = item.get("reason", "")
        buy_val = item.get("buyVal", 0)
        sell_val = item.get("sellVal", 0)
        net = buy_val - sell_val

        buy_str = f"{buy_val/1e8:.2f}亿" if buy_val else "-"
        sell_str = f"{sell_val/1e8:.2f}亿" if sell_val else "-"
        net_str = f"{net/1e8:+.2f}亿" if net else "-"

        lines.append(f"  {code} {name:<10} 买:{buy_str} 卖:{sell_str} 净:{net_str}")
        if reason:
            lines.append(f"    上榜原因: {reason}")

    lines.append("=" * 75)
    return "\n".join(lines)
```

---

### §11.4 指数估值分位

通过 `windmill` 服务获取主要指数的 PE/PB 历史分位数，辅助判断指数当前估值水平（低估/合理/偏高/高估）。

```python
"""指数估值分位 — 广发MCP (windmill服务)"""

import json
import os
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_TIMEOUT = 30
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """MCP JSON-RPC 2.0 通用调用（参见§11.1）"""
    if not _API_KEY or requests is None:
        return None
    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()
        result = outer.get("result")
        if result is None:
            return None
        content = result.get("content", [])
        if not content:
            return None
        inner_text = content[0].get("text", "")
        if not inner_text:
            return None
        return json.loads(inner_text)
    except Exception:
        return None


def get_index_valuation(page: int = 0, per_page: int = 20) -> List[Dict]:
    """获取指数估值分位数据"""
    data = _mcp_call("windmill", "valuation_windmill_get", {
        "page": page, "perPage": per_page,
    })
    if not data or data.get("retcode") != 0:
        return []
    return data.get("data", {}).get("list", [])


def format_index_valuation(results: List[Dict]) -> str:
    """格式化指数估值分位"""
    if not results:
        return "未获取到指数估值数据"

    val_map = {"1": "低估", "2": "合理", "3": "偏高", "4": "高估"}

    lines = [
        "=" * 90,
        f"  指数估值分位 (共{len(results)}个)",
        "=" * 90,
        f"  {'指数名称':<12} {'PE分位':>8} {'PB分位':>8} {'PE评估':>6} {'PB评估':>6} {'近1年涨幅':>10} {'关联ETF':<16}",
        "-" * 90,
    ]

    for item in results:
        name = item.get("indexName", "")
        pe_pct = item.get("pePercent") or 0
        pb_pct = item.get("pbPercent") or 0
        pe_val = val_map.get(str(item.get("valuationResult", "")), "-")
        pb_val = val_map.get(str(item.get("valuationResultPB", "")), "-")
        earning = item.get("earning") or 0
        fund_name = item.get("fundName", "")

        earn_str = f"{earning:+.2f}%" if earning else "-"

        lines.append(f"  {name:<12} {pe_pct:>7.1f}% {pb_pct:>7.1f}% {pe_val:>6} {pb_val:>6} {earn_str:>10} {fund_name:<16}")

    lines.append("=" * 90)
    lines.append("  评估: 低估=关注机会 | 合理=持有 | 偏高/高估=注意风险")
    return "\n".join(lines)
```

---

### §11.5 广发财务对比

通过 `quant` 服务获取个股的基本指标：总市值、PE(TTM)、PB、百分位排名、行业均值对比等。支持批量查询。

```python
"""广发财务对比 — 广发MCP (quant服务)"""

import json
import os
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_TIMEOUT = 30
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """MCP JSON-RPC 2.0 通用调用（参见§11.1）"""
    if not _API_KEY or requests is None:
        return None
    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()
        result = outer.get("result")
        if result is None:
            return None
        content = result.get("content", [])
        if not content:
            return None
        inner_text = content[0].get("text", "")
        if not inner_text:
            return None
        return json.loads(inner_text)
    except Exception:
        return None


def _normalize_gf_code(stock_code: str) -> str:
    """转换为广发格式 SH600519 / SZ000858"""
    code = stock_code.strip()
    if code.startswith(("sh", "SH")):
        return "SH" + code[2:]
    if code.startswith(("sz", "SZ")):
        return "SZ" + code[2:]
    if code.isdigit() and len(code) == 6:
        return ("SH" if code.startswith(("6", "9")) else "SZ") + code
    return code


def get_gf_basic(stock_codes: List[str]) -> List[Dict]:
    """获取基本指标（市值/估值/PE百分位/PB百分位）"""
    codes = [_normalize_gf_code(c) for c in stock_codes]
    data = _mcp_call("quant", "common_basic_post", {"stock_codes": codes})
    if not data or data.get("retcode") != 0:
        return []
    return data.get("data", [])


def format_gf_basic(results: List[Dict]) -> str:
    """格式化广发基本指标"""
    if not results:
        return "未获取到广发财务数据"

    lines = [
        "=" * 75,
        f"  广发财务指标 (市值/估值/百分位)",
        "=" * 75,
    ]

    for item in results:
        code = item.get("stock_code", "")
        name = item.get("stock_name", "")
        basic = item.get("basic", {})
        val = item.get("valuation", {})

        mktcap = basic.get("total_marketcap", 0)
        list_date = basic.get("list_date", "")
        pettm = val.get("pettm", 0)
        pb = val.get("pb", 0)
        pe_pct = val.get("pettm_percent", 0)
        pb_pct = val.get("pb_percent", 0)
        pe_avg = val.get("pettm_avg", 0)
        pb_avg = val.get("pb_avg", 0)
        trade_date = val.get("trade_date", "")

        lines.append(f"\n  {code} {name}")
        lines.append(f"    总市值: {mktcap:.2f}亿 | 上市: {list_date}")
        lines.append(f"    PE(TTM): {pettm:.2f} | 行业均值: {pe_avg:.2f} | 百分位: {pe_pct:.1f}%")
        lines.append(f"    PB: {pb:.2f} | 行业均值: {pb_avg:.2f} | 百分位: {pb_pct:.1f}%")
        lines.append(f"    交易日: {trade_date}")

    lines.append("\n" + "=" * 75)
    return "\n".join(lines)
```

---

### §11.6 广发F10扩展

F10 模块通过独立的 REST 接口（非 MCP 协议）获取公司基础信息。`quant` 服务还提供盈利能力分析、资本结构、现金流量、行业信息等扩展接口。

```python
"""广发F10扩展 — 财务分析 + F10基础信息"""

import json
import os
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

_BASE = "https://mcp-api.gf.com.cn/server/mcp"
_F10_URL = "https://mcp-api.gf.com.cn/gf-skills/skills/mcp/call"
_TIMEOUT = 30
_API_KEY = os.environ.get("GF_SKILLS_APIKEY", "")


def _get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }


def _mcp_call(server: str, tool: str, arguments: Dict) -> Optional[Dict]:
    """MCP JSON-RPC 2.0 通用调用（参见§11.1）"""
    if not _API_KEY or requests is None:
        return None
    url = f"{_BASE}/{server}/mcp"
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        outer = resp.json()
        result = outer.get("result")
        if result is None:
            return None
        content = result.get("content", [])
        if not content:
            return None
        inner_text = content[0].get("text", "")
        if not inner_text:
            return None
        return json.loads(inner_text)
    except Exception:
        return None


def _f10_call(service_name: str, tool_name: str, args: Dict) -> Optional[Dict]:
    """调用广发 F10 REST API (非MCP协议)"""
    if not _API_KEY or requests is None:
        return None
    payload = {
        "service_name": service_name,
        "tool_name": tool_name,
        "args": args,
    }
    try:
        resp = requests.post(_F10_URL, json=payload, headers=_get_headers(), timeout=_TIMEOUT)
        resp.raise_for_status()
        d = resp.json()
        if d.get("retcode") != 0:
            return None
        return d.get("data", {}).get("data")
    except Exception:
        return None


def _normalize_gf_code(stock_code: str) -> str:
    """转换为广发格式 SH600519 / SZ000858"""
    code = stock_code.strip()
    if code.startswith(("sh", "SH")):
        return "SH" + code[2:]
    if code.startswith(("sz", "SZ")):
        return "SZ" + code[2:]
    if code.isdigit() and len(code) == 6:
        return ("SH" if code.startswith(("6", "9")) else "SZ") + code
    return code


# ── 盈利能力分析 ──
def get_gf_profit_analysis(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """盈利能力分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_profit_ability_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


# ── 资本结构分析 ──
def get_gf_capital_structure(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """资本结构分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_capital_structure_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


# ── 现金流量分析 ──
def get_gf_cashflow(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """现金流量分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_crashflow_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


# ── 行业信息 ──
def get_gf_industry_info(stock_codes: List[str]) -> List[Dict]:
    """获取行业信息（行业代码/龙头/PE相近/市值相近）"""
    codes = [_normalize_gf_code(c) for c in stock_codes]
    data = _mcp_call("quant", "common_industry_info_post", {"stock_codes": codes})
    if not data or data.get("retcode") != 0:
        return []
    return data if isinstance(data, list) else data.get("data", [])


# ── F10 基础信息 (REST接口) ──
def get_f10_basic(code: str, market: str = "SH") -> Optional[Dict]:
    """获取F10基础信息（公司全称/板块/上市日期/主营业务/行业）"""
    pure_code = code
    if code.startswith(("sh", "SH", "sz", "SZ")):
        pure_code = code[2:]
        market = code[:2].upper()

    return _f10_call("wechat_f10", "f10_basic_post", {
        "code": pure_code, "market": market,
    })
```

---

## §12 东方财富妙想AI

### §12.1 AI配置与请求

东方财富妙想 (MXClaw) 提供免费 AI 金融数据 API，支持股票诊断、基金诊断、选股、资讯搜索、AI 问答等功能。通过 `em_api_key` 环境变量或 `config.yaml` 配置鉴权。

```python
"""
东方财富妙想 (MXClaw) API 封装 — 免费 AI 金融数据接口
依赖：requests
配置：环境变量 EM_API_KEY 或 config.yaml 中设置 em_api_key
注册：https://ai.eastmoney.com/mxClaw
"""

import json
import os
import requests

API_BASE = "https://ai-saas.eastmoney.com/proxy"

# 各功能的 API 端点
ENDPOINTS = {
    'stock_analysis': '/app-robo-advisor-api/assistant/stock-analysis',
    'fund_analysis':  '/app-robo-advisor-api/assistant/fund-analysis',
    'search_data':    '/b/mcp/tool/searchData',
    'select_security':'/b/mcp/tool/selectSecurity',
    'search_news':    '/b/mcp/tool/searchNews',
    'write_report':   '/app-robo-advisor-api/assistant/write/tracking/report',
    'ask':            '/app-robo-advisor-api/assistant/ask',
    'comparable':     '/app-robo-advisor-api/assistant/comparable-company-analysis',
}

TIMEOUT = 60


def _get_api_key():
    """获取 API Key：环境变量 > config.yaml"""
    key = os.environ.get('EM_API_KEY', '')
    if key:
        return key
    try:
        # 从 config.yaml 读取（项目内部引用，使用时需自行实现）
        # from lib.settings import get
        # key = get('em_api_key', '')
        pass
    except Exception:
        pass
    return ''


def is_configured():
    """是否已配置 API Key"""
    return bool(_get_api_key())


def _fix_gbk(text):
    """
    修复 API 返回的 GBK 编码中文。
    东方财富 API 的 displayData 有时返回 GBK 编码的字节序列，
    被错误解码为 latin-1/utf-8 导致乱码。
    """
    if not isinstance(text, str):
        return text

    garbled_count = sum(1 for c in text if ord(c) > 127 and ord(c) < 0x2E80)
    if garbled_count > len(text) * 0.1:
        try:
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            return decoded
        except Exception:
            pass

    if '\ufffd' in text or any(ord(c) > 0xE000 for c in text[:100]):
        try:
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            if decoded != text:
                return decoded
        except Exception:
            pass

    return text


def _call(endpoint_key, payload, extra_headers=None):
    """
    通用 API 调用

    Parameters
    ----------
    endpoint_key : str - ENDPOINTS 中的 key
    payload : dict - 请求体
    extra_headers : dict - 额外请求头

    Returns
    -------
    dict - API 响应
    """
    api_key = _get_api_key()
    if not api_key:
        return {'error': '未配置 EM_API_KEY，请在 config.yaml 中设置 em_api_key 或设置环境变量 EM_API_KEY。注册地址：https://ai.eastmoney.com/mxClaw'}

    url = API_BASE + ENDPOINTS.get(endpoint_key, '')
    headers = {
        'Content-Type': 'application/json',
        'em_api_key': api_key,
    }
    if extra_headers:
        headers.update(extra_headers)

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT,
                         proxies={'http': None, 'https': None})
        result = r.json()
        if result.get('code') == 401 or result.get('status', 0) < 0:
            msg = result.get('message', '未知错误')
            msg = _fix_gbk(msg)
            return {'error': f'API错误: {msg}'}
        return result
    except requests.exceptions.ConnectionError:
        return {'error': '网络连接失败，无法访问东方财富妙想 API'}
    except requests.exceptions.Timeout:
        return {'error': '请求超时，请稍后重试'}
    except Exception as e:
        return {'error': f'请求失败: {str(e)}'}


def _extract_ai_content(result):
    """提取 AI 文本类回复（股票诊断、问答等）— 修复 GBK"""
    if 'error' in result:
        return None, result['error']

    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'

    display_data = data.get('displayData', '')
    if isinstance(display_data, str) and display_data.strip():
        return _fix_gbk(display_data.strip()), None

    return None, 'API 返回空内容'
```

---

### §12.2 AI诊断

股票诊断和基金诊断均优先使用专用端点，若 API 不支持则自动降级到通用 `ask` 端点，从多维度生成综合分析报告。

```python
"""东方财富妙想 — AI诊断"""

import json
import os
import requests

API_BASE = "https://ai-saas.eastmoney.com/proxy"

ENDPOINTS = {
    'stock_analysis': '/app-robo-advisor-api/assistant/stock-analysis',
    'fund_analysis':  '/app-robo-advisor-api/assistant/fund-analysis',
    'ask':            '/app-robo-advisor-api/assistant/ask',
}

TIMEOUT = 60


def _get_api_key():
    """获取 API Key：环境变量 > config.yaml"""
    key = os.environ.get('EM_API_KEY', '')
    if key:
        return key
    return ''


def _fix_gbk(text):
    """修复 API 返回的 GBK 编码中文"""
    if not isinstance(text, str):
        return text
    garbled_count = sum(1 for c in text if ord(c) > 127 and ord(c) < 0x2E80)
    if garbled_count > len(text) * 0.1:
        try:
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            return decoded
        except Exception:
            pass
    return text


def _call(endpoint_key, payload, extra_headers=None):
    """通用 API 调用"""
    api_key = _get_api_key()
    if not api_key:
        return {'error': '未配置 EM_API_KEY'}
    url = API_BASE + ENDPOINTS.get(endpoint_key, '')
    headers = {'Content-Type': 'application/json', 'em_api_key': api_key}
    if extra_headers:
        headers.update(extra_headers)
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT,
                         proxies={'http': None, 'https': None})
        result = r.json()
        if result.get('code') == 401 or result.get('status', 0) < 0:
            msg = _fix_gbk(result.get('message', '未知错误'))
            return {'error': f'API错误: {msg}'}
        return result
    except Exception as e:
        return {'error': f'请求失败: {str(e)}'}


def _extract_ai_content(result):
    """提取 AI 文本类回复"""
    if 'error' in result:
        return None, result['error']
    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'
    display_data = data.get('displayData', '')
    if isinstance(display_data, str) and display_data.strip():
        return _fix_gbk(display_data.strip()), None
    return None, 'API 返回空内容'


def stock_diagnosis(question):
    """
    股票综合诊断（自然语言）
    优先用 stock-analysis 端点，若 API 不支持则降级到 ask 端点

    Parameters
    ----------
    question : str - 如 "分析贵州茅台"、"贵州茅台怎么样"

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    result = _call('stock_analysis', {'question': question})
    content, error = _extract_ai_content(result)

    # 降级到通用问答
    if error and ('不支持' in error or '空内容' in error):
        fallback_q = f"请从基本面、技术面、资金面、估值、风险五个维度，综合分析{question.replace('分析','').replace('怎么样','').strip()}这只股票，给出详细诊断报告"
        result2 = _call('ask', {'question': fallback_q})
        content, error = _extract_ai_content(result2)

    return {'content': content, 'error': error}


def fund_diagnosis(question):
    """
    基金综合诊断（自然语言）
    优先用 fund-analysis 端点，若 API 不支持则降级到 ask 端点

    Parameters
    ----------
    question : str - 如 "分析招商中证白酒"、"这只基金怎么样"

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    result = _call('fund_analysis', {'question': question})
    content, error = _extract_ai_content(result)

    # 降级到通用问答
    if error and ('不支持' in error or '空内容' in error):
        fallback_q = f"请从基金类型、业绩表现、持仓结构、基金经理、费率、风险收益特征六个维度，综合分析{question.replace('分析','').replace('怎么样','').strip()}这只基金"
        result2 = _call('ask', {'question': fallback_q})
        content, error = _extract_ai_content(result2)

    return {'content': content, 'error': error}
```

---

### §12.3 AI选股/资讯/问答

自然语言选股（支持 A 股/港股/美股，股票/基金/ETF/债券/可转债/板块/概念）、金融资讯搜索、AI 金融问答（支持深度思考模式）。

```python
"""东方财富妙想 — AI选股/资讯/问答"""

import json
import os
import requests

API_BASE = "https://ai-saas.eastmoney.com/proxy"

ENDPOINTS = {
    'select_security': '/b/mcp/tool/selectSecurity',
    'search_news':     '/b/mcp/tool/searchNews',
    'ask':             '/app-robo-advisor-api/assistant/ask',
}

TIMEOUT = 60


def _get_api_key():
    """获取 API Key：环境变量 > config.yaml"""
    key = os.environ.get('EM_API_KEY', '')
    if key:
        return key
    return ''


def _fix_gbk(text):
    """修复 API 返回的 GBK 编码中文"""
    if not isinstance(text, str):
        return text
    garbled_count = sum(1 for c in text if ord(c) > 127 and ord(c) < 0x2E80)
    if garbled_count > len(text) * 0.1:
        try:
            raw_bytes = text.encode('latin-1')
            decoded = raw_bytes.decode('gbk', errors='replace')
            return decoded
        except Exception:
            pass
    return text


def _call(endpoint_key, payload, extra_headers=None):
    """通用 API 调用"""
    api_key = _get_api_key()
    if not api_key:
        return {'error': '未配置 EM_API_KEY'}
    url = API_BASE + ENDPOINTS.get(endpoint_key, '')
    headers = {'Content-Type': 'application/json', 'em_api_key': api_key}
    if extra_headers:
        headers.update(extra_headers)
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT,
                         proxies={'http': None, 'https': None})
        result = r.json()
        if result.get('code') == 401 or result.get('status', 0) < 0:
            msg = _fix_gbk(result.get('message', '未知错误'))
            return {'error': f'API错误: {msg}'}
        return result
    except Exception as e:
        return {'error': f'请求失败: {str(e)}'}


def _extract_ai_content(result):
    """提取 AI 文本类回复"""
    if 'error' in result:
        return None, result['error']
    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'
    display_data = data.get('displayData', '')
    if isinstance(display_data, str) and display_data.strip():
        return _fix_gbk(display_data.strip()), None
    return None, 'API 返回空内容'


def _extract_select_stock(result):
    """提取选股结果（partialResults 中的 markdown 表格）"""
    if 'error' in result:
        return None, result['error']
    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'
    partial = data.get('partialResults', '')
    if isinstance(partial, str) and partial.strip():
        content = _fix_gbk(partial.strip())
        conditions = data.get('totalCondition', '')
        count = data.get('securityCount', 0)
        header = f"选股条件: {_fix_gbk(conditions)}\n符合条件: {count} 只\n\n"
        return header + content, None
    return None, '选股返回空结果'


def _extract_news(result):
    """提取资讯搜索结果"""
    if 'error' in result:
        return None, result['error']
    data = result.get('data', {})
    if not isinstance(data, dict):
        return None, 'API 返回格式异常'
    llm_resp = data.get('llmSearchResponse', {})
    news_list = llm_resp.get('data', [])
    if not news_list:
        return None, '未找到相关资讯'
    lines = []
    for i, item in enumerate(news_list[:15], 1):
        title = _fix_gbk(item.get('title', ''))
        date = item.get('date', '')
        source = item.get('source', '')
        url = item.get('jumpUrl', '')
        content = _fix_gbk(item.get('content', '')[:200])
        lines.append(f"{i}. 【{title}】")
        lines.append(f"   时间: {date}  来源: {source}")
        if content:
            lines.append(f"   摘要: {content}")
        if url:
            lines.append(f"   链接: {url}")
        lines.append('')
    return '\n'.join(lines), None


# ── 自然语言选股 ──
def select_security(query, market='a_share', category='stock', top_n=10):
    """
    自然语言选股

    Parameters
    ----------
    query : str - 自然语言，如 "市盈率最低的50只股票"、"连续上涨的创业板股票"
    market : str - 市场 ('a_share'|'hk'|'us')
    category : str - 品类 ('stock'|'fund'|'etf'|'bond'|'convertible_bond'|'sector'|'concept')
    top_n : int - 返回数量

    Returns
    -------
    dict: {'content': str, 'data': list, 'error': str or None}
    """
    payload = {
        'query': query,
        'market': market,
        'category': category,
        'count': top_n,
    }
    result = _call('select_security', payload)

    if 'error' in result:
        return {'content': None, 'data': [], 'error': result['error']}

    content, error = _extract_select_stock(result)
    raw_data = result.get('data', {})

    return {'content': content, 'data': raw_data, 'error': error}


# ── 金融资讯搜索 ──
def search_news(query, market='', count=10):
    """
    金融资讯搜索

    Parameters
    ----------
    query : str - 搜索关键词
    market : str - 市场筛选 (''|'cn'|'hk'|'us')
    count : int - 返回数量

    Returns
    -------
    dict: {'content': str, 'data': list, 'error': str or None}
    """
    payload = {
        'query': query,
        'market': market,
        'count': count,
    }
    result = _call('search_news', payload)

    if 'error' in result:
        return {'content': None, 'data': [], 'error': result['error']}

    content, error = _extract_news(result)
    raw_data = result.get('data', {})

    return {'content': content, 'data': raw_data, 'error': error}


# ── AI 金融问答 ──
def ask(question, deep_think=False):
    """
    金融 AI 问答

    Parameters
    ----------
    question : str - 问题
    deep_think : bool - 是否启用深度思考

    Returns
    -------
    dict: {'content': str, 'error': str or None}
    """
    payload = {
        'question': question,
        'deepThink': deep_think,
    }
    result = _call('ask', payload)
    content, error = _extract_ai_content(result)
    return {'content': content, 'error': error}
```
