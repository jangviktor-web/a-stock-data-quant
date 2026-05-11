# quant-china

A股量化分析工具箱 — 技术指标、形态识别、策略回测、多股对比、市场扫描

通过 OpenClaw 使用，或直接命令行调用。

## 用法

```bash
# 综合分析
python3 bin/quant.py analyze sh000001

# 多股对比
python3 bin/quant.py compare sh600519,sz000858,sh601212

# 多策略共振回测
python3 bin/quant.py backtest sh510500 --strategy ensemble

# 市场扫描
python3 bin/quant.py scan --strategy ma_cross
```

详见 [README.md](README.md)
