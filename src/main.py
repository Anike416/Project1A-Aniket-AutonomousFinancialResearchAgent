"""
Main entry point for ARA-1 agent
"""
import asyncio
import sys
import typer
from typing import Optional
from src.config.logger import log, setup_logging
from src.config.settings import settings
from src.agents.research_agent import get_agent
from src.evaluation.framework import EvaluationFramework
from src.tools.base_tool import get_tool_registry
from src.tools.financial_tools import (
    SecFilingSearchTool,
    WebSearchTool,
    FinancialDataAPITool,
)
from src.tools.research_tools import (
    EarningsTranscriptTool,
    NewsSentimentTool,
    CompanyProfileTool,
    PeerComparisonTool,
    FactCheckerTool,
    CalculationEngineTool,
)
from src.tools.memory_tools import (
    ReportGeneratorTool,
    VectorDBSearchTool,
    VectorDBStoreTool,
)

# Initialize CLI app
app = typer.Typer(help="ARA-1: Autonomous Research Agent")


def setup_tools():
    """Initialize and register all tools"""
    registry = get_tool_registry()
    
    tools = [
        SecFilingSearchTool(),
        WebSearchTool(),
        FinancialDataAPITool(),
        EarningsTranscriptTool(),
        NewsSentimentTool(),
        CompanyProfileTool(),
        PeerComparisonTool(),
        FactCheckerTool(),
        CalculationEngineTool(),
        ReportGeneratorTool(),
        VectorDBSearchTool(),
        VectorDBStoreTool(),
    ]
    
    for tool in tools:
        registry.register_tool(tool)
    
    log.info(f"Registered {len(tools)} tools")
    return registry


@app.command()
def research(
    query: str = typer.Argument(..., help="Research query"),
    research_type: str = typer.Option("general", help="Type of research"),
    output_file: Optional[str] = typer.Option(None, help="Output file for report"),
):
    """Execute a research task"""
    setup_logging()
    log.info(f"Starting research: {query}")
    
    # Setup tools
    setup_tools()
    
    # Get agent
    agent = get_agent()
    
    # Execute research
    try:
        result = asyncio.run(agent.execute_research(query, research_type))
        
        if result["status"] == "success":
            print(f"\n✓ Research completed successfully")
            print(f"  Iterations: {result['iterations']}")
            print(f"\nReport:\n{result['report']}")
            
            # Save to file if specified
            if output_file:
                with open(output_file, "w") as f:
                    f.write(result["report"])
                print(f"\nReport saved to: {output_file}")
        else:
            print(f"\n✗ Research failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        log.error(f"Error executing research: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


@app.command()
def evaluate():
    """Run comprehensive evaluation suite"""
    setup_logging()
    log.info("Starting agent evaluation")
    
    # Setup tools
    setup_tools()
    
    # Get agent
    agent = get_agent()
    
    # Run evaluation
    try:
        framework = EvaluationFramework()
        results = asyncio.run(framework.run_evaluation(agent))
        
        # Print report
        print(framework.get_evaluation_report())
        
        # Print summary
        summary = results["summary"]
        print(f"\nSummary:")
        print(f"  Average Score: {summary['average_score']:.2%}")
        print(f"  Pass Rate: {summary['pass_rate']:.2%}")
        print(f"  Challenges Passed: {summary['evaluations_passed']}/{summary['total_challenges']}")
        
    except Exception as e:
        log.error(f"Error running evaluation: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


@app.command()
def status():
    """Get agent status and statistics"""
    setup_logging()
    
    # Setup tools
    setup_tools()
    
    # Get agent
    agent = get_agent()
    
    # Print status
    status_info = agent.get_agent_status()
    
    print("Agent Status Report")
    print("=" * 50)
    print(f"Active Threads: {status_info['active_threads']}")
    print(f"Completed Research: {status_info['completed_research']}")
    print()
    
    print("Tool Registry Stats:")
    print("-" * 50)
    tools_stats = status_info["tool_registry_stats"]
    print(f"Total Tools: {tools_stats['total_tools']}")
    
    for tool_name, stats in tools_stats["tools"].items():
        efficiency = stats["efficiency"] * 100
        print(f"  {tool_name}:")
        print(f"    Calls: {stats['call_count']}")
        print(f"    Success Rate: {efficiency:.1f}%")
    
    print()
    print("Memory System Status:")
    print("-" * 50)
    memory_status = status_info["memory_status"]
    short_term = memory_status.get("short_term", {})
    print(f"Short-term Memory Utilization: {short_term.get('utilization_percent', 0):.1f}%")


@app.command()
def interactive():
    """Start interactive research session"""
    setup_logging()
    log.info("Starting interactive session")
    
    # Setup tools
    setup_tools()
    
    # Get agent
    agent = get_agent()
    
    print("ARA-1 Interactive Research Session")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit\n")
    
    session_count = 0
    
    while True:
        try:
            user_input = input("Research Query > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Exiting...")
                break
            
            if user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  quit - Exit the session")
                print("  status - Show agent status")
                print("  help - Show this help message")
                print("  Or enter a research query\n")
                continue
            
            if user_input.lower() == "status":
                status_info = agent.get_agent_status()
                print(f"Active threads: {status_info['active_threads']}")
                print(f"Completed research: {status_info['completed_research']}\n")
                continue
            
            # Execute research
            session_count += 1
            print(f"\n[Session {session_count}] Processing query...")
            
            result = asyncio.run(agent.execute_research(user_input))
            
            if result["status"] == "success":
                print(f"\n✓ Completed in {result['iterations']} iterations\n")
                print("Report Preview:")
                print("-" * 50)
                report_preview = result["report"][:500] + "..." if len(result["report"]) > 500 else result["report"]
                print(report_preview)
                print("-" * 50)
                
                save_choice = input("\nSave full report? (y/n): ").strip().lower()
                if save_choice == "y":
                    filename = f"research_report_{session_count}.md"
                    with open(filename, "w") as f:
                        f.write(result["report"])
                    print(f"Report saved to: {filename}")
            else:
                print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted by user")
            break
        except Exception as e:
            log.error(f"Error in interactive session: {str(e)}")
            print(f"Error: {str(e)}")


@app.command()
def init():
    """Initialize the agent and verify configuration"""
    setup_logging()
    log.info("Initializing ARA-1 Agent")
    
    print("Initializing ARA-1 Agent")
    print("=" * 50)
    
    # Check settings
    print("\n✓ Configuration loaded")
    print(f"  Region: {settings.aws_region}")
    print(f"  Model: {settings.bedrock_model_id}")
    print(f"  Max Iterations: {settings.agent_max_iterations}")
    
    # Initialize tools
    print("\n✓ Initializing tools...")
    registry = setup_tools()
    
    # Get agent
    print("\n✓ Initializing agent...")
    agent = get_agent()
    
    # Print summary
    print("\n✓ Agent initialized successfully")
    print(f"  Tools available: {len(registry.list_tools())}")
    
    print("\nReady to use! Try:")
    print("  ara-agent research 'Your research query'")
    print("  ara-agent evaluate")
    print("  ara-agent interactive")


def main():
    """Main entry point"""
    setup_logging()
    app()


if __name__ == "__main__":
    main()
