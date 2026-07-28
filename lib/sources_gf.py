"""
广发证券 MCP 数据接口适配层
端点: mcp-api.gf.com.cn (streamableHttp, JSON-RPC 2.0)
鉴权: Bearer token (GF_SKILLS_APIKEY)

覆盖: ETF排行 / 龙虎榜 / 财务对比 / 指数估值分位 / F10基础信息
"""

import json
import os
from typing import Dict, List, Optional

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


# ── ETF 排行 ──────────────────────────────────────────────────

ETF_RANK_TYPES = {
    "gainers": ("1", "涨幅榜"),
    "losers": ("2", "跌幅榜"),
    "turnover": ("3", "换手榜"),
    "capital": ("4", "主力资金榜"),
    "search": ("5", "搜索榜"),
    "focus": ("6", "关注榜"),
    "5d-gainers": ("7", "5日涨幅榜"),
    "5d-losers": ("8", "5日跌幅榜"),
    "streak-up": ("9", "连涨榜"),
    "streak-down": ("10", "连跌榜"),
    "5d-capital": ("11", "5日主力资金榜"),
    "subscription": ("12", "净申购榜"),
    "premium": ("13", "溢价率榜"),
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


# ── 龙虎榜 ──────────────────────────────────────────────────

def get_lhb_by_date(market: str = "sh", date: int = 20260724) -> List[Dict]:
    """获取指定日期+市场的龙虎榜上榜个股"""
    data = _mcp_call("lhb", "lhb_aborttrade_market_date_get", {
        "market": market, "date": date,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_stock_history(market: str, code: str) -> List[Dict]:
    """获取个股历史上榜记录"""
    data = _mcp_call("lhb", "lhb_aborttrade_stock_market_code_get", {
        "market": market, "code": code,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_stock_detail(market: str, code: str, date: int) -> List[Dict]:
    """获取个股某日上榜的买卖席位明细"""
    data = _mcp_call("lhb", "lhb_aborttrade_market_code_date_get", {
        "market": market, "code": code, "date": date,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_rank(market: str = "sh", months: str = "m1") -> List[Dict]:
    """获取时间区间内上榜个股排行"""
    data = _mcp_call("lhb", "lhb_stat_stock_months_get", {
        "market": market, "months": months,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_dept_stat(dept_id: str, months: str = "m1") -> List[Dict]:
    """获取营业部在区间内的统计数据"""
    data = _mcp_call("lhb", "lhb_stat_dept_id_months_get", {
        "deptId": dept_id, "months": months,
    })
    if not data or data.get("errCode") != 0:
        return []
    return data.get("data", [])


def get_lhb_outline() -> Optional[Dict]:
    """获取龙虎榜整体概况"""
    data = _mcp_call("lhb", "lhb_outline_plate_get", {})
    if not data or data.get("errCode") != 0:
        return None
    return data.get("data")


def get_lhb_calendar(market: str = "sh", month: int = 202607) -> List[Dict]:
    """获取龙虎榜日历（某月交易日）"""
    data = _mcp_call("lhb", "lhb_calendar_market_month_get", {
        "market": market, "month": month,
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


# ── 指数估值分位 (windmill) ──────────────────────────────────

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


# ── 财务对比 (quant) ──────────────────────────────────────────

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


def get_gf_profit_analysis(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """盈利能力分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_profit_ability_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


def get_gf_capital_structure(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """资本结构分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_capital_structure_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


def get_gf_cashflow(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """现金流量分析"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "analyze_crashflow_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


def get_gf_industry_info(stock_codes: List[str]) -> List[Dict]:
    """获取行业信息（行业代码/龙头/PE相近/市值相近）"""
    codes = [_normalize_gf_code(c) for c in stock_codes]
    data = _mcp_call("quant", "common_industry_info_post", {"stock_codes": codes})
    if not data or data.get("retcode") != 0:
        return []
    return data if isinstance(data, list) else data.get("data", [])


def get_gf_profit_statement(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """利润表"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "major_indicator_profit_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


def get_gf_balance_sheet(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """资产负债表"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "major_indicator_liabilty_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


def get_gf_main_business(stock_code: str, report_type: int = None) -> Optional[Dict]:
    """主营业务构成"""
    args = {"stock_code": _normalize_gf_code(stock_code)}
    if report_type:
        args["report_type"] = report_type
    data = _mcp_call("quant", "major_indicator_main_business_get", args)
    if not data or data.get("retcode") != 0:
        return None
    return data


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


# ── F10 基础信息 ──────────────────────────────────────────────

def get_f10_basic(code: str, market: str = "SH") -> Optional[Dict]:
    """获取F10基础信息（公司全称/板块/上市日期/主营业务/行业）"""
    # 去掉前缀
    pure_code = code
    if code.startswith(("sh", "SH", "sz", "SZ")):
        pure_code = code[2:]
        market = code[:2].upper()

    return _f10_call("wechat_f10", "f10_basic_post", {
        "code": pure_code, "market": market,
    })


def format_f10_basic(data: Dict) -> str:
    """格式化F10基础信息"""
    if not data:
        return "未获取到F10基础信息"

    lines = [
        "=" * 60,
        f"  F10 基础信息",
        "=" * 60,
        f"  公司全称: {data.get('compName', 'N/A')}",
        f"  板块: {data.get('boardName', 'N/A')}",
        f"  上市日期: {data.get('listDate', 'N/A')}",
        f"  所属行业: {data.get('industries', 'N/A')}",
        f"  主营业务: {data.get('businessScope', 'N/A')[:100]}...",
        "=" * 60,
    ]
    return "\n".join(lines)
