"""
授权流程脚本 —— 幂等的 ensure 命令。

用法：
    python3 auth.py ensure

行为（惰性检查，不轮询、不等用户）：
    1) 已有可用 EM_API_KEY（环境变量或 ~/.mx-skills/em_api_key）→ exit 0
    2) 有未过期的 pending token → 调 result 接口：
         done → 落盘 key，exit 0；pending → 重打 authUrl，exit 10；invalid → 清理后走 3
    3) 无可复用 pending → 调 create，写 pending，打印 authUrl 与 apiKeyUrl，exit 10

已集成进 get_data.py，此处仅作调试入口。
凭据：~/.mx-skills/em_api_key；pending：~/.mx-skills/pending_auth.json
"""

import json
import os
import stat
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx

AUTH_BASE = os.environ.get("EM_AUTH_BASE", "https://ai-saas.eastmoney.com").rstrip("/")
EM_API_KEY_PLACEHOLDER = "{em" + "_api_key}"
EM_API_KEY_DEFAULT = "".strip()
CLIENT_ID = "mx-stocks-screener"
# 兜底默认值：create 接口正常会返回 apiKeyUrl，此值仅在接口未返回时使用
API_KEY_PAGE_URL = f"{AUTH_BASE}/mxClaw"
# pending token 最长约 1 个月，以接口返回的 expiresIn 为准
DEFAULT_EXPIRES_IN = 30 * 24 * 60 * 60

EXIT_OK = 0
EXIT_NEED_USER = 10
EXIT_ERROR = 2

# ensure_auth() 的状态码
AUTH_OK = "ok"
AUTH_NEED_USER = "need_user"
AUTH_ERROR = "error"


def _mx_dir() -> Path:
    return Path.home() / ".mx-skills"


def _key_path() -> Path:
    return _mx_dir() / "em_api_key"


def _pending_path() -> Path:
    return _mx_dir() / "pending_auth.json"


def _has_valid_key() -> bool:
    env_value = (os.environ.get("EM_API_KEY") or "").strip()
    if env_value:
        return True
    if EM_API_KEY_DEFAULT and EM_API_KEY_DEFAULT != EM_API_KEY_PLACEHOLDER:
        os.environ.setdefault("EM_API_KEY", EM_API_KEY_DEFAULT)
        return True
    p = _key_path()
    if p.exists() and p.read_text(encoding="utf-8").strip():
        return True
    return False


def _write_api_key(api_key: str) -> Path:
    path = _key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(api_key.strip() + "\n", encoding="utf-8")
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass
    return path


def _read_pending() -> Optional[Dict[str, Any]]:
    p = _pending_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        _clear_pending()
        return None
    if not isinstance(data, dict) or not data.get("token"):
        _clear_pending()
        return None
    if int(data.get("expiresAt", 0)) <= int(time.time()):
        _clear_pending()
        return None
    return data


def _write_pending(token: str, auth_url: str, api_key_url: str, expires_in: int) -> None:
    p = _pending_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token": token,
        "authUrl": auth_url,
        "apiKeyUrl": api_key_url,
        "expiresAt": int(time.time()) + int(expires_in) - 5,  # 留 5s buffer
    }
    p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass


def _clear_pending() -> None:
    p = _pending_path()
    if p.exists():
        try:
            p.unlink()
        except OSError:
            pass


def _unwrap(resp_json: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(resp_json, dict):
        raise RuntimeError(f"接口返回不是 JSON 对象: {resp_json!r}")
    code = resp_json.get("code")
    if code not in (0, "0", 200, "200", None):
        msg = resp_json.get("message") or resp_json.get("msg") or ""
        raise RuntimeError(f"接口业务错误 code={code} message={msg}")
    data = resp_json.get("data")
    if data is None:
        raise RuntimeError(f"接口返回缺少 data: {resp_json!r}")
    return data


def _api_create() -> Tuple[str, str, str, int]:
    r = httpx.post(
        f"{AUTH_BASE}/api/auth/token/create",
        json={"clientId": CLIENT_ID},
        timeout=30.0,
    )
    r.raise_for_status()
    data = _unwrap(r.json())
    token = data.get("token")
    auth_url = data.get("authUrl")
    if not token or not auth_url:
        raise RuntimeError(f"接口未返回 token 或 authUrl: {data}")
    api_key_url = data.get("apiKeyUrl") or API_KEY_PAGE_URL
    return token, auth_url, api_key_url, int(data.get("expiresIn", DEFAULT_EXPIRES_IN))


def _api_result(token: str) -> Tuple[str, Optional[str]]:
    r = httpx.post(
        f"{AUTH_BASE}/api/auth/token/result",
        json={"token": token},
        timeout=30.0,
    )
    r.raise_for_status()
    data = _unwrap(r.json())
    state = data.get("state") or "invalid"
    api_key = data.get("apiKey")
    return state, api_key


def _print_pending_hint(auth_url: str, api_key_url: str) -> None:
    print("尚未完成授权，请让用户任选一种方式：")
    print(f"  方式一（扫码授权）: 展示为二维码链接 → {auth_url}")
    print(f"  方式二（手动 apikey）: 访问 {api_key_url} 复制 apikey")
    print("完成后重新发送指令即可，Skill 会在下次调用时自动检测并落盘 EM_API_KEY。")


def ensure_auth() -> Dict[str, Any]:
    """
    幂等授权检查的纯逻辑：不打印、不 sys.exit，返回结构化结果。

    返回结构：
        {"status": AUTH_OK}
            已有可用 key（环境变量或落盘文件）。
        {"status": AUTH_OK, "api_key": str, "newly_obtained": True}
            刚从 pending token 取得并落盘 key；仅本次返回实际 key。
        {"status": AUTH_NEED_USER, "auth_url": str, "api_key_url": str}
            需要用户扫码或手动复制 apikey。可能来自未完成的 pending token，
            也可能是刚 create 的新 token。调用方应把 auth_url 展示给用户，
            让其完成后重新触发本流程——下次调用会自动检测 done 并落盘。
        {"status": AUTH_ERROR, "message": str}
            网络/接口错误，可重试。
    """
    if _has_valid_key():
        return {"status": AUTH_OK}

    # 优先复用未过期的 pending token
    pending = _read_pending()
    if pending is not None:
        try:
            state, api_key = _api_result(pending["token"])
        except Exception as exc:
            return {"status": AUTH_ERROR, "message": f"查询授权结果失败: {exc}"}

        if state == "done" and api_key:
            _write_api_key(api_key)
            _clear_pending()
            return {
                "status": AUTH_OK,
                "api_key": api_key,
                "newly_obtained": True,
            }
        if state == "pending":
            # 复用 create 时落盘的 authUrl / apiKeyUrl；兼容旧缓存里的 qrUrl 字段
            return {
                "status": AUTH_NEED_USER,
                "auth_url": pending.get("authUrl") or pending.get("qrUrl"),
                "api_key_url": pending.get("apiKeyUrl") or API_KEY_PAGE_URL,
            }
        # state == "invalid" 或未知：清理后往下走 create
        _clear_pending()

    # 需要新建 token
    try:
        token, auth_url, api_key_url, expires_in = _api_create()
    except Exception as exc:
        return {"status": AUTH_ERROR, "message": f"创建授权 token 失败: {exc}"}

    _write_pending(token, auth_url, api_key_url, expires_in)
    return {
        "status": AUTH_NEED_USER,
        "auth_url": auth_url,
        "api_key_url": api_key_url,
    }


def ensure() -> int:
    """CLI 入口：包装 ensure_auth()，负责打印与退出码。"""
    r = ensure_auth()
    status = r.get("status")
    if status == AUTH_OK:
        return EXIT_OK
    if status == AUTH_NEED_USER:
        _print_pending_hint(r["auth_url"], r["api_key_url"])
        return EXIT_NEED_USER
    print(f"错误: {r.get('message', '授权流程出错')}", file=sys.stderr)
    return EXIT_ERROR


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    if len(sys.argv) >= 2 and sys.argv[1] not in ("ensure", "-h", "--help"):
        print(f"未知命令: {sys.argv[1]}。仅支持 `ensure`。", file=sys.stderr)
        return EXIT_ERROR
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return EXIT_OK
    return ensure()


if __name__ == "__main__":
    sys.exit(main())
