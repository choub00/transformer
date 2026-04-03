"""
AlphaTransformer 回测引擎
Anti-Churn 版本（方案 C：集合差集替换）

核心原则：
  1. 对数收益率累加（单利，禁止复利乘法）
  2. 交易成本在每步对数收益中扣除（减法，不乘法）
  3. 每日调仓，但只针对真正发生资产替换的情况
  4. 输出 策略曲线 vs 等权基准曲线
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class BacktestMetrics:
    """回测评估指标容器"""
    total_log_return: float = 0.0
    annualized_return: float = 0.0
    annualized_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0     # 范围 [-1, 0]
    max_drawdown_duration: int = 0  # 最大回撤持续天数
    num_trades: int = 0           # 实际交易次数（卖出动作）
    turnover_rate: float = 0.0    # 平均换手率

    # 对比基准
    benchmark_total_return: float = 0.0
    benchmark_annualized: float = 0.0
    excess_return: float = 0.0     # 超额收益（策略 - 基准）
    excess_sharpe: float = 0.0     # 超额夏普


class BacktestEngine:
    """
    回测引擎

    核心逻辑（方案 C - 集合差集替换）：
        1. 每日计算预测截面排名
        2. 确定今日目标做多 Top2 和做空 Bottom2
        3. 与昨日持仓对比：
           - 卖出：昨日在持仓，今日跌出前2名
           - 买入：今日新进前2名，昨日不在持仓
           - 持有：昨日在持仓，今日仍在前2名 → 不操作
        4. 对数收益累加，扣除交易成本

    收益率计算（防数值爆炸）：
        每日组合对数收益 = Σ(做多资产收益) + Σ(做空资产收益 * -1)
                        - Σ(卖出动作 × 手续费)
        注意：使用减法（对数域），而非乘法（复利域）
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        transaction_cost: float = 0.0015,
        top_k_long: int = 2,
        bottom_k_short: int = 2,
        risk_free_rate: float = 0.02,
        annualization_factor: int = 252,
    ):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.top_k_long = top_k_long
        self.bottom_k_short = bottom_k_short
        self.risk_free_rate = risk_free_rate
        self.annualization_factor = annualization_factor

        # 运行状态
        self._current_capital = initial_capital
        self._portfolio_log_returns: List[float] = []
        self._benchmark_log_returns: List[float] = []
        self._equity_curve: List[float] = [initial_capital]
        self._benchmark_curve: List[float] = [initial_capital]
        self._trade_log: List[Dict] = []
        self._daily_positions: List[Dict] = []

        # 持仓状态（方案 C 核心）
        self._current_long_set: set = set()   # 当前做多资产集合
        self._current_short_set: set = set()  # 当前做空资产集合

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def run(
        self,
        predictions_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        predictions_date_offset: int = 0,
    ) -> BacktestMetrics:
        """
        运行完整回测

        Args:
            predictions_df:  [Date, Asset] 每日每资产的预测值（未来3日对数收益均值）
            returns_df:      [Date, Asset] 每日每资产的真实对数收益率（r_t = ln(P_t / P_{t-1})）
            predictions_date_offset: 预测值相对于收益的偏移量
                                     0 = 用当天预测做当天收益（错误！会导致泄露）
                                     1 = 用前一天的预测做当天收益（正确！T时刻无法感知T+1收益）
                                     默认 1 确保信号在收益之前

        Returns:
            BacktestMetrics 包含所有评估指标

        数据对齐：
            核心原则：Signal[t-1] * Return[t]
            即：用 T-1 时刻的预测信号，乘以 T 时刻的真实收益
        """
        common_dates = predictions_df.index.intersection(returns_df.index)
        common_assets = predictions_df.columns.intersection(returns_df.columns)

        predictions_df = predictions_df.loc[common_dates, common_assets]
        returns_df = returns_df.loc[common_dates, common_assets]

        # 对齐日期：预测信号需要提前一天
        # predictions_df 的时间戳是预测产生的时间
        # returns_df 的时间戳是收益发生的时间
        # 如果 predictions_df[t] 用于计算 returns_df[t] 的收益 → 泄露！
        # 正确做法：predictions_df[t-1] * returns_df[t]

        # 初始化：首日设定基准
        self._reset()
        self._equity_curve = [self.initial_capital]
        self._benchmark_curve = [self.initial_capital]

        dates = returns_df.index.tolist()  # 用 returns 的日期作为主索引

        # 构建前一天的预测信号（用于今日收益计算）
        # 如果 predictions 索引与 returns 一致，需要 shift(-1) 对齐
        pred_dates = predictions_df.index.tolist()

        # 初始化前一天的持仓（空仓）
        prev_preds = None

        for i, date in enumerate(dates):
            rets = returns_df.loc[date].values         # [N_assets] 当日真实收益
            asset_names = returns_df.columns.tolist()

            # ---- 关键修复：获取前一天的预测信号 ----
            # 信号必须在收益之前产生，否则泄露
            if pred_dates and i > 0:
                prev_date = pred_dates[min(i - 1, len(pred_dates) - 1)]
                prev_preds = predictions_df.loc[prev_date].values
            else:
                # 首日无信号，用零
                prev_preds = np.zeros(len(asset_names))

            # 用前一天的预测决定今日持仓
            target_long, target_short = self._compute_target_positions(
                prev_preds, asset_names
            )

            # ---- Step 2: 方案 C - 集合差集计算实际交易 ----
            long_to_sell = self._current_long_set - set(target_long)
            long_to_buy = set(target_long) - self._current_long_set
            short_to_cover = self._current_short_set - set(target_short)
            short_to_sell = set(target_short) - self._current_short_set

            # 交易次数统计（卖出动作）
            num_trades_today = len(long_to_sell) + len(short_to_cover)
            self._num_trades += num_trades_today

            # ---- Step 3: 计算今日对数收益（使用真实收益，而非预测值）----
            # 关键：Signal[t-1] * Return[t]
            # 用前一天的信号（prev_preds）乘以今日真实收益（rets）
            daily_ret = self._compute_portfolio_return(
                real_returns=rets,  # 使用真实收益，不是预测值！
                asset_names=asset_names,
                target_long=target_long,
                target_short=target_short,
            )

            # ---- Step 4: 扣除交易成本（对数域减法） ----
            # 每笔卖出/买回收取单边 0.0015
            trading_cost = num_trades_today * self.transaction_cost
            daily_net_ret = daily_ret - trading_cost

            # ---- Step 5: 更新权益曲线 ----
            new_capital = self._equity_curve[-1] * np.exp(daily_net_ret)
            self._equity_curve.append(new_capital)

            # ---- Step 6: 更新持仓状态（方案 C） ----
            self._current_long_set = set(target_long)
            self._current_short_set = set(target_short)

            # ---- Step 7: 基准（等权 Top/Bottom 平分） ----
            benchmark_ret = self._compute_benchmark_return(
                rets=rets, asset_names=asset_names
            )
            new_benchmark = self._benchmark_curve[-1] * np.exp(benchmark_ret)
            self._benchmark_curve.append(new_benchmark)

            self._portfolio_log_returns.append(daily_net_ret)
            self._benchmark_log_returns.append(benchmark_ret)

            # ---- 日志记录 ----
            self._trade_log.append({
                "date": date,
                "long": list(target_long),
                "short": list(target_short),
                "num_trades": num_trades_today,
                "gross_return": daily_ret,
                "trading_cost": trading_cost,
                "net_return": daily_net_ret,
                "equity": new_capital,
            })

        return self._compute_metrics()

    # ------------------------------------------------------------------
    # 核心算法
    # ------------------------------------------------------------------

    def _compute_target_positions(
        self, preds: np.ndarray, asset_names: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        根据预测值计算目标做多/做空资产列表
        """
        # 按预测值降序排列
        sorted_indices = np.argsort(preds)[::-1]
        long_assets = [asset_names[i] for i in sorted_indices[: self.top_k_long]]
        short_assets = [asset_names[i] for i in sorted_indices[-self.bottom_k_short:][::-1]]
        return long_assets, short_assets

    def _compute_portfolio_return(
        self,
        real_returns: np.ndarray,
        asset_names: List[str],
        target_long: List[str],
        target_short: List[str],
    ) -> float:
        """
        计算组合对数收益率（等权分配）

        公式：
            组合收益 = (1/K) * Σ r_long - (1/K) * Σ r_short
            其中 K = top_k_long = bottom_k_short = 2

        关键：
            - 必须使用 real_returns（真实收益），而非预测值 preds
            - 对数收益是加性的，直接求和即可！
            - 不使用：capital * weight * return（避免复利爆炸）
        """
        K = self.top_k_long  # 做多/做空各 K 只

        long_ret = 0.0
        for asset in target_long:
            idx = asset_names.index(asset)
            long_ret += real_returns[idx]  # 真实收益

        short_ret = 0.0
        for asset in target_short:
            idx = asset_names.index(asset)
            short_ret += real_returns[idx]

        # 等权分配，平均后再相减
        portfolio_ret = (long_ret / K) - (short_ret / K)
        return portfolio_ret

    def _compute_benchmark_return(
        self, rets: np.ndarray, asset_names: List[str]
    ) -> float:
        """
        等权基准：每日对所有资产等权做多，计算平均对数收益
        """
        # 简单等权基准：全部资产的平均收益
        return np.mean(rets)

    # ------------------------------------------------------------------
    # 指标计算
    # ------------------------------------------------------------------

    def _compute_metrics(self) -> BacktestMetrics:
        """
        计算所有回测指标

        对数收益率安全转换：
            总收益 = exp(Σ log_returns) - 1
            如果 Σ log_returns 过小（< 100），exp() 数值稳定
        """
        n = len(self._portfolio_log_returns)
        if n == 0:
            return BacktestMetrics()

        port_rets = np.array(self._portfolio_log_returns)
        bench_rets = np.array(self._benchmark_log_returns)

        # ---- 基本统计 ----
        total_log_ret = np.sum(port_rets)
        bench_total_log_ret = np.sum(bench_rets)

        # ---- 年化收益率 ----
        annualization = self.annualization_factor / n
        annualized_return = total_log_ret * annualization
        bench_annualized = bench_total_log_ret * annualization

        # ---- 年化波动率 ----
        ann_vol = np.std(port_rets, ddof=1) * np.sqrt(self.annualization_factor)

        # ---- 夏普比率 ----
        excess_ret = annualized_return - self.risk_free_rate
        sharpe = excess_ret / ann_vol if ann_vol > 1e-10 else 0.0

        # ---- 最大回撤（对数累积收益曲线） ----
        # 在对数域计算回撤，确保数值稳定
        equity = np.array(self._equity_curve[1:])  # 去掉初始点
        log_equity = np.log(equity + 1e-12)        # 避免 log(0)
        cumulative = np.cumsum(port_rets)

        peak = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - peak              # ≤ 0
        max_drawdown = np.min(drawdowns)          # 最负的数 ∈ [-1, 0]（理论）

        # 限制在 [-1, 0] 范围（实际回撤通常不会超过 100%）
        max_drawdown = max(max_drawdown, -1.0)

        # ---- 回撤持续天数 ----
        in_drawdown = drawdowns < 0
        max_dd_duration = 0
        current_dd_duration = 0
        for is_dd in in_drawdown:
            if is_dd:
                current_dd_duration += 1
                max_dd_duration = max(max_dd_duration, current_dd_duration)
            else:
                current_dd_duration = 0

        # ---- 换手率 ----
        avg_trades_per_day = self._num_trades / max(n, 1)
        turnover_rate = avg_trades_per_day / (self.top_k_long + self.bottom_k_short)

        # ---- 超额收益 ----
        excess_return = total_log_ret - bench_total_log_ret

        # 超额夏普（以日波动率计）
        port_vol = np.std(port_rets, ddof=1)
        bench_vol = np.std(bench_rets, ddof=1)
        cov = np.cov(port_rets, bench_rets, ddof=1)[0, 1]
        tracking_err = np.sqrt(max(port_vol ** 2 + bench_vol ** 2 - 2 * cov, 0))
        excess_sharpe = excess_return / tracking_err if tracking_err > 1e-10 else 0.0

        metrics = BacktestMetrics(
            total_log_return=total_log_ret,
            annualized_return=annualized_return,
            annualized_volatility=ann_vol,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            num_trades=self._num_trades,
            turnover_rate=turnover_rate,
            benchmark_total_return=bench_total_log_ret,
            benchmark_annualized=bench_annualized,
            excess_return=excess_return,
            excess_sharpe=excess_sharpe,
        )
        return metrics

    def get_equity_curves(self) -> Tuple[np.ndarray, np.ndarray]:
        """返回 (策略权益曲线, 基准权益曲线)"""
        return np.array(self._equity_curve), np.array(self._benchmark_curve)

    def get_trade_log(self) -> pd.DataFrame:
        """返回每日交易日志"""
        return pd.DataFrame(self._trade_log)

    def _reset(self):
        self._current_capital = self.initial_capital
        self._portfolio_log_returns = []
        self._benchmark_log_returns = []
        self._equity_curve = [self.initial_capital]
        self._benchmark_curve = [self.initial_capital]
        self._trade_log = []
        self._daily_positions = []
        self._current_long_set = set()
        self._current_short_set = set()
        self._num_trades = 0

    # ------------------------------------------------------------------
    # 可视化辅助
    # ------------------------------------------------------------------

    def print_summary(self, metrics: BacktestMetrics):
        """打印回测报告"""
        total_ret_pct = (np.exp(metrics.total_log_return) - 1) * 100
        bench_ret_pct = (np.exp(metrics.benchmark_total_return) - 1) * 100

        print("\n" + "=" * 60)
        print("              AlphaTransformer 回测报告")
        print("=" * 60)
        print(f"  初始资金          : ${self.initial_capital:,.0f}")
        print(f"  交易次数（卖出）  : {metrics.num_trades}")
        print(f"  换手率（日均）    : {metrics.turnover_rate:.4f}")
        print("-" * 60)
        print(f"  {'指标':<20} {'策略':>15} {'基准':>15}")
        print(f"  {'-'*20} {'-'*15} {'-'*15}")
        print(f"  {'总收益率':.<20} {total_ret_pct:>+14.2f}% {bench_ret_pct:>+14.2f}%")
        print(f"  {'年化收益率':.<20} {metrics.annualized_return:>+14.4f} {metrics.benchmark_annualized:>+14.4f}")
        print(f"  {'年化波动率':.<20} {metrics.annualized_volatility:>+14.4f}")
        print(f"  {'夏普比率':.<20} {metrics.sharpe_ratio:>+14.4f}")
        print(f"  {'最大回撤':.<20} {metrics.max_drawdown:>+14.4f}  (范围 [-1, 0])")
        print(f"  {'回撤持续天数':.<20} {metrics.max_drawdown_duration:>+14}d")
        print("-" * 60)
        print(f"  {'超额收益':.<20} {metrics.excess_return:>+14.4f}")
        print(f"  {'超额夏普':.<20} {metrics.excess_sharpe:>+14.4f}")
        print("=" * 60)
        print()
