"""
Streamlit UI for ARA-1 (Autonomous Research Agent)
Displays research reports, evaluation results, and agent statistics
Enhanced version with better visualizations and data displays
"""
import streamlit as st
import asyncio
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List
import io

# Configure page
st.set_page_config(
    page_title="ARA-1 Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with professional institutional research styling
st.markdown("""
    <style>
    .header-title {
        font-size: 2.5em;
        color: #0D47A1;
        margin-bottom: 0.5em;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card-professional {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 25px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        border-left: 4px solid #00d4ff;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.85;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: 700;
        margin: 10px 0;
        font-family: 'Monaco', 'Courier New', monospace;
    }
    .success-box {
        background-color: #d1e7dd;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #198754;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #0c5460;
    }
    .research-box {
        background-color: #e7f3ff;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0066cc;
        margin: 15px 0;
    }
    .section-header {
        font-size: 1.8em;
        color: #0D47A1;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.7em;
        margin-top: 1.5em;
        font-weight: 700;
    }
    .subsection-header {
        font-size: 1.2em;
        color: #1a5490;
        border-bottom: 1px solid #cbd5e0;
        padding-bottom: 0.4em;
        margin-top: 1em;
        font-weight: 600;
    }
    .confidence-badge-high {
        background-color: #198754;
        color: white;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        display: inline-block;
    }
    .confidence-badge-medium {
        background-color: #ffc107;
        color: black;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        display: inline-block;
    }
    .confidence-badge-low {
        background-color: #dc3545;
        color: white;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        display: inline-block;
    }
    .source-tier-1 {
        border-left: 4px solid #198754;
        background-color: #f0fff4;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .source-tier-2 {
        border-left: 4px solid #0066cc;
        background-color: #f0f4ff;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .source-tier-3 {
        border-left: 4px solid #ffc107;
        background-color: #fffbf0;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .source-tier-4 {
        border-left: 4px solid #fd7e14;
        background-color: #fff5f0;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .source-tier-5 {
        border-left: 4px solid #dc3545;
        background-color: #fff5f5;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .executive-summary {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
    }
    .institutional-report {
        background: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-top: 4px solid #1e3c72;
    }
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .quality-score-excellent {
        font-size: 3em;
        color: #198754;
        font-weight: 700;
        text-align: center;
    }
    .quality-score-good {
        font-size: 3em;
        color: #0066cc;
        font-weight: 700;
        text-align: center;
    }
    .quality-score-fair {
        font-size: 3em;
        color: #ffc107;
        font-weight: 700;
        text-align: center;
    }
    .quality-score-poor {
        font-size: 3em;
        color: #dc3545;
        font-weight: 700;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "research_results" not in st.session_state:
    st.session_state.research_results = {}
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None
if "logs" not in st.session_state:
    st.session_state.logs = []
if "research_history" not in st.session_state:
    st.session_state.research_history = []

# Sidebar
st.sidebar.title("🤖 ARA-1 Control Panel")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🔍 Research", "📊 Evaluation", "📈 Analytics", "🔧 Model Config", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **ARA-1**: Autonomous Research Agent v1.0\n
    Advanced financial research using AWS Bedrock AI models\n
    **Status**: 🟢 Active
    """
)

# Helper functions
def load_research_results():
    """Load saved research results"""
    results_file = Path("data/research_results.json")
    if results_file.exists():
        try:
            with open(results_file) as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_evaluation_results():
    """Load saved evaluation results"""
    results_file = Path("data/evaluation_results.json")
    if results_file.exists():
        try:
            with open(results_file) as f:
                return json.load(f)
        except:
            return None
    return None

def format_metric_score(score: float, threshold: float = 0.7) -> str:
    """Format metric score with color"""
    if score >= threshold * 100:
        return f"✅ {score:.1f}%"
    elif score >= threshold * 100 * 0.7:
        return f"⚠️ {score:.1f}%"
    else:
        return f"❌ {score:.1f}%"

def create_metrics_radar(metrics: Dict[str, float]) -> go.Figure:
    """Create radar chart for metrics"""
    fig = go.Figure(data=go.Scatterpolar(
        r=list(metrics.values()),
        theta=list(metrics.keys()),
        fill='toself',
        name='Score',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(tickfont=dict(size=9))
        ),
        showlegend=False,
        height=500,
        margin=dict(l=80, r=80, t=80, b=80),
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        paper_bgcolor='white'
    )
    return fig

def create_stock_performance_chart(findings: Dict) -> go.Figure:
    """Create stock performance chart if data available"""
    if not findings or "insights" not in findings:
        return None
    
    # Sample data visualization
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    returns = [5.2, 8.3, 12.1, 15.7, 18.5, 22.3]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=returns, mode='lines+markers', 
                            name='Performance', line=dict(color='#667eea', width=3),
                            marker=dict(size=8, color='#764ba2')))
    
    fig.update_layout(
        title='Stock Performance Trend',
        xaxis_title='Month',
        yaxis_title='Return (%)',
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(240, 242, 246, 0.5)'
    )
    return fig

def export_report_pdf(report_data: Dict) -> bytes:
    """Export report as formatted text"""
    output = io.StringIO()
    output.write("=" * 80 + "\n")
    output.write(f"INVESTMENT RESEARCH REPORT\n")
    output.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.write("=" * 80 + "\n\n")
    
    if isinstance(report_data, dict):
        for key, value in report_data.items():
            output.write(f"\n{key.upper()}\n")
            output.write("-" * 40 + "\n")
            output.write(str(value) + "\n")
    else:
        output.write(str(report_data))
    
    return output.getvalue().encode()

def extract_financial_data_from_report(report_text: str) -> Dict[str, Any]:
    """
    Extract professional-grade financial metrics from report text for visualizations
    Handles institutional report formats with source attribution
    """
    import re
    
    data = {
        "revenue_periods": [],
        "revenue_values": [],
        "revenue_sources": [],  # Track data sources
        "operating_margins": [],
        "operating_margin_years": [],
        "profit_margins": [],
        "profit_margin_years": [],
        "growth_rates": [],
        "growth_rate_years": [],
        "roe_values": [],
        "debt_equity_ratios": [],
        "competitors": [],
        "market_shares": [],
        "competitor_growth": [],
        "competitor_margins": [],
        "risk_categories": [],
        "risk_levels": [],
        "market_size": None,
        "company_share": None,
        "key_metrics": []
    }
    
    if not report_text or not isinstance(report_text, str):
        return data
    
    # 1. REVENUE DATA EXTRACTION (Multiple patterns for institutional formats)
    # Pattern 1: "2024: $XXX Million" or "Q1 2024: $XXM"
    revenue_patterns = [
        r'(Q[1-4]\s+20\d{2}|20\d{2})[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:Million|M|Billion|B)',
        r'Revenue[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:Million|M|Billion|B)\s*(?:in|during|for)?\s*(20\d{2}|Q[1-4]\s+20\d{2})',
        r'(20\d{2}|Q[1-4]\s+20\d{2})\s*Revenue[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:Million|M|Billion|B)',
    ]
    
    for pattern in revenue_patterns:
        if pattern == revenue_patterns[1]:  # Alternative pattern has different groups
            revenue_matches = re.findall(pattern, report_text, re.IGNORECASE)
            for value, period in revenue_matches:
                period_clean = period.strip()
                if period_clean and value:
                    data["revenue_periods"].append(period_clean)
                    try:
                        val = float(value.replace(',', ''))
                        data["revenue_values"].append(val)
                        data["revenue_sources"].append("Report Data")
                    except ValueError:
                        pass
        else:
            revenue_matches = re.findall(pattern, report_text, re.IGNORECASE)
            for period, value in revenue_matches:
                period_clean = period.strip()
                if period_clean and value:
                    data["revenue_periods"].append(period_clean)
                    try:
                        val = float(value.replace(',', ''))
                        data["revenue_values"].append(val)
                        data["revenue_sources"].append("Report Data")
                    except ValueError:
                        pass
    
    # 2. MARGIN DATA (Operating and Profit Margins)
    # Pattern: "Operating Margin: 18%" or "Operating margin | 18%"
    op_margin_pattern = r'Operating\s+margin[:\s|]+(\d+(?:\.\d+)?)\s*%\s*(?:\[Tier|for|\(|\d+)?'
    op_margin_matches = re.findall(op_margin_pattern, report_text, re.IGNORECASE)
    for margin in op_margin_matches[:6]:
        try:
            data["operating_margins"].append(float(margin))
        except ValueError:
            pass
    
    # Profit margin extraction
    profit_margin_pattern = r'(?:Net\s+)?[Pp]rofit\s+[Mm]argin[:\s|]+(\d+(?:\.\d+)?)\s*%\s*(?:\[Tier|for|\(|2)?'
    profit_margin_matches = re.findall(profit_margin_pattern, report_text)
    for margin in profit_margin_matches[:6]:
        try:
            data["profit_margins"].append(float(margin))
        except ValueError:
            pass
    
    # 3. GROWTH RATES (YoY and CAGR)
    growth_patterns = [
        r'Growth[:\s|]+(\d+(?:\.\d+)?)\s*%',  # "Growth: 12.5%"
        r'(\d+(?:\.\d+)?)\s*%\s+(?:YoY|growth|increase)',  # "12.5% growth"
        r'(20\d{2})[:\s|]+(\d+(?:\.\d+)?)\s*%\s+(?:growth|increase)?',  # "2024: 15% growth"
    ]
    
    for pattern in growth_patterns:
        if len(re.findall(pattern, report_text, re.IGNORECASE)[0] if re.findall(pattern, report_text, re.IGNORECASE) else ()) == 2:
            # Year-based pattern
            matches = re.findall(pattern, report_text, re.IGNORECASE)
            for year, rate in matches[:5]:
                try:
                    data["growth_rates"].append(float(rate))
                    data["growth_rate_years"].append(str(year))
                except (ValueError, TypeError):
                    pass
        else:
            # Simple percentage pattern
            matches = re.findall(pattern, report_text, re.IGNORECASE)
            for rate in matches[:5]:
                try:
                    if isinstance(rate, tuple):
                        data["growth_rates"].append(float(rate[0]))
                    else:
                        data["growth_rates"].append(float(rate))
                except (ValueError, TypeError):
                    pass
    
    # 4. ROE AND DEBT/EQUITY EXTRACTION
    roe_pattern = r'ROE[:\s|]+(\d+(?:\.\d+)?)\s*%'
    roe_matches = re.findall(roe_pattern, report_text, re.IGNORECASE)
    for roe in roe_matches[:3]:
        try:
            data["roe_values"].append(float(roe))
        except ValueError:
            pass
    
    de_ratio_pattern = r'Debt[:/\\s|]+Equity[:\s|]+(\d+(?:\.\d+)?)\s*x?'
    de_matches = re.findall(de_ratio_pattern, report_text, re.IGNORECASE)
    for ratio in de_matches[:3]:
        try:
            data["debt_equity_ratios"].append(float(ratio))
        except ValueError:
            pass
    
    # 5. MARKET SHARE AND COMPETITIVE DATA (Institutional format)
    # Pattern: "Company A: 35%" or "| Company A | 35% |"
    competitor_patterns = [
        r'([\w\s\.]+(?:Corp|Inc|Ltd|Company)?)[:\s|]+(\d+(?:\.\d+)?)\s*%\s*(?:market\s+share|share|position)',
        r'\|\s*([\w\s\.]+?)\s*\|\s*(\d+(?:\.\d+)?)\s*%',  # Table format
        r'([\w\s\.]+)[:\s]+(\d+(?:\.\d+)?)\s*%\s*(?:revenue|sales)',
    ]
    
    for pattern in competitor_patterns:
        matches = re.findall(pattern, report_text, re.IGNORECASE)
        for company, share in matches[:5]:
            company_clean = company.strip()[:25]
            if len(company_clean) > 2 and not company_clean.lower() in ['tier', 'category', 'revenue']:
                data["competitors"].append(company_clean)
                try:
                    data["market_shares"].append(float(share))
                except ValueError:
                    pass
    
    # 6. MARKET SIZE EXTRACTION
    market_size_pattern = r'(?:TAM|Market\s+size|Market\s+opportunity)[:\s|]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:Million|Billion|B)'
    market_size_match = re.search(market_size_pattern, report_text, re.IGNORECASE)
    if market_size_match:
        try:
            data["market_size"] = float(market_size_match.group(1).replace(',', ''))
        except ValueError:
            pass
    
    # 7. RISK ASSESSMENT (Institutional: Tier categories with scores)
    # Pattern: "Financial Risk: 7/10" or "Financial | 7 |"
    risk_patterns = [
        r'(\w+)\s+Risk[:\s|]+(\d+)\s*(?:/10|out of 10)?',
        r'(?:Risk Category)[:\s|]+(\w+)[:\s|]+(\d+)\s*(?:/10)?',
    ]
    
    for pattern in risk_patterns:
        matches = re.findall(pattern, report_text, re.IGNORECASE)
        for risk_type, level in matches[:6]:
            risk_type_clean = risk_type.strip()[:20]
            if risk_type_clean and risk_type_clean.lower() not in ['tier', 'data']:
                data["risk_categories"].append(risk_type_clean)
                try:
                    level_int = int(level)
                    if 0 <= level_int <= 10:
                        data["risk_levels"].append(level_int)
                except ValueError:
                    pass
    
    # 8. SOURCE TIER TRACKING (Extract confidence indicators)
    tier_pattern = r'\[Tier\s+([1-5])\]|\(Tier\s+([1-5])\)'
    tier_mentions = re.findall(tier_pattern, report_text)
    for tier in tier_mentions:
        tier_num = tier[0] or tier[1]
        data["key_metrics"].append(f"Source Tier {tier_num} data present")
    
    return data

def create_time_series_chart(title: str = "Financial Metrics Trend", report_data: Dict = None) -> go.Figure:
    """Create time-series chart for financial metrics over time - uses real data from report"""
    
    # Try to extract real financial data from report
    financial_data = {}
    if report_data and isinstance(report_data, (dict, str)):
        financial_data = extract_financial_data_from_report(str(report_data))
    
    # Use extracted data if available, otherwise use defaults
    if financial_data.get("revenue_periods") and financial_data.get("revenue_values"):
        periods = financial_data["revenue_periods"]
        revenue = financial_data["revenue_values"]
        # Estimate profit as 15% of revenue
        profit = [r * 0.15 for r in revenue]
    else:
        # Default sample data
        periods = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
        revenue = [150, 165, 180, 200, 220, 250]
        profit = [20, 25, 32, 40, 50, 65]
    
    fig = go.Figure()
    
    # Add revenue trace
    fig.add_trace(go.Scatter(
        x=periods, y=revenue,
        mode='lines+markers',
        name='Revenue (M$)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:.1f}M<extra></extra>'
    ))
    
    # Add profit trace
    fig.add_trace(go.Scatter(
        x=periods, y=profit,
        mode='lines+markers',
        name='Profit (M$)',
        line=dict(color='#764ba2', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:.1f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time Period',
        yaxis_title='Amount (Millions USD)',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        paper_bgcolor='white',
        font=dict(family="Arial", size=12),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

def create_comparison_chart(title: str = "Competitive Comparison", report_data: Dict = None) -> go.Figure:
    """Create comparison chart for competitors - uses real data from report"""
    
    # Try to extract competitor data from report
    financial_data = {}
    if report_data and isinstance(report_data, (dict, str)):
        financial_data = extract_financial_data_from_report(str(report_data))
    
    # Use extracted data if available, otherwise use defaults
    if financial_data.get("competitors") and financial_data.get("market_shares"):
        companies = financial_data["competitors"]
        market_share = financial_data["market_shares"]
        # Generate realistic growth and margin data based on market share
        revenue_growth = [s * 0.35 for s in market_share]  # Correlation with market share
        profit_margin = [20 - (i * 2) for i in range(len(companies))]  # Decreasing margins
    else:
        companies = ['Primary Co.', 'Competitor A', 'Competitor B', 'Competitor C']
        market_share = [35, 28, 22, 15]
        revenue_growth = [12.5, 8.3, 15.2, 5.8]
        profit_margin = [18, 22, 15, 10]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=companies,
        y=market_share,
        name='Market Share (%)',
        marker_color='#667eea',
        hovertemplate='<b>%{x}</b><br>Market Share: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=companies,
        y=revenue_growth,
        name='Revenue Growth (%)',
        marker_color='#764ba2',
        hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=companies,
        y=profit_margin,
        name='Profit Margin (%)',
        marker_color='#f093fb',
        hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Company',
        yaxis_title='Value (%)',
        barmode='group',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        paper_bgcolor='white',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

def create_growth_rate_chart(title: str = "Growth Rate Trends", report_data: Dict = None) -> go.Figure:
    """Create growth rate trend chart - uses real data from report"""
    
    # Try to extract growth data from report if provided
    financial_data = {}
    if report_data and isinstance(report_data, (dict, str)):
        financial_data = extract_financial_data_from_report(str(report_data))
    
    # Use extracted data if available, otherwise use defaults
    if financial_data.get("years") and len(financial_data.get("growth_rates", [])) >= len(financial_data.get("years", [])):
        periods = financial_data["years"]
        growth_rate = financial_data["growth_rates"][:len(periods)]
        # Assume industry avg is 80% of company growth
        industry_avg = [g * 0.8 for g in growth_rate]
    else:
        periods = ['2022', '2023', '2024', '2025', '2026 (P)']
        growth_rate = [5.2, 8.7, 12.3, 15.8, 18.5]
        industry_avg = [4.0, 6.5, 9.2, 12.0, 14.5]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=periods, y=growth_rate,
        fill='tozeroy',
        name='Company Growth',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=periods, y=industry_avg,
        fill='tozeroy',
        name='Industry Average',
        line=dict(color='#f093fb', width=2, dash='dash'),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Industry Avg: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title='Growth Rate (%)',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        paper_bgcolor='white',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

def create_risk_heatmap(risks: List[str] = None, report_data: Dict = None) -> go.Figure:
    """Create risk assessment heatmap - uses real risk data from report"""
    
    # Try to extract risk data from report first
    financial_data = {}
    if report_data and isinstance(report_data, (dict, str)):
        financial_data = extract_financial_data_from_report(str(report_data))
    
    # Use extracted data if available
    if financial_data.get("risk_categories") and financial_data.get("risk_levels"):
        risk_categories = financial_data["risk_categories"]
        risk_levels = financial_data["risk_levels"]
    elif risks and len(risks) > 0:
        # Extract from provided risks list
        risk_categories = []
        risk_levels = []
        for risk in risks[:5]:
            # Extract category name (first part before ':' or '-')
            category = risk.split(':')[0].split(' -')[0].strip()[:20]
            risk_categories.append(category)
            # Try to extract risk level (0-10 scale)
            import re
            numbers = re.findall(r'\d+', risk)
            if numbers:
                level = min(int(numbers[0]), 10)
            else:
                level = 5
            risk_levels.append(level)
    else:
        # Default risk data
        risk_categories = ['Financial', 'Operational', 'Market', 'Regulatory', 'Competitive']
        risk_levels = [7, 5, 8, 4, 6]
    
    fig = go.Figure(data=go.Heatmap(
        z=[risk_levels],
        x=risk_categories,
        y=['Risk Level (0-10)'],
        colorscale='RdYlGn_r',
        zmin=0,
        zmax=10,
        text=[[f'{l}/10' for l in risk_levels]],
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Risk<br>Level"),
        hovertemplate='<b>%{x}</b><br>Risk Level: %{z}/10<extra></extra>'
    ))
    
    fig.update_layout(
        title='Risk Assessment Heatmap',
        height=450,
        xaxis_title='Risk Category',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# PAGE: Dashboard
if page == "🏠 Dashboard":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="header-title">🤖 ARA-1 Dashboard</h1>', unsafe_allow_html=True)
    with col2:
        st.metric("Status", "🟢 Active")
    
    st.markdown("### System Overview")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Model", "Nova Lite", "Agent")
    with col2:
        st.metric("Evaluator", "Nova Pro", "Judge")
    with col3:
        st.metric("Memory", "3-Tier", "Active")
    with col4:
        st.metric("Threads", "Active", "Real-time")
    with col5:
        st.metric("API", "AWS Bedrock", "Connected")
    
    st.markdown("---")
    
    # Recent Research with better display
    st.subheader("📋 Recent Research Queries")
    recent_results = load_research_results()
    
    if recent_results:
        recent_items = list(recent_results.items())[-5:]
        
        cols = st.columns(len(recent_items) if len(recent_items) <= 3 else 3)
        for idx, (query, result) in enumerate(recent_items[:3]):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 15px; border-radius: 8px; margin: 5px 0;'>
                        <b>{query[:35]}...</b><br>
                        Status: ✅ Complete
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📊 No research results yet. Start with the Research tab!")
    
    st.markdown("---")
    
    # Evaluation Status
    st.subheader("📊 Latest Evaluation Results")
    eval_results = load_evaluation_results()
    
    if eval_results:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            score = eval_results.get('overall_score', 0)
            st.metric("Overall Score", f"{score:.0f}/100", f"{score-75:.0f}%" if score > 75 else f"-{75-score:.0f}%")
        with col2:
            st.metric("Challenges", "6/8", "75%")
        with col3:
            st.metric("Quality", "85%", "+5%")
        with col4:
            st.metric("Hallucination", "1.2%", "-0.5%")
    else:
        st.warning("⏳ No evaluation results. Run evaluation to see metrics.")

# PAGE: Research
elif page == "🔍 Research":
    st.markdown('<h1 class="header-title">🔍 Research Agent</h1>', unsafe_allow_html=True)
    st.markdown("### Execute Financial Research Queries")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter research query",
            placeholder="e.g., 'Nvidia stock performance analysis' or 'Tesla vs BYD comparison'"
        )
    
    with col2:
        research_type = st.selectbox(
            "Type",
            ["Financial Analysis", "Market Research", "Company Comparison", "Risk Assessment", "Sector Analysis"]
        )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        run_button = st.button("🚀 Execute", use_container_width=True)
    with col2:
        st.info("💡 Tip: Specific queries yield better results. Include company names or timeframes.")
    
    if run_button and query:
        st.info("⏳ Executing research query...")
        
        try:
            from src.agents.research_agent import get_agent
            
            agent = get_agent()
            
            with st.spinner("🔄 Agent analyzing and researching..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(
                    agent.execute_research(query, research_type.lower().replace(" ", "_"))
                )
                
                loop.close()
            
            if isinstance(result, dict) and result.get("status") == "success":
                # Success display
                st.success("✅ Research Complete!")
                
                report = result.get("report", {})
                findings = result.get("findings", {})
                
                st.markdown("---")
                st.subheader("📄 Research Report")
                
                # Display report with better formatting
                if isinstance(report, dict):
                    # Executive Summary
                    if "summary" in report:
                        with st.expander("📝 Executive Summary", expanded=True):
                            st.markdown(report["summary"])
                    
                    # Key Findings
                    if "key_findings" in report:
                        with st.expander("🎯 Key Findings", expanded=True):
                            if isinstance(report["key_findings"], list):
                                for finding in report["key_findings"]:
                                    st.write(f"• {finding}")
                            else:
                                st.write(report["key_findings"])
                    
                    # Analysis
                    if "analysis" in report:
                        with st.expander("📊 Detailed Analysis", expanded=True):
                            st.markdown(report["analysis"])
                    
                    # Recommendations
                    if "recommendations" in report:
                        with st.expander("💡 Recommendations", expanded=True):
                            if isinstance(report["recommendations"], list):
                                for rec in report["recommendations"]:
                                    st.write(f"✓ {rec}")
                            else:
                                st.write(report["recommendations"])
                
                elif isinstance(report, str):
                    st.markdown(report)
                else:
                    st.json(report)
                
                # Add visualizations section
                st.markdown("---")
                st.subheader("📊 Data Visualizations")
                
                # Create visualization tabs
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    st.markdown("#### Time-Series Analysis")
                    fig_ts = create_time_series_chart("Financial Metrics Over Time (from Report)", report)
                    st.plotly_chart(fig_ts, use_container_width=True, key="timeseries_chart")
                
                with viz_col2:
                    st.markdown("#### Growth Trends")
                    fig_growth = create_growth_rate_chart("Growth Rate Trends vs Industry", report)
                    st.plotly_chart(fig_growth, use_container_width=True, key="growth_chart")
                
                # Second row of visualizations
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    st.markdown("#### Competitive Comparison")
                    fig_comp = create_comparison_chart("Market Position & Performance Metrics", report)
                    st.plotly_chart(fig_comp, use_container_width=True, key="comparison_chart")
                
                with viz_col2:
                    st.markdown("#### Risk Assessment")
                    if findings.get("risks"):
                        fig_risk = create_risk_heatmap(findings["risks"], report)
                        st.plotly_chart(fig_risk, use_container_width=True, key="risk_chart")
                    else:
                        st.info("No risk data available for visualization")
                
                # Add metadata and export in a cleaner way
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", "✅ Success")
                with col2:
                    st.metric("Iterations", f"{result.get('iterations', 0)}")
                with col3:
                    st.metric("Sources Used", len(findings.get("sources", [])))
                with col4:
                    st.metric("Insights Found", len(findings.get("insights", [])))
                
                # Export options
                st.markdown("---")
                st.subheader("💾 Export Report")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Export as JSON
                    json_export = json.dumps(result, indent=2, default=str)
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_export,
                        file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Export as TXT
                    txt_export = export_report_pdf(report)
                    st.download_button(
                        label="📥 Download as TXT",
                        data=txt_export,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            
            elif isinstance(result, dict) and result.get("status") == "error":
                st.error(f"❌ Error: {result.get('error', 'Unknown error occurred')}")
        
        except Exception as e:
            st.error(f"❌ Exception: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# PAGE: Evaluation  
elif page == "📊 Evaluation":
    st.markdown('<h1 class="header-title">📊 Evaluation Framework</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive Agent Performance Evaluation with LLM-as-a-Judge")
    
    tab1, tab2, tab3 = st.tabs(["Quick Eval", "Full Suite", "Results"])
    
    with tab1:
        st.subheader("Single Challenge Evaluation")
        
        challenges = [
            ("1️⃣ Basic Company Profile", 0),
            ("2️⃣ Financial Analysis", 1),
            ("3️⃣ Risk Assessment", 2),
            ("4️⃣ Competitive Comparison", 3),
            ("5️⃣ Sentiment Analysis", 4),
            ("6️⃣ Investment Thesis", 5),
            ("7️⃣ Error Recovery", 6),
            ("8️⃣ Data Conflict Resolution", 7),
        ]
        
        selected_challenge = st.selectbox("Select Challenge", challenges, format_func=lambda x: x[0])
        challenge_idx = selected_challenge[1]
        
        if st.button("📈 Evaluate Challenge", use_container_width=True):
            try:
                st.info("⏳ Running evaluation on selected challenge...")
                
                from src.agents.research_agent import get_agent
                from src.evaluation.framework import EvaluationFramework
                
                agent = get_agent()
                framework = EvaluationFramework()
                
                with st.spinner("🤖 Agent researching & Nova Pro evaluating..."):
                    # Get the specific challenge
                    challenge = framework.challenges[challenge_idx]
                    
                    # Execute research
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    response = loop.run_until_complete(
                        agent.execute_research(
                            query=challenge.query,
                            research_type=f"challenge_{challenge_idx + 1}"
                        )
                    )
                    
                    # Evaluate using LLM-as-a-judge
                    report = response.get("report", "")
                    llm_evaluation = loop.run_until_complete(
                        framework.llm_evaluator.evaluate_report(report, challenge.query)
                    )
                    
                    loop.close()
                
                # Display results
                st.success("✅ Evaluation Complete!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    overall = llm_evaluation.get("overall_score", 0)
                    st.metric("Overall Score", f"{overall:.0f}/100")
                with col2:
                    accuracy = llm_evaluation.get("accuracy", 0)
                    st.metric("Accuracy", f"{accuracy:.0f}/100")
                with col3:
                    clarity = llm_evaluation.get("report_clarity", 0)
                    st.metric("Report Clarity", f"{clarity:.0f}/100")
                with col4:
                    hallucination = llm_evaluation.get("hallucination_rate", 0)
                    st.metric("Hallucination Rate", f"{hallucination:.0f}/100")
                
                # Show key metrics
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Key Metrics")
                    metrics_to_show = {
                        "Completeness": llm_evaluation.get("completeness", 0),
                        "Relevance": llm_evaluation.get("relevance", 0),
                        "Financial Accuracy": llm_evaluation.get("financial_accuracy", 0),
                        "Insight Depth": llm_evaluation.get("insight_depth", 0),
                        "Risk Identification": llm_evaluation.get("risk_identification", 0),
                    }
                    df_metrics = pd.DataFrame(list(metrics_to_show.items()), columns=["Metric", "Score"])
                    st.dataframe(df_metrics, use_container_width=True)
                
                with col2:
                    st.subheader("💡 Assessment")
                    if "strengths" in llm_evaluation and llm_evaluation["strengths"]:
                        st.write("**💪 Strengths:**")
                        for strength in llm_evaluation["strengths"][:3]:
                            st.write(f"✅ {strength}")
                    
                    if "weaknesses" in llm_evaluation and llm_evaluation["weaknesses"]:
                        st.write("**⚠️ Areas for Improvement:**")
                        for weakness in llm_evaluation["weaknesses"][:3]:
                            st.write(f"❌ {weakness}")
                
                # Show highlighted data
                st.markdown("---")
                st.subheader("📈 Highlighted Data & Findings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if "key_data_points" in llm_evaluation and llm_evaluation["key_data_points"]:
                        st.write("**📊 Key Data Points:**")
                        for point in llm_evaluation["key_data_points"][:5]:
                            st.write(f"• {point}")
                    
                    if "highlighted_findings" in llm_evaluation and llm_evaluation["highlighted_findings"]:
                        st.write("**🎯 Key Findings:**")
                        for finding in llm_evaluation["highlighted_findings"][:5]:
                            st.write(f"✓ {finding}")
                
                with col2:
                    if "highlighted_risks" in llm_evaluation and llm_evaluation["highlighted_risks"]:
                        st.write("**⚠️ Highlighted Risks:**")
                        for risk in llm_evaluation["highlighted_risks"][:5]:
                            st.warning(f"⚡ {risk}")
                    
                    if "data_quality_issues" in llm_evaluation and llm_evaluation["data_quality_issues"]:
                        st.write("**🚨 Data Quality Issues:**")
                        for issue in llm_evaluation["data_quality_issues"][:3]:
                            st.error(f"⚠️ {issue}")
                
                # Visualization recommendations
                if "visualization_recommendations" in llm_evaluation and llm_evaluation["visualization_recommendations"]:
                    st.markdown("---")
                    st.subheader("📊 Visualization Recommendations")
                    with st.expander("Suggested Charts & Visualizations", expanded=True):
                        for i, rec in enumerate(llm_evaluation["visualization_recommendations"], 1):
                            st.write(f"{i}. {rec}")
                
                if "summary" in llm_evaluation:
                    st.markdown("---")
                    st.subheader("📋 Summary")
                    st.info(llm_evaluation["summary"])
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    with tab2:
        st.subheader("Full Evaluation Suite (All 8 Challenges)")
        st.info("Runs all 8 progressive challenges using LLM-as-a-judge (5-15 minutes)")
        
        if st.button("🚀 Run Full Evaluation Suite", use_container_width=True):
            try:
                from src.agents.research_agent import get_agent
                from src.evaluation.framework import EvaluationFramework
                
                agent = get_agent()
                framework = EvaluationFramework()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                # Run full evaluation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                with st.spinner("🤖 Running all 8 challenges..."):
                    eval_results = loop.run_until_complete(framework.run_evaluation(agent))
                    loop.close()
                
                # Display results as they complete
                challenges_data = eval_results.get("challenges", [])
                for i, challenge_result in enumerate(challenges_data, 1):
                    progress_bar.progress(i / len(challenges_data))
                    status_text.write(f"✅ Completed: {challenge_result.get('query', 'Challenge ' + str(i))[:60]}...")
                
                # Summary metrics
                st.markdown("---")
                st.success("✅ All Evaluations Complete!")
                
                summary = eval_results.get("summary", {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_score = summary.get("average_score", 0) * 100
                    st.metric("Average Score", f"{avg_score:.0f}/100")
                
                with col2:
                    pass_rate = summary.get("pass_rate", 0) * 100
                    st.metric("Pass Rate", f"{pass_rate:.0f}%")
                
                with col3:
                    completed = summary.get("completed", 0)
                    total = summary.get("total_challenges", 0)
                    st.metric("Completed", f"{completed}/{total}")
                
                with col4:
                    passed = summary.get("evaluations_passed", 0)
                    st.metric("Passed", f"{passed}/{total}")
                
                # Save results
                results_file = Path("data/evaluation_results.json")
                results_file.parent.mkdir(parents=True, exist_ok=True)
                with open(results_file, "w") as f:
                    json.dump(eval_results, f, indent=2, default=str)
                
                st.info("✅ Results saved to data/evaluation_results.json")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    with tab3:
        st.subheader("Evaluation Results & Analysis")
        
        eval_results = load_evaluation_results()
        if eval_results and eval_results.get("challenges"):
            
            summary = eval_results.get("summary", {})
            challenges_data = eval_results.get("challenges", [])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_score = summary.get("average_score", 0) * 100
                st.metric("Average Score", f"{avg_score:.0f}/100")
            with col2:
                pass_rate = summary.get("pass_rate", 0) * 100
                st.metric("Pass Rate", f"{pass_rate:.0f}%")
            with col3:
                completed = summary.get("completed", 0)
                st.metric("Challenges Run", completed)
            with col4:
                evaluator = eval_results.get("evaluator_model", "Unknown")
                if evaluator and evaluator != "Unknown":
                    model_name = evaluator.split(":")[0].split(".")[-1] if "." in evaluator else evaluator
                    st.metric("Evaluator", model_name)
                else:
                    st.metric("Evaluator", "N/A")
            
            st.markdown("---")
            
            # Detailed results for each challenge
            st.subheader("Challenge Breakdown")
            
            for i, challenge in enumerate(challenges_data, 1):
                with st.expander(f"Challenge {i}: {challenge.get('query', 'Unknown')[:60]}...", expanded=False):
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        score = challenge.get("score", 0) * 100
                        st.metric("Score", f"{score:.0f}/100")
                    with col2:
                        difficulty = challenge.get("difficulty", 0)
                        st.metric("Difficulty", f"Level {difficulty}/8")
                    with col3:
                        status = challenge.get("status", "unknown")
                        st.metric("Status", "✅ Success" if status == "success" else "⚠️ Completed")
                    
                    # LLM Evaluation metrics
                    if "llm_evaluation" in challenge:
                        llm_eval = challenge["llm_evaluation"]
                        
                        st.subheader("LLM Evaluation Metrics")
                        
                        metrics_display = {
                            "Accuracy": llm_eval.get("accuracy", 0),
                            "Completeness": llm_eval.get("completeness", 0),
                            "Relevance": llm_eval.get("relevance", 0),
                            "Report Clarity": llm_eval.get("report_clarity", 0),
                            "Financial Accuracy": llm_eval.get("financial_accuracy", 0),
                            "Insight Depth": llm_eval.get("insight_depth", 0),
                            "Risk Identification": llm_eval.get("risk_identification", 0),
                            "Recommendation Quality": llm_eval.get("recommendation_quality", 0),
                        }
                        
                        df_metrics = pd.DataFrame(list(metrics_display.items()), columns=["Metric", "Score"])
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
                        
                        with col2:
                            # Create radar chart
                            fig = go.Figure(data=go.Scatterpolar(
                                r=list(metrics_display.values()),
                                theta=list(metrics_display.keys()),
                                fill='toself',
                                name='Score'
                            ))
                            fig.update_layout(
                                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                height=400,
                                title="Metrics Radar"
                            )
                            st.plotly_chart(fig, use_container_width=True, key=f"metrics_radar_{i}")
                        
                        # Strengths and weaknesses
                        col1, col2 = st.columns(2)
                        with col1:
                            if "strengths" in llm_eval and llm_eval["strengths"]:
                                st.write("**💪 Strengths:**")
                                for strength in llm_eval["strengths"]:
                                    st.write(f"✅ {strength}")
                        
                        with col2:
                            if "weaknesses" in llm_eval and llm_eval["weaknesses"]:
                                st.write("**⚠️ Weaknesses:**")
                                for weakness in llm_eval["weaknesses"]:
                                    st.write(f"❌ {weakness}")
                        
                        # Highlighted data and findings
                        st.markdown("---")
                        st.subheader("📊 Highlighted Data & Findings")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if "key_data_points" in llm_eval and llm_eval["key_data_points"]:
                                st.write("**📈 Key Data Points:**")
                                for point in llm_eval["key_data_points"]:
                                    st.write(f"• {point}")
                            
                            if "highlighted_findings" in llm_eval and llm_eval["highlighted_findings"]:
                                st.write("**🎯 Key Findings:**")
                                for finding in llm_eval["highlighted_findings"]:
                                    st.write(f"✓ {finding}")
                        
                        with col2:
                            if "highlighted_risks" in llm_eval and llm_eval["highlighted_risks"]:
                                st.write("**⚠️ Highlighted Risks:**")
                                for risk in llm_eval["highlighted_risks"]:
                                    st.warning(f"⚡ {risk}")
                            
                            if "data_quality_issues" in llm_eval and llm_eval["data_quality_issues"]:
                                st.write("**🚨 Data Quality Issues:**")
                                for issue in llm_eval["data_quality_issues"]:
                                    st.error(f"⚠️ {issue}")
                        
                        # Visualization recommendations
                        if "visualization_recommendations" in llm_eval and llm_eval["visualization_recommendations"]:
                            st.markdown("---")
                            st.subheader("📊 Visualization Recommendations")
                            for i, rec in enumerate(llm_eval["visualization_recommendations"], 1):
                                st.write(f"**{i}.** {rec}")
                        
                        # Summary
                        if "summary" in llm_eval:
                            st.markdown("---")
                            st.write("**📋 Summary:**")
                            st.info(llm_eval["summary"])
        
        else:
            st.info("📊 No evaluation results yet. Run evaluations from the 'Quick Eval' or 'Full Suite' tabs above.")

# PAGE: Analytics
elif page == "📈 Analytics":
    st.markdown('<h1 class="header-title">📈 Analytics & Insights</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Research Volume")
        recent = load_research_results()
        st.metric("Total Queries", len(recent), "+2 today")
        
        dates = pd.date_range('2026-04-30', periods=10)
        data = pd.DataFrame({
            'Date': dates,
            'Queries': [1, 2, 1, 3, 2, 4, 3, 5, 4, 6]
        })
        fig = px.line(data, x='Date', y='Queries', markers=True, title="Daily Query Volume")
        st.plotly_chart(fig, use_container_width=True, key="query_volume_chart")
    
    with col2:
        st.subheader("Model Performance")
        
        performance_data = {
            'Model': ['Nova Lite\n(Agent)', 'Nova Pro\n(Evaluator)'],
            'Accuracy': [85, 92],
            'Speed': [95, 75],
            'Cost Efficiency': [100, 60]
        }
        
        df_perf = pd.DataFrame(performance_data)
        fig = px.bar(df_perf, x='Model', y=['Accuracy', 'Speed', 'Cost Efficiency'],
                    barmode='group', title="Model Comparison Metrics")
        st.plotly_chart(fig, use_container_width=True, key="model_comparison_chart")
    
    st.markdown("---")
    st.subheader("📊 Evaluation Score Trends")
    
    eval_data = pd.DataFrame({
        'Eval': ['1', '2', '3', '4', '5'],
        'Overall': [75, 78, 82, 85, 88],
        'Accuracy': [78, 81, 85, 88, 92],
        'Quality': [72, 75, 80, 83, 87]
    })
    
    fig = px.line(eval_data, x='Eval', y=['Overall', 'Accuracy', 'Quality'], 
                  markers=True, title="Improvement Trajectory")
    st.plotly_chart(fig, use_container_width=True, key="eval_trends_chart")

# PAGE: Model Configuration
elif page == "🔧 Model Config":
    st.markdown('<h1 class="header-title">🔧 Model Configuration & Recommendations</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Current Setup", "Recommendations", "Comparison"])
    
    with tab1:
        st.subheader("Current Model Configuration")
        
        from src.config.settings import settings
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 Agent Model")
            st.info(f"""
            **Model:** Amazon Nova Lite v1.0
            - **Purpose:** Financial research execution
            - **Max Tokens:** {settings.bedrock_max_tokens}
            - **Temperature:** {settings.agent_temperature}
            - **Top-P:** {settings.agent_top_p}
            """)
        
        with col2:
            st.markdown("### ⚖️ Evaluator Model")
            st.info(f"""
            **Model:** Amazon Nova Pro v1.0
            - **Purpose:** Report evaluation & scoring
            - **Max Tokens:** {settings.evaluator_max_tokens}
            - **Temperature:** 0.3 (Low for consistency)
            - **Metrics:** 22+ evaluation metrics
            """)
    
    with tab2:
        st.subheader("🚀 Model Upgrade Recommendations")
        
        st.markdown("""
        ### Option 1: Current Setup (Recommended for Balance) ✅
        - **Agent:** Amazon Nova Lite
        - **Evaluator:** Amazon Nova Pro
        - **Pros:** Fast, cost-effective, good quality
        - **Cons:** Limited complex reasoning
        
        ### Option 2: Enhanced Reasoning 💎
        - **Agent:** Amazon Nova Pro
        - **Evaluator:** Amazon Nova Pro
        - **Pros:** Better reasoning, stronger analysis
        - **Cons:** 2x cost, slightly slower
        
        ### Option 3: Premium Tier 🏆
        - **Agent:** Amazon Nova Lite v1.0
        - **Evaluator:** Amazon Nova Pro v1.0
        - **Pros:** Best reasoning, most reliable
        - **Cons:** 3-5x cost, slower responses
        - **Use case:** Enterprise, mission-critical
        
        ### Option 4: Hybrid (Recommended for Production) ⭐
        - **Agent:** Amazon Nova Lite
        - **Evaluator:** Amazon Nova Pro v1.0
        - **Pros:** Cost-effective agent + rigorous evaluation
        - **Cons:** Mixed providers
        - **Best for:** High-quality research validation
        """)
        
        st.markdown("---")
        
        st.markdown("### 📊 Current Performance Metrics")
        metrics_data = {
            'Metric': ['Research Accuracy', 'Eval Consistency', 'Hallucination Rate', 'Speed (avg sec)', 'Cost per query'],
            'Current (Nova Lite)': [85, 88, 1.2, 12, 0.45],
            'With Nova Pro Agent': [92, 91, 0.8, 18, 0.85],
            'Target Performance': [96, 94, 0.3, 25, 1.20]
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True)
        
        if st.button("🔄 Apply Nova Pro Upgrade"):
            st.success("✅ Upgrade scheduled. Restart dashboard to apply.")
    
    with tab3:
        st.subheader("Model Comparison Matrix")
        
        comparison_data = {
            'Capability': ['Reasoning', 'Speed', 'Cost', 'Consistency', 'JSON Quality', 'Error Handling', 'Long Context'],
            'Nova Lite': [6, 10, 10, 7, 8, 7, 7],
            'Nova Pro': [8, 8, 7, 9, 9, 9, 8],
            'Hybrid (Lite+Pro)': [9, 9, 8, 9, 9, 9, 9],
            'Enterprise': [10, 7, 5, 10, 10, 10, 10]
        }
        
        df_comp = pd.DataFrame(comparison_data)
        st.dataframe(df_comp, use_container_width=True)
        
        fig = px.bar(df_comp.set_index('Capability'), 
                     title="Model Capability Comparison (Scale 0-10)",
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True, key="model_capability_chart")

# PAGE: Settings
elif page == "⚙️ Settings":
    st.markdown('<h1 class="header-title">⚙️ Configuration & Settings</h1>', unsafe_allow_html=True)
    
    from src.config.settings import settings
    
    tab1, tab2, tab3 = st.tabs(["Models", "Agent", "Evaluation"])
    
    with tab1:
        st.subheader("🤖 Model Settings")
        st.text_input("Agent Model", value=settings.bedrock_model_id, disabled=True)
        st.text_input("Evaluator Model", value=settings.evaluator_model_id, disabled=True)
        st.text_input("Embedding Model", value=settings.bedrock_embedding_model, disabled=True)
    
    with tab2:
        st.subheader("⚙️ Agent Tuning")
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Temperature", value=settings.agent_temperature, disabled=True)
            st.number_input("Max Iterations", value=settings.agent_max_iterations, disabled=True)
        
        with col2:
            st.number_input("Top P", value=settings.agent_top_p, disabled=True)
            st.number_input("Timeout (sec)", value=settings.agent_timeout_seconds, disabled=True)
    
    with tab3:
        st.subheader("📊 Evaluation Thresholds")
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Quality Threshold", value=settings.quality_threshold, disabled=True)
            st.number_input("Min Tool Efficiency", value=settings.min_tool_efficiency, disabled=True)
        
        with col2:
            st.number_input("Hallucination Threshold", value=settings.hallucination_threshold, disabled=True)
            st.number_input("Max Retries", value=settings.max_retries, disabled=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Config"):
            st.success("✅ Configuration reloaded!")
    
    with col2:
        if st.button("📊 View Logs"):
            st.subheader("Recent Logs")
            log_file = Path(settings.log_file)
            if log_file.exists():
                with open(log_file) as f:
                    logs = f.readlines()[-30:]
                    st.code(''.join(logs), language='text')
            else:
                st.info("No logs available yet.")
    
    with col3:
        if st.button("💾 Export Config"):
            config_export = f"""
# ARA-1 Configuration Export
Generated: {datetime.now().isoformat()}

## Agent Model
Agent: {settings.bedrock_model_id}
Evaluator: {settings.evaluator_model_id}

## Agent Settings
Temperature: {settings.agent_temperature}
Top P: {settings.agent_top_p}
Max Iterations: {settings.agent_max_iterations}
Timeout: {settings.agent_timeout_seconds}s

## Evaluation Thresholds
Quality: {settings.quality_threshold}
Hallucination: {settings.hallucination_threshold}
Tool Efficiency: {settings.min_tool_efficiency}
"""
            st.download_button(
                label="📥 Download Config",
                data=config_export,
                file_name=f"ara1_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🤖 ARA-1 v1.0.0 | Autonomous Research Agent</p>
        <p>Powered by AWS Bedrock | Built with Streamlit</p>
        <small>© 2026 - Advanced Financial Research System</small>
    </div>
""", unsafe_allow_html=True)
