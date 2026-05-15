"""
HTML 图表模块 - 参考 stock-quant 的 html 输出设计
生成交互式 K 线图、权益曲线、信号标注、交易明细
"""

import os
import json
import datetime


def _get_html_dir():
    """获取 HTML 输出目录"""
    from lib.settings import get
    html_dir = get('html_output_dir', 'html')
    if not os.path.isabs(html_dir):
        html_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), html_dir)
    os.makedirs(html_dir, exist_ok=True)
    return html_dir


def _make_candlestick_html(code, df, signals=None, trades=None, title=''):
    """生成 K 线图 + 信号 + 交易标注的 HTML"""

    # 准备数据
    dates = []
    for idx in df.index:
        try:
            dates.append(str(idx)[:10])
        except Exception:
            dates.append(str(idx))

    ohlcv = {
        'date': dates,
        'open': [round(float(x), 2) for x in df['open'].values] if 'open' in df.columns else [],
        'high': [round(float(x), 2) for x in df['high'].values] if 'high' in df.columns else [],
        'low': [round(float(x), 2) for x in df['low'].values] if 'low' in df.columns else [],
        'close': [round(float(x), 2) for x in df['close'].values],
        'volume': [int(x) for x in df['volume'].values] if 'volume' in df.columns else [],
    }

    # 信号数据
    buy_signals = []
    sell_signals = []
    if signals is not None:
        for i, sig in enumerate(signals):
            if sig == 1 and i < len(dates):
                buy_signals.append({'date': dates[i], 'price': ohlcv['low'][i] * 0.99 if ohlcv['low'] else 0})
            elif sig == -1 and i < len(dates):
                sell_signals.append({'date': dates[i], 'price': ohlcv['high'][i] * 1.01 if ohlcv['high'] else 0})

    # 交易数据
    trade_markers = []
    if trades:
        for t in trades:
            if t.get('date') and t.get('price'):
                trade_markers.append({
                    'date': t['date'],
                    'price': round(float(t['price']), 2),
                    'type': t.get('type', ''),
                    'reason': t.get('reason', ''),
                    'pnl_pct': round(float(t.get('pnl_pct', 0)), 2),
                    'qty': int(t.get('qty', 0)),
                })

    # 构建 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{code} - {title or '量化分析报告'}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: #e0e0e0; }}
  .header {{ text-align: center; margin-bottom: 20px; }}
  .header h1 {{ color: #fff; margin: 0; font-size: 24px; }}
  .header p {{ color: #888; margin: 5px 0; }}
  .chart-container {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
  .chart {{ width: 100%; height: 500px; }}
  .vol-chart {{ width: 100%; height: 150px; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px; }}
  .stat-card {{ background: #16213e; border-radius: 8px; padding: 16px; text-align: center; }}
  .stat-value {{ font-size: 28px; font-weight: bold; }}
  .stat-label {{ color: #888; font-size: 12px; margin-top: 4px; }}
  .positive {{ color: #22c55e; }}
  .negative {{ color: #ef4444; }}
  .neutral {{ color: #f59e0b; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid #333; }}
  th {{ color: #888; font-weight: normal; font-size: 12px; }}
  td {{ font-size: 13px; }}
  tr:hover {{ background: #1e293b; }}
  .trade-buy {{ color: #22c55e; }}
  .trade-sell {{ color: #ef4444; }}
</style>
</head>
<body>

<div class="header">
  <h1>{code} - {title}</h1>
  <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>

<div class="chart-container">
  <div id="kline" class="chart"></div>
  <div id="volume" class="vol-chart"></div>
</div>

<div id="stats-container" class="stats"></div>

<div class="chart-container" id="trades-section" style="display:none;">
  <h3 style="margin-top:0;">📋 交易明细</h3>
  <table id="trades-table">
    <thead>
      <tr>
        <th style="text-align:left">日期</th><th>方向</th><th>价格</th><th>数量</th><th>盈亏%</th><th>原因</th>
      </tr>
    </thead>
    <tbody id="trades-body"></tbody>
  </table>
</div>

<script>
const ohlcv = {json.dumps(ohlcv, ensure_ascii=False)};
const buySignals = {json.dumps(buy_signals, ensure_ascii=False)};
const sellSignals = {json.dumps(sell_signals, ensure_ascii=False)};
const tradeMarkers = {json.dumps(trade_markers, ensure_ascii=False)};

// K 线图
const klineChart = echarts.init(document.getElementById('kline'));
const klineOption = {{
  backgroundColor: '#1a1a2e',
  tooltip: {{
    trigger: 'axis',
    axisPointer: {{ type: 'cross' }},
    backgroundColor: 'rgba(20,20,40,0.9)',
    borderColor: '#333',
    textStyle: {{ color: '#fff' }}
  }},
  legend: {{ data: ['K线', 'MA5', 'MA20', '买入信号', '卖出信号'], textStyle: {{ color: '#888' }} }},
  grid: {{ left: '8%', right: '4%', bottom: '15%', top: '10%' }},
  xAxis: {{
    type: 'category',
    data: ohlcv.date,
    axisLine: {{ lineStyle: {{ color: '#333' }} }},
    axisLabel: {{ color: '#888' }}
  }},
  yAxis: {{
    scale: true,
    splitLine: {{ lineStyle: {{ color: '#222' }} }},
    axisLabel: {{ color: '#888' }}
  }},
  dataZoom: [
    {{ type: 'inside', start: 60, end: 100 }},
    {{ type: 'slider', bottom: 0, height: 20, borderColor: '#333', fillerColor: 'rgba(100,100,200,0.2)' }}
  ],
  series: [
    {{
      name: 'K线',
      type: 'candlestick',
      data: ohlcv.open.map((o, i) => [o, ohlcv.close[i], ohlcv.low[i], ohlcv.high[i]]),
      itemStyle: {{
        color: '#22c55e',
        color0: '#ef4444',
        borderColor: '#22c55e',
        borderColor0: '#ef4444'
      }}
    }},
    {{
      name: 'MA5',
      type: 'line',
      data: calcMA(ohlcv.close, 5),
      lineStyle: {{ width: 1, color: '#f59e0b' }},
      symbol: 'none'
    }},
    {{
      name: 'MA20',
      type: 'line',
      data: calcMA(ohlcv.close, 20),
      lineStyle: {{ width: 1, color: '#3b82f6' }},
      symbol: 'none'
    }},
    {{
      name: '买入信号',
      type: 'scatter',
      data: buySignals.map(s => [ohlcv.date.indexOf(s.date), s.price]),
      symbol: 'triangle',
      symbolSize: 10,
      itemStyle: {{ color: '#22c55e' }}
    }},
    {{
      name: '卖出信号',
      type: 'scatter',
      data: sellSignals.map(s => [ohlcv.date.indexOf(s.date), s.price]),
      symbol: 'triangle',
      symbolSize: 10,
      symbolRotate: 180,
      itemStyle: {{ color: '#ef4444' }}
    }},
    // 交易标注
    {{
      name: '买入',
      type: 'scatter',
      data: tradeMarkers.filter(t => t.type === 'buy').map(t => [ohlcv.date.indexOf(t.date), t.price * 0.98]),
      symbol: 'pin',
      symbolSize: 20,
      itemStyle: {{ color: '#22c55e' }},
      label: {{ show: true, position: 'bottom', fontSize: 9, color: '#22c55e',
        formatter: p => tradeMarkers.filter(t => t.type === 'buy')[p.dataIndex].reason
      }}
    }},
    {{
      name: '卖出',
      type: 'scatter',
      data: tradeMarkers.filter(t => t.type === 'sell').map(t => [ohlcv.date.indexOf(t.date), t.price * 1.02]),
      symbol: 'pin',
      symbolSize: 20,
      itemStyle: {{ color: '#ef4444' }},
      label: {{ show: true, position: 'top', fontSize: 9, color: '#ef4444',
        formatter: p => {{
          const t = tradeMarkers.filter(t2 => t2.type === 'sell')[p.dataIndex];
          return t.reason + ' ' + (t.pnl_pct > 0 ? '+' : '') + t.pnl_pct + '%';
        }}
      }}
    }}
  ]
}};
klineChart.setOption(klineOption);

// 成交量图
const volChart = echarts.init(document.getElementById('volume'));
const volColors = ohlcv.close.map((c, i) => {{
  if (i === 0) return '#666';
  return c >= ohlcv.close[i-1] ? 'rgba(34,197,94,0.6)' : 'rgba(239,68,68,0.6)';
}});
volChart.setOption({{
  backgroundColor: '#1a1a2e',
  grid: {{ left: '8%', right: '4%', bottom: '5%', top: '5%' }},
  xAxis: {{ type: 'category', data: ohlcv.date, axisLine: {{ lineStyle: {{ color: '#333' }} }}, axisLabel: {{ show: false }} }},
  yAxis: {{ splitLine: {{ show: false }}, axisLabel: {{ color: '#666', formatter: v => (v/1e6).toFixed(0)+'M' }} }},
  series: [{{
    type: 'bar',
    data: ohlcv.volume.map((v, i) => ({{ value: v, itemStyle: {{ color: volColors[i] }} }})),
  }}]
}});

// 联动
klineChart.on('dataZoom', function(params) {{
  const range = klineChart.getOption().dataZoom[0];
  volChart.dispatchAction({{ type: 'dataZoom', start: range.start, end: range.end }});
}});

// 计算MA
function calcMA(data, n) {{
  const result = [];
  for (let i = 0; i < data.length; i++) {{
    if (i < n - 1) {{ result.push('-'); continue; }}
    let sum = 0;
    for (let j = 0; j < n; j++) sum += data[i - j];
    result.push((sum / n).toFixed(2));
  }}
  return result;
}}

// 交易明细表格
if (tradeMarkers.length > 0) {{
  document.getElementById('trades-section').style.display = 'block';
  const tbody = document.getElementById('trades-body');
  tradeMarkers.forEach(t => {{
    const row = document.createElement('tr');
    const cls = t.type === 'buy' ? 'trade-buy' : 'trade-sell';
    const dir = t.type === 'buy' ? '买入' : '卖出';
    row.innerHTML = `<td style="text-align:left">${{t.date}}</td><td class="${{cls}}">${{dir}}</td><td>${{t.price.toFixed(2)}}</td><td>${{t.qty}}</td><td class="${{cls}}">${{t.pnl_pct > 0 ? '+' : ''}}${{t.pnl_pct}}%</td><td>${{t.reason}}</td>`;
    tbody.appendChild(row);
  }});
}}

// 响应式
window.addEventListener('resize', () => {{
  klineChart.resize();
  volChart.resize();
}});
</script>

</body>
</html>"""
    return html


def save_backtest_chart(code, df, result, strategy_name='', signals=None):
    """
    保存回测结果为 HTML 图表

    Parameters
    ----------
    code : str - 股票代码
    df : DataFrame - K线数据
    result : BacktestResult - 回测结果
    strategy_name : str - 策略名称
    signals : array - 信号数组

    Returns
    -------
    str - HTML 文件路径
    """
    d = result.to_dict()
    title = f"回测报告 - {strategy_name}" if strategy_name else "回测报告"

    html = _make_candlestick_html(
        code, df,
        signals=signals,
        trades=result.trades,
        title=title,
    )

    # 在 HTML 末尾追加回测统计
    stats_html = f"""
<div class="stats" style="margin: 20px auto; max-width: 1000px;">
  <div class="stat-card"><div class="stat-value {'positive' if d['total_return'] > 0 else 'negative'}">{d['total_return']:+.2f}%</div><div class="stat-label">策略总收益</div></div>
  <div class="stat-card"><div class="stat-value {'positive' if d['annual_return'] > 0 else 'negative'}">{d['annual_return']:+.2f}%</div><div class="stat-label">年化收益</div></div>
  <div class="stat-card"><div class="stat-value negative">{d['max_drawdown']:.2f}%</div><div class="stat-label">最大回撤</div></div>
  <div class="stat-card"><div class="stat-value {'positive' if d['sharpe_ratio'] > 1 else 'neutral'}">{d['sharpe_ratio']:.4f}</div><div class="stat-label">夏普比率</div></div>
  <div class="stat-card"><div class="stat-value">{d['win_rate']:.1f}%</div><div class="stat-label">胜率</div></div>
  <div class="stat-card"><div class="stat-value">{d['total_trades']}</div><div class="stat-label">交易次数</div></div>
  <div class="stat-card"><div class="stat-value {'positive' if d['final_capital'] > d['initial_capital'] else 'negative'}">{d['final_capital']:,.0f}</div><div class="stat-label">最终资金</div></div>
  <div class="stat-card"><div class="stat-value neutral">{d['buy_hold_return']:+.2f}%</div><div class="stat-label">买入持有收益</div></div>
</div>
<div style="text-align:center; padding: 20px; color: #666; font-size: 12px;">
  ⚠️ 以上分析仅供参考，不构成投资建议 | 由 quant-china 生成
</div>
"""
    # 在 </body> 前插入统计面板
    html = html.replace('</body>', stats_html + '</body>')

    # 保存文件
    html_dir = _get_html_dir()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_code = code.replace('.', '_')
    filename = f"{safe_code}_{strategy_name}_{timestamp}.html"
    filepath = os.path.join(html_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return os.path.abspath(filepath)


def save_analyze_chart(code, df, all_results, signals_map=None):
    """
    保存综合分析为 HTML（多策略回测对比）

    Parameters
    ----------
    code : str - 股票代码
    df : DataFrame - K线数据
    all_results : dict - {strategy_name: BacktestResult}
    signals_map : dict - {strategy_name: signals_array}

    Returns
    -------
    str - HTML 文件路径
    """
    html = _make_candlestick_html(
        code, df,
        signals=signals_map.get('ensemble') if signals_map else None,
        title='综合分析报告',
    )

    # 追加多策略回测对比表
    rows_html = ''
    for name, result in all_results.items():
        d = result.to_dict()
        cls_r = 'positive' if d['total_return'] > 0 else 'negative'
        cls_s = 'positive' if d['sharpe_ratio'] > 1 else ('neutral' if d['sharpe_ratio'] > 0 else 'negative')
        rows_html += f"""<tr>
          <td style="text-align:left;font-weight:bold">{name}</td>
          <td class="{cls_r}">{d['total_return']:+.2f}%</td>
          <td class="{cls_r}">{d['annual_return']:+.2f}%</td>
          <td class="negative">{d['max_drawdown']:.2f}%</td>
          <td class="{cls_s}">{d['sharpe_ratio']:.4f}</td>
          <td>{d['win_rate']:.1f}%</td>
          <td>{d['total_trades']}</td>
        </tr>"""

    stats_html = f"""
<div style="margin: 20px auto; max-width: 1000px; background: #1a1a2e; border-radius: 12px; padding: 20px;">
  <h3 style="margin-top:0;">🧪 多策略回测对比</h3>
  <table>
    <thead>
      <tr><th style="text-align:left">策略</th><th>总收益</th><th>年化</th><th>最大回撤</th><th>夏普</th><th>胜率</th><th>交易数</th></tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
<div style="text-align:center; padding: 20px; color: #666; font-size: 12px;">
  ⚠️ 以上分析仅供参考，不构成投资建议 | 由 quant-china 生成
</div>
"""
    html = html.replace('</body>', stats_html + '</body>')

    html_dir = _get_html_dir()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_code = code.replace('.', '_')
    filename = f"{safe_code}_analyze_{timestamp}.html"
    filepath = os.path.join(html_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return os.path.abspath(filepath)
