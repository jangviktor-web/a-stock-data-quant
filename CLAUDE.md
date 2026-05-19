# a-stock-data-quant 项目上下文

## 基本信息
- 项目: a-stock-data-quant v3.2.0
- 用途: A股量化分析工具箱
- Python: `python` (Windows环境，非 python3)
- 代理: 127.0.0.1:7888 (Clash)

## 常用命令
```bash
python bin/quant.py analyze sh600519                    # 综合分析
python bin/quant.py compare sh600519,sz000858           # 多股对比
python bin/quant.py backtest sh510500 --strategy ensemble --html  # 回测
python bin/quant.py realtime sh600519,sz000858          # 实时行情
python bin/quant.py em-diagnose sh600519                # AI诊断
python bin/quant.py scan --market A                     # 市场扫描
python bin/quant.py search 白银                          # 搜索股票
```

## 目录结构
- `bin/` - 主程序入口
- `lib/` - 核心库代码
- `cache/` - 数据缓存 (4小时过期)
- `html/` - HTML图表输出
- `results.tsv` - 扫描结果

## Git 推送
需要代理: `git -c http.proxy=http://127.0.0.1:7888 -c https.proxy=http://127.0.0.1:7888 push`

## 依赖
- akshare, numpy, pandas, requests

## 东方财富妙想 API
- Key: em_IjcEMTprwBcjOdyC7dqv1ZNJ1HlV3mIH
- 用途: AI金融分析 (em-diagnose 命令)
