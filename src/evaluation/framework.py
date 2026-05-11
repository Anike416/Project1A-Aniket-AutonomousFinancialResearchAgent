"""
Evaluation framework for assessing agent performance
"""
from typing import Any, Dict, List
from datetime import datetime
import json
from src.config.logger import log
from src.config.settings import settings
from src.config.bedrock_client import BedrockClient
 

class LLMEvaluator:
    """LLM-based evaluator using Amazon Nova Pro as a judge"""
    
    def __init__(self):
        self.client = BedrockClient()
        # Override with evaluator model
        self.client.model_id = settings.evaluator_model_id
        log.info(f"Initialized LLMEvaluator with model: {self.client.model_id}")
    
    async def evaluate_report(self, report: str, query: str) -> Dict[str, Any]:
        """
        Evaluate research report using institutional quality standards
        Assesses: Accuracy, Source Attribution, Confidence Scoring, Multi-Source Synthesis
        
        Args:
            report: The research report to evaluate
            query: The original research query
            
        Returns:
            Dictionary with 25+ professional evaluation metrics
        """
        evaluation_prompt = f"""You are a senior research quality officer at Goldman Sachs evaluating investment research reports.
Evaluate this report against INSTITUTIONAL RESEARCH STANDARDS with focus on SOURCE ATTRIBUTION and DATA QUALITY.

RESEARCH QUERY: {query}

RESEARCH REPORT:
{report}

============================================================================
PROFESSIONAL EVALUATION CRITERIA (Score 0-100 each)
============================================================================

SECTION A: FACTUAL ACCURACY & DATA INTEGRITY
1. **Numerical Accuracy** - Are all financial figures correct? Check for unit confusion (M vs B).
2. **Citation Accuracy** - Are cited sources real, accessible, and actually support claims?
3. **Temporal Accuracy** - Correct time periods specified? No confusion between Q1 2024 vs Q1 2025?
4. **Entity Accuracy** - Company names, executives, tickers all correct?
5. **Hallucination Detection** - Any fabricated data, companies, or events? (0=none, 100=many)
6. **Data Conflict Resolution** - If sources disagreed, were conflicts documented and resolved?

SECTION B: SOURCE ATTRIBUTION & CONFIDENCE SCORING
7. **Source Tier Compliance** - Are sources correctly categorized?
   * Tier 1: SEC Filings (highest credibility)
   * Tier 2: Financial APIs (Bloomberg-level)
   * Tier 3: Earnings Transcripts
   * Tier 4: Major News (Reuters, FT)
   * Tier 5: Web/Other (lowest credibility)
8. **Citation Density** - What % of claims have source attribution? Target: 95%+
9. **Confidence Level Justification** - HIGH/MEDIUM/LOW properly justified by source count?
10. **Source Diversity** - Multiple source types used? (SEC, APIs, Earnings, News) Target: 4+ types
11. **Tier Weighting** - When conflicts exist, are higher-tier sources preferred?

SECTION C: MULTI-SOURCE SYNTHESIS
12. **Cross-Source Triangulation** - Same metrics verified from 3+ independent sources?
13. **Disagreement Documentation** - Conflicts between sources clearly documented?
14. **Synthesis Quality** - Evidence of connecting data points to derive insights?
15. **Conflict Resolution Transparency** - Clear explanation of how source conflicts were resolved?

SECTION D: RESEARCH QUALITY & COMPLETENESS
16. **Analytical Depth** - Non-obvious insights beyond fact-restating? (Target: 3+ per page)
17. **Section Coverage** - All required sections present?
   [Executive Summary, Company Profile, Financial Analysis, Market Analysis, Risk Assessment,
    Competitive Analysis, Data Sources, Methodology, Visualizations]
18. **Temporal Coverage** - Historical trends covered (3-5 year horizon)?
19. **Financial Analysis Depth** - Revenue trends, margins, ratios, balance sheet all covered?
20. **Risk Quantification** - Risks rated on 1-10 scale with supporting metrics?
21. **Competitive Benchmarking** - Peer comparison with specific metrics (market share, growth, margins)?

SECTION E: DATA INTEGRITY & VALIDATION
22. **Balance Sheet Health** - Debt/Equity, Current Ratio, Liquidity properly assessed?
23. **Growth Calculations** - YoY and CAGR calculations correct?
24. **Industry Benchmarking** - Company metrics compared to industry averages?
25. **Data Freshness** - Most recent data used? Timestamps clear?

SECTION F: PROFESSIONAL PRESENTATION
26. **Report Structure** - Follows institutional template? Professional formatting?
27. **Executive Summary Quality** - Accurately captures full report findings in 1-2 pages?
28. **Visualization Recommendations** - Specific charts recommended with data ranges?
29. **Clarity & Readability** - Free of jargon confusion? Easy to navigate?
30. **Documentation Quality** - Methodology notes complete? Limitations acknowledged?

CRITICAL DATA EXTRACTION:
- All financial figures with time periods (Q1 2024: $XXM)
- Growth rates and margins by period
- Market share percentages and competitive positions
- Risk factors quantified (X/10 by category)
- Source citations with tier assignments
- Confidence levels: HIGH (3+ sources), MEDIUM (2 sources), LOW (1 source)
- Visualization recommendations (time-series, comparisons, trends)
- Data conflicts discovered and resolution method

VISUALIZATION ASSESSMENT:
- Are time-series charts recommended for historical trends? [YES/NO]
- Are comparison charts suggested for peer benchmarking? [YES/NO]
- Is risk heatmap recommended for risk category assessment? [YES/NO]
- Would market share evolution chart clarify competitive position? [YES/NO]
- Are data ranges specified for each visualization? [YES/NO]

Return ONLY valid JSON in this exact format:
{{
  "section_a_accuracy": {{"numerical": 0-100, "citation": 0-100, "temporal": 0-100, "entity": 0-100, "hallucination_rate": 0-100, "conflict_resolution": 0-100}},
  "section_b_attribution": {{"source_tier_compliance": 0-100, "citation_density": 0-100, "confidence_justification": 0-100, "source_diversity": 0-100, "tier_weighting": 0-100}},
  "section_c_synthesis": {{"triangulation": 0-100, "disagreement_docs": 0-100, "synthesis_quality": 0-100, "conflict_transparency": 0-100}},
  "section_d_research": {{"analytical_depth": 0-100, "section_coverage": 0-100, "temporal_coverage": 0-100, "financial_depth": 0-100, "risk_quantification": 0-100, "competitive_benchmarking": 0-100}},
  "section_e_validation": {{"balance_sheet": 0-100, "growth_calcs": 0-100, "benchmarking": 0-100, "data_freshness": 0-100}},
  "section_f_presentation": {{"structure": 0-100, "exec_summary": 0-100, "visualizations": 0-100, "clarity": 0-100, "documentation": 0-100}},
  "overall_score": 0-100,
  "source_attribution_score": 0-100,
  "multi_source_synthesis_score": 0-100,
  "hallucination_rate_percent": 0-100,
  "data_quality_score": 0-100,
  "key_metrics_extracted": [{{"metric": "Revenue Q1 2024", "value": "$XXM", "sources": ["Tier 1", "Tier 2"], "confidence": "HIGH"}}, ...],
  "sources_used": {{"tier_1_count": 0, "tier_2_count": 0, "tier_3_count": 0, "tier_4_count": 0, "tier_5_count": 0}},
  "conflicts_identified": [{{"metric": "Revenue", "source_a": "$100M (Tier 1)", "source_b": "$95M (Tier 2)", "resolution": "Preferred Tier 1", "impact": "Low"}}, ...],
  "source_diversity": ["SEC Filings", "Financial APIs", "Earnings Calls", "News"], 
  "visualization_recommendations_quality": {{"time_series": true, "comparisons": true, "risk_heatmap": true, "data_ranges_specified": true}},
  "strengths": ["strength1 with specific evidence", "strength2 with specific evidence", "strength3 with specific evidence"],
  "critical_issues": ["issue1 with severity", "issue2 with severity"],
  "areas_for_improvement": ["improvement1 with suggestion", "improvement2 with suggestion"],
  "summary": "Professional assessment highlighting key metrics, source quality, and data integrity findings",
  "recommendation": "PASS/FAIL/REVIEW with specific reasoning"
}}

STRICT REQUIREMENTS:
✓ Every metric scored 0-100
✓ Hallucination rate as percentage (0-100)
✓ Source tier counts provided
✓ Data conflicts documented with resolution
✓ Visualization recommendations assessed
✓ Specific evidence for strengths/issues
✓ Professional tone matching institutional standards"""

        try:
            messages = [{"role": "user", "content": evaluation_prompt}]
            
            response = self.client.invoke_model(
                messages=messages,
                temperature=0.3,  # Lower temperature for consistent evaluation
                max_tokens=settings.evaluator_max_tokens,
            )
            
            # Extract text from response
            response_text = self._extract_response_text(response)
            
            if not response_text:
                raise ValueError("Failed to extract text from LLM response")
            
            # Clean markdown if present
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text[response_text.find("\n") + 1:]
            if response_text.endswith("```"):
                response_text = response_text[:response_text.rfind("```")]
            
            # Parse JSON
            evaluation = json.loads(response_text)
            log.info(f"Professional evaluation complete. Overall: {evaluation.get('overall_score', 0)}/100")
            
            return evaluation
            
        except Exception as e:
            log.error(f"Error during professional evaluation: {str(e)}")
            return {
                "overall_score": 0,
                "error": str(e),
                "summary": "Evaluation failed"
            }
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """Extract text from Bedrock response (handles Claude, Nova, and Meta Llama formats)"""
        log.debug(f"_extract_response_text called with response keys: {list(response.keys()) if isinstance(response, dict) else 'not a dict'}")
        
        # Meta Llama format: {"generation": "..."}
        if "generation" in response:
            text = response.get("generation", "")
            log.debug(f"Extracted from 'generation' key: {text[:100]}")
            return text
        
        # Nova format: {"output": {"message": {"content": [{"text": "..."}]}}}
        if "output" in response:
            try:
                content = response["output"]["message"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    log.debug(f"Extracted from Nova 'output' key: {text[:100]}")
                    return text
            except (KeyError, TypeError) as e:
                log.debug(f"Nova format extraction failed: {e}")
        
        # Claude format: {"content": [{"text": "..."}]}
        if "content" in response:
            content = response.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                text = content[0].get("text", "")
                log.debug(f"Extracted from Claude 'content' key: {text[:100]}")
                return text
        
        log.error(f"Could not extract text! None of the expected keys found in response")
        return ""
        
        return ""


class QualityMetrics:
    """Quality metrics for evaluating agent performance"""
    
    def __init__(self):
        self.metrics = {
            "accuracy": 0.0,              # % of verified claims
            "completeness": 0.0,          # % of query answered
            "relevance": 0.0,             # % of relevant information
            "timeliness": 0.0,            # Response time efficiency
            "credibility": 0.0,           # Source credibility score
            "consistency": 0.0,           # Internal consistency
            "hallucination_rate": 0.0,    # % of hallucinated content
            "tool_efficiency": 0.0,       # Tool utilization efficiency
            "error_recovery": 0.0,        # Recovery success rate
            "memory_utilization": 0.0,    # Memory system efficiency
            "research_quality": 0.0,      # Overall research quality
            "report_clarity": 0.0,        # Report readability and clarity
            "source_diversity": 0.0,      # Diversity of sources used
            "data_validation": 0.0,       # Data cross-validation success
            "risk_identification": 0.0,   # Risk identification score
            "competitive_analysis": 0.0,  # Competitive positioning analysis
            "financial_accuracy": 0.0,    # Financial data accuracy
            "insight_depth": 0.0,         # Depth of analysis
            "recommendation_quality": 0.0, # Quality of recommendations
            "response_time": 0.0,         # Response time in seconds
        }
    
    def calculate_overall_score(self) -> float:
        """Calculate overall quality score"""
        valid_metrics = [v for v in self.metrics.values() if v is not None]
        if not valid_metrics:
            return 0.0
        return sum(valid_metrics) / len(valid_metrics)
    
    def get_report(self) -> str:
        """Get formatted quality report"""
        lines = ["Quality Metrics Report", "=" * 50]
        
        for metric_name, value in self.metrics.items():
            lines.append(f"{metric_name}: {value:.2%}")
        
        overall = self.calculate_overall_score()
        lines.append("=" * 50)
        lines.append(f"Overall Score: {overall:.2%}")
        
        return "\n".join(lines)


class ResearchChallenge:
    """A research challenge for evaluating the agent"""
    
    def __init__(self, challenge_id: str, difficulty: int, query: str, expected_components: List[str]):
        self.challenge_id = challenge_id
        self.difficulty = difficulty  # 1-8
        self.query = query
        self.expected_components = expected_components
        self.created_at = datetime.now()
    
    def evaluate_response(self, response: Dict[str, Any]) -> float:
        """
        Evaluate agent's response to this challenge
        
        Args:
            response: Agent's research response
            
        Returns:
            Score 0-1
        """
        score = 0.0
        report = response.get("report", "")
        
        # Check for expected components
        for component in self.expected_components:
            if component.lower() in report.lower():
                score += 1.0 / len(self.expected_components)
        
        # Penalize for hallucination
        hallucination_penalty = response.get("hallucination_rate", 0) * 0.5
        score = max(0, score - hallucination_penalty)
        
        return min(1.0, score)


class EvaluationFramework:
    """Framework for comprehensive agent evaluation"""
    
    def __init__(self):
        self.challenges: List[ResearchChallenge] = []
        self.results: List[Dict[str, Any]] = []
        self.llm_evaluator = LLMEvaluator()
        self._create_evaluation_challenges()
        log.info("Initialized EvaluationFramework with LLM-as-a-judge evaluator")
    
    def _create_evaluation_challenges(self):
        """Create 8 progressive research challenges"""
        
        self.challenges = [
            ResearchChallenge(
                "challenge_1",
                1,
                "Provide a basic company profile for Apple Inc.",
                ["company name", "sector", "market cap", "employees", "headquarters"]
            ),
            ResearchChallenge(
                "challenge_2",
                2,
                "Analyze Apple's recent financial performance (last 2 years)",
                ["revenue", "net income", "growth rate", "profitability", "financial ratios"]
            ),
            ResearchChallenge(
                "challenge_3",
                3,
                "Identify and assess key risks for Tesla Inc.",
                ["regulatory risk", "competition", "supply chain", "market risk", "operational risk"]
            ),
            ResearchChallenge(
                "challenge_4",
                4,
                "Compare Microsoft, Google, and Amazon in cloud computing",
                ["market position", "revenue breakdown", "market share", "competitive advantages", "strategies"]
            ),
            ResearchChallenge(
                "challenge_5",
                5,
                "Conduct sentiment analysis on recent news for tech sector",
                ["positive indicators", "negative indicators", "sentiment score", "trend analysis", "drivers"]
            ),
            ResearchChallenge(
                "challenge_6",
                6,
                "Generate an investment thesis for JPMorgan Chase stock",
                ["thesis statement", "financial analysis", "market opportunity", "risks", "valuation", "recommendation"]
            ),
            ResearchChallenge(
                "challenge_7",
                7,
                "Analyze pharma company with simulated API failures for 2 tools",
                ["alternative sources", "error recovery", "data validation", "research completion", "quality maintenance"]
            ),
            ResearchChallenge(
                "challenge_8",
                8,
                "Comprehensive financial research with conflicting data resolution",
                ["data reconciliation", "source prioritization", "reliability hierarchy", "conflict resolution", "final report"]
            ),
        ]
    
    async def run_evaluation(self, agent: Any) -> Dict[str, Any]:
        """Run complete evaluation suite with LLM-as-a-judge"""
        log.info("Starting agent evaluation with LLM-as-a-judge...")
        
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "challenges": [],
            "summary": {},
            "evaluator_model": settings.evaluator_model_id,
        }
        
        for i, challenge in enumerate(self.challenges, 1):
            log.info(f"Running challenge {i}/8: {challenge.query}")
            
            try:
                # Execute research
                response = await agent.execute_research(
                    query=challenge.query,
                    research_type=f"challenge_{i}"
                )
                
                # Use LLM-as-a-judge for evaluation
                report = response.get("report", "")
                llm_evaluation = await self.llm_evaluator.evaluate_report(report, challenge.query)
                
                # Extract overall score from LLM evaluation
                overall_score = llm_evaluation.get("overall_score", 0) / 100
                
                challenge_result = {
                    "challenge_id": challenge.challenge_id,
                    "difficulty": challenge.difficulty,
                    "query": challenge.query,
                    "score": overall_score,
                    "status": response.get("status", "unknown"),
                    "iterations": response.get("iterations", 0),
                    "llm_evaluation": llm_evaluation,
                }
                
                evaluation_results["challenges"].append(challenge_result)
                self.results.append(challenge_result)
                
                log.info(f"Challenge {i} LLM score: {overall_score:.2%}")
                
            except Exception as e:
                log.error(f"Error evaluating challenge {i}: {str(e)}")
                evaluation_results["challenges"].append({
                    "challenge_id": challenge.challenge_id,
                    "score": 0.0,
                    "error": str(e),
                })
        
        # Calculate summary statistics
        scores = [r["score"] for r in evaluation_results["challenges"] if "score" in r]
        evaluation_results["summary"] = {
            "total_challenges": len(self.challenges),
            "completed": len(scores),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "pass_rate": sum(1 for s in scores if s >= settings.quality_threshold) / len(scores) if scores else 0,
            "evaluations_passed": sum(1 for s in scores if s >= settings.quality_threshold),
        }
        
        log.info(f"Evaluation complete. Average score: {evaluation_results['summary']['average_score']:.2%}")
        
        return evaluation_results
    
    def get_evaluation_report(self) -> str:
        """Generate formatted evaluation report with LLM metrics"""
        lines = [
            "Agent Evaluation Report (LLM-as-a-Judge)",
            "=" * 80,
            f"Evaluator Model: {settings.evaluator_model_id}",
            f"Challenges Completed: {len(self.results)}",
            "",
        ]
        
        for i, result in enumerate(self.results, 1):
            lines.append(f"Challenge {i} ({result.get('challenge_id', 'unknown')}):")
            lines.append(f"  Difficulty: {result.get('difficulty', 'N/A')}")
            lines.append(f"  Score: {result.get('score', 0):.2%}")
            lines.append(f"  Status: {result.get('status', 'unknown')}")
            
            # Include LLM evaluation metrics if available
            if "llm_evaluation" in result:
                llm_eval = result["llm_evaluation"]
                lines.append(f"  LLM Metrics:")
                lines.append(f"    - Accuracy: {llm_eval.get('accuracy', 0)}/100")
                lines.append(f"    - Completeness: {llm_eval.get('completeness', 0)}/100")
                lines.append(f"    - Relevance: {llm_eval.get('relevance', 0)}/100")
                lines.append(f"    - Clarity: {llm_eval.get('report_clarity', 0)}/100")
                lines.append(f"    - Risk Identification: {llm_eval.get('risk_identification', 0)}/100")
                lines.append(f"    - Financial Accuracy: {llm_eval.get('financial_accuracy', 0)}/100")
                lines.append(f"    - Insight Depth: {llm_eval.get('insight_depth', 0)}/100")
                lines.append(f"    - Recommendation Quality: {llm_eval.get('recommendation_quality', 0)}/100")
                
                if "strengths" in llm_eval and llm_eval["strengths"]:
                    lines.append(f"  Strengths: {', '.join(llm_eval['strengths'][:2])}")
                if "weaknesses" in llm_eval and llm_eval["weaknesses"]:
                    lines.append(f"  Weaknesses: {', '.join(llm_eval['weaknesses'][:2])}")
            
            lines.append("")
        
        if self.results:
            avg_score = sum(r.get("score", 0) for r in self.results) / len(self.results)
            lines.append("=" * 80)
            lines.append(f"Average Score: {avg_score:.2%}")
            lines.append(f"Passed Threshold ({settings.quality_threshold:.0%}): {sum(1 for r in self.results if r.get('score', 0) >= settings.quality_threshold)}/{len(self.results)}")
            lines.append(f"Overall Assessment: {'PASSED' if avg_score >= settings.quality_threshold else 'NEEDS IMPROVEMENT'}")
        
        return "\n".join(lines)
