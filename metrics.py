"""Portfolio performance metrics computation."""
import pandas as pd
import numpy as np
from typing import Dict


def compute_metrics(
    portfolio_returns: pd.Series,
    portfolio_value: pd.Series,
    trading_days_per_year: int = 252
) -> Dict[str, float]:
    """Computes standard portfolio performance metrics."""
    # Validate inputs
    if portfolio_returns.empty or portfolio_value.empty:
        raise ValueError("portfolio_returns and portfolio_value cannot be empty")


    returns = portfolio_returns.copy()
    values = portfolio_value.copy()
    returns = returns.dropna()
    if returns.empty or values.empty:
        raise ValueError("After dropping NaN values, series are empty")


    # 1. TOTAL RETURN
    # Total return = (Final Value / Initial Value) - 1
    # Since initial value is 1.0, this simplifies to: Final Value - 1
    final_value = values.iloc[-1]
    total_return = final_value - 1.0


    # 2. CAGR (Compound Annual Growth Rate)
    # CAGR = (Final Value) ^ (1 / years) - 1
    # where years = number_of_trading_days / trading_days_per_year
    number_of_trading_days = len(returns)
    years = number_of_trading_days / trading_days_per_year

    # Handle edge case: avoid division by zero or negative exponents
    if years <= 0:
        cagr = np.nan
    elif final_value <= 0:
        cagr = np.nan
    else:
        cagr = (final_value ** (1.0 / years)) - 1.0


    # 3. VOLATILITY (Annualized)
    # Volatility = Daily Std Dev * sqrt(trading_days_per_year)
    # This annualizes the daily volatility using the square-root-of-time rule,
    # which assumes returns have zero autocorrelation (reasonable for equities).
    daily_volatility = returns.std()
    volatility = daily_volatility * np.sqrt(trading_days_per_year)

    # 4. MAXIMUM DRAWDOWN
    # Maximum Drawdown = min(Current Value / Running Peak - 1)
    # This represents the largest peak-to-trough decline.
    running_max = values.cummax()
    drawdown = (values / running_max) - 1.0
    max_drawdown = drawdown.min()

    # RETURN METRICS DICTIONARY
    metrics = {
        'total_return': float(total_return),
        'cagr': float(cagr),
        'volatility': float(volatility),
        'max_drawdown': float(max_drawdown)
    }

    return metrics


def print_metrics(metrics_dict: Dict[str, float], strategy_name: str = "Strategy") -> None:
    """Prints portfolio metrics in a formatted table."""
    print(f"{strategy_name.upper():^50}")

    total_return = metrics_dict.get('total_return', np.nan)
    cagr = metrics_dict.get('cagr', np.nan)
    volatility = metrics_dict.get('volatility', np.nan)
    max_drawdown = metrics_dict.get('max_drawdown', np.nan)

    print(f"{'Total Return':<30} {total_return:>10.2%}")
    print(f"{'CAGR':<30} {cagr:>10.2%}")
    print(f"{'Annualized Volatility':<30} {volatility:>10.2%}")
    print(f"{'Maximum Drawdown':<30} {max_drawdown:>10.2%}")


def compute_sharpe_ratio(
    portfolio_returns: pd.Series,
    risk_free_rate: float = 0.0,
    trading_days_per_year: int = 252
) -> float:
    """Computes annualized Sharpe Ratio."""
    returns = portfolio_returns.dropna()

    if returns.empty:
        return np.nan

    # Annualized return and volatility
    annual_return = returns.mean() * trading_days_per_year
    annual_volatility = returns.std() * np.sqrt(trading_days_per_year)

    # Avoid division by zero
    if annual_volatility == 0:
        return np.nan

    # Sharpe Ratio with risk-free rate adjustment
    sharpe = (annual_return - risk_free_rate) / annual_volatility

    return float(sharpe)


def compute_sortino_ratio(
    portfolio_returns: pd.Series,
    target_return: float = 0.0,
    trading_days_per_year: int = 252
) -> float:
    """Computes annualized Sortino Ratio."""
    returns = portfolio_returns.dropna()

    if returns.empty:
        return np.nan

    annual_return = returns.mean() * trading_days_per_year
    downside_returns = returns[returns < target_return]
    if downside_returns.empty:
        return np.inf if annual_return > target_return else 0.0


    downside_deviation = downside_returns.std() * np.sqrt(trading_days_per_year)
    # Avoid division by zero
    if downside_deviation == 0:
        return np.inf if annual_return > target_return else 0.0

    sortino = (annual_return - target_return) / downside_deviation
    return float(sortino)
