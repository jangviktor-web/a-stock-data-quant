"""
集中化配置管理 - 参考 stock-quant 的 settings.py 设计
命令行参数优先，config.yaml 缺省值兜底
"""

import os
import base64
import yaml

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
