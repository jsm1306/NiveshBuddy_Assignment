"""Momentum strategy engine for portfolio management."""

import pandas as pd
import numpy as np
from typing import Dict


def compute_strategy(df: pd.DataFrame, lookback_days: int) -> Dict[str, pd.Series | pd.DataFrame]:
    """Computes a momentum-based portfolio strategy with monthly rebalancing."""
    

    # Step 1: Identify asset columns (all except the first Date column)
    date_col = df.columns[0]
    asset_cols = df.columns[1:].tolist()

    # Create a working copy with proper datetime type
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col])

    # Step 2: Compute daily returns for each asset
    # Return_t = (Price_t / Price_{t-1}) - 1
    daily_returns = data[asset_cols].pct_change()

    # Step 3: Compute momentum scores (lookback period return)
    # Momentum_t = (Price_t / Price_{t-lookback_days}) - 1
    # Using shift to look back exactly lookback_days trading days
    momentum_scores = (data[asset_cols] / data[asset_cols].shift(lookback_days)) - 1

    # Step 4: Identify rebalance dates (first trading day of each month)
    # Use period grouping to detect month boundaries using the Date column
    data['year_month'] = data[date_col].dt.to_period('M')
    rebalance_mask = data.groupby('year_month').cumcount() == 0
    rebalance_indices = data.loc[rebalance_mask].index.tolist()

    # Step 5: Initialize weights dataframe with zeros
    # This will be populated at each rebalance date
    weights = pd.DataFrame(0.0, index=data.index, columns=asset_cols)

    # Assign weights at each rebalance date, holding until next rebalance
    for i, rebal_pos in enumerate(rebalance_indices):
        # Get momentum scores at this rebalance date
        momentum_row = momentum_scores.iloc[rebal_pos]

        # Only assign weights if we have valid momentum data for at least 2 assets
        valid_momentum_count = momentum_row.notna().sum()
        if valid_momentum_count >= 2:
            # Rank assets by momentum and select top 2
            top_2_assets = momentum_row.nlargest(2).index.tolist()

            # Determine the date range where these weights apply
            start_pos = rebal_pos
            end_pos = rebalance_indices[i + 1] if i + 1 < len(rebalance_indices) else len(data)

            # Assign equal weights (0.5 each) to top 2 assets for this holding period
            for asset in top_2_assets:
                weights.iloc[start_pos:end_pos, weights.columns.get_loc(asset)] = 0.5

    # Step 5: Compute daily portfolio returns
    # Portfolio Return_t = sum(Asset_Return_t * Weight_t) across all assets
    portfolio_returns = (daily_returns * weights).sum(axis=1)

    # Step 6: Compute cumulative portfolio value
    # Value_t = 1.0 * prod(1 + Return_i) for i = 1 to t
    portfolio_value = (1 + portfolio_returns).cumprod()

    return {
        'portfolio_returns': portfolio_returns,
        'portfolio_value': portfolio_value,
        'weights': weights
    }
