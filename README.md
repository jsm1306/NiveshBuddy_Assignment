# AI-Powered Momentum Strategy Analysis

A quantitative portfolio analysis system that implements dual momentum strategies (30-day and 90-day lookback), computes comprehensive performance metrics, and leverages Google's Gemini AI to generate actionable insights.

---

## Setup Instructions

### Prerequisites

-   Python 3.8+
-   pip (Python package manager)

### Installation

1.  **Create and Activate Virtual Environment**
    
    ```bash
    # Create virtual environmentpython -m venv nbenv# Activate virtual environment# On Windows:nbenvScriptsactivate# On macOS/Linux:source nbenv/bin/activate
    ```
    
2.  **Install Dependencies**
    
    ```bash
    pip install -r requirements.txt
    ```
    
    This installs all required packages listed in `requirements.txt`.
    
3.  **Set Up Environment Variable**
    
    -   Create a `.env` file in the project root with your Gemini API key:
    
    ```
    GEMINI_API_KEY=your_api_key_here
    ```
    
    -   Or set it in your system environment variables:
    
    ```bash
    # Windows PowerShell:$env:GEMINI_API_KEY="your_api_key_here"# Windows CMD:set GEMINI_API_KEY=your_api_key_here# macOS/Linux:export GEMINI_API_KEY="your_api_key_here"
    ```
    
4.  **Prepare Data**
    
    -   Place your CSV file in the `data/` directory
    -   File format: First column must be `Date` (YYYY-MM-DD), remaining columns are asset prices
    -   Example:
    
    ```
    Date,AAPL,MSFT,GOOGL2023-01-01,150.00,200.00,100.002023-01-02,151.00,201.00,101.00...
    ```
    
5.  **Run the Application**
    
    ```bash
    python main.py
    ```
    
    The workflow runs automatically: data loading → strategy execution → AI analysis.
    

## Project Structure

```
./├── main.py                 # Workflow orchestrator (3 STEPS)├── data_loader.py          # Data loading & cleaning├── strategy_engine.py      # Momentum strategy implementation├── metrics.py              # Performance metrics├── ai_analysis.py          # Gemini AI integration├── test_analysis.ipynb     # Jupyter notebook testing├── data/│   ├── assets.csv          # Raw data│   └── assets_clean.csv    # Cleaned data (auto-generated)├── .env                    # Environment variables└── README.md               # This file
```

## Assumptions Made

### Lookback Period ⚠️ CRITICAL

-   **30-Day Strategy**: Uses **30 TRADING DAYS** (NOT calendar days) for momentum lookback
-   **90-Day Strategy**: Uses **90 TRADING DAYS** (NOT calendar days) for momentum lookback
-   **Lookback Calculation**: Momentum = (Price_Today / Price_N_Trading_Days_Ago) - 1
-   **Calendar Reference**: ~6 trading days ≈ 1 calendar week; ~30 trading days ≈ 1.5 calendar months; ~90 trading days ≈ 4.5 calendar months

### Market Assumptions

-   **Trading Calendar**: 252 trading days per year (US equity market standard)
-   **Rebalancing**: Monthly on the last trading day of each calendar month
-   **Asset Selection**: Top 2 performing assets identified by momentum score
-   **Position Sizing**: Equal weight (50/50) allocation to selected assets
-   **Risk-Free Rate**: 0.0% (for Sharpe and Sortino ratio calculations)

## Design Principles

### 1. Modular Architecture

Module

Responsibility

`data_loader.py`

Load, clean, save CSV

`strategy_engine.py`

Implement momentum logic

`metrics.py`

Calculate performance metrics

`ai_analysis.py`

JSON building, prompt engineering, API calls

`main.py`

Orchestrate 3-step workflow

### 2. Momentum Strategy Implementation

-   **Why Momentum?** Time-tested signal; simple, interpretable, data-driven.
-   **Why Two Lookbacks?** Compare 30-trading-day vs. 90-trading-day approaches.
-   **Why Monthly Rebalancing?** Industry-standard; balances responsiveness vs. transaction costs.
-   **Why Top 2 Assets?** Concentrated exposure; stronger signal clarity.

---

## Gemini API Integration

### JSON Data Embedding

```json
{  "strategy_30_day": {    "lookback_period_days": 30,    "metrics": {      "total_return": 0.2543,      "cagr": 0.082,      "volatility": 0.12,      "max_drawdown": -0.15,      "sharpe_ratio": 0.67,      "sortino_ratio": 0.95    }  },  "strategy_90_day": {    "lookback_period_days": 90,    "metrics": {...}  },  "metadata": {    "strategy_type": "momentum_rebalancing",    "rebalance_frequency": "monthly",    "asset_selection": "top_2_equal_weight"  }}
```

### Structured Analysis Requirements

The prompt enforces **5 required analysis points**:

1.  **Performance Comparison** - Compare total return, CAGR, Sharpe, Sortino
2.  **Performance Differences** - Quantify gaps and consistency metrics
3.  **Risk-Return Trade-Off** - Which strategy is more efficient for the risk taken
4.  **When Each Outperforms** - Specific market conditions/scenarios favoring each
5.  **One Improvement Idea** - Actionable suggestion for the underperformer

### API Configuration

```python
model = genai.GenerativeModel("gemini-2.5-flash")generation_config = {    "temperature": 0.3,           # Low randomness (analytical focus)    "max_output_tokens": 3500     # Ensure all 5 sections fit}
```

**Why these settings?**

-   **Temperature 0.3**: Ensures consistent, analytical output (not creative)
-   **Max Tokens 3500**: Sufficient space for comprehensive 5-point analysis
-   **Gemini 2.5 Flash**: Fast, accurate, free-tier suitable

---

## Complete Workflow

```
python main.py    ↓STEP 1: Data Loading & Cleaning├─ Load raw CSV├─ Parse dates, sort, handle missing values├─ Save cleaned CSV└─ Print diagnostics    ↓STEP 2: Strategy Execution├─ Strategy A (30 trading days):│  ├─ Compute momentum scores│  ├─ Monthly rebalance (top 2 assets)│  ├─ Calculate daily returns│  └─ Compute 6 metrics├─ Strategy B (90 trading days):│  ├─ Compute momentum scores│  ├─ Monthly rebalance (top 2 assets)│  ├─ Calculate daily returns│  └─ Compute 6 metrics└─ Print summaries    ↓STEP 3: AI Analysis via Gemini API├─ Build JSON payload with metrics├─ Create structured prompt (5 required points)├─ Call Gemini 2.5 Flash│  ├─ Temperature: 0.3│  ├─ Max Tokens: 3500│  └─ Response: All 5 analytical sections├─ Format output (markdown → readable)└─ Display to console    ↓Workflow Complete ✓
```

---

## Running the Application

```bash
python main.py
```

---

## Key Features

✅ **Dual Momentum Strategies** - 30-trading-day vs. 90-trading-day lookback approaches  
✅ **Performance Metrics** - Total return, CAGR, volatility, max drawdown, Sharpe, Sortino  
✅ **AI-Powered Analysis** - Gemini API with 5-point structured reasoning  
✅ **Modular Design** - Clean separation of concerns; easy to modify and extend

**Python Version**: 3.8+