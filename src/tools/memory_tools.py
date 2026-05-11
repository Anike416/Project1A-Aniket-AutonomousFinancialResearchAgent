"""
Report generation and memory tools
"""
from typing import Any, Dict, List
from datetime import datetime
from src.tools.base_tool import BaseTool, ToolParameter, ToolResult, ToolStatus
from src.config.logger import log


class ReportGeneratorTool(BaseTool):
    """Tool for generating structured financial research reports"""
    
    def __init__(self):
        parameters = [
            ToolParameter(
                name="template",
                type="string",
                description="Report template type",
                enum=["company_analysis", "investment_thesis", "risk_assessment", "competitor_analysis"],
                required=True,
            ),
            ToolParameter(name="sections", type="object", description="Report sections and content", required=True),
            ToolParameter(name="sources", type="array", description="List of sources cited", required=False),
        ]
        super().__init__(
            name="report_generator",
            description="Format researched data into a structured investment research report",
            parameters=parameters,
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute report generation"""
        try:
            template = kwargs.get("template")
            sections = kwargs.get("sections", {})
            sources = kwargs.get("sources", [])
            
            if not template:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILURE,
                    data=None,
                    error="Missing required parameter: template",
                )
            
            log.info(f"Generating report with template: {template}")
            
            # Generate markdown report
            report = self._generate_markdown_report(template, sections, sources)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.SUCCESS,
                data=report,
                metadata={"template": template, "sections_count": len(sections)},
                confidence=0.92,
            )
            
        except Exception as e:
            log.error(f"Error generating report: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILURE,
                data=None,
                error=str(e),
            )
    
    def _generate_markdown_report(self, template: str, sections: Dict[str, Any], sources: List[str]) -> str:
        """Generate markdown formatted report"""
        report_lines = []
        
        # Header
        report_lines.append(f"# {template.replace('_', ' ').title()}")
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append(sections.get("summary", "Summary not provided") + "\n")
        
        # Sections
        for section_name, content in sections.items():
            if section_name != "summary":
                report_lines.append(f"## {section_name.replace('_', ' ').title()}")
                report_lines.append(str(content) + "\n")
        
        # Sources
        if sources:
            report_lines.append("## Sources")
            for source in sources:
                report_lines.append(f"- {source}")
        
        return "\n".join(report_lines)


class VectorDBSearchTool(BaseTool):
    """Tool for searching long-term memory via vector database"""
    
    def __init__(self):
        parameters = [
            ToolParameter(name="query", type="string", description="Search query", required=True),
            ToolParameter(name="top_k", type="integer", description="Top K results", required=False, default=5),
            ToolParameter(name="filter", type="object", description="Metadata filter", required=False),
        ]
        super().__init__(
            name="vector_db_search",
            description="Search the agent's long-term memory for previously researched information",
            parameters=parameters,
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute vector DB search"""
        try:
            query = kwargs.get("query")
            top_k = kwargs.get("top_k", 5)
            filter_dict = kwargs.get("filter")
            
            if not query:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILURE,
                    data=None,
                    error="Missing required parameter: query",
                )
            
            log.info(f"Searching vector DB for: {query}")
            
            # In production, this would integrate with Pinecone
            from src.memory.memory_system import AgentMemorySystem
            
            # Simulate search results
            results = [
                {
                    "id": f"result-{i+1}",
                    "content": f"Previously researched information about {query}",
                    "similarity_score": 0.92 - (i * 0.05),
                    "source_type": "research",
                    "date": datetime.now().isoformat(),
                }
                for i in range(top_k)
            ]
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.SUCCESS,
                data=results,
                metadata={"query": query, "results_count": len(results)},
                confidence=0.88,
            )
            
        except Exception as e:
            log.error(f"Error searching vector DB: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILURE,
                data=None,
                error=str(e),
            )


class VectorDBStoreTool(BaseTool):
    """Tool for storing research findings in long-term memory"""
    
    def __init__(self):
        parameters = [
            ToolParameter(name="content", type="string", description="Content to store", required=True),
            ToolParameter(name="metadata", type="object", description="Metadata (ticker, date, source_type)", required=True),
        ]
        super().__init__(
            name="vector_db_store",
            description="Store new research findings in the agent's long-term memory",
            parameters=parameters,
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute vector DB store"""
        try:
            content = kwargs.get("content")
            metadata = kwargs.get("metadata", {})
            
            if not content:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILURE,
                    data=None,
                    error="Missing required parameter: content",
                )
            
            log.info(f"Storing in vector DB: {metadata.get('ticker', 'unknown')}")
            
            # Generate embedding and store (placeholder)
            doc_id = f"{metadata.get('ticker', 'doc')}-{datetime.now().timestamp()}"
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.SUCCESS,
                data={"document_id": doc_id, "stored": True},
                metadata={"content_length": len(content), "ticker": metadata.get("ticker")},
                confidence=0.9,
            )
            
        except Exception as e:
            log.error(f"Error storing in vector DB: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILURE,
                data=None,
                error=str(e),
            )
