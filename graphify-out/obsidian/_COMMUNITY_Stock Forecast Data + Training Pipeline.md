---
type: community
cohesion: 0.04
members: 74
---

# Stock Forecast Data + Training Pipeline

**Cohesion:** 0.04 - loosely connected
**Members:** 74 nodes

## Members
- [[.__getitem__()_2]] - code - d:\transformer\Stock Forecast\data\dataset.py
- [[.__init__()_47]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[.__init__()_53]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[.__init__()_44]] - code - d:\transformer\Stock Forecast\data\dataset.py
- [[.__init__()_45]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.__init__()_46]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[.__init__()_52]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.__len__()_1]] - code - d:\transformer\Stock Forecast\data\dataset.py
- [[._build_optimizer()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[._build_scheduler()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[._calc_metrics()]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[._diagnose_signals()]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[._evaluate_wf_fold()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[._plot_results()]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[._print_wf_summary()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[._reset_weights()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[._validate_fold()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.add_cross_sectional_features()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.add_momentum_features()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.add_pattern_features()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.add_target()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.add_technical_indicators()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.add_volatility_features()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[.clip_features()]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[.fill_missing()]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[.fit()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.listnet_loss()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.load_checkpoint()_1]] - code - d:\transformer\trainer\trainer.py
- [[.remove_anomalies()]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[.rolling_normalize()]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[.run()_1]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[.run_benchmark_comparison()]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[.save_checkpoint()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.setup()]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[.simulate_trading()]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[.test_dataloader()]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[.train_dataloader()]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[.val_dataloader()]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[.validate()_1]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[.walk_forward_validate()]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[Adaptive Long-Only Strategy         - Bot_k = 0 no shorting         - Market]] - rationale - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[Add cross-sectional (market-level) features on the FULL DataFrame.     Must be]] - rationale - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[All benchmarks use the same raw_returns.         Two-layer protection against n]] - rationale - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[Backtester]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[Calculate metrics using log returns throughout.         (1+r)T overflows float]] - rationale - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[Clip feature values to remove extreme outliers.]] - rationale - d:\transformer\Stock Forecast\data\preprocess.py
- [[DataModule]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[Evaluate current model on test set, compute all metrics.]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[FeatureEngineer]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[ListNet Loss (Listwise ranking).         Cross-entropy between predicted and ta]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[Market-level and cross-sectional features.         MUST be called AFTER all tic]] - rationale - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[Pipeline for a single ticker's data.     Order matters technical (per-ticker)]] - rationale - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[Preprocessor]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[Rebuild optimizer from scratch (used between walk-forward folds).]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[Reset model weights for a fresh fold (used with model.apply()).]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[StockDataset]] - code - d:\transformer\Stock Forecast\data\dataset.py
- [[Trainer]] - code - d:\transformer\Stock Forecast\train\trainer.py
- [[Validate during fold training (shares model state).]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[Walk-Forward Validation         - Train rolling window of 4 years         -]] - rationale - d:\transformer\Stock Forecast\train\trainer.py
- [[__init__.py_13]] - code - d:\transformer\trainer\__init__.py
- [[add_cross_sectional_features_full()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[backtest.py_2]] - code - d:\transformer\Stock Forecast\evaluation\backtest.py
- [[config.py]] - code - d:\transformer\Stock Forecast\utils\config.py
- [[data_module.py]] - code - d:\transformer\Stock Forecast\utils\data_module.py
- [[dataset.py]] - code - d:\transformer\Stock Forecast\data\dataset.py
- [[feature_engineering.py]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[load_config()]] - code - d:\transformer\Stock Forecast\utils\config.py
- [[main()_2]] - code - d:\transformer\Stock Forecast\main_optimized.py
- [[main_optimized.py]] - code - d:\transformer\Stock Forecast\main_optimized.py
- [[preprocess.py]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[process_ticker_data()]] - code - d:\transformer\Stock Forecast\data\preprocess.py
- [[process_ticker_group()]] - code - d:\transformer\Stock Forecast\data\feature_engineering.py
- [[set_seed()_1]] - code - d:\transformer\Stock Forecast\main_optimized.py
- [[trainer.py]] - code - d:\transformer\Stock Forecast\train\trainer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Stock_Forecast_Data_+_Training_Pipeline
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_AlphaTransformer Core Models]]
- 9 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 2 edges to [[_COMMUNITY_Graphify Hooks + Agents CLI]]
- 2 edges to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]
- 1 edge to [[_COMMUNITY_Sample Fixtures + Serve]]
- 1 edge to [[_COMMUNITY_Thesis Word Conversion + Frontend API]]

## Top bridge nodes
- [[.run()_1]] - degree 12, connects to 4 communities
- [[Trainer]] - degree 17, connects to 2 communities
- [[.setup()]] - degree 7, connects to 2 communities
- [[load_config()]] - degree 4, connects to 2 communities
- [[.load_checkpoint()_1]] - degree 4, connects to 2 communities