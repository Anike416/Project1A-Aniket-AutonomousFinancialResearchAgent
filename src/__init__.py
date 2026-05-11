"""ARA-1: Autonomous Research Agent"""

__version__ = "1.0.0"
__author__ = "Zetheta Algorithms"

from src.agents.research_agent import get_agent, AutonomousResearchAgent
from src.tools.base_tool import get_tool_registry, ToolRegistry
from src.memory.memory_system import AgentMemorySystem
from src.config.settings import settings

__all__ = [
    "get_agent",
    "AutonomousResearchAgent",
    "get_tool_registry",
    "ToolRegistry",
    "AgentMemorySystem",
    "settings",
]
