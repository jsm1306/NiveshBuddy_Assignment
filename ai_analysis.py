# STRUCTURED PROMPT ENGINEERING (MODE-BASED)

def build_prompt(comparison_data: dict, mode: str = "quick") -> str:
    """Builds a mode-based prompt for Gemini API analysis from metrics."""
    import json
    metrics_json = json.dumps(comparison_data, indent=2)
    
    if mode == "quick":
        prompt = f"""You are a quantitative portfolio analyst evaluating two momentum strategies.

Analyze ONLY the provided JSON metrics below.

STRATEGY METRICS (JSON):
{metrics_json}

Return a concise analysis with ONLY 5 bullet insights:

WINNER:
- Which strategy performs better overall?

KEY DIFFERENCE:
- What is the most significant performance gap?

RISK NOTE:
- What is the main risk trade-off?

ONE IMPROVEMENT IDEA:
- Suggest a single realistic enhancement.

TONE:
- Use percentages for metrics.
- Maximum 5 bullets total.
- Be concise and business-readable.
- No long essays.
- Reason ONLY from provided JSON.
- Maintain professional fintech analyst tone."""
    
    elif mode == "detailed":
        prompt = f"""You are a quantitative portfolio analyst evaluating two momentum strategies.

Analyze ONLY the provided JSON metrics below.

STRATEGY METRICS (JSON):
{metrics_json}

Return your analysis in the following structured sections:

PERFORMANCE COMPARISON:
- Compare returns, CAGR, and risk-adjusted metrics across both strategies.
- Use specific values from the JSON data.

RISK VS RETURN ANALYSIS:
- Explain the efficiency frontier positions.
- Discuss drawdown, volatility, and Sharpe ratio trade-offs.
- Determine which strategy offers better risk-adjusted returns.

WHEN EACH STRATEGY OUTPERFORMS:
- Describe market conditions where the 30-day strategy excels.
- Describe market conditions where the 90-day strategy excels.
- Specify risk tolerance scenarios.

IMPROVEMENT SUGGESTION:
- Propose ONE actionable enhancement to the underperforming strategy.
- Explain how it would improve the metrics.
- Be concrete and implementable.

STYLE CONSTRAINTS:
- Use percentages when referring to metrics.
- Ground every claim directly in the provided JSON data.
- Maintain professional fintech analyst tone.
- Allow depth but avoid unnecessary length.
- Quantify all comparisons with actual numbers, not vague language."""
    
    else:
        raise ValueError(f"Mode must be 'quick' or 'detailed', got '{mode}'")
    
    return prompt
import os
import json
from typing import Dict, Optional
import google.generativeai as genai


# CONFIGURATION & INITIALIZATION

def _initialize_gemini_client() -> None:
    """Initializes Gemini API client from environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
    genai.configure(api_key=api_key)


# STRUCTURED DATA PREPARATION

def _build_comparison_payload(
    strategy_30: Dict[str, float],
    strategy_90: Dict[str, float]
) -> Dict:
    """Creates a JSON payload comparing two strategy metrics."""
    comparison_data = {
        "strategy_30_day": {
            "lookback_period_days": 30,
            "metrics": strategy_30
        },
        "strategy_90_day": {
            "lookback_period_days": 90,
            "metrics": strategy_90
        },
        "metadata": {
            "strategy_type": "momentum_rebalancing",
            "rebalance_frequency": "monthly",
            "asset_selection": "top_2_equal_weight"
        }
    }
    
    return comparison_data


# STRUCTURED PROMPT ENGINEERING

def _build_analysis_prompt(comparison_json_str: str) -> str:
    """Builds a prompt string for strategy analysis from JSON metrics."""
    
    prompt = f"""You are a quantitative investment analyst specializing in systematic strategy evaluation.

Your task is to analyze the following two momentum strategies based ONLY on the performance metrics provided. 
Do not use external knowledge or assumptions not grounded in the data.

STRATEGY METRICS (JSON):
{comparison_json_str}

================================================================================
YOU MUST ADDRESS ALL 5 POINTS BELOW - NO EXCEPTIONS
================================================================================

## 1. PERFORMANCE COMPARISON
Compare the two strategies on:
- Total return (absolute performance)
- CAGR (annualized growth)
- Sharpe ratio (risk-adjusted return per volatility)
- Sortino ratio (risk-adjusted return per downside risk)
State which strategy performed better on each metric.

## 2. PERFORMANCE DIFFERENCES
Highlight specific performance gaps:
- Return differences (quantify in percentage points)
- Growth rate differences
- Which strategy achieved more consistent returns

## 3. RISK-RETURN TRADE-OFF ANALYSIS
Analyze the efficiency frontier positions:
- Which strategy offers better risk-adjusted returns
- Is higher return justified by higher risk?
- Compare maximum drawdown vs return potential
- Which strategy is more efficient for the risk taken

## 4. WHEN EACH STRATEGY OUTPERFORMS
Specify conditions/scenarios when:
- 30-day strategy would be preferred
- 90-day strategy would be preferred
- Market conditions that favor each approach
- Risk tolerance scenarios

## 5. ONE SPECIFIC IMPROVEMENT IDEA
Suggest ONE actionable improvement to the underperforming strategy:
- Target the strategy with lower Sharpe ratio
- Propose a specific, practical change
- Explain how it would improve the metrics
- Be concrete and implementable

================================================================================
OUTPUT REQUIREMENTS:
- YOU MUST INCLUDE ALL 5 SECTIONS WITH HEADERS
- Use specific metric values directly from the JSON data
- Quantify all comparisons (use numbers, not vague language)
- Ground every claim in the data
- Be comprehensive and thorough
- Approximate length: 500-700 words (enough for all 5 points)

Begin your analysis with Section 1 and work through all 5 sections:"""
    
    return prompt


# =============================================================================
# GEMINI API INTEGRATION
# =============================================================================

def run_ai_analysis(
    strategy_30: Dict[str, float],
    strategy_90: Dict[str, float],
    mode: str = "quick",
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.3
) -> str:
    """Runs Gemini API analysis for two strategies and returns the result."""
    
    # Validate mode parameter
    if mode not in ["quick", "detailed"]:
        raise ValueError(f"Mode must be 'quick' or 'detailed', got '{mode}'")
    
    # STEP 1: Initialize API client (credentials from environment)
    try:
        _initialize_gemini_client()
    except ValueError as e:
        raise ValueError(f"AI Analysis initialization failed: {e}")
    
    # STEP 2: Build structured JSON payload
    comparison_payload = _build_comparison_payload(strategy_30, strategy_90)
    
    # STEP 3: Create mode-based prompt
    analysis_prompt = build_prompt(comparison_payload, mode)
    
    # STEP 4: Call Gemini API with structured input
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 3500
            }
        )
        
        response = model.generate_content(analysis_prompt)
        
    except Exception as api_error:
        raise Exception(
            f"Gemini API call failed: {api_error}. "
            "Check API key validity and rate limits."
        )
    
    # STEP 5: Extract and return text response
    if response and response.text:
        return response.text
    else:
        raise Exception("Gemini API returned empty response")


# OUTPUT FORMATTING (Optional Presentation Layer)


def format_analysis_output(analysis_text: str) -> str:
    """Converts markdown analysis text to formatted plain text."""
    
    lines = analysis_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Handle ## Headers (main sections)
        if line.startswith('##'):
            header = line.replace('##', '').strip()
            formatted_lines.append('')
            formatted_lines.append('─' * 70)
            formatted_lines.append(f"  ▶ {header.upper()}")
            formatted_lines.append('─' * 70)
            formatted_lines.append('')
        
        # Handle ### Sub-headers
        elif line.startswith('###'):
            subheader = line.replace('###', '').strip()
            formatted_lines.append(f"\n  ◆ {subheader}")
            formatted_lines.append('')
        
        # Handle **bold** text
        elif '**' in line:
            # Replace **text** with UPPERCASE text
            formatted_line = line
            import re
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'>>> \1 <<<', formatted_line)
            formatted_lines.append(formatted_line)
        
        # Handle bullet points
        elif line.strip().startswith('-'):
            formatted_lines.append(f"    • {line.strip()[1:].strip()}")
        
        # Regular lines
        else:
            if line.strip():
                formatted_lines.append(line)
            else:
                formatted_lines.append('')
    
    return '\n'.join(formatted_lines)


def print_analysis(analysis_text: str, strategy_name: str = "Strategy Comparison") -> None:
    """Prints formatted AI analysis to stdout."""
    
    formatted_text = format_analysis_output(analysis_text)
    
    print("\n" + "="*80)
    print(f"{strategy_name.upper():^80}")
    print("="*80)
    print(f"\n{formatted_text}\n")
    print("="*80 + "\n")


# =============================================================================
# OPTIONAL: Logging and Debugging
# =============================================================================

def log_analysis_request(
    strategy_30: Dict[str, float],
    strategy_90: Dict[str, float],
    output_file: Optional[str] = None
) -> None:
    """Logs the analysis request input metrics and payload."""
    
    comparison_payload = _build_comparison_payload(strategy_30, strategy_90)
    comparison_json_str = json.dumps(comparison_payload, indent=2)
    
    log_message = f"""
[AI ANALYSIS REQUEST LOG]
Timestamp: (auto-generated by caller)
Model: gemini-2.5-flash
Temperature: 0.3

INPUT PAYLOAD:
{comparison_json_str}
"""
    
    print(log_message)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(log_message)
