# NiveshBuddy: AI-Powered Momentum Strategy Analysis

A quantitative portfolio analysis system that implements dual momentum strategies (30-day and 90-day lookback), computes comprehensive performance metrics, and leverages Google's Gemini AI to generate actionable insights.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Create and Activate Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv nbenv
   
   # Activate virtual environment
   # On Windows:
   nbenv\Scripts\activate
   # On macOS/Linux:
   source nbenv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   This installs all required packages listed in `requirements.txt`.

3. **Set Up Environment Variable**
   - Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   - Or set it in your system environment variables:
   ```bash
   # Windows PowerShell:
   $env:GEMINI_API_KEY="your_api_key_here"
   
   # Windows CMD:
   set GEMINI_API_KEY=your_api_key_here
   
   # macOS/Linux:
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **Prepare Data**
   - Place your CSV file in the `data/` directory
   - File format: First column must be `Date` (YYYY-MM-DD), remaining columns are asset prices
   - Example:
   ```
   Date,AAPL,MSFT,GOOGL
   2023-01-01,150.00,200.00,100.00
   2023-01-02,151.00,201.00,101.00
   ...
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```
   When prompted, select analysis mode (1 for quick, 2 for detailed).

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

### Data & Market
- **Trading Calendar**: 252 trading days per year (US equity market standard)
- **Asset Universe**: Equities with daily price data in CSV format
- **Data Quality**: No data validation for individual assets; trust in input data integrity

### Strategy Parameters
- **30-Day Strategy**: Uses 30-day momentum lookback to select assets
- **90-Day Strategy**: Uses 90-day momentum lookback for longer-term trends
- **Rebalancing**: Monthly portfolio rebalancing occurs on the last day of each month
- **Asset Selection**: Always selects top 2 performing assets by momentum score
- **Position Sizing**: Equal weight (50/50) allocation to selected assets
- **Cash Handling**: Uninvested capital sits in cash (no returns)

### Financial Metrics
- **Risk-Free Rate**: 0.0% (default for Sharpe Ratio & Sortino Ratio calculations)
- **Target Return**: 0.0% (default for Sortino Ratio; below this is considered "downside")
- **Initial Portfolio Value**: 1.0 (normalized); metrics express returns as decimals

### AI Model
- **Model**: Gemini 2.5 Flash (free tier, fast inference)
- **Temperature**: 0.3 (low randomness for analytical consistency)
- **Max Tokens**: 3,500 per response
- **Input**: JSON-serialized strategy metrics (passed dynamically)

## Design Decisions

### Modular Architecture
The codebase is organized into **separate, single-responsibility modules**:
- `data_loader.py` → Data I/O only
- `strategy_engine.py` → Strategy computation only
- `metrics.py` → Metric calculations only
- `ai_analysis.py` → AI layer isolation
- `main.py` → High-level orchestration

**Rationale**: Easy testing, modification, and debugging without touching other components.

### Momentum Strategy Implementation
- **Why Momentum?** Time-tested quantitative signal; simple, interpretable, and data-driven.
- **Why Two Lookbacks?** Compare short-term vs. long-term trend capture to illustrate risk/return trade-offs.
- **Why Monthly Rebalancing?** Balance between responsiveness and trading costs; monthly is industry-standard for tactical strategies.
- **Why Top 2 Assets?** Concentrated exposure to signal leaders; reduces diversification but increases signal clarity.

### Mode-Based AI Analysis
Two explanation modes are supported to serve different user needs:
- **Quick Mode** (Default): 5 concise bullet insights—ideal for busy decision-makers
- **Detailed Mode**: Full analytical sections—ideal for deep research and documentation

**Rationale**: One-size-fits-all prompts fail to balance brevity vs. rigor. Users select at runtime.

### Metrics Computed
- **Total Return**: Absolute wealth creation from inception
- **CAGR**: Annualized growth for fair period comparison
- **Volatility**: Annualized daily standard deviation
- **Max Drawdown**: Largest peak-to-trough decline (risk indicator)
- **Sharpe Ratio**: Excess return per unit of volatility
- **Sortino Ratio**: Excess return per unit of downside volatility only

**Rationale**: Comprehensive view of return, risk, and risk-adjusted performance.

### Output Formatting & Storage
- Analysis is displayed **formatted** on-screen (clean headers, bullet points, proper line breaks)
- Same formatted analysis is saved to `ai_suggestion.txt` for future review
- Raw API responses are never shown to the user (always formatted)

**Rationale**: Readability and archiving for compliance/documentation.

## AI Prompt Structure Explanation

### Overview
The AI layer uses **dynamic prompt construction** based on user-selected mode and runtime metrics. Prompts are built *after* metrics are computed, embedding real data into instructions.

### Prompt Architecture

#### 1. **Role Definition**
Every prompt starts with:
```
You are a quantitative portfolio analyst evaluating two momentum strategies.
```
**Why?** Establishes analytical context and professional tone.

#### 2. **Data Embedding**
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

#### 3. **Mode-Specific Instructions**

**QUICK MODE** (5 bullets):
```
WINNER:
- Which strategy performs better overall?

KEY DIFFERENCE:
- What is the most significant performance gap?

RISK NOTE:
- What is the main risk trade-off?

ONE IMPROVEMENT IDEA:
- Suggest a single realistic enhancement.
```
**Output**: ~200-400 words. Suitable for executive summaries.

**DETAILED MODE** (4 sections):
```
PERFORMANCE COMPARISON:
- Compare returns, CAGR, and risk-adjusted metrics.

RISK VS RETURN ANALYSIS:
- Discuss drawdown, volatility, Sharpe ratio trade-offs.

WHEN EACH STRATEGY OUTPERFORMS:
- Describe favorable market conditions for each.

IMPROVEMENT SUGGESTION:
- Propose ONE actionable enhancement.
```
**Output**: ~800-1200 words. Suitable for research reports.

#### 4. **Constraint Enforcement**
All prompts include explicit constraints:
- "Reason ONLY from provided JSON."
- "Use percentages for metrics."
- "Avoid generic statements."
- "Maintain professional fintech analyst tone."

**Why?** Reduces model drift and ensures output quality consistency.

### Function: `build_prompt(comparison_data: dict, mode: str) -> str`

**Signature:**
```python
def build_prompt(comparison_data: dict, mode: str = "quick") -> str:
    # Returns formatted prompt string with embedded JSON
```

**Process:**
1. Validate `mode` is "quick" or "detailed"
2. Serialize `comparison_data` to indented JSON
3. Select template based on mode
4. Insert JSON into template using f-strings
5. Return complete prompt ready for API

**Example Call:**
```python
comparison_data = {
    "strategy_30_day": {...},
    "strategy_90_day": {...},
    "metadata": {...}
}
prompt = build_prompt(comparison_data, mode="detailed")
analysis = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
```

### Runtime Flow

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

## Usage Example

### Run with Interactive Mode Selection
```bash
python main.py

# ... data loads, strategies execute ...

# When prompted:
AI ANALYSIS MODE SELECTION
======================================================================
1. Quick Mode   - 5 concise insights
2. Detailed Mode - Full analytical breakdown

Select mode (1 or 2): 2
✓ Detailed mode selected

[INFO] Calling Gemini API for strategy analysis...

# ... analysis displays on screen ...

# Also saved to ai_suggestion.txt
```

### Programmatic Usage
```python
from ai_analysis import run_ai_analysis

strategy_30_metrics = {...}
strategy_90_metrics = {...}

# Quick analysis
quick_analysis = run_ai_analysis(strategy_30_metrics, strategy_90_metrics, mode="quick")

# Detailed analysis
detailed_analysis = run_ai_analysis(strategy_30_metrics, strategy_90_metrics, mode="detailed")
```

## Key Features

✅ **Dual Momentum Strategies** - Compare short-term vs. long-term momentum approaches  
✅ **Comprehensive Metrics** - Return, risk, and risk-adjusted performance measures  
✅ **AI-Powered Insights** - Gemini-based analysis with mode selection  
✅ **Professional Formatting** - Clean, business-readable output  
✅ **Automated Persistence** - Analysis saved to file for archiving  
✅ **Modular Design** - Easy to extend, test, and maintain  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not found` | Ensure `.env` file exists with valid API key, or set environment variable |
| `ModuleNotFoundError: genai` | Run `pip install -r requirements.txt` to install all dependencies |
| `Empty CSV` or `No Date column` | Verify data format: Date must be first column, asset prices in remaining columns |
| Slow API response | Normal for Gemini. Max timeout is ~30 seconds. Check internet connection. |

## Performance Notes

- **Data Loading**: ~100ms for 5 years of daily data
- **Strategy Computation**: ~50ms per strategy
- **Metrics Calculation**: ~10ms
- **Gemini API Call**: ~3-8 seconds (network dependent)
- **Total Workflow**: ~10-15 seconds typical

## Future Enhancements

- [ ] Custom lookback periods (not just 30/90)
- [ ] Multiple asset universe selection
- [ ] Risk constraints (max drawdown limits)
- [ ] Visualization (equity curves, distribution plots)
- [ ] Backtesting statistics (win rate, Sortino, Calmar)
- [ ] Database schema for historical analysis tracking

## License

This project is provided as-is for educational and research purposes.

---

**Last Updated**: February 21, 2026  
**Python Version**: 3.8+  
**Dependencies**: See `requirements.txt` for all package versions
