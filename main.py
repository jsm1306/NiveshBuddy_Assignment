import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import pandas as pd
from dotenv import load_dotenv
from data_loader import load_data
from strategy_engine import compute_strategy
from metrics import compute_metrics, compute_sharpe_ratio, compute_sortino_ratio
from ai_analysis import run_ai_analysis, format_analysis_output

load_dotenv()


def extract_monthly_performance(df, portfolio_value, weights):
    results_df = pd.DataFrame({
        'Date': df['Date'].values,
        'PortfolioValue': portfolio_value.values
    })
    
    for col in weights.columns:
        results_df[col] = weights[col].values
    
    results_df['YearMonth'] = results_df['Date'].dt.to_period('M')
    monthly = results_df.groupby('YearMonth').agg({
        'Date': 'last',
        'PortfolioValue': 'last'
    }).reset_index()
    
    monthly['PrevValue'] = monthly['PortfolioValue'].shift(1)
    monthly['MonthlyReturn'] = (monthly['PortfolioValue'] / monthly['PrevValue'] - 1) * 100
    monthly.loc[0, 'MonthlyReturn'] = (monthly.loc[0, 'PortfolioValue'] - 1) * 100
    asset_cols = weights.columns.tolist()
    for asset in asset_cols:
        monthly[f'{asset}_weight'] = results_df.groupby('YearMonth')[asset].last().values
    
    return monthly


def print_monthly_performance(strategy_name, monthly_df, weights_df):
    print(f"\n{strategy_name}")
    print("-" * 70)
    asset_cols = weights_df.columns.tolist()
    
    header = f"{'Month':<12} {'PortValue':<12} {'Return %':<12} {'Selected Assets':<50}"
    print(header)
    print("-" * 70)
    
    for idx, row in monthly_df.iterrows():
        month_str = str(row['YearMonth'])
        port_val = f"{row['PortfolioValue']:.4f}"
        ret_pct = f"{row['MonthlyReturn']:.2f}%"
        
        selected = []
        for asset in asset_cols:
            weight_col = f'{asset}_weight'
            if weight_col in row and row[weight_col] > 0.01:
                selected.append(f"{asset} ({row[weight_col]:.1%})")
        
        assets_str = ", ".join(selected) if selected else "Cash"
        
        print(f"{month_str:<12} {port_val:<12} {ret_pct:<12} {assets_str:<50}")
    
    print("-" * 70)


def main():
    """Load data, execute momentum strategies, and run AI analysis"""

    # STEP 1: DATA LOADING & CLEANING
    print("\n" + "-"*70)
    print("STEP 1: DATA LOADING & CLEANING\n")
    
    df = load_data(r'data\assets.csv', output_path=r'data\assets_clean.csv')
    print(f"✓ Data loaded and cleaned: {df.shape[0]} trading days, {df.shape[1]-1} assets")
    
    # STEP 2: MOMENTUM STRATEGY EXECUTION
    print("\n" + "-"*70)
    print("STEP 2: MOMENTUM STRATEGY EXECUTION\n")

    df = pd.read_csv('data/assets_clean.csv')
    df['Date'] = pd.to_datetime(df['Date'])

    print(f"  Shape: {df.shape[0]} trading days, {df.shape[1] - 1} assets")
    print(f"  Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"  Assets: {', '.join(df.columns[1:].tolist())}")


    print("\nSTRATEGY A: 30-Day Momentum Lookback")
    result_a = compute_strategy(df, lookback_days=30)
    monthly_a = extract_monthly_performance(df, result_a['portfolio_value'], result_a['weights'])

    print(f"\n[EXECUTION] Strategy A completed successfully")
    print(f"  Total trading days: {result_a['portfolio_returns'].shape[0]}")
    print(f"  Total months: {len(monthly_a)}")
    print(f"\n[SUMMARY] Overall Portfolio Performance (30-day lookback):")
    print(f"  Final portfolio value: {result_a['portfolio_value'].iloc[-1]:.4f}")
    print(f"  Total return: {(result_a['portfolio_value'].iloc[-1] - 1) * 100:.2f}%")
    print(f"  Mean daily return: {result_a['portfolio_returns'].mean() * 100:.4f}%")
    print(f"  Std dev daily return: {result_a['portfolio_returns'].std() * 100:.4f}%")
    print(f"\n[MONTHLY BREAKDOWN] Strategy A")
    print_monthly_performance("30-Day Momentum Strategy", monthly_a, result_a['weights'])


    print("\nSTRATEGY B: 90-Day Momentum Lookback")
    result_b = compute_strategy(df, lookback_days=90)
    monthly_b = extract_monthly_performance(df, result_b['portfolio_value'], result_b['weights'])

    print(f"\n[EXECUTION] Strategy B completed successfully")
    print(f"  Total trading days: {result_b['portfolio_returns'].shape[0]}")
    print(f"  Total months: {len(monthly_b)}")
    print(f"\n[SUMMARY] Overall Portfolio Performance (90-day lookback):")
    print(f"  Final portfolio value: {result_b['portfolio_value'].iloc[-1]:.4f}")
    print(f"  Total return: {(result_b['portfolio_value'].iloc[-1] - 1) * 100:.2f}%")
    print(f"  Mean daily return: {result_b['portfolio_returns'].mean() * 100:.4f}%")
    print(f"  Std dev daily return: {result_b['portfolio_returns'].std() * 100:.4f}%")
    print(f"\n[MONTHLY BREAKDOWN] Strategy B")
    print_monthly_performance("90-Day Momentum Strategy", monthly_b, result_b['weights'])

    print("\nSTRATEGY COMPARISON")
    print(f"\nStrategy A (30-day) vs Strategy B (90-day):")
    print(f"  Final Value (A): {result_a['portfolio_value'].iloc[-1]:.4f} vs (B): {result_b['portfolio_value'].iloc[-1]:.4f}")
    print(f"  Total Return (A): {(result_a['portfolio_value'].iloc[-1] - 1) * 100:.2f}% vs (B): {(result_b['portfolio_value'].iloc[-1] - 1) * 100:.2f}%")

    # STEP 3: AI-POWERED ANALYSIS
    print("\n" + "-"*70)
    print("STEP 3: AI-POWERED STRATEGY ANALYSIS\n")
    
    try:
        # Compute comprehensive metrics for Strategy A (30-day)
        strategy_30_metrics = compute_metrics(
            result_a['portfolio_returns'],
            result_a['portfolio_value'],
            trading_days_per_year=252
        )
        strategy_30_metrics['sharpe_ratio'] = compute_sharpe_ratio(
            result_a['portfolio_returns'],
            risk_free_rate=0.0,
            trading_days_per_year=252
        )
        strategy_30_metrics['sortino_ratio'] = compute_sortino_ratio(
            result_a['portfolio_returns'],
            target_return=0.0,
            trading_days_per_year=252
        )

        # Compute comprehensive metrics for Strategy B (90-day)
        strategy_90_metrics = compute_metrics(
            result_b['portfolio_returns'],
            result_b['portfolio_value'],
            trading_days_per_year=252
        )
        strategy_90_metrics['sharpe_ratio'] = compute_sharpe_ratio(
            result_b['portfolio_returns'],
            risk_free_rate=0.0,
            trading_days_per_year=252
        )
        strategy_90_metrics['sortino_ratio'] = compute_sortino_ratio(
            result_b['portfolio_returns'],
            target_return=0.0,
            trading_days_per_year=252
        )

        print("\n[INFO] Computed metrics for both strategies")
        print(f"  Strategy 30-day Sharpe Ratio: {strategy_30_metrics['sharpe_ratio']:.4f}")
        print(f"  Strategy 90-day Sharpe Ratio: {strategy_90_metrics['sharpe_ratio']:.4f}")
        print("\nAI ANALYSIS MODE SELECTION\n")
        print("\n1. Quick Mode   - 5 concise insights (WINNER, KEY DIFFERENCE, RISK NOTE, IDEA)")
        print("2. Detailed Mode - Full analytical breakdown with comprehensive sections")
        print("\n" + "-"*70)
        
        mode_choice = None
        while mode_choice not in ["1", "2"]:
            user_input = input("\nSelect mode (1 or 2): ").strip()
            if user_input == "1":
                mode_choice = "1"
                selected_mode = "quick"
                print("✓ Quick mode selected")
            elif user_input == "2":
                mode_choice = "2"
                selected_mode = "detailed"
                print("✓ Detailed mode selected")
            else:
                print("  Invalid input. Please enter 1 or 2.")
        
        print("\n[INFO] Calling Gemini API for strategy analysis...\n")
        analysis_text = run_ai_analysis(strategy_30_metrics, strategy_90_metrics, mode=selected_mode)
        
        formatted_analysis = format_analysis_output(analysis_text)
        print(formatted_analysis)
        with open('ai_suggestion.txt', 'w', encoding='utf-8') as f:
            f.write(formatted_analysis + '\n')

    except Exception as e:
        print(f"\n[ERROR] AI analysis failed: {e}")
        

    print("\nWORKFLOW COMPLETE")


if __name__ == "__main__":
    main()
