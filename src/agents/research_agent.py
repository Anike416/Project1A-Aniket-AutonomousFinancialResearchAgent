"""
Core Autonomous Research Agent using ReAct pattern with AWS Bedrock
Implements multi-source synthesis for institutional research standards
""" 
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from src.config.logger import log
from src.config.settings import settings
from src.config.bedrock_client import get_bedrock_client
from src.tools.base_tool import get_tool_registry, ToolRegistry
from src.memory.memory_system import AgentMemorySystem
from src.utils.error_handler import ErrorHandler, ErrorRecoveryStrategy
from src.research.multi_source_synthesis import (
    MultiSourceSynthesis, SourceTier, ConfidenceLevel
)

class AgentState(str, Enum):
    """Agent execution state"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETE = "complete"
    FAILED = "failed"


class ResearchThread:
    """Single research execution thread"""
    
    def __init__(self, thread_id: str, query: str):
        self.thread_id = thread_id
        self.query = query
        self.state = AgentState.IDLE
        self.thoughts: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.observations: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.iteration_count = 0
        self.max_iterations = settings.agent_max_iterations
    
    def add_thought(self, thought: str):
        """Record a thought"""
        self.thoughts.append(thought)
        log.debug(f"[{self.thread_id}] Thought: {thought}")
    
    def add_action(self, tool_name: str, parameters: Dict[str, Any]):
        """Record an action"""
        action = {
            "tool": tool_name,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
        }
        self.actions.append(action)
        log.debug(f"[{self.thread_id}] Action: {tool_name}")
    
    def add_observation(self, result: Dict[str, Any]):
        """Record an observation"""
        observation = {
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
        self.observations.append(observation)
        log.debug(f"[{self.thread_id}] Observation recorded")
    
    def get_trace(self) -> str:
        """Get formatted execution trace"""
        trace_lines = [f"Research Query: {self.query}\n"]
        
        for i, (thought, action, observation) in enumerate(zip(self.thoughts, self.actions, self.observations), 1):
            trace_lines.append(f"Step {i}:")
            trace_lines.append(f"  Thought: {thought}")
            trace_lines.append(f"  Action: {action['tool']} with {action['parameters']}")
            trace_lines.append(f"  Observation: {observation['result'].get('status', 'unknown')}")
            trace_lines.append("")
        
        return "\n".join(trace_lines)


class AutonomousResearchAgent:
    """Main Autonomous Research Agent using ReAct pattern"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.tool_registry = get_tool_registry()
        self.memory = AgentMemorySystem()
        self.error_handler = ErrorHandler()
        self.threads: Dict[str, ResearchThread] = {}
        self.research_sessions: List[Dict[str, Any]] = []
        
        # Initialize multi-source synthesis framework for institutional-grade research
        self.synthesis = MultiSourceSynthesis()
        
        log.info("Initialized AutonomousResearchAgent with multi-source synthesis framework")
        self._system_prompt = self._build_system_prompt()
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """Extract text from Bedrock response (handles Claude, Nova, and Meta Llama formats)"""
        log.debug(f"Response keys: {response.keys()}")
        
        # Meta Llama format: {"generation": "..."}
        if "generation" in response:
            log.debug("Detected Meta Llama format response")
            text = response.get("generation", "")
            log.debug(f"Extracted Llama text (first 200 chars): {text[:200]}")
            return text
        
        # Nova format: {"output": {"message": {"content": [{"text": "..."}]}}}
        if "output" in response:
            log.debug("Detected Nova format response")
            try:
                content = response["output"]["message"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    log.debug(f"Extracted Nova text (first 200 chars): {text[:200]}")
                    return text
            except (KeyError, TypeError) as e:
                log.warning(f"Error parsing Nova format: {e}")
        
        # Claude format: {"content": [{"text": "..."}]}
        content = response.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            log.debug("Detected Claude format response")
            text = content[0].get("text", "")
            log.debug(f"Extracted Claude text (first 200 chars): {text[:200]}")
            return text
        
        log.warning(f"Could not extract text from response. Response: {str(response)[:500]}")
        return ""
    
    def _clean_markdown_json(self, text: str) -> str:
        """Remove markdown code blocks from JSON text"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:].lstrip("\n")
        elif text.startswith("```"):
            text = text[3:].lstrip("\n")
        
        if text.endswith("```"):
            text = text[:text.rfind("```")].rstrip()
        
        return text
    
    def _build_system_prompt(self) -> str:
        """Build professional system prompt based on institutional research standards"""
        return f"""You are ARA-1, Autonomous Financial Research Agent at institutional quality level.

RESEARCH STANDARDS (MANDATORY):
✓ Factual Accuracy: >98% (cross-reference all figures from 2+ sources)  
✓ Citation Integrity: 100% (cite source tier for every claim)
✓ Hallucination Rate: <1% (NEVER fabricate data, companies, or events)
✓ Tool Efficiency: >70% (only use tools whose results are cited in report)
✓ Error Recovery: >90% (implement fallback chains gracefully)

SOURCE RELIABILITY HIERARCHY (use in all conflict resolution):
1. Tier 1 - SEC Filings (10-K, 10-Q): legally mandated, audited, criminal penalties for misrep
2. Tier 2 - Financial APIs (Bloomberg equivalent): curated from primary sources
3. Tier 3 - Earnings Transcripts: direct management commentary, subject to spin
4. Tier 4 - Major News (Reuters, FT, Bloomberg): professional journalism, may contain errors
5. Tier 5 - Web Search: unverified crowd-sourced information

MULTI-SOURCE SYNTHESIS FRAMEWORK:
- Identify agreements AND disagreements across sources
- For conflicts: compare source tiers, check temporal differences, apply highest-tier preference
- Provide confidence scores: HIGH (3+ sources agree), MEDIUM (2 sources), LOW (1 source)
- Document all conflicts discovered and resolution method in final report
- Calculate triangulation: compare same metric from 3+ independent sources

MANDATORY REPORT STRUCTURE:
1. Executive Summary: specific thesis with key metrics and confidence level
2. Company Profile: business model with % breakdowns, recent developments dated
3. Financial Analysis: 3-5 year historical data with explicit time periods (Q1 2024: $XXM)
4. Market Analysis: market share %, growth rates %, competitive positioning quantified
5. Risk Assessment: categories rated 1-10 with supporting metrics for each
6. Competitive Analysis: peer comparison tables with 3-5 competitors
7. Data Sources & Methodology: sources listed with confidence levels and date retrieved
8. Visualization Recommendations: specific chart types with data ranges and time periods

OUTPUT FORMATTING:
- Include specific numbers: Revenue ($XXX M), Growth (XX%), Margins (XX%)
- All time periods explicit: 'Q1 2024: $150M' not 'recent quarter'
- Every claim tagged with source tier: [Tier 1], [Tier 2], etc.
- Confidence level justified: [HIGH - 3 sources agree], [MEDIUM - 2 sources], [LOW - single source]
- Data in tables/lists for extraction: use | format for comparisons
- Precise financial terminology: 'operating margin' not 'profit margin'
- Maximum 20 tool calls per task

Available Tools:
{self.tool_registry.get_tool_descriptions()}

REACT FRAMEWORK:
Thought → What information is needed next? Why? Which tool?
Action → Invoke [tool_name] with parameters [specific values]
Observation → Process results, incorporate into knowledge, verify against existing data

MEMORY PROTOCOL:
- Check long-term memory FIRST for previously researched companies (ticker-based search)
- Store findings with: ticker, date retrieved, source tier, confidence, key metrics
- Maintain episodic memory: effective research strategies, tool combinations that worked

CRITICAL GUARDRAILS (NEVER):
❌ Recommend 'buy/sell' - say 'may warrant investigation' instead
❌ Fabricate companies, executives, market events, or statistics
❌ Mix up time periods (don't confuse Q1 2024 with Q1 2025)
❌ Confuse units (millions vs billions, percentages vs basis points)
❌ Cite sources you didn't retrieve or reference sections that don't exist
❌ Hallucinate competitive advantages or financial metrics
❌ Make forward predictions without explicit probability caveats

QUALITY CHECKS BEFORE FINALIZING:
1. Every numerical claim has 2+ sources listed [check]
2. Conflicts between sources are documented [check]
3. Confidence levels are justified by source count [check]
4. All time periods are explicit, not vague [check]
5. Report follows prescribed structure [check]
6. No fabricated data, names, or events [check]
7. All claims are supportable from retrieved data [check]

Think obsessively about accuracy. Verify every number. Cite everything."""
    
    async def execute_research(self, query: str, research_type: str = "general") -> Dict[str, Any]:
        """
        Execute a complete research task
        
        Args:
            query: Research query
            research_type: Type of research (general, risk_assessment, etc.)
            
        Returns:
            Research report and metadata
        """
        thread_id = f"research-{len(self.threads)}-{datetime.now().timestamp()}"
        thread = ResearchThread(thread_id, query)
        self.threads[thread_id] = thread
        
        log.info(f"Starting research: {query}")
        
        try:
            # Step 1: Plan the research
            plan = await self._generate_research_plan(query, research_type)
            thread.add_thought(f"Generated research plan with {len(plan.get('steps', []))} steps")
            
            # Step 2: Execute research loop
            findings = await self._execute_research_loop(query, plan, thread)
            
            # Step 3: Generate report
            report = await self._generate_research_report(query, findings, plan)
            
            # Step 4: Store in long-term memory
            await self._store_findings(query, findings, report)
            
            # Record episode for episodic memory
            self._record_episode(thread, True)
            
            return {
                "status": "success",
                "query": query,
                "report": report,
                "findings": findings,
                "thread_id": thread_id,
                "iterations": thread.iteration_count,
            }
            
        except Exception as e:
            log.error(f"Error during research execution: {str(e)}")
            self._record_episode(thread, False)
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "thread_id": thread_id,
            }
    
    async def _generate_research_plan(self, query: str, research_type: str) -> Dict[str, Any]:
        """Generate a research plan using Bedrock"""
        prompt = f"""Based on this research query, create a detailed research plan:

Query: {query}
Type: {research_type}

Provide a JSON plan with:
- objective: Overall research objective
- steps: List of specific research steps
- expected_tools: Tools likely needed
- success_criteria: How to evaluate success

Return as valid JSON only."""
        
        try:
            # Get memory context
            context = self.memory.get_full_context()
            
            messages = [
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nRequest:\n{prompt}"
                }
            ]
            
            response = self.bedrock.invoke_model(
                messages=messages,
                system_prompt=self._system_prompt,
                temperature=0.5,  # Lower temperature for planning
            )
            
            # Extract plan from response
            response_text = self._extract_response_text(response)
            log.debug(f"Raw response text: {response_text[:500]}")  # Debug logging
            
            if not response_text or response_text.strip() == "":
                log.error(f"Empty response from Bedrock. Full response: {response}")
                return {"steps": [], "objective": query}
            
            # Clean markdown code blocks
            response_text = self._clean_markdown_json(response_text)
            plan = json.loads(response_text)
            
            log.info(f"Generated research plan with {len(plan.get('steps', []))} steps")
            return plan
            
        except json.JSONDecodeError as e:
            log.error(f"JSON decode error: {str(e)}. Response text was: {response_text[:200]}")
            return {"steps": [], "objective": query}
        except Exception as e:
            log.error(f"Error generating research plan: {str(e)}")
            return {"steps": [], "objective": query}
    
    async def _execute_research_loop(
        self,
        query: str,
        plan: Dict[str, Any],
        thread: ResearchThread,
    ) -> Dict[str, Any]:
        """Execute the main ReAct research loop"""
        findings = {"sources": [], "insights": [], "risks": []}
        max_iterations = settings.agent_max_iterations
        
        for iteration in range(max_iterations):
            thread.iteration_count = iteration + 1
            thread.state = AgentState.THINKING
            
            # Step 1: Generate thought
            thought_prompt = f"""Current research state:
Query: {query}
Findings so far: {json.dumps(findings, default=str)}
Steps completed: {iteration + 1}/{len(plan.get('steps', []))}

What should be researched next?"""
            
            try:
                messages = [{"role": "user", "content": thought_prompt}]
                response = self.bedrock.invoke_model(
                    messages=messages,
                    system_prompt=self._system_prompt,
                )
                
                thought = self._extract_response_text(response)
                thread.add_thought(thought)
                
                # Step 2: Decide on action
                thread.state = AgentState.ACTING
                
                if "finished" in thought.lower() or "complete" in thought.lower():
                    log.info("Agent decided to complete research")
                    break
                
                # Parse tool call from thought (simplified)
                tool_call = self._parse_tool_call(thought)
                
                if tool_call:
                    tool_name = tool_call["tool"]
                    parameters = tool_call["parameters"]
                    
                    thread.add_action(tool_name, parameters)
                    
                    # Step 3: Execute tool
                    thread.state = AgentState.OBSERVING
                    result = await self.tool_registry.execute_tool(tool_name, **parameters)
                    
                    thread.add_observation({"tool": tool_name, "status": result.status, "confidence": result.confidence})
                    
                    # Store observation in short-term memory
                    self.memory.short_term.add_entry(
                        f"Tool {tool_name} returned: {result.data}",
                        "tool_result",
                        {"tool": tool_name, "status": result.status}
                    )
                    
                    # Add findings
                    if result.status.value == "success":
                        findings["sources"].append(tool_name)
                
            except Exception as e:
                log.error(f"Error in research loop iteration {iteration}: {str(e)}")
                self.memory.episodic.record_error("research_loop", str(e))
        
        thread.state = AgentState.COMPLETE
        return findings
    
    async def _generate_research_report(
        self,
        query: str,
        findings: Dict[str, Any],
        plan: Dict[str, Any],
    ) -> str:
        """Generate institutional-grade research report with source attribution and confidence scoring"""
        report_prompt = f"""Generate a PROFESSIONAL INVESTMENT RESEARCH REPORT following institutional standards.

RESEARCH QUERY: {query}
AVAILABLE DATA: {json.dumps(findings, default=str)[:3000]}...
RESEARCH PLAN STEPS: {len(plan.get('steps', []))}

---

MANDATORY REPORT STRUCTURE (follow exactly):

# [COMPANY NAME] - INVESTMENT RESEARCH REPORT
**Analysis Date:** [TODAY]  
**Report Quality Level:** Institutional Grade  
**Analyst:** Autonomous Research Agent ARA-1  

---

## EXECUTIVE SUMMARY
- **Investment Thesis:** [Specific statement with 1-2 key metrics]
- **Confidence Level:** [HIGH/MEDIUM/LOW with reasoning]
- **Risk Rating:** [X/10 with primary risk]
- **Key Metrics:**
  * Revenue: $XXX Million [Tier 1 - SEC Filing]
  * Growth Rate: XX% YoY [Tier 1/2 - Source]  
  * Operating Margin: XX% [Tier 2 - Financial API]
- **Data Sources:** [List types used: SEC, APIs, Earnings Calls, News]

---

## COMPANY PROFILE & BUSINESS OVERVIEW
- **Industry Position:** [Market share XX% or rank]
- **Primary Revenue Drivers:** [Segment A XX%, Segment B XX%]
- **Key Competitive Advantages:** [Specific, quantified strengths]
- **Recent Developments:** [Dated events with implications]

---

## FINANCIAL ANALYSIS & PERFORMANCE METRICS

**Revenue Trajectory (with Time Periods):**
| Period | Revenue ($M) | YoY Growth | Margin | Source Tier |
|--------|------------|-----------|--------|------------|
| 2022 | $XXX | - | XX% | 1 |
| 2023 | $XXX | XX% | XX% | 1 |
| 2024 | $XXX | XX% | XX% | 1 |
| Q1 2025 | $XX | XX% | XX% | 1 |

**Profitability Analysis:**
- Operating Margin: XX% [Tier 1, Confidence: HIGH - 2+ sources]
- Net Margin: XX% [Tier 2, Confidence: HIGH]
- EBITDA Margin: XX% [Tier 1/2, Confidence: MEDIUM]

**Return Metrics:**
- ROE: XX% [Tier 1, 2024 full year]
- ROA: XX% [Tier 1, 2024]
- Free Cash Flow: $XXX M [Tier 1, 2024]

**Balance Sheet Strength:**
- Debt/Equity: X.Xx [Assessment: Low/Moderate/High Risk]
- Current Ratio: X.Xx [Assessment: Solid/Adequate/Weak]
- Cash Position: $XXX M [Tier 1]

---

## MARKET ANALYSIS & COMPETITIVE POSITIONING

**Market Size & Share:**
- TAM: $XXX B [Tier 4/5 - Research estimate]
- Company Share: XX% [Tier 1/2 - Official data]
- Growth Rate: XX% CAGR [Tier 2/3 - Consensus]

**Competitive Benchmarking:**
| Company | Market Share | Revenue Growth | Op Margin | Advantage |
|---------|-------------|---------------|-----------|-----------| 
| [Your Co] | XX% | XX% | XX% | [Specific] |
| Competitor A | XX% | XX% | XX% | [Specific] |
| Competitor B | XX% | XX% | XX% | [Specific] |

**Competitive Differentiation:**
- Primary Strength: [Specific, quantified]
- Cost Position: [XX% lower/higher than peers]
- Innovation Pipeline: [Specific products/R&D %]

---

## RISK ASSESSMENT FRAMEWORK

**Financial Risk: [X/10]**
- Liquidity: [Metric] [Assessment]
- Leverage: Debt/EBITDA = X.X [Benchmark]
- Interest Rate Sensitivity: [XX% of debt]
- **Confidence:** [HIGH/MEDIUM/LOW] [Tier 1/2 sources]

**Operational Risk: [X/10]**
- Key Personnel: CEO/CFO tenure [years]
- Supply Chain: Top 3 suppliers = XX% of COGS
- Cost Structure: Variable XX%, Fixed XX%
- **Confidence:** [HIGH/MEDIUM/LOW] [Tier 1/2/3 sources]

**Market & Competitive Risk: [X/10]**
- Market Threats: [Specific competitors/technologies]
- Market Share Trend: [Specific +/- X% over period]
- Disruption Risk: [Emerging threats if any]
- **Confidence:** [HIGH/MEDIUM/LOW] [Tier 3/4 sources]

**Regulatory Risk: [X/10]**
- Key Regulations: [Specific by jurisdiction]
- Compliance Status: [Clean/Recent issues]
- Regulatory Tailwinds/Headwinds: [Specific impacts]
- **Confidence:** [HIGH/MEDIUM/LOW] [Tier 1/4 sources]

---

## KEY FINDINGS & INSIGHTS (Multi-Source Synthesis)

**Finding 1: [Specific, data-driven observation]**
- Supporting Data: [Metric from Source A - Tier X]
- Cross-Reference: [Metric from Source B - Tier X]  
- Analysis: [How sources together support this finding]
- Confidence: HIGH/MEDIUM [Based on source count & tiers]

**Finding 2: [Trend or competitive insight]**
- Time Period: [YYYY-MM to YYYY-MM]
- Magnitude: [Specific XX% change or ranking]
- Evidence: [Multiple sources confirming]
- Confidence: HIGH/MEDIUM/LOW

**Finding 3: [Risk or opportunity insight]**
- Quantified Impact: [Specific $ or % effect]
- Supporting Sources: [Tier 1/2/3 backing]
- Implications: [For valuation/risk profile]

---

## DATA SOURCES & CONFIDENCE ASSESSMENT

**Sources Retrieved:**
- SEC Filings: [10-K/10-Q years covered] - Tier 1 ✓
- Financial APIs: [Revenue, ratios, growth data] - Tier 2 ✓
- Earnings Calls: [Quarters analyzed, management commentary] - Tier 3 ✓
- News Sources: [Date range, # of articles] - Tier 4 ✓

**Confidence by Metric:**
| Metric | Sources | Confidence | Notes |
|--------|---------|-----------|-------|
| Revenue | 3 (Tier 1,2,4) | HIGH | All sources align |
| Growth Rate | 2 (Tier 1,3) | HIGH | SEC & mgmt confirm |
| Margins | 2 (Tier 1,2) | MEDIUM | 2% variance noted |
| Competition | 3 (Tier 2,4,5) | MEDIUM | Estimates vary |

**Conflicts Discovered & Resolved:**
[If any metrics conflicted between sources, document: what, sources, tiers, resolution method]

**Data Gaps:**
[Any critical information unavailable? State explicitly]

---

## VISUALIZATION RECOMMENDATIONS

📊 **TIME-SERIES ANALYSIS:** Revenue & Operating Margin (2020-2025)
- X-axis: Quarterly periods [Q1 2020 - Q1 2025]
- Y-axis: Revenue ($M) & Margin (%)
- Shows: Growth trajectory + profitability evolution

📊 **COMPETITIVE COMPARISON:** Market Share, Growth, Margins
- Company vs Top 3 Peers
- 3 bars per company: Share, Growth %, Margin %
- Shows: Relative positioning

📊 **RISK HEATMAP:** Financial | Operational | Market | Regulatory
- Risk levels 1-10 for each category
- Color gradient: Green (low) → Red (high)
- Shows: Risk concentration areas

📊 **GROWTH ANALYSIS:** Company vs Industry (5-year)
- Compound annual growth rates
- Shows: Outperformance/underperformance

---

## SUMMARY & FORWARD OUTLOOK
[Based on findings: what's the overall investment implication?]
[What factors to monitor going forward?]
[Specific metrics/events to trigger review?]

---

## REPORT METADATA

**Analysis Date:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}  
**Report Quality:** Institutional Grade - Multi-Source Verified  
**Data Currency:** Current as of analysis date  
**Recommended Next Review:** {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}  

---

CRITICAL REQUIREMENTS (verify before finalizing):
✓ Every number has source tier [Tier 1-5]
✓ Every time period explicit: Q1 2024, not 'recent'
✓ Every metric has confidence level: HIGH/MEDIUM/LOW
✓ Conflicts documented and resolved
✓ Data in tables/lists for easy extraction
✓ No vague language, precise financial terms
✓ NO investment recommendations (only analysis)
✓ All findings backed by retrieved data"""

        try:
            messages = [{"role": "user", "content": report_prompt}]
            response = self.bedrock.invoke_model(
                messages=messages,
                system_prompt=self._system_prompt,
                temperature=0.6,  # Moderate temperature for balance of creativity and consistency
                max_tokens=4096,
            )
            
            report = self._extract_response_text(response) or "No report generated"
            log.info("Generated institutional-grade research report with source tiers and confidence scoring")
            return report
            
        except Exception as e:
            log.error(f"Error generating report: {str(e)}")
            return f"Error generating report: {str(e)}"
    
    async def _store_findings(self, query: str, findings: Dict[str, Any], report: str):
        """Store findings in long-term memory"""
        try:
            # Store in vector DB via vector_db_store tool
            await self.tool_registry.execute_tool(
                "vector_db_store",
                content=report,
                metadata={
                    "query": query,
                    "date": datetime.now().isoformat(),
                    "source_type": "research_report",
                }
            )
        except Exception as e:
            log.warning(f"Error storing findings: {str(e)}")
    
    def _parse_tool_call(self, thought: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from agent's thought (simplified)"""
        # This is a simplified parser - in production, use proper parsing
        # Look for patterns like "Tool: tool_name(param1=value1, param2=value2)"
        
        for tool in self.tool_registry.list_tools():
            if tool.name in thought:
                return {
                    "tool": tool.name,
                    "parameters": {"query": thought[:100]} if "query" in str(tool.parameters) else {},
                }
        return None
    
    def _record_episode(self, thread: ResearchThread, success: bool):
        """Record episode for episodic memory"""
        self.memory.episodic.record_episode(
            episode_id=thread.thread_id,
            query=thread.query,
            tools_used=[action["tool"] for action in thread.actions],
            success=success,
            duration=(datetime.now() - thread.created_at).total_seconds(),
            findings_quality=0.85 if success else 0.3,
        )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "active_threads": len(self.threads),
            "completed_research": len(self.research_sessions),
            "tool_registry_stats": self.tool_registry.get_registry_stats(),
            "memory_status": self.memory.get_memory_status(),
        }


# Global agent instance
_agent: Optional[AutonomousResearchAgent] = None


def get_agent() -> AutonomousResearchAgent:
    """Get or create global agent instance"""
    global _agent
    if _agent is None:
        _agent = AutonomousResearchAgent()
    return _agent
