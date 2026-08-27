"""
宏观数据查询：请求接口获取 JSON，转换为 CSV 并生成描述文件。

可通过文本输入查询宏观数据；结果保存为 CSV 与说明 txt。
"""

import asyncio
import csv
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import httpx

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from auth import ensure_auth, AUTH_OK, AUTH_NEED_USER, AUTH_ERROR

EM_BASE_URL = "https://ai-saas.eastmoney.com".rstrip("/")
EM_API_KEY_PLACEHOLDER = "{em" + "_api_key}"
# 内置默认 Key（base64 混淆存储；用户可用 EM_API_KEY 环境变量覆盖）
_EM_API_KEY_BUILTIN = __import__("base64").b64decode("ZW1fSWpjRU1UcHJ3QmNqT2R5QzdkcXYxWk5KMUhsVjNtSUg=").decode()
EM_API_KEY = os.environ.get("EM_API_KEY") or _EM_API_KEY_BUILTIN

if EM_API_KEY and EM_API_KEY != EM_API_KEY_PLACEHOLDER:
    os.environ.setdefault("EM_API_KEY", EM_API_KEY)

AUTH_API_KEY_URL_FALLBACK = f"{EM_BASE_URL}/mxClaw"
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "mx_macro_data"
# MCP 服务器地址
DEFAULT_URL = EM_BASE_URL
DEFAULT_PATH = "/proxy/b/mcp/tool/searchMacroData"


def _load_em_api_key() -> str:
    """加载 EM_API_KEY，优先级：环境变量 > ~/.mx-skills/em_api_key。"""
    env_value = (os.environ.get("EM_API_KEY") or "").strip()
    if env_value:
        return env_value
    if EM_API_KEY and EM_API_KEY != EM_API_KEY_PLACEHOLDER:
        return EM_API_KEY
    key_path = Path.home() / ".mx-skills" / "em_api_key"
    if key_path.exists():
        return key_path.read_text(encoding="utf-8").strip()
    return ""


class _AuthRevoked(Exception):
    """EM_API_KEY 已被服务端判定失效。"""


def _clear_em_api_key_file() -> None:
    try:
        (Path.home() / ".mx-skills" / "em_api_key").unlink(missing_ok=True)
    except OSError:
        pass


def _handle_auth_revoked(reason: str, result: Dict[str, Any]) -> Dict[str, Any]:
    result.pop("remember_api_key", None)
    result.pop("api_key", None)
    _clear_em_api_key_file()
    env_key = os.environ.pop("EM_API_KEY", None)
    try:
        reauth = ensure_auth()
    finally:
        if env_key is not None:
            os.environ["EM_API_KEY"] = env_key
    if reauth["status"] == AUTH_NEED_USER:
        result["need_auth"] = True
        result["authUrl"] = reauth["auth_url"]
        result["apiKeyUrl"] = reauth["api_key_url"]
        result["auth_message"] = (
            f"EM_API_KEY 已失效（{reason}），已自动清理并生成新的授权链接。"
            "请扫码重新授权，完成后重发原指令即可查询。"
        )
        if env_key and env_key.strip():
            result["auth_message"] += " 环境变量 EM_API_KEY 仍含有失效 key，请先清除该环境变量。"
    elif reauth["status"] == AUTH_OK:
        result["error"] = (
            "EM_API_KEY 服务端已失效，但环境变量 EM_API_KEY 仍存在。"
            "请清除该环境变量后重发原指令以触发重新授权。"
        )
    else:
        result["error"] = (
            "EM_API_KEY 失效后重新生成授权链接失败: "
            f"{reauth.get('message', '未知错误')}"
        )
    return result


def _check_auth_business_status(payload: Any) -> None:
    if not isinstance(payload, dict):
        return
    code = payload.get("code")
    status = payload.get("status")
    if code in (401, "401", 403, "403") or status in (401, "401", 403, "403"):
        raise _AuthRevoked(f"业务码鉴权失败: code={code}, status={status}")

def _flatten_value(v: Any) -> str:
    """
    将任意单元格值转换为字符串。
    对 dict/list 使用 JSON 序列化，None 转为空字符串。
    用于统一 CSV 写入时的字段格式。
    """
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _extract_frequency(entity_name: str) -> str:
    """
    从 entityName 中提取频率并映射为英文标识。
    支持年/季/月/周/日等常见中文频率关键词。
    未匹配时返回 unknown。
    """
    # 频率映射字典
    frequency_map = {
        # 年度频率
        '年': 'yearly',
        '年度': 'yearly',
        # 季度频率
        '季度': 'quarterly',
        '季': 'quarterly',
        # 月度频率
        '月': 'monthly',
        '月度': 'monthly',
        # 周度频率
        '周': 'weekly',
        '周度': 'weekly',
        # 日度频率
        '日': 'daily',
        '日度': 'daily',
        '天': 'daily',
}
    
    match = re.search(r'[（(]([^）)]+)[）)]', entity_name)
    if match:
        freq_chinese = match.group(1)
        # 如果找到对应的英文翻译则返回，否则返回原始中文
        return frequency_map.get(freq_chinese, freq_chinese)
    return "unknown"


def _parse_macro_table(data_item: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    """
    解析宏观数据的table格式。

    根据实际返回数据格式：
    {
        "table": {
            "EMM00000015": ["140.2万亿", "134.8万亿", ...],
            "headName": ["数据来源", "2025", "2024", ...]
        },
        "nameMap": {
            "EMM00000015": "中国:GDP:现价(元)",
            "headNameSub": "数据来源"
        },
        "entityName": "GDP（年）"
    }

    Returns:
        (rows, frequency) - 解析出的数据行和频率
    """
    rows = []

    table = data_item.get("table", {})
    name_map = data_item.get("nameMap", {})
    entity_name = data_item.get("entityName", "")
 

    # 提取频率
    frequency = _extract_frequency(entity_name)

    if not table or not isinstance(table, dict):
        return rows, frequency

    # 获取列名（headName）
    headers = table.get("headName", [])
    if not headers:
        # 尝试其他可能的列名键
        headers = table.get("date", [])
        if not headers:
            return rows, frequency

    # 找出所有的指标键（排除headName、date等元数据键）
    exclude_keys = {"headName", "headNameSub", "date"}
    metric_keys = [k for k in table.keys() if k not in exclude_keys]

    if not metric_keys:
        return rows, frequency

    # 对于每个指标键，创建一行数据
    for metric_key in metric_keys:
        values = table.get(metric_key, [])
        if not values:
            continue

        # 获取指标名称（从nameMap或使用键名）
        metric_name = name_map.get(metric_key, metric_key)

        # 创建一行数据
        row = {
            "entity_name": entity_name,
            "indicator_code": metric_key,
            "indicator_name": metric_name,
            "frequency": frequency,  # 添加频率字段
        }

        # 将每个年份/字段的值添加到行中
        for i, header in enumerate(headers):
            if i < len(values):
                value = values[i]
                # 如果值是列表，可能需要特殊处理
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value) if value else ""
                row[header] = value

        rows.append(row)

    return rows, frequency


def _build_headers(api_key: str) -> Dict[str, str]:
    """
    构建宏观数据接口请求头。
    包含 em_api_key 与 JSON 内容类型。
    返回可直接用于 HTTP 请求的 headers 字典。
    """
    headers = {
        "em_api_key": api_key,
        "Content-Type": "application/json",
    }
    return headers

def _build_request_body(query: str) -> Dict[str, Any]:
    """
    构建 searchMacroData 接口请求体。
    自动生成 callId 与 userId，并携带查询文本。
    返回可直接发送的 JSON 对象。
    """
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    body = {
        "query": query,
        "toolContext": {
            "callId": call_id,
            "userInfo": {
                "userId": user_id
            }
        }
    }
    return body

def _write_csv_file(rows: List[Dict[str, Any]], frequency: str, unique_suffix: str, output_dir: Path) -> Tuple[Path, int]:
    """
    将指定频率的数据写入单个 CSV 文件。
    自动整理列顺序并优先展示关键字段与日期列。
    返回 (csv_path, row_count)。
    """
    if not rows:
        return None, 0

    # 列名：统一取所有出现过的键
    fieldnames_set: Dict[str, None] = {}
    for row in rows:
        for k in row:
            fieldnames_set[k] = None

    # 调整列的顺序，让重要字段靠前
    priority_fields = ["entity_name", "indicator_name", "indicator_code", "frequency", "数据来源"]
    fieldnames = []
    for field in priority_fields:
        if field in fieldnames_set:
            fieldnames.append(field)
            del fieldnames_set[field]

    # 将日期列排序
    date_fields = []
    other_fields = []
    for field in fieldnames_set.keys():
        # 判断是否是日期格式（年或年月日）
        if (field.isdigit() and len(field) == 4) or \
           (re.match(r'^\d{4}-\d{2}-\d{2}$', field)):  # 匹配 YYYY-MM-DD 格式
            date_fields.append(field)
        else:
            other_fields.append(field)

    # 日期降序排列（最新的在前）
    date_fields.sort(reverse=True)
    other_fields.sort()

    fieldnames.extend(other_fields)
    fieldnames.extend(date_fields)

    # 生成文件名
    csv_path = output_dir / f"mx_macro_data_{unique_suffix}_{frequency}.csv"

    # 写CSV
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _flatten_value(v) for k, v in row.items()})

    return csv_path, len(rows)


async def query_mx_macro_data(
    query: str,
    output_dir: Optional[Path] = None,  # Python 3.6 兼容
    api_base: Optional[str] = None,      # Python 3.6 兼容
) -> Dict[str, Any]:
    """
    通过文本查询宏观数据，将返回的JSON转为CSV并生成描述txt。

    Args:
        query: 自然语言查询，如「中国GDP」
        output_dir: 保存CSV和txt的目录；默认当前目录

    Returns:
        包含 csv_paths, description_path, row_counts, error(若有) 的字典
    """
    output_dir = output_dir or Path.cwd()
    output_dir = Path(output_dir)

    result: Dict[str, Any] = {
        "csv_paths": [],  # 改为列表，支持多个CSV文件
        "description_path": None,
        "row_counts": {},  # 频率 -> 行数
        "query": query,
    }

    auth = ensure_auth()
    if auth["status"] == AUTH_NEED_USER:
        result["need_auth"] = True
        result["authUrl"] = auth["auth_url"]
        result["apiKeyUrl"] = auth["api_key_url"]
        result["auth_message"] = (
            "尚未完成授权。请优先扫码授权，或通过 apiKeyUrl 手动复制 apikey。"
            "完成后重新发送原指令即可查询。"
        )
        return result
    if auth["status"] == AUTH_ERROR:
        result["error"] = auth.get("message", "授权流程出错")
        return result

    newly_obtained_key = auth.get("api_key") if auth.get("newly_obtained") else None
    if newly_obtained_key:
        result["remember_api_key"] = True
        result["api_key"] = newly_obtained_key

    api_key = newly_obtained_key or _load_em_api_key()
    if not api_key:
        result["error"] = "EM_API_KEY 落盘异常，请重新执行或检查 ~/.mx-skills/em_api_key"
        return result

    output_dir.mkdir(parents=True, exist_ok=True)
    unique_suffix = uuid.uuid4().hex[:8]
    try:
        headers = _build_headers(api_key)
        body = _build_request_body(query)
        api_base = DEFAULT_URL.rstrip("/")
        url = f"{api_base}{DEFAULT_PATH}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            payload = resp.json()
            _check_auth_business_status(payload)
            data = payload.get("data")


    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return _handle_auth_revoked(f"HTTP {e.response.status_code}: {e.response.text[:100]}", result)
        result["error"] = f"HTTP错误: {e.response.status_code} - {e.response.text[:200]}"
        return result
    except _AuthRevoked as e:
        return _handle_auth_revoked(str(e), result)
    except Exception as e:
        result["error"] = f"请求失败: {e!s}"
        return result

    # 解析返回的数据结构 - 按频率分组
    frequency_groups: Dict[str, List[Dict[str, Any]]] = {}
    description_parts = []

    # 检查可能的返回路径
    if isinstance(data, dict):
        # 包含dataTable字段（主要数据结构）
        data_list = data.get("dataTables", [])
        if data_list and isinstance(data_list, list):
            for item_list in data_list:

                # 解析table数据，同时获取频率
                rows, frequency = _parse_macro_table(item_list)

                if rows:
                    if frequency not in frequency_groups:
                        frequency_groups[frequency] = []
                    frequency_groups[frequency].extend(rows)

                    # 收集描述信息
                    entity_name = item_list.get("entityName", "")
                    title = item_list.get("title", "")

                    if entity_name:
                        description_parts.append(f"实体名称 [{frequency}]: {entity_name}")
                    if title:
                        description_parts.append(f"标题 [{frequency}]: {title}")

                    # 添加字段信息
                    field_set = item_list.get("fieldSet", [])
                    if field_set and isinstance(field_set, list) and len(field_set) > 0:
                        field = field_set[0]
                        data_source = field.get("dataSource", "")
                        unit_name = field.get("unitName", "")
                        if data_source:
                            description_parts.append(f"数据来源 [{frequency}]: {data_source}")
                        if unit_name:
                            description_parts.append(f"单位 [{frequency}]: {unit_name}")


    preferred_message = None
    if isinstance(data, dict):
        data_message = data.get("message")
        if isinstance(data_message, str) and data_message.strip():
            preferred_message = data_message.strip()
            if "检测到您的数据范围较大，由于系统限制，现为您返回的是精简后的部分数据" in preferred_message:
                preferred_message += (
                    "\n免费用户仅支持查询3年范围的数据。本次请求的时间范围超出了权限限制，"
                    "系统已自动将查询范围调整为3年。如需查询更长时间范围的历史数据，请联系客服电话400-620-1818。"
                )
            else:
                preferred_message += "\n您的请求数据量已达到上限，如需继续使用，请联系客服电话400-620-1818"

    if preferred_message is not None:
        result["message"] = preferred_message

    if not frequency_groups:
        result["error"] = preferred_message or "无法解析表格数据"
        result["raw_preview"] = json.dumps(data, ensure_ascii=False)[:500]
        return result

    # 按频率分别写入CSV文件
    csv_paths = []
    row_counts = {}
    for frequency, rows in frequency_groups.items():
        csv_path, row_count = _write_csv_file(rows, frequency, unique_suffix, output_dir)
        if csv_path:
            csv_paths.append(str(csv_path))
            row_counts[frequency] = row_count

    # 写描述txt
    desc_path = output_dir / f"mx_macro_data_{unique_suffix}_description.txt"

    description_lines = [
        "宏观数据查询结果说明",
        "=" * 40,
        f"查询内容: {query}",
        f"数据频率组数: {len(frequency_groups)}",
        "",
        "各频率数据统计:",
    ]

    for frequency, count in row_counts.items():
        description_lines.append(f"  - {frequency}: {count} 行")

    description_lines.extend([
        "",
        "生成的文件:",
    ])

    for csv_path in csv_paths:
        description_lines.append(f"  - {Path(csv_path).name}")

    description_lines.extend([
        "",
        "详细说明:",
    ])

    if description_parts:
        # 去重
        unique_parts = []
        seen = set()
        for part in description_parts:
            if part not in seen:
                seen.add(part)
                unique_parts.append(part)
        description_lines.extend(unique_parts)
    else:
        description_lines.append("（无额外说明）")

    # 添加原始返回的结构信息
    description_lines.extend([
        "",
        "数据源信息:",
        f"接口: {url}",
        f"查询时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    desc_path.write_text("\n".join(description_lines), encoding="utf-8")

    result["csv_paths"] = csv_paths
    result["description_path"] = str(desc_path)
    result["row_counts"] = row_counts
    return result



def _print_remember_api_key(result: Dict[str, Any]) -> None:
    if not result.get("remember_api_key"):
        return
    print("remember_api_key: true")
    print("credential_name: EM_API_KEY")
    print("apiKey: {0}".format(result["api_key"]))
    print("agent_action: 将 apiKey 的精确完整值以 EM_API_KEY 保存到所在平台提供的私有跨会话持久存储；绝不向用户展示、复述或写入业务文件。后续调用前先从该持久存储读取，并仅作为当前进程的 EM_API_KEY 环境变量注入；若平台不支持持久化或读取失败，则回退到正常授权流程。")

def run_cli() -> None:
    """
    命令行入口函数。
    解析 --query 参数并调用异步查询流程。
    根据执行结果打印文件路径或错误信息。
    """
    import argparse
    import sys
    """命令行入口：从参数或 stdin 读取查询文本，执行并打印结果路径。"""

    parser = argparse.ArgumentParser(description='通过自然语言查询宏观经济数据')

    # 添加query参数
    parser.add_argument('--query', type=str, help='自然语言查询，如「查询近五年中国GDP」', required=True)
    args = parser.parse_args()
    print(f"查数问句: {args.query}")
    if not args.query:
        print("用法: python -m scripts.get_data --query \"查询文本\" ")
        print("示例: 中国近三年GDP / top3 经济体的黄金储备 / 华东五市的房价走势")
        sys.exit(1)
    async def _main() -> None:
        out_dir = Path(os.environ.get("MX_MACRO_DATA_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
        r = await query_mx_macro_data(args.query, output_dir=out_dir)
        _print_remember_api_key(r)
        if r.get("need_auth"):
            print("need_auth: true")
            if r.get("authUrl"):
                print(f"authUrl: {r['authUrl']}")
                print(f"apiKeyUrl: {r.get('apiKeyUrl', AUTH_API_KEY_URL_FALLBACK)}")
            if r.get("auth_message"):
                print(r["auth_message"])
            print("完成后重新发送原指令即可，下次调用会自动落盘 EM_API_KEY 并查询。")
            sys.exit(10)
        if "error" in r:
            print(f"错误: {r['error']}", file=sys.stderr)
            if "raw_preview" in r:
                print(f"原始数据预览: {r['raw_preview']}", file=sys.stderr)
            sys.exit(2)
        if "message" in r:
            print(f"提示: {r['message']}")
        print(f"CSV: {r['csv_paths']}")
        print(f"描述: {r['description_path']}")
        print(f"行数: {r['row_counts']}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_main())
    loop.close()

if __name__ == "__main__":
    run_cli()
