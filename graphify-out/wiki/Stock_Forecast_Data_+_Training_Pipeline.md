# Stock Forecast Data + Training Pipeline

> 74 nodes ， cohesion 0.04

## Key Concepts

- **Trainer** (17 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **.walk_forward_validate()** (13 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **.run()** (12 connections) ！ `d:\transformer\Stock Forecast\evaluation\backtest.py`
- **main()** (11 connections) ！ `d:\transformer\Stock Forecast\main_optimized.py`
- **Backtester** (10 connections) ！ `d:\transformer\Stock Forecast\evaluation\backtest.py`
- **FeatureEngineer** (10 connections) ！ `d:\transformer\Stock Forecast\data\feature_engineering.py`
- **DataModule** (9 connections) ！ `d:\transformer\Stock Forecast\utils\data_module.py`
- **process_ticker_group()** (8 connections) ！ `d:\transformer\Stock Forecast\data\feature_engineering.py`
- **.setup()** (7 connections) ！ `d:\transformer\Stock Forecast\utils\data_module.py`
- **StockDataset** (7 connections) ！ `d:\transformer\Stock Forecast\data\dataset.py`
- **Preprocessor** (7 connections) ！ `d:\transformer\Stock Forecast\data\preprocess.py`
- **process_ticker_data()** (7 connections) ！ `d:\transformer\Stock Forecast\data\preprocess.py`
- **.fit()** (7 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **.listnet_loss()** (7 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **.run_benchmark_comparison()** (5 connections) ！ `d:\transformer\Stock Forecast\evaluation\backtest.py`
- **add_cross_sectional_features_full()** (5 connections) ！ `d:\transformer\Stock Forecast\data\feature_engineering.py`
- **.simulate_trading()** (4 connections) ！ `d:\transformer\Stock Forecast\evaluation\backtest.py`
- **load_config()** (4 connections) ！ `d:\transformer\Stock Forecast\utils\config.py`
- **.add_cross_sectional_features()** (4 connections) ！ `d:\transformer\Stock Forecast\data\feature_engineering.py`
- **.load_checkpoint()** (4 connections) ！ `d:\transformer\trainer\trainer.py`
- **._evaluate_wf_fold()** (4 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **.save_checkpoint()** (4 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **._validate_fold()** (4 connections) ！ `d:\transformer\Stock Forecast\train\trainer.py`
- **._calc_metrics()** (3 connections) ！ `d:\transformer\Stock Forecast\evaluation\backtest.py`
- **feature_engineering.py** (3 connections) ！ `d:\transformer\Stock Forecast\data\feature_engineering.py`
- *... and 49 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `d:\transformer\Stock Forecast\data\dataset.py`
- `d:\transformer\Stock Forecast\data\feature_engineering.py`
- `d:\transformer\Stock Forecast\data\preprocess.py`
- `d:\transformer\Stock Forecast\evaluation\backtest.py`
- `d:\transformer\Stock Forecast\main_optimized.py`
- `d:\transformer\Stock Forecast\train\trainer.py`
- `d:\transformer\Stock Forecast\utils\config.py`
- `d:\transformer\Stock Forecast\utils\data_module.py`
- `d:\transformer\trainer\__init__.py`
- `d:\transformer\trainer\trainer.py`

## Audit Trail

- EXTRACTED: 195 (77%)
- INFERRED: 59 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*