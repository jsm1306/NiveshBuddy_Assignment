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
    # Create virtual environment
    
    python -m venv nbenv
    # Activate virtual environment
    
    # On Windows:
    nbenvScriptsactivate
    
    # On macOS/Linux:
    source nbenv/bin/activate
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
    # Windows PowerShell:
    $env:GEMINI_API_KEY="your_api_key_here"
    
    # Windows CMD:
    set GEMINI_API_KEY=your_api_key_here
    
    # macOS/Linux:
    export GEMINI_API_KEY="your_api_key_here"
    ```
    
4.  **Prepare Data**
    
    -   Place your CSV file in the `data/` directory
    -   File format: First column must be `Date` (YYYY-MM-DD), remaining columns are asset prices
    -   Example:
    
    ```
    Date,AAPL,MSFT,GOOGL
    2023-01-01,150.00,200.00,100.00
    2023-01-02,151.00,201.00,101.00...
    ```
    
5.  **Run the Application**
    
    ```bash
    python main.py
    ```
    
    The workflow runs automatically: data loading → strategy execution → AI analysis.
    

## Project Structure

```
./
├── main.py                 # Main workflow orchestrator
├── data_loader.py          # Data loading and cleaning
├── strategy_engine.py      # Momentum strategy implementation
├── metrics.py              # Performance metrics computation
├── ai_analysis.py          # Gemini AI integration & prompts
├── test_analysis.ipynb     # Jupyter notebook for testing
├── data/
│   ├── assets.csv          # Raw asset price data
│   └── assets_clean.csv    # Cleaned data (auto-generated)
├── ai_suggestion.txt       # AI-generated analysis output
├── .env                    # Environment variables (not in repo)
└── README.md               # This file
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

## Design Principles

### 1. Modular Architecture

The codebase is organized into **separate, single-responsibility modules**:
- `data_loader.py` → Data I/O only
- `strategy_engine.py` → Strategy computation only
- `metrics.py` → Metric calculations only
- `ai_analysis.py` → AI layer isolation
- `main.py` → High-level orchestration

**Rationale**: Easy testing, modification, and debugging without touching other components.

### 2. Momentum Strategy Implementation

-   **Why Momentum?** Time-tested signal; simple, interpretable, data-driven.
-   **Why Two Lookbacks?** Compare 30-trading-day vs. 90-trading-day approaches.
-   **Why Monthly Rebalancing?** Industry-standard; balances responsiveness vs. transaction costs.
-   **Why Top 2 Assets?** Concentrated exposure; stronger signal clarity.

---

## Gemini API Integration

### JSON Data Embedding

Metrics are dynamically inserted as JSON:
```json
{
  "strategy_30_day": {
    "lookback_period_days": 30,
    "metrics": {...}
  },
  "strategy_90_day": {
    "lookback_period_days": 90,
    "metrics": {...}
  },
  "metadata": {...}
}
```
**Why?** Model sees *actual numbers*, not placeholders. Prevents hallucination.

### Structured Analysis Requirements

The prompt enforces **5 required analysis points**:

1.  **Performance Comparison** - Compare total return, CAGR, Sharpe, Sortino
2.  **Performance Differences** - Quantify gaps and consistency metrics
3.  **Risk-Return Trade-Off** - Which strategy is more efficient for the risk taken
4.  **When Each Outperforms** - Specific market conditions/scenarios favoring each
5.  **One Improvement Idea** - Actionable suggestion for the underperformer

### API Configuration

```python
model = genai.GenerativeModel("gemini-2.5-flash")
generation_config = {
"temperature": 0.3,            # Low randomness (analytical focus)
"max_output_tokens": 3500     # Ensure all 5 sections fit
}
```

**Why these settings?**

-   **Temperature 0.3**: Ensures consistent, analytical output (not creative)
-   **Max Tokens 3500**: Sufficient space for comprehensive 5-point analysis
-   **Gemini 2.5 Flash**: Fast, accurate, free-tier suitable

---

## Runtime flow

```
User Selects Mode
    ↓
run_ai_analysis() called with mode parameter
    ↓
build_prompt() constructs instruction + JSON embedding
    ↓
Gemini API receives complete prompt
    ↓
Model generates analysis (mode-specific structure)
    ↓
format_analysis_output() converts markdown → plain text
    ↓
Formatted text saved to ai_suggestion.txt
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
