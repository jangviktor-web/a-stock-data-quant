"""
多数据源降级引擎

try_sources() 按顺序尝试数据源，失败时自动降级并打印提示
"""

import sys


def try_sources(sources, is_valid=None):
    """
    按顺序尝试数据源，返回第一个有效结果。

    Parameters
    ----------
    sources : list of (name: str, callable)
        数据源列表，按优先级排列
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
    short_err = error_msg.split(': ', 1)[-1] if ': ' in error_msg else error_msg
    print(f"  [降级] {from_source} 不可用({short_err[:40]})，尝试备用源 {to_source}", file=sys.stderr)
