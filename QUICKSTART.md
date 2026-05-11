# Quick Start Guide - ARA-1 Agent

## 5-Minute Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- AWS Account with Bedrock access
- API Keys (get from: SEC API, Alpha Vantage, News API)

### 2. Installation

```bash
# Clone/navigate to project
cd ara_agent

# Install dependencies (1 minute)
pip install -r requirements.txt

# Configure environment (2 minutes)
cp .env.example .env
# Edit .env with your credentials:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - BEDROCK_MODEL_ID
# - PINECONE_API_KEY
# - API keys for data sources
```

### 3. First Research Query

```bash
# Quick test (run in project root)
python -m src.main init

# Execute a research query
python -m src.main research "What is Apple's current financial position?"

# Interactive mode
python -m src.main interactive
```

### 4. Run Evaluation

```bash
# Test against 8 progressive challenges
python -m src.main evaluate
```

## Configuration Quick Reference

### Minimum Required Settings (.env)

```
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=financial-research-index

# Quality Thresholds
QUALITY_THRESHOLD=0.70
HALLUCINATION_THRESHOLD=0.02
```

## Usage Examples

### Example 1: Company Analysis
```bash
python -m src.main research \
  "Analyze Tesla's competitive position in the EV market" \
  --output-file tesla_analysis.md
```

### Example 2: Risk Assessment
```bash
python -m src.main research \
  "Identify key risks for Meta Platforms in 2024" \
  --output-file meta_risks.md
```

### Example 3: Peer Comparison
```bash
python -m src.main research \
  "Compare JPMorgan, Goldman Sachs, and Morgan Stanley"
```

## Understanding Agent Output

### Report Structure
```
# Research Report
*Generated: 2024-01-15 14:30:00*

## Executive Summary
Key findings and overall assessment

## Company Profile
Basic information about the target company

## Financial Analysis
Revenue, profitability, growth metrics

## Risk Assessment
Identified risks and their impact

## Competitive Position
Peer comparison and market position

## Key Insights
Major findings and patterns

## Recommendations
Investment or strategic recommendations

## Sources
List of all data sources used
```

### Quality Metrics
After each report, check:
- **Accuracy**: Cross-referenced against multiple sources
- **Tool Efficiency**: % of successful tool calls
- **Hallucination Rate**: % of unverified claims
- **Completeness**: % of query answered

## Troubleshooting

### Issue: "Bedrock API not available"
```
Solution:
1. Check AWS credentials in .env
2. Verify Bedrock is available in your region
3. Check AWS IAM permissions for Bedrock
```

### Issue: "Pinecone connection failed"
```
Solution:
1. Verify PINECONE_API_KEY in .env
2. Check network connectivity
3. Ensure index exists in Pinecone dashboard
```

### Issue: "Tool execution timeout"
```
Solution:
1. Agent will automatically use fallback tools
2. Check AGENT_TIMEOUT_SECONDS in .env (default 300)
3. Reduce complex queries to simpler components
```

## Performance Tips

1. **Faster Results**: Use simpler, focused queries
   - Instead of: "Give me everything about Apple"
   - Use: "What is Apple's revenue growth rate?"

2. **Better Quality**: Specify research type
   ```bash
   python -m src.main research "query" \
     --research-type financial_analysis
   ```

3. **Reuse Results**: Agent stores findings in long-term memory
   - Similar queries will retrieve cached results
   - Faster execution on follow-up questions

## Evaluation Challenges (8 Levels)

```
1. Basic Profile (Easy)
   - Retrieve company information

2. Financial Analysis (Easy-Medium)
   - Multi-year financial data

3. Risk Assessment (Medium)
   - Identify and categorize risks

4. Competitive Analysis (Medium-Hard)
   - Compare 3+ companies

5. Sentiment Analysis (Medium-Hard)
   - News sentiment with trends

6. Investment Thesis (Hard)
   - Complete research report

7. Error Recovery (Hard)
   - Handle tool failures gracefully

8. Data Reconciliation (Very Hard)
   - Resolve conflicting information
```

## Advanced Configuration

### Adjust Agent Parameters

```env
# Max iterations before stopping
AGENT_MAX_ITERATIONS=15

# How "creative" the agent is (0.0-1.0)
AGENT_TEMPERATURE=0.7

# How many top alternatives to consider (0.0-1.0)
AGENT_TOP_P=0.9

# Request timeout
AGENT_TIMEOUT_SECONDS=300
```

### Memory Settings

```env
# Short-term memory limit (tokens)
SHORT_TERM_MAX_TOKENS=8000

# How long to keep long-term memories (days)
LONG_TERM_RETENTION_DAYS=365

# Enable learning from past research
EPISODIC_MEMORY_ENABLED=true
```

## Python API Usage

```python
import asyncio
from src.agents.research_agent import get_agent

async def main():
    agent = get_agent()
    
    result = await agent.execute_research(
        query="Analyze Tesla's competitive position",
        research_type="competitive_analysis"
    )
    
    print(result["report"])
    print(f"Iterations: {result['iterations']}")

asyncio.run(main())
```

## Next Steps

1. ✓ Install and configure
2. ✓ Run first research query
3. ✓ Review generated report
4. ✓ Run evaluation suite
5. → Fine-tune quality thresholds
6. → Add custom tools if needed
7. → Deploy to production

## Support Resources

- README.md - Full documentation
- tests/ - Test examples
- logs/ara_agent.log - Debug information
- docs/ - Detailed guides (when created)

## Success Metrics

Your agent is working well if:
- ✓ Average evaluation score > 70%
- ✓ Hallucination rate < 2%
- ✓ Tool efficiency > 70%
- ✓ Error recovery rate > 90%
- ✓ Report generation < 5 minutes

---

**Ready to use? Start with:**
```bash
python -m src.main init
python -m src.main research "Your research question"
```
