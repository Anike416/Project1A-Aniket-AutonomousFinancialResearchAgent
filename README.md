# ARA-1: Autonomous Research Agent

A fully autonomous AI agent that replicates the research workflow of a junior financial analyst using AWS Bedrock, LangChain, and advanced agentic AI patterns.

## Overview

ARA-1 is a sophisticated financial research agent that:

- **Autonomous Research**: Executes complex research tasks without human step-by-step guidance
- **Multi-Source Integration**: Gathers data from SEC EDGAR, financial APIs, earnings transcripts, news feeds, and web search
- **Intelligent Synthesis**: Combines findings into professional investment research reports
- **Error Resilience**: Implements graceful degradation with fallback chains and circuit breakers
- **Three-Layer Memory**: Short-term (session), long-term (vector DB), and episodic (learning) memory systems
- **Tool Registry**: 12+ specialized financial research tools
- **Quality Metrics**: 20+ evaluation criteria with comprehensive benchmarking

## Architecture

### Core Components

1. **Bedrock Agent**: AWS Bedrock-powered LLM orchestration using Claude 3 Sonnet
2. **Tool Registry**: Extensible tool system with automatic fallback chains
3. **Memory System**:
   - Short-term: Current session context (managed in token window)
   - Long-term: Vector database (Pinecone) for persistent knowledge
   - Episodic: Learning from past research strategies and errors
4. **Error Handler**: Sophisticated error recovery with multiple fallback strategies
5. **Evaluation Framework**: 8 progressive challenges with 20+ quality metrics

### Tool Registry (12 Tools)

1. **sec_filing_search** - SEC EDGAR filings retrieval
2. **web_search** - Current news and analysis
3. **earnings_transcript** - Earnings call transcripts
4. **financial_data_api** - Structured financial statements
5. **news_sentiment** - NLP sentiment analysis
6. **company_profile** - Company information
7. **peer_comparison** - Competitive analysis
8. **fact_checker** - Cross-reference verification
9. **calculation_engine** - Financial computations
10. **report_generator** - Structured report generation
11. **vector_db_search** - Long-term memory search
12. **vector_db_store** - Memory persistence

## Installation

### Prerequisites

- Python 3.10+
- AWS Account with Bedrock access
- API Keys for:
  - SEC API
  - Financial data providers (Alpha Vantage, etc.)
  - News APIs
  - Pinecone (vector database)

### Setup

1. **Clone and Install**
```bash
cd ara_agent
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - AWS credentials
# - Bedrock configuration
# - API keys
# - Pinecone connection
```

3. **Initialize**
```bash
python -m src.main init
```

## Usage

### Command Line Interface

#### Execute Research
```bash
python -m src.main research "Analyze Apple's competitive position in AI"

# With output file
python -m src.main research "Research query" --output-file report.md
```

#### Run Evaluation Suite
```bash
python -m src.main evaluate
```

#### Interactive Session
```bash
python -m src.main interactive
```

#### Check Status
```bash
python -m src.main status
```

### Python API

```python
from src.agents.research_agent import get_agent
import asyncio

async def main():
    agent = get_agent()
    
    result = await agent.execute_research(
        query="Prepare an investment thesis for Tesla",
        research_type="investment_thesis"
    )
    
    print(result["report"])

asyncio.run(main())
```

## Evaluation Framework

The evaluation framework includes 8 progressive challenges:

1. **Basic Profile** - Company information retrieval
2. **Financial Analysis** - Multi-year financial analysis
3. **Risk Assessment** - Comprehensive risk identification
4. **Competitive Analysis** - Peer comparison
5. **Sentiment Analysis** - News sentiment with trend analysis
6. **Investment Thesis** - Complete investment report
7. **Error Recovery** - Handling tool failures gracefully
8. **Data Reconciliation** - Resolving conflicting information

**Success Criteria**:
- Average score ≥ 70%
- Hallucination rate < 2%
- Tool efficiency ≥ 70%

## Quality Metrics (20+)

- Accuracy
- Completeness
- Relevance
- Credibility
- Consistency
- Hallucination Rate
- Tool Efficiency
- Error Recovery
- Memory Utilization
- Research Quality
- Report Clarity
- Source Diversity
- Data Validation
- Risk Identification
- Competitive Analysis
- Financial Accuracy
- Insight Depth
- Recommendation Quality
- Response Time
- And more...

## Architecture Patterns

### ReAct (Reasoning + Acting)
Agent alternates between:
- **Thought**: LLM reasoning about next steps
- **Action**: Tool invocation
- **Observation**: Tool result processing

### Error Handling & Graceful Degradation
- Circuit breaker pattern
- Automatic fallback chains
- Retry with exponential backoff
- Degraded mode operation

### Memory System
- **Short-term**: Context window management
- **Long-term**: Vector embeddings with metadata
- **Episodic**: Strategy learning and error patterns

## Configuration

Key environment variables:

```
# AWS
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Bedrock
BEDROCK_MAX_TOKENS=4096
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0

# Vector DB
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=financial-research-index

# Agent Settings
AGENT_MAX_ITERATIONS=15
AGENT_TEMPERATURE=0.7
QUALITY_THRESHOLD=0.70
HALLUCINATION_THRESHOLD=0.02
```

## Performance Metrics

Target Performance:
- **Tool Efficiency**: > 70%
- **Hallucination Rate**: < 2%
- **Quality Score**: > 70%
- **Average Response Time**: < 5 minutes
- **Error Recovery Rate**: > 90%

## Project Structure

```
ara_agent/
├── src/
│   ├── agents/           # Agent implementations
│   ├── tools/            # Tool definitions
│   ├── memory/           # Memory system
│   ├── config/           # Configuration
│   ├── utils/            # Utilities
│   ├── evaluation/       # Evaluation framework
│   └── main.py           # CLI entry point
├── tests/                # Test suites
├── data/                 # Data storage
├── logs/                 # Log files
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
└── README.md            # This file
```

## Development

### Adding New Tools

1. Extend `BaseTool` class
2. Implement `execute()` method
3. Define parameters with `ToolParameter`
4. Register in tool registry

Example:
```python
from src.tools.base_tool import BaseTool, ToolParameter

class MyTool(BaseTool):
    def __init__(self):
        parameters = [
            ToolParameter(name="param", type="string", required=True)
        ]
        super().__init__(name="my_tool", description="...", parameters=parameters)
    
    async def execute(self, **kwargs):
        # Implementation
        pass
```

### Running Tests

```bash
pytest tests/ -v --cov=src
```

## Troubleshooting

### Common Issues

**Bedrock API Not Available**
- Check AWS credentials in .env
- Verify Bedrock access in your AWS region
- Check model ID availability

**Vector DB Connection Failed**
- Verify Pinecone API key
- Check network connectivity
- Confirm index name matches configuration

**Rate Limiting**
- Agent implements automatic backoff
- Check API quotas for financial data providers

## Timeline

- **Phase 1-2** (Days 1-2): Setup, configuration, AWS integration
- **Phase 3** (Days 3-5): Tool implementation
- **Phase 4** (Days 6-8): Memory system and agent orchestration
- **Phase 5** (Days 9-10): Error handling and recovery
- **Phase 6** (Days 11-12): Report generation and quality metrics
- **Phase 7** (Days 13-14): Evaluation framework and testing
- **Phase 8** (Day 15): Optimization, documentation, deployment

## Contributing

1. Create feature branches from `main`
2. Implement with comprehensive logging
3. Add tests for new functionality
4. Submit PR with evaluation results

## License

Proprietary - Zetheta Algorithms Private Limited

## Support

For issues and questions:
1. Check logs in `logs/ara_agent.log`
2. Review error messages and stack traces
3. Consult the evaluation framework for performance issues
4. Check AWS Bedrock documentation

## Acknowledgments

- AWS Bedrock for LLM infrastructure
- Claude 3 Sonnet for reasoning capabilities
- Pinecone for vector database services
- LangChain for agent orchestration patterns
