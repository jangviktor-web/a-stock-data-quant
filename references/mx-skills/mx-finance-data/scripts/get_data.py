

import argparse
import asyncio
import json
import os
import re
import sys
import uuid
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
import pandas as pd

EM_API_KEY = os.environ.get("EM_API_KEY", "")
DEFAULT_SEARCH_API_URL = (
    "https://ai-saas.eastmoney.com/proxy/b/mcp/tool/searchData"
)
DEFAULT_ENTITY_API_URL = (
    "https://ai-saas.eastmoney.com/proxy/entity/saas"
)
MAX_ENTITY_TAGS = 500
DIRECT_QUERY_ENTITY_LIMIT = 5
ENTITY_TAG_FIELDS = ("entityId", "secuCode", "marketChar", "fullName", "market", "classCode")
_ENTITY_CODE_RE = re.compile(r"\(([0-9A-Z.]+\.[A-Z]+)\)")
_CREATABLE_NUM_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")
_WAN = Decimal("10000")
_YI = Decimal("100000000")
_WAN_YI = Decimal("1000000000000")
_CTR_TABLE_TYPE = "6"


def _get_default_output_dir() -> Path:
    """
    返回默认输出目录路径。
    默认目录为当前工作目录下的 miaoxiang/mx_finance_data。
    仅负责路径拼接，不创建目录。
    """
    return Path.cwd() / "miaoxiang" / "mx_finance_data"


def _flatten_value(v: Any) -> str:
    """
    将任意值规范为字符串表示。
    对 dict/list 使用 JSON 序列化，None 转为空字符串。
    用于统一写表与展示时的字段格式。
    """
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _to_decimal(value: Any) -> Optional[Decimal]:
    text = _flatten_value(value).strip().replace(",", "")
    if not text or not _CREATABLE_NUM_RE.match(text):
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _plain_strip(number: Decimal) -> str:
    text = format(number, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _format_number_in_range(number: Decimal, max_digit: int = 4) -> str:
    """对齐 NumberFormatter.formatNumberInRange：保留 max_digit 位有效数字。"""
    if number == 0:
        return "0"
    if max_digit <= 0:
        return _plain_strip(number)
    exponent = number.adjusted() - max_digit + 1
    quant = Decimal("1e%d" % exponent)
    rounded = number.quantize(quant, rounding=ROUND_HALF_UP)
    return _plain_strip(rounded)


def _format_big_number_with_ch_unit(number: Decimal) -> str:
    """对齐 NumberFormatter.formatBigNumberWithChUnitV2。"""
    abs_value = abs(number)
    if abs_value > _WAN_YI:
        return _format_number_in_range(number / _WAN_YI) + "万亿"
    if abs_value > _YI:
        return _format_number_in_range(number / _YI) + "亿"
    if abs_value > _WAN:
        return _format_number_in_range(number / _WAN) + "万"
    return _format_number_in_range(number)


def _has_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _entity_tag_from_block(block: Dict[str, Any], row_key: Any = None) -> Dict[str, Any]:
    name_map = block.get("entityName2TagMap")
    if isinstance(name_map, dict) and row_key is not None:
        mapped = name_map.get(str(row_key))
        if isinstance(mapped, dict):
            return mapped
    tag = block.get("entityTagDTO")
    if isinstance(tag, dict) and tag:
        return tag
    tags = block.get("entityTagDTOList")
    if isinstance(tags, list) and tags and isinstance(tags[0], dict):
        return tags[0]
    return {}


def _field_lookup(block: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    fields: List[Dict[str, Any]] = []
    single = block.get("field")
    if isinstance(single, dict):
        fields.append(single)
    field_set = block.get("fieldSet")
    if isinstance(field_set, list):
        fields.extend(item for item in field_set if isinstance(item, dict))
    for field in fields:
        for key in (field.get("returnSourceCode"), field.get("returnCode")):
            if key not in (None, ""):
                index[str(key)] = field
    return index


def _resolve_field(block: Dict[str, Any], data_key: Any, field_index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    key = str(data_key)
    if key in field_index:
        return field_index[key]
    field = block.get("field")
    if isinstance(field, dict):
        return field
    return {}


def _currency_unit(real_unit: str, entity_tag: Dict[str, Any]) -> str:
    if real_unit != "元":
        return real_unit
    market = str(entity_tag.get("marketChar") or "").upper()
    secu = str(entity_tag.get("secuCode") or "")
    if market == ".HK" and not secu.startswith("8"):
        return "港元"
    if market in {".US", ".O", ".N", ".A", ".AMEX"} or "US" in market:
        return "美元"
    return "元"


def _unit_suffix(field: Dict[str, Any], entity_tag: Dict[str, Any]) -> str:
    if str(field.get("quantType") or "") == "EDB":
        return ""
    unit_name = _flatten_value(field.get("unitName")).strip()
    if not unit_name:
        return ""
    unit_desc = _flatten_value(field.get("unitDesc")).strip()
    real_unit = unit_name
    if unit_desc:
        parts = unit_desc.split(":")
        real_unit = parts[1] if len(parts) > 1 else parts[0]
    if real_unit == "100%":
        real_unit = "%"
    elif real_unit == "1000‰":
        real_unit = "‰"
    if len(real_unit) == 2 and "基点" not in unit_desc:
        real_unit = real_unit[1:]
    return _currency_unit(real_unit, entity_tag)


def _format_display_value(
        raw: Any,
        *,
        field: Dict[str, Any],
        entity_tag: Dict[str, Any],
) -> str:
    """
    将 rawTable 单元格格式化为查数 table 的展示形态。
    rawTable 已是元/股等底层单位，不再按 unitDesc 做万/亿倍率还原。
    """
    text = _flatten_value(raw).strip()
    if not text or _has_chinese(text):
        return text
    number = _to_decimal(text)
    if number is None:
        return text

    unit_flag = str(field.get("unit") if field.get("unit") not in (None, "") else "1")
    table_type = str(field.get("tableType") or "")
    formatted = text

    if unit_flag == "2":
        formatted = _plain_strip(number.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    elif unit_flag != "0" and table_type != _CTR_TABLE_TYPE:
        formatted = _format_big_number_with_ch_unit(number)

    suffix = _unit_suffix(field, entity_tag)
    if suffix and suffix not in formatted:
        formatted += suffix
    return formatted


def _ordered_keys(table: Dict[str, Any], indicator_order: List[Any]) -> List[Any]:
    """
    按 indicator_order 生成指标键的输出顺序。
    先保留接口给定顺序，再追加未覆盖的数据键。
    返回去重后的最终键列表。
    """
    data_keys = [k for k in table.keys() if k != "headName"]
    key_map = {str(k): k for k in data_keys}
    preferred: List[Any] = []
    seen: Set[str] = set()
    for key in indicator_order:
        key_str = str(key)
        if key_str in key_map and key_str not in seen:
            preferred.append(key_map[key_str])
            seen.add(key_str)
    for key in data_keys:
        key_str = str(key)
        if key_str not in seen:
            preferred.append(key)
            seen.add(key_str)
    return preferred


def _normalize_values(raw_values: List[Any], expected_len: int) -> List[str]:
    """
    规范化一行指标值长度与类型。
    先将原始值转字符串，再按列数补空或截断。
    返回长度固定的字符串列表。
    """
    values = [_flatten_value(v) for v in raw_values]
    if len(values) < expected_len:
        values.extend([""] * (expected_len - len(values)))
    return values[:expected_len]


def _return_code_map(block: Dict[str, Any]) -> Dict[str, str]:
    """
    从数据块中提取指标代码映射表。
    兼容 returnCodeMap/returnCodeNameMap/codeMap 三种字段名。
    若未找到有效映射则返回空字典。
    """
    for key in ("returnCodeMap", "returnCodeNameMap", "codeMap"):
        data = block.get(key)
        if isinstance(data, dict):
            return {str(k): _flatten_value(v) for k, v in data.items()}
    return {}


def _format_indicator_label(key: str, name_map: Dict[str, Any], code_map: Dict[str, str]) -> str:
    """
    生成指标键对应的展示名称。
    优先使用 nameMap，其次使用 codeMap，最后回退原始 key。
    纯数字且无映射时返回空字符串。
    """
    mapped = name_map.get(key)
    if mapped is None and key.isdigit():
        mapped = name_map.get(int(key))
    if mapped not in (None, ""):
        return _flatten_value(mapped)
    mapped_code = code_map.get(key)
    if mapped_code not in (None, ""):
        return _flatten_value(mapped_code)
    if key.isdigit():
        return ""
    return key


def _table_to_rows_generic(table: Any, name_map: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    将通用表结构转换为行记录列表。
    兼容 list/dict 等多种 table 形态，并尽量推断列名。
    返回可直接写入 DataFrame 的字典行数组。
    """
    name_map = name_map or {}
    if isinstance(table, list):
        if not table:
            return []
        if isinstance(table[0], dict):
            rows = table
        else:
            rows = [
                dict(zip([f"column_{i}" for i in range(len(table[0]))], row))
                for row in table
            ]
    elif isinstance(table, dict):
        vals = [v for v in table.values() if isinstance(v, list)]
        if vals and all(isinstance(v, list) for v in table.values()):
            n = len(vals[0])
            if all(len(v) == n for v in vals):
                cols = list(table.keys())
                rows = [dict(zip(cols, [v[i] for v in table.values()])) for i in range(n)]
            else:
                rows = []
        else:
            cols = table.get("columns") or table.get("fields") or []
            rows_data = table.get("rows") or table.get("data") or []
            if not cols and rows_data:
                cols = [f"column_{i}" for i in range(len(rows_data[0]))]
            rows = [dict(zip(cols, r)) for r in rows_data]
    else:
        return []

    mapped = [{name_map.get(k, k): v for k, v in row.items()} for row in rows]
    return mapped


def _format_row_values(
        row: Dict[str, Any],
        fieldnames: List[str],
        *,
        data_key: Any,
        block: Dict[str, Any],
        field_index: Dict[str, Dict[str, Any]],
        label_col: Optional[str] = None,
) -> Dict[str, Any]:
    field = _resolve_field(block, data_key, field_index)
    default_tag = _entity_tag_from_block(block, data_key)
    formatted: Dict[str, Any] = {}
    for col in fieldnames:
        value = row.get(col, "")
        if col == label_col:
            formatted[col] = value
        else:
            entity_tag = _entity_tag_from_block(block, col) or default_tag
            formatted[col] = _format_display_value(value, field=field, entity_tag=entity_tag)
    return formatted


MD_PARTIAL_NOTICE = (
    "> **说明**：本 Markdown 仅为接口 `table` 字段的部分展示数据；"
    "完整数据请见同目录 Excel（`.xlsx`）文件。"
)


def _is_nonempty_payload(payload: Any) -> bool:
    """判断 table/rawTable 载荷是否非空。"""
    if payload is None:
        return False
    if isinstance(payload, (dict, list)):
        return bool(payload)
    return bool(payload)


def _table_data_volume(payload: Any) -> int:
    """
    估算表格载荷的数据量（单元格数），用于比较 table 与 rawTable 是否一致。
    """
    if not _is_nonempty_payload(payload):
        return 0
    if isinstance(payload, list):
        total = 0
        for item in payload:
            if isinstance(item, dict):
                total += len(item)
            elif isinstance(item, list):
                total += len(item)
            else:
                total += 1
        return total
    if isinstance(payload, dict):
        total = 0
        for key, value in payload.items():
            if key == "headName":
                continue
            if isinstance(value, list):
                total += len(value)
            else:
                total += 1
        return total
    return 0


def _payload_to_rows(
        table: Any,
        block: Dict[str, Any],
        *,
        apply_display_format: bool,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    将单个 table/rawTable 载荷解析为行数据与字段列表。
    apply_display_format=True 时按查数展示规则格式化（仅作 Markdown 在无 table 时的回退）。
    """
    name_map = block.get("nameMap") or {}
    if isinstance(name_map, list):
        name_map = {str(i): v for i, v in enumerate(name_map)}
    elif not isinstance(name_map, dict):
        name_map = {}
    field_index = _field_lookup(block)

    def _maybe_format(
            row: Dict[str, Any],
            fieldnames: List[str],
            *,
            data_key: Any,
            label_col: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not apply_display_format:
            return {col: _flatten_value(row.get(col, "")) for col in fieldnames}
        return _format_row_values(
            row,
            fieldnames,
            data_key=data_key,
            block=block,
            field_index=field_index,
            label_col=label_col,
        )

    if not isinstance(table, dict):
        raw_generic = _table_to_rows_generic(table, name_map)
        fieldnames = list(raw_generic[0].keys()) if raw_generic else []
        raw_rows = [{k: _flatten_value(v) for k, v in row.items()} for row in raw_generic]
        rows = [
            _maybe_format(row, fieldnames, data_key="")
            for row in raw_rows
        ]
        return rows, fieldnames

    headers = table.get("headName") or []
    if not isinstance(headers, list):
        headers = []
    order = _ordered_keys(table, block.get("indicatorOrder") or [])
    entity_name = _flatten_value(block.get("entityName") or "") or "指标"
    code_map = _return_code_map(block)
    data_key_count = len([key for key in table.keys() if key != "headName"])

    if len(headers) > 1 and data_key_count >= 1:
        fieldnames = [entity_name] + [_flatten_value(h) for h in headers]
        label_col = fieldnames[0]
        rows: List[Dict[str, Any]] = []
        for key in order:
            raw_values = table.get(key, [])
            if not isinstance(raw_values, list):
                raw_values = [raw_values]
            values = _normalize_values(raw_values, len(headers))
            label = _format_indicator_label(str(key), name_map, code_map)
            row = dict(zip(fieldnames, [label] + values))
            rows.append(_maybe_format(row, fieldnames, data_key=key, label_col=label_col))
        return rows, fieldnames

    if len(headers) == 1 and data_key_count >= 1:
        fieldnames = [entity_name, _flatten_value(headers[0])]
        label_col = fieldnames[0]
        rows = []
        for key in order:
            raw_values = table.get(key, [])
            value = raw_values[0] if isinstance(raw_values, list) and raw_values else raw_values
            label = _format_indicator_label(str(key), name_map, code_map)
            row = {fieldnames[0]: label, fieldnames[1]: _flatten_value(value)}
            rows.append(_maybe_format(row, fieldnames, data_key=key, label_col=label_col))
        return rows, fieldnames

    fallback_raw = [
        {k: _flatten_value(v) for k, v in row.items()}
        for row in _table_to_rows_generic(table, name_map)
    ]
    if fallback_raw:
        fieldnames = list(fallback_raw[0].keys())
        rows = [
            _maybe_format(row, fieldnames, data_key="")
            for row in fallback_raw
        ]
        return rows, fieldnames
    return [], []


def _table_to_rows(
        block: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str], List[str], bool]:
    """
    将单个 dataTableDTO 块转换为 Excel / Markdown 两套行数据。
    Excel 优先 rawTable；Markdown 优先接口 table 字段。
    返回 (excel_rows, md_rows, excel_fieldnames, md_fieldnames, md_partial)。
    """
    raw_payload = block.get("rawTable")
    display_payload = block.get("table")
    has_raw = _is_nonempty_payload(raw_payload)
    has_display = _is_nonempty_payload(display_payload)

    md_partial = False
    if has_raw and has_display:
        md_partial = _table_data_volume(display_payload) != _table_data_volume(raw_payload)

    if has_raw:
        excel_rows, excel_fieldnames = _payload_to_rows(
            raw_payload, block, apply_display_format=False
        )
    elif has_display:
        excel_rows, excel_fieldnames = _payload_to_rows(
            display_payload, block, apply_display_format=False
        )
    else:
        excel_rows, excel_fieldnames = [], []

    if has_display:
        md_rows, md_fieldnames = _payload_to_rows(
            display_payload, block, apply_display_format=False
        )
    elif has_raw:
        md_rows, md_fieldnames = _payload_to_rows(
            raw_payload, block, apply_display_format=True
        )
    else:
        md_rows, md_fieldnames = [], []

    return excel_rows, md_rows, excel_fieldnames, md_fieldnames, md_partial


def _normalize_entity_tag(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    从实体识别结果中提取批量查数所需的实体字段。
    查数接口需要完整实体信息，仅传 entityId 时只会返回首个实体数据。
    """
    entity_id = _flatten_value(raw.get("entityId")).strip()
    if not entity_id:
        raise ValueError("实体识别结果缺少 entityId")
    tag: Dict[str, Any] = {"entityId": entity_id}
    for field in ENTITY_TAG_FIELDS:
        if field == "entityId":
            continue
        value = raw.get(field)
        if value not in (None, ""):
            tag[field] = _flatten_value(value)
    return tag


def _build_multi_entity_query(indicators: str) -> str:
    """多实体查数时，将指标拼为「选定实体的{indicators}」格式。"""
    return f"选定实体的{indicators.strip()}"


def _build_request_body(
        query: str,
        entity_tags: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    构建 searchData 接口请求体。
    自动生成 callId，并写入 userInfo.userId。
    若提供 entity_tags（实体数 > 5 时），则在 toolContext 中写入 toolPreTaskResultList。
    返回可直接用于 HTTP JSON 请求的字典对象。
    """
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    tool_context: Dict[str, Any] = {
        "callId": call_id,
        "userInfo": {
            "userId": user_id,
        },
    }
    if entity_tags:
        tool_context["toolPreTaskResultList"] = [
            {
                "taskName": "股票基金筛选",
                "entityTagListMap": {
                    "1": entity_tags,
                },
            },
        ]

    return {
        "query": query,
        "toolContext": tool_context,
    }


def _extract_entity_tags_from_recognition_response(api_result: Any) -> List[Dict[str, Any]]:
    """
    从实体识别接口返回中提取实体 tag 列表。
    每个输入实体仅取第一个候选：entityMetricList 取每组首项，entityList 按顺序取各项。
    """
    if not isinstance(api_result, dict):
        return []

    data_node = api_result.get("data")
    if not isinstance(data_node, dict):
        return []

    raw_items: List[Dict[str, Any]] = []
    entity_metric_list = data_node.get("entityMetricList")
    if isinstance(entity_metric_list, list):
        for group in entity_metric_list:
            if isinstance(group, list) and group and isinstance(group[0], dict):
                raw_items.append(group[0])
    else:
        entity_list = data_node.get("entityList")
        if isinstance(entity_list, list):
            for item in entity_list:
                if isinstance(item, dict):
                    raw_items.append(item)

    tags: List[Dict[str, Any]] = []
    for item in raw_items:
        try:
            tags.append(_normalize_entity_tag(item))
        except ValueError:
            continue
    return tags


async def _recognize_entities(
        client: httpx.AsyncClient,
        query: str,
        api_key: str,
        entity_api_url: str,
) -> List[Dict[str, Any]]:
    """
    调用实体识别接口，将用户 query 作为 content 传入。
    每个实体仅取第一个候选，返回查数所需的实体 tag 列表。
    """
    resp = await client.post(
        entity_api_url,
        json={"content": query, "typeCodes": "002,006005,006006,006007,006001,006002,006009,006010,006011,006012,005101,005201,005202,005203,005204,016,001001,001002,003007,003005,003002,003003,003008,003006,003004,003001,003200,003100,007,008,004,010,003300,003400,003500,003600,003700"},
        headers={
            "Content-Type": "application/json",
            "em_api_key": api_key,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    status_err = _check_business_status(data)
    if status_err:
        raise RuntimeError(status_err)

    entity_tags: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for tag in _extract_entity_tags_from_recognition_response(data):
        entity_id = tag["entityId"]
        if entity_id not in seen:
            entity_tags.append(tag)
            seen.add(entity_id)

    return entity_tags[:MAX_ENTITY_TAGS]


def _safe_sheet_name(raw_name: Any, used_names: Set[str]) -> str:
    """
    生成合法且唯一的 Excel sheet 名称。
    会清洗非法字符、裁剪到 31 字符并处理重名后缀。
    返回最终可写入工作簿的 sheet 名。
    """
    name = _flatten_value(raw_name).strip() or "表"
    name = re.sub(r"[:\\/?*\[\]]", "_", name)
    if len(name) > 31:
        name = name[:31]

    base = name or "表"
    candidate = base
    idx = 2
    while candidate in used_names:
        suffix = f"_{idx}"
        if len(base) + len(suffix) > 31:
            candidate = base[: 31 - len(suffix)] + suffix
        else:
            candidate = base + suffix
        idx += 1
    used_names.add(candidate)
    return candidate


def _extract_entity_code(text: Any) -> Optional[str]:
    """从实体名称、sheet 名或列名中提取证券代码（如 300059.SZ）。"""
    match = _ENTITY_CODE_RE.search(_flatten_value(text))
    return match.group(1) if match else None


_GENERIC_ENTITY_HEADERS = frozenset({"指标", "指标名称"})


def _entity_identifier(text: Any) -> Optional[str]:
    """将实体名称规范为唯一标识：有证券代码时用 code，否则用 name。"""
    raw = _flatten_value(text).strip()
    if not raw:
        return None
    code = _extract_entity_code(raw)
    if code:
        return f"code:{code}"
    return f"name:{raw}"


def _first_col_has_entity_codes(fieldnames: List[str], rows: List[Dict[str, Any]]) -> bool:
    """首列行值是否包含证券代码（多实体横向对比表的典型结构）。"""
    if not fieldnames or not rows:
        return False
    first_col = fieldnames[0]
    return any(_extract_entity_code(row.get(first_col, "")) for row in rows)


def _extract_entity_from_sheet_title(sheet_name: Any) -> Optional[str]:
    """从 sheet 标题提取实体标识，如「中信期货有限公司的单季度.净利润」。"""
    text = _flatten_value(sheet_name).strip()
    if not text:
        return None
    ident = _entity_identifier(text)
    if ident and ident.startswith("code:"):
        return ident
    if "的" in text:
        prefix = text.split("的", 1)[0].strip()
        if len(prefix) >= 2:
            return _entity_identifier(prefix)
    return None


def _collect_entity_identifiers_from_table(table: Dict[str, Any]) -> Set[str]:
    """从单个结果表中收集唯一实体标识。"""
    identifiers: Set[str] = set()

    for source in (
        table.get("sheet_name"),
        *(table.get("fieldnames") or []),
    ):
        code = _extract_entity_code(source)
        if code:
            identifiers.add(f"code:{code}")

    fieldnames = table.get("fieldnames") or table.get("display_fieldnames") or []
    rows = table.get("rows") or table.get("display_rows") or []
    if fieldnames and rows:
        first_col = fieldnames[0]
        for row in rows:
            code = _extract_entity_code(row.get(first_col, ""))
            if code:
                identifiers.add(f"code:{code}")

    if identifiers:
        return identifiers

    entity_name = _flatten_value(table.get("entity_name") or "").strip()
    if entity_name and entity_name not in _GENERIC_ENTITY_HEADERS:
        identifiers.add(f"name:{entity_name}")

    if fieldnames and rows and not _first_col_has_entity_codes(fieldnames, rows):
        header = _flatten_value(fieldnames[0]).strip()
        if header and header not in _GENERIC_ENTITY_HEADERS:
            identifiers.add(f"name:{header}")

    if not identifiers:
        title_ident = _extract_entity_from_sheet_title(table.get("sheet_name"))
        if title_ident:
            identifiers.add(title_ident)

    return identifiers


def _count_returned_entities(tables: List[Dict[str, Any]]) -> int:
    """
    统计查数结果中覆盖的唯一实体数量。
    优先识别证券代码；非上市主体等无代码场景回退到公司名称。
    """
    identifiers: Set[str] = set()
    for table in tables:
        identifiers.update(_collect_entity_identifiers_from_table(table))
    return len(identifiers)


_GENERIC_SUCCESS_MESSAGES = frozenset({"成功", "ok", "OK", "success", "Success"})


def _is_generic_success_message(message: str) -> bool:
    """根级 message 常为业务状态（如「成功」），不作为用户提示输出。"""
    return message.strip() in _GENERIC_SUCCESS_MESSAGES


def _get_raw_data_message(api_result: Any) -> Optional[str]:
    """提取接口 message 原文（优先 data.message，其次非成功态的根级 message）。"""
    if not isinstance(api_result, dict):
        return None
    data_node = api_result.get("data")
    if isinstance(data_node, dict):
        data_message = data_node.get("message")
        if isinstance(data_message, str) and data_message.strip():
            return data_message.strip()
    root_message = api_result.get("message")
    if isinstance(root_message, str) and root_message.strip():
        msg = root_message.strip()
        if not _is_generic_success_message(msg):
            return msg
    return None


def _api_message_indicates_truncation(api_result: Any) -> bool:
    """接口 message 已说明截断/权限/数据量上限时，不再重复输出脚本侧完整性警告。"""
    raw = _get_raw_data_message(api_result)
    if not raw:
        return False
    indicators = (
        "截断",
        "精简后的部分数据",
        "检测到您的数据范围较大",
        "权限不足",
        "数据量已达到上限",
    )
    return any(key in raw for key in indicators)


def _build_completeness_warning(recognized: int, returned: int) -> Optional[str]:
    """多实体查数时，若返回实体数少于识别成功数，生成完整性警告文案。"""
    if recognized <= 0 or returned >= recognized:
        return None
    missing = recognized - returned
    return (
        f"警告: 查数结果仅覆盖 {returned}/{recognized} 个实体，缺失 {missing} 个。"
        f"当前一次请求的数据量过大，多指标或大范围查询可能触发接口返回上限，部分数据可能会有缺失，建议拆分 query 或分批查数。"
    )


def _extract_data_table_dto_list(api_result: Any) -> Tuple[Optional[List[Any]], Optional[str]]:
    """
    从接口返回中提取 dataTableDTOList 列表。
    兼容新结构 data.searchDataResultDTO.dataTableDTOList。
    同时兼容旧结构 dataTableDTOList 与 data.dataTableDTOList。
    """
    if not isinstance(api_result, dict):
        return None, "接口返回不是 JSON 对象"

    dto_list = api_result.get("dataTableDTOList")
    if isinstance(dto_list, list):
        return dto_list, None

    data_node = api_result.get("data")
    if isinstance(data_node, dict):
        search_result = data_node.get("searchDataResultDTO")
        if isinstance(search_result, dict):
            dto_list = search_result.get("dataTableDTOList")
            if isinstance(dto_list, list):
                return dto_list, None

        dto_list = data_node.get("dataTableDTOList")
        if isinstance(dto_list, list):
            return dto_list, None

    return None, "接口返回中无 data.searchDataResultDTO.dataTableDTOList"


def _check_business_status(api_result: Any) -> Optional[str]:
    """
    校验接口业务状态是否成功。
    兼容常见成功语义：code/status 为 200、0（含字符串）或缺失。
    返回 None 表示通过，否则返回可读错误信息。
    """
    if not isinstance(api_result, dict):
        return "接口返回不是 JSON 对象"

    code = api_result.get("code")
    status = api_result.get("status")
    success_values = (None, 0, 200, "0", "200")
    if code not in success_values or status not in success_values:
        message = _flatten_value(api_result.get("message") or "业务状态非成功")
        return f"接口业务错误: code={code}, status={status}, message={message}"
    return None


def _extract_preferred_message(api_result: Any) -> Optional[str]:
    """
    提取接口 message 并补充已知场景的说明文案。
    返回去除首尾空白后的字符串；无有效内容则返回 None。
    """
    raw = _get_raw_data_message(api_result)
    if not raw:
        return None
    message = raw
    if "检测到您的数据范围较大，由于系统限制，现为您返回的是精简后的部分数据" in message:
        message += (
            "\n免费用户仅支持查询3年范围的数据。本次请求的时间范围超出了权限限制，"
            "系统已自动将查询范围调整为3年。如需查询更长时间范围的历史数据，请联系客服电话400-620-1818。"
        )
    else:
        message += "\n您的请求数据量已达到上限，如需继续使用，请联系客服电话400-620-1818"
    return message


def _append_result_message(result: Dict[str, Any], message: str) -> None:
    """向 result 追加 message，已有内容时用换行拼接。"""
    existing = result.get("message")
    if existing:
        result["message"] = f"{existing}\n{message}"
    else:
        result["message"] = message


def _parse_data_table_response(
        api_result: Any,
) -> Tuple[List[Dict[str, Any]], List[str], int, Optional[str]]:
    """
    解析接口返回并抽取可落盘的表格数据。
    遍历 dataTableDTOList 生成 sheet 信息、条件说明与总行数。
    返回 (tables, condition_parts, total_rows, error) 四元组。
    """
    dto_list, extract_err = _extract_data_table_dto_list(api_result)
    if extract_err:
        return [], [], 0, extract_err
    if not dto_list:
        return [], [], 0, "接口返回的 dataTableDTOList 为空（多实体查数请确认 toolPreTaskResultList 格式正确）"

    condition_parts: List[str] = []
    tables: List[Dict[str, Any]] = []
    total_rows = 0
    used_sheet_names: Set[str] = set()

    for i, dto in enumerate(dto_list):
        if not isinstance(dto, dict):
            continue

        sheet_name = _safe_sheet_name(
            dto.get("title") or dto.get("inputTitle") or dto.get("entityName") or f"表{i + 1}",
            used_sheet_names,
        )
        condition = dto.get("condition")
        if condition is not None and condition != "":
            entity = dto.get("entityName") or sheet_name
            condition_parts.append(f"[{entity}]\n{condition}")

        rows, display_rows, fieldnames, display_fieldnames, md_partial = _table_to_rows(dto)
        if not rows and not display_rows:
            continue
        entity_name = _flatten_value(dto.get("entityName") or "").strip()
        tables.append(
            {
                "sheet_name": sheet_name,
                "rows": rows,
                "display_rows": display_rows,
                "fieldnames": fieldnames,
                "display_fieldnames": display_fieldnames,
                "entity_name": entity_name,
                "md_partial": md_partial,
            }
        )
        total_rows += len(rows) if rows else len(display_rows)

    if not tables:
        return [], condition_parts, 0, "dataTableDTOList 中无有效 table 数据"
    return tables, condition_parts, total_rows, None


def _escape_md_cell(value: Any) -> str:
    """转义 Markdown 表格单元格中的特殊字符。"""
    text = _flatten_value(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _rows_to_markdown_table(rows: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    """将行数据转为 Markdown 表格字符串。"""
    if not fieldnames:
        return ""
    header = "| " + " | ".join(_escape_md_cell(h) for h in fieldnames) + " |"
    separator = "| " + " | ".join("---" for _ in fieldnames) + " |"
    body_lines = [
        "| " + " | ".join(_escape_md_cell(row.get(col, "")) for col in fieldnames) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body_lines])


def _tables_to_markdown(tables: List[Dict[str, Any]]) -> str:
    """
    将多 sheet 表格数据转为 Markdown（使用接口 table 展示数据）。
    若任一 sheet 的 table 与 rawTable 数据量不一致，在文首标注部分展示说明。
    """
    sections: List[str] = []
    if any(table.get("md_partial") for table in tables):
        sections.append(MD_PARTIAL_NOTICE)

    for table in tables:
        sheet_name = _flatten_value(table["sheet_name"]).strip() or "数据"
        md_fieldnames = table.get("display_fieldnames") or table["fieldnames"]
        md_table = _rows_to_markdown_table(
            table.get("display_rows") or table["rows"],
            md_fieldnames,
        )
        if md_table:
            sheet_sections = [f"## {sheet_name}"]
            if table.get("md_partial"):
                sheet_sections.append(
                    "> 本表仅为部分展示数据，完整数据见 Excel 文件。"
                )
            sheet_sections.append(md_table)
            sections.append("\n\n".join(sheet_sections))
    return "\n\n".join(sections)


def _write_output_files(
        *,
        output_dir: Path,
        tables: List[Dict[str, Any]],
) -> Tuple[Path, Path]:
    """
    将解析后的查询结果写入本地文件。
    Excel 使用 rawTable 原始单位；Markdown 使用接口 table 展示数据。
    返回 (excel_path, md_path)。
    """
    unique_suffix = uuid.uuid4().hex[:8]
    file_path = output_dir / f"mx_finance_data_{unique_suffix}.xlsx"
    md_path = output_dir / f"mx_finance_data_{unique_suffix}.md"

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        wrote_sheet = False
        for table in tables:
            if not table.get("rows") or not table.get("fieldnames"):
                continue
            df = pd.DataFrame(table["rows"], columns=table["fieldnames"])
            df.to_excel(writer, sheet_name=table["sheet_name"], index=False)
            wrote_sheet = True
        if not wrote_sheet:
            # openpyxl 要求至少一个 sheet；无 raw 时用 Markdown 同源数据兜底
            for table in tables:
                rows = table.get("display_rows") or []
                fields = table.get("display_fieldnames") or table.get("fieldnames") or []
                if rows and fields:
                    df = pd.DataFrame(rows, columns=fields)
                    df.to_excel(writer, sheet_name=table["sheet_name"], index=False)
                    wrote_sheet = True
            if not wrote_sheet:
                pd.DataFrame({"说明": ["无有效表格数据"]}).to_excel(
                    writer, sheet_name="数据", index=False
                )

    md_path.write_text(_tables_to_markdown(tables), encoding="utf-8")
    return file_path, md_path


def _make_result_base(query_text: str) -> Dict[str, Any]:
    """
    构造统一的返回结果基础结构。
    初始化路径字段、行数字段与原始查询文本。
    用于成功与异常场景的统一返回格式。
    """
    return {
        "file_path": None,
        "csv_path": None,
        "description_path": None,  # 兼容字段，指向 Markdown 结果文件
        "md_path": None,
        "row_count": 0,
        "returned_entity_count": 0,
        "query": query_text,
    }


async def query_mx_finance_data(
        query: str,
        indicators: Optional[str] = None,
        output_dir: Optional[Path] = None,
        api_base: Optional[str] = None,
        entity_api_base: Optional[str] = None,
) -> Dict[str, Any]:
    """
    执行金融数据主查询流程并输出文件结果。
    先对 query 做实体识别：<=5 个实体直接查数，>5 个实体通过 entity tags 查数。
    多实体查数时，查数接口 query 使用「选定实体的{indicators}」。
    返回包含文件路径、行数及错误信息的结果字典。
    """
    output_dir = output_dir or _get_default_output_dir()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    url = api_base or DEFAULT_SEARCH_API_URL
    entity_api_url = entity_api_base or DEFAULT_ENTITY_API_URL
    result = _make_result_base(query)
    entity_tags: Optional[List[Dict[str, Any]]] = None

    try:
        api_key = EM_API_KEY
        async with httpx.AsyncClient(timeout=120.0) as client:
            recognized_tags = await _recognize_entities(
                client=client,
                query=query,
                api_key=api_key,
                entity_api_url=entity_api_url,
            )
            recognized_count = len(recognized_tags)
            result["recognized_entity_count"] = recognized_count
            if recognized_count > DIRECT_QUERY_ENTITY_LIMIT:
                if not indicators or not indicators.strip():
                    result["error"] = (
                        "多实体查数（识别实体数 > 5）缺少 --indicators，"
                        "请从 query 中提取金融指标后传入，用于构造「选定实体的{indicators}」"
                    )
                    return result
                entity_tags = recognized_tags
                result["use_entity_tags"] = True
                search_query = _build_multi_entity_query(indicators)
                result["indicators"] = indicators.strip()
                result["search_query"] = search_query
            else:
                result["use_entity_tags"] = False
                search_query = query
                if indicators and indicators.strip():
                    result["indicators"] = indicators.strip()
            body = _build_request_body(search_query, entity_tags=entity_tags)
            resp = await client.post(
                url,
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "em_api_key": api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        result["error"] = f"HTTP 错误: {exc.response.status_code} - {exc.response.text[:200]}"
        return result
    except Exception as exc:
        result["error"] = f"请求失败: {exc!s}"
        return result

    status_err = _check_business_status(data)
    if status_err:
        preferred_message = _extract_preferred_message(data)
        result["raw_response"] = json.dumps(data, ensure_ascii=False)
        result["error"] = preferred_message or status_err
        result["raw_preview"] = json.dumps(data, ensure_ascii=False)[:500]
        return result

    preferred_message = _extract_preferred_message(data)
    if preferred_message:
        _append_result_message(result, preferred_message)

    tables, condition_parts, total_rows, err = _parse_data_table_response(data)
    if err:
        preferred_message = _extract_preferred_message(data)
        result["raw_response"] = json.dumps(data, ensure_ascii=False)
        if preferred_message and err.startswith("接口返回的 dataTableDTOList 为空"):
            result["error"] = f"{preferred_message}\n（{err}）"
        else:
            result["error"] = preferred_message or err
        result["raw_preview"] = json.dumps(data, ensure_ascii=False)[:500]
        return result

    try:
        file_path_out, md_path = _write_output_files(
            output_dir=output_dir,
            tables=tables,
        )
    except ModuleNotFoundError as exc:
        result["error"] = f"写入 Excel 失败，缺少依赖: {exc.name}"
        return result
    except Exception as exc:
        result["error"] = f"写入结果文件失败: {exc!s}"
        return result

    result["file_path"] = str(file_path_out)
    result["csv_path"] = str(file_path_out)  # 兼容旧字段名
    result["md_path"] = str(md_path)
    result["description_path"] = str(md_path)
    result["row_count"] = total_rows
    result["md_partial"] = any(table.get("md_partial") for table in tables)
    result["returned_entity_count"] = _count_returned_entities(tables)
    recognized = result.get("recognized_entity_count", 0)
    completeness_warning = _build_completeness_warning(
        recognized, result["returned_entity_count"]
    )
    if completeness_warning and not _api_message_indicates_truncation(data):
        result["completeness_warning"] = completeness_warning
    return result


def _print_cli_result(result: Dict[str, Any]) -> None:
    """打印查数结果的全部日志信息。"""
    print(f"识别实体数: {result.get('recognized_entity_count', 0)}")

    if result.get("use_entity_tags"):
        print("查数模式: 多实体")
    else:
        print("查数模式: 直接查数")

    if result.get("indicators"):
        print(f"指标: {result['indicators']}")

    search_query = result.get("search_query") or result.get("query")
    if search_query:
        print(f"查数问句: {search_query}")

    print(f"返回实体数: {result.get('returned_entity_count', 0)}")

    message = result.get("message")
    if message:
        for line in message.splitlines():
            if line.strip():
                print(f"提示: {line.strip()}")

    completeness_warning = result.get("completeness_warning")
    if completeness_warning:
        for line in completeness_warning.splitlines():
            if line.strip():
                print(line.strip())

    file_path = result.get("file_path") or result.get("csv_path")
    if file_path:
        print(f"文件: {file_path}")

    md_path = result.get("md_path") or result.get("description_path")
    if md_path:
        print(f"Markdown: {md_path}")
        if result.get("md_partial"):
            print("Markdown说明: 仅为 table 部分展示数据，完整数据见 Excel")

    print(f"表格行数: {result.get('row_count', 0)}")


def _print_cli_error(result: Dict[str, Any]) -> None:
    """打印错误场景下的全部日志信息。"""
    if result.get("error"):
        print(f"错误: {result['error']}", file=sys.stderr)

    message = result.get("message")
    if message:
        for line in message.splitlines():
            if line.strip():
                print(f"提示: {line.strip()}", file=sys.stderr)

    completeness_warning = result.get("completeness_warning")
    if completeness_warning:
        for line in completeness_warning.splitlines():
            if line.strip():
                print(line.strip(), file=sys.stderr)

    if result.get("raw_preview"):
        print(f"响应预览: {result['raw_preview']}", file=sys.stderr)


async def query_mx_finance_data_direct(
        query: str,
        indicators: Optional[str] = None,
        output_dir: Optional[Path] = None,
        api_base: Optional[str] = None,
) -> Dict[str, Any]:
    """
    直接查询入口，兼容外部旧调用方式。
    参数与返回值与 query_mx_finance_data 保持一致。
    内部仅做透明转发，不额外处理逻辑。
    """
    return await query_mx_finance_data(
        query=query,
        indicators=indicators,
        output_dir=output_dir,
        api_base=api_base,
    )


def run_cli() -> None:
    """
    命令行执行入口。
    负责参数解析、异步调用主查询流程并输出执行结果。
    发生参数或运行错误时返回对应退出码。
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="金融数据查数：传入自然语言 query，自动识别实体后查数并导出 Excel 与 Markdown。"
    )
    parser.add_argument("--query", required=True, help="查询问句（自然语言，含实体与指标）")
    parser.add_argument(
        "--indicators",
        help="从 query 提取的金融指标；多实体查数时拼为「选定实体的{indicators}」",
    )
    args = parser.parse_args()
    query = args.query.strip()
    if not query:
        print("错误: 缺少查询文本", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    indicators = args.indicators.strip() if args.indicators else None

    out_dir = _get_default_output_dir()

    async def _main() -> None:
        try:
            result = await query_mx_finance_data(
                query=query,
                indicators=indicators,
                output_dir=out_dir,
            )
        except Exception as exc:
            print(f"错误: {exc}", file=sys.stderr)
            sys.exit(1)

        if "error" in result:
            _print_cli_error(result)
            sys.exit(2)

        _print_cli_result(result)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()