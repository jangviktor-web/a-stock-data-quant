---
name: mx-finance-search
description: 基于东方财富数据库，按明确公司、板块、事件或政策检索最新公告、研报、财经新闻和交易所动态，适用于资讯查找、事件跟踪、公告精读与舆情监控。用户要发现“今日市场热点、热门股票、活跃赛道”等市场级热点时不要使用，改用 stock-market-hotspot-discovery。Natural language search for targeted financial news, announcements, research and policies; not for broad market hotspot discovery.
version: 1.1.1
category: investment-finance
author: 东方财富
license: proprietary
agent_created: true
---

# 金融资讯搜索

通过**自然语言查询**检索时效性金融信息，数据来自于妙想大模型，适用场景包括：
- **最新新闻与政策动态**
- **公司公告与事件跟踪**
- **券商研报与市场解读**
- **宏观事件对市场/板块影响分析**


## 功能范围

### 基础检索能力
- 检索个股、板块、主题的最新资讯
- 聚合公告、研报、新闻等公开信息
- 返回可读正文内容（优先提取 `llmSearchResponse`）
- 支持将结果保存为本地 `.txt` 文件，便于追溯与复盘

### 输入建议
- 查询建议包含至少一个明确目标：公司、板块、事件、政策或时间范围
- 对语义不清的问句，应先做一次简洁澄清再执行检索
- 汇总时保持关键数值、专有名词和原始语义不被篡改
- 不处理“今日市场热点、热门股票、活跃赛道”等市场级热点发现；此类请求改用 `stock-market-hotspot-discovery`

### 查询示例

| 类型 | query 示例 |
|---|---|
| 个股资讯 | 格力电器最新研报与公告、寒武纪 688256 最新动态 |
| 板块/主题 | 商业航天板块近期新闻、新能源政策解读 |
| 宏观/风险 | 美联储加息对A股影响、汇率风险相关公司案例 |
| 综合解读 | 今日大盘异动原因、北向资金流向解读 |


## 前提条件

### 授权（已内联，无需单独跑）

本 Skill 依赖 `EM_API_KEY`。授权检查已集成进 `get_data.py`，**不要先跑 `auth.py ensure`**，直接执行检索命令即可。

| 退出码 | 含义 | agent 动作 |
|---|---|---|
| `0` | 成功 | 读取 `Saved:`（若有）及随后输出的资讯正文 |
| `10` | 需用户授权 | 按下方 `need_auth` 流程处理 |
| `2` | 授权网络错误、接口错误或业务错误 | 检查网络后最多重试 1 次，持续失败则向用户说明 |
| `1` | 参数错误 | 不重试，向用户说明缺少或无效参数 |

退出码 `10` 时 stdout 会打印：

```text
need_auth: true
authUrl: <以实际返回为准>
apiKeyUrl: <以实际返回为准>
```


授权、凭据持久化及 401 失效处理必须遵循 [授权协议](references/auth_protocol.md)。安装依赖时运行 `pip3 install -r requirements.txt`。


## 快速开始

### 1. 命令行调用

```bash
python3 scripts/get_data.py "寒武纪 688256 最新研报与公告"
```


**输出示例**
```text
Saved: /path/to/workspace/mx_finance_search/mx_finance_search_90bf169c.txt
（随后输出资讯正文内容）
```

**参数说明：**

| 参数 | 说明 | 必填 |
|---|---|---|
| `query`（位置参数） | 自然语言查询文本 | ✅（位置参数或 stdin 二选一） |
| `--no-save` | 仅输出结果，不写入本地文件 | 否 |

### 2. 代码调用

```python
import asyncio
from pathlib import Path
from scripts.get_data import query_financial_news

async def main():
    result = await query_financial_news(
        query="新能源板块近期政策与龙头公司动态",
        output_dir=Path("workspace/mx_finance_search"),
        save_to_file=True,
    )
    if "error" in result:
        print(result["error"])
    else:
        print(result["content"])
        if result.get("output_path"):
            print("已保存至:", result["output_path"])

asyncio.run(main())
```

## 输出文件说明

| 文件 | 说明 |
|---|---|
| `mx_finance_search_<ID>.txt` | 资讯正文文本（从返回中提取） |

## 返回字段说明

- `content`：提取后的资讯正文（优先 `llmSearchResponse`）。
- `output_path`：当 `save_to_file=True` 且有内容时，返回保存路径。
- `raw`：原始接口返回，便于调试或二次处理。
- `error`：检索失败时返回错误信息。


## 常见问题

**没有传 query 时为什么直接退出？**  
→ 命令行会先读取位置参数 `query`，若为空再读取 stdin；两者都为空时打印帮助并退出。

**如何只看输出，不落盘？**
```bash
python3 -m scripts.get_data "商业航天板块近期新闻" --no-save
```

## 合规说明
- 禁止在代码或提示词中硬编码账号 ID、会话 ID 或 token。
- 环境变量按敏感信息处理，不在日志或回复中泄露。
- 检索失败时不得编造事实，应返回明确错误或不确定性说明。
- 输出应保持可追溯、可审计。
