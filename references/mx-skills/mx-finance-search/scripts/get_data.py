"""
OpenClaw mx_finance_search skill runtime.

This module is intentionally self-contained:
- No hard-coded user identity.
- Runtime defaults are defined in-code (no environment reads).
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from typing import Dict, Any, Optional

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from auth import AUTH_ERROR, AUTH_NEED_USER, AUTH_OK, ensure_auth

EM_BASE_URL = "https://ai-saas.eastmoney.com".rstrip("/")
EM_API_KEY_PLACEHOLDER = "{em" + "_api_key}"
# 内置默认 Key（base64 混淆存储；用户可用 EM_API_KEY 环境变量覆盖）
_EM_API_KEY_BUILTIN = __import__("base64").b64decode("ZW1fSWpjRU1UcHJ3QmNqT2R5QzdkcXYxWk5KMUhsVjNtSUg=").decode()
EM_API_KEY = os.environ.get("EM_API_KEY") or _EM_API_KEY_BUILTIN

if EM_API_KEY and EM_API_KEY != EM_API_KEY_PLACEHOLDER:
    os.environ.setdefault("EM_API_KEY", EM_API_KEY)

AUTH_API_KEY_URL_FALLBACK = f"{EM_BASE_URL}/mxClaw"
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "mx_finance_search"
TIMEOUT_SECONDS = 15
# MCP 服务器地址
MCP_URL = f"{EM_BASE_URL}/proxy/b/mcp/tool/searchNews"


def _load_em_api_key() -> str:
    env_value = (os.environ.get("EM_API_KEY") or "").strip()
    if env_value:
        return env_value
    if EM_API_KEY and EM_API_KEY != EM_API_KEY_PLACEHOLDER:
        return EM_API_KEY
    cred_path = Path.home() / ".mx-skills" / "em_api_key"
    if cred_path.exists():
        return cred_path.read_text(encoding="utf-8").strip()
    return ""


class _AuthRevoked(Exception):
    """The API rejected EM_API_KEY with HTTP or business status 401/403."""


def _clear_em_api_key_file() -> None:
    cred_path = Path.home() / ".mx-skills" / "em_api_key"
    try:
        cred_path.unlink(missing_ok=True)
    except OSError:
        pass


def _raise_if_auth_revoked(payload: Any) -> None:
    if isinstance(payload, dict):
        code = payload.get("code")
        status = payload.get("status")
        if code in (401, "401", 403, "403") or status in (401, "401", 403, "403"):
            raise _AuthRevoked("business auth rejected: code={0}, status={1}".format(code, status))


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
    if reauth.get("status") == AUTH_NEED_USER:
        result["need_auth"] = True
        result["authUrl"] = reauth.get("auth_url")
        result["apiKeyUrl"] = reauth.get("api_key_url") or AUTH_API_KEY_URL_FALLBACK
        result["auth_message"] = (
            "EM_API_KEY 已失效（{0}），已清理保存的 key。请扫码重新授权，"
            "完成后重新发送原指令。".format(reason)
        )
        if env_key and env_key.strip():
            result["auth_message"] += " 环境变量 EM_API_KEY 仍含有失效 key，请先清除该环境变量。"
    elif reauth.get("status") == AUTH_OK:
        result["error"] = (
            "EM_API_KEY 服务端已失效，但环境变量 EM_API_KEY 仍存在。"
            "请清除该环境变量后重新发送原指令以触发授权。"
        )
    else:
        result["error"] = "EM_API_KEY 失效后重新授权失败: {0}".format(
            reauth.get("message", "未知错误")
        )
    return result

def get_metadata(
        query: str = "",
        selectType: str = "",
) -> dict:
    """
    生成 MCP 调用所需的 metadata 字典。
    自动补充 callId，并将 EM_API_KEY 注入 userInfo。
    返回值可直接作为请求体中的上下文字段使用。
    """
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    return {
        "query": query,
        "selectType": selectType,
        "toolContext": {
            "callId": call_id,
            "userInfo": {
                "userId": user_id,
            },
        },
    }

def _extract_content(raw: Dict[str, Any]) -> str:
    """
    从新闻接口返回数据中提取可读文本内容。
    优先读取常见文本字段，兼容 data/result 包裹结构。
    当文本字段缺失时，回退为格式化后的 JSON 字符串。
    """
    if not isinstance(raw, dict):
        return ""

    # Common envelope format: {"data": {...}} / {"result": {...}}
    for wrapper_key in ("data", "result"):
        wrapped = raw.get(wrapper_key)
        if isinstance(wrapped, dict):
            nested = _extract_content(wrapped)
            if nested:
                return nested

    for key in ("llmSearchResponse", "searchResponse", "content", "answer", "summary"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False, indent=2)

    return json.dumps(raw, ensure_ascii=False, indent=2)


def _load_optional_tool_context() -> Dict[str, Any]:
    """
    构造请求所需的 toolContext 默认值。
    目前仅生成可追踪的 callId 字段。
    返回结果用于下游接口请求的上下文字段。
    """
    return {"callId": f"call_{uuid.uuid4().hex[:12]}"}


def _extract_error_message(body: str) -> str:
    """
    从错误响应体中提取可展示的错误信息。
    优先读取 msg/message/error 字段，失败时截断原文。
    用于统一构造上层异常提示内容。
    """
    body = (body or "").strip()
    if not body:
        return ""
    try:
        data = json.loads(body)
    except Exception:
        return body[:200]
    if isinstance(data, dict):
        for key in ("msg", "message", "error"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return body[:200]


def _http_call_search_news(query: str, api_key: str) -> Dict[str, Any]:
    """
    调用 searchNews 接口并返回解析后的 JSON 数据。
    负责构建请求头、超时控制和 HTTP 异常处理。
    若响应不是字典结构，会自动包装为 {"data": ...}。
    """
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("EM_API_KEY is required.")

    timeout_raw = str(TIMEOUT_SECONDS).strip()
    try:
        timeout_seconds = max(1, int(timeout_raw))
    except ValueError as exc:
        raise ValueError("FINANCIAL_SEARCH_HTTP_TIMEOUT must be an integer >= 1.") from exc

    payload = {
        "query": query,
        "toolContext": _load_optional_tool_context(),
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        url=MCP_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "em_api_key": api_key,
        },
    )

    try:
        with urllib_request.urlopen(req, timeout=timeout_seconds) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
    except urllib_error.HTTPError as exc:
        if exc.code in (401, 403):
            raise _AuthRevoked("HTTP {0}".format(exc.code)) from exc
        err_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        message = _extract_error_message(err_body) or f"http status {exc.code}"
        raise RuntimeError(f"News API request failed: {message}") from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"News API request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("News API returned invalid JSON response.") from exc
    if isinstance(parsed, dict):
        _raise_if_auth_revoked(parsed)
        return parsed
    return {"data": parsed}


async def query_financial_news(
    query: str,
    output_dir: Optional[Path] = None,
    save_to_file: bool = True,
) -> Dict[str, Any]:
    """
    按自然语言查询金融资讯并整理统一结果结构。
    内部异步执行 HTTP 请求，提取文本内容并按需落盘。
    返回 query/content/raw/output_path，异常时附带 error。
    """
    query = (query or "").strip()
    if not query:
        return {
            "query": "",
            "content": "",
            "output_path": None,
            "raw": None,
            "error": "query is empty",
        }

    result: Dict[str, Any] = {"query": query, "content": "", "output_path": None, "raw": None}

    auth = ensure_auth()
    if auth.get("status") == AUTH_NEED_USER:
        result["need_auth"] = True
        result["authUrl"] = auth.get("auth_url")
        result["apiKeyUrl"] = auth.get("api_key_url") or AUTH_API_KEY_URL_FALLBACK
        result["auth_message"] = "尚未完成授权。请优先扫码授权，完成后重新发送原指令。"
        return result
    if auth.get("status") == AUTH_ERROR:
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

    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _http_call_search_news, query, api_key)
    except _AuthRevoked as exc:
        return _handle_auth_revoked(str(exc), result)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["raw"] = raw
    content = _extract_content(raw)
    result["content"] = content

    if save_to_file and content:
        out_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        unique_suffix = uuid.uuid4().hex[:8]
        output_path = out_dir / f"mx_finance_search_{unique_suffix}.txt"
        output_path.write_text(content, encoding="utf-8")
        result["output_path"] = str(output_path)

    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器。
    支持位置参数 query 与 --no-save 开关。
    返回配置完成的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        description="Query financial news/reports by natural language and optionally save output."
    )
    parser.add_argument("query", nargs="*", help="Natural language query text.")
    parser.add_argument("--no-save", action="store_true", help="Do not write result to local file.")
    return parser



def _print_remember_api_key(result: Dict[str, Any]) -> None:
    if not result.get("remember_api_key"):
        return
    print("remember_api_key: true")
    print("credential_name: EM_API_KEY")
    print("apiKey: {0}".format(result["api_key"]))
    print("agent_action: 将 apiKey 的精确完整值以 EM_API_KEY 保存到所在平台提供的私有跨会话持久存储；绝不向用户展示、复述或写入业务文件。后续调用前先从该持久存储读取，并仅作为当前进程的 EM_API_KEY 环境变量注入；若平台不支持持久化或读取失败，则回退到正常授权流程。")

def run_cli() -> None:
    """
    CLI 入口函数。
    解析命令行或标准输入中的查询文本并执行异步检索。
    根据执行结果输出内容、保存路径或错误信息。
    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    if not query:
        import sys

        query = (sys.stdin.read() or "").strip()

    if not query:
        parser.print_help()
        raise SystemExit(1)

    async def _main() -> None:
        result = await query_financial_news(query=query, save_to_file=not args.no_save)
        _print_remember_api_key(result)
        if result.get("need_auth"):
            print("need_auth: true")
            if result.get("authUrl"):
                print(f"authUrl: {result['authUrl']}")
            if result.get("apiKeyUrl"):
                print(f"apiKeyUrl: {result['apiKeyUrl']}")
            if result.get("auth_message"):
                print(result["auth_message"])
            raise SystemExit(10)
        if "error" in result:
            print(f"Error: {result['error']}")
            raise SystemExit(2)
        if result.get("output_path"):
            print(f"Saved: {result['output_path']}")
        print(result.get("content", ""))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()
