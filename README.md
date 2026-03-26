# AlphaTransformer

Quantitative stock alpha prediction — Walk-Forward 验证框架 + FastAPI 推理服务。

## 模型权重

`Stock Forecast/checkpoints/best.pt` — **PatchTSTHybrid**（2.7MB）
- PatchEmbedding → 2×TransformerEncoder → CrossAssetAttention → RevIN → GRN → Head
- 输入: `[Batch, Assets=55, History=60, Features=40]`
- 输出: 每只股票的 alpha 得分（越高越看涨）

## 快速启动

```bash
cd "d:/transformer/Stock Forecast"
conda activate graduation_design

# 推荐方式（带 checkpoint 检查）
python run_api.py

# 或直接用 uvicorn（需先确认 Lib/site-packages 在 sys.path）
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

**API 文档**: 启动后访问 http://localhost:8000/docs

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 服务健康检查（不触发模型加载） |
| `/api/v1/predict` | POST | 输入 OHLCV → 输出 Top-N 推荐名单 |
| `/api/v1/backtest/report` | GET | 最新回测报告（指标 + Base64 图表） |

## 研究脚本

```bash
# Walk-Forward 验证（LightGBM + Vol Penalty + 多组合）
python run_walkforward_fixed.py

# 回测（Long-Short, hold_days=5）
python run_walkforward_backtest.py

# 最终评估（测试集）
python run_final_evaluation.py

# 结果汇总
python run_final_summary.py
```

## 依赖

```
conda activate graduation_design
pip install -r requirements.txt
```

## 项目结构

```
Stock Forecast/
├── api/
│   ├── server.py        ← FastAPI 主服务（3 个接口）
│   ├── predictor.py      ← AlphaPredictor 单例推理引擎
│   ├── preprocessing.py ← 推理预处理（特征工程 + 滚动归一化）
│   └── schemas.py       ← Pydantic 数据模型
├── checkpoints/
│   └── best.pt          ← 已训练模型权重（PatchTSTHybrid）
├── configs/
│   └── config.yaml      ← 主配置文件
├── data/
│   ├── dataset.py        ← StockDataset（特征标准化 + target 构建）
│   ├── feature_engineering.py  ← 特征工程
│   └── preprocess.py     ← 滚动归一化
├── models/
│   ├── alpha_transformer.py ← PatchTSTHybrid 模型定义
│   ├── light_alpha_net.py    ← LightAlphaNet（备选）
│   └── lightgbm_rank.py      ← LambdaRank 基线
└── evaluation/
    └── backtest.py      ← 回测引擎
```
