"""
Test suite for ARA-1 agent
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.agents.research_agent import AutonomousResearchAgent
from src.tools.base_tool import BaseTool, ToolParameter, ToolRegistry
from src.memory.memory_system import AgentMemorySystem
from src.evaluation.framework import EvaluationFramework


@pytest.fixture
def agent():
    """Create agent instance for testing"""
    return AutonomousResearchAgent()


@pytest.fixture
def memory_system():
    """Create memory system for testing"""
    return AgentMemorySystem()


class TestToolRegistry:
    """Test tool registry functionality"""
    
    def test_register_tool(self):
        """Test tool registration"""
        registry = ToolRegistry()
        
        # Create mock tool
        tool = Mock(spec=BaseTool)
        tool.name = "test_tool"
        
        registry.register_tool(tool)
        
        assert registry.get_tool("test_tool") == tool
    
    def test_tool_not_found(self):
        """Test tool not found"""
        registry = ToolRegistry()
        assert registry.get_tool("nonexistent") is None
    
    def test_list_tools(self):
        """Test listing tools"""
        registry = ToolRegistry()
        tool1 = Mock(spec=BaseTool, name="tool1")
        tool2 = Mock(spec=BaseTool, name="tool2")
        
        registry.register_tool(tool1)
        registry.register_tool(tool2)
        
        tools = registry.list_tools()
        assert len(tools) == 2


class TestMemorySystem:
    """Test memory system functionality"""
    
    def test_short_term_memory_add(self, memory_system):
        """Test adding to short-term memory"""
        memory_system.short_term.add_entry(
            "Test content",
            "test_source",
            {"key": "value"}
        )
        
        assert len(memory_system.short_term.entries) == 1
    
    def test_short_term_memory_context(self, memory_system):
        """Test getting context from short-term memory"""
        memory_system.short_term.add_entry("Content 1", "source1", {})
        memory_system.short_term.add_entry("Content 2", "source2", {})
        
        context = memory_system.short_term.get_context()
        
        assert "Content 1" in context
        assert "Content 2" in context
    
    def test_episodic_memory_record(self, memory_system):
        """Test episodic memory recording"""
        memory_system.episodic.record_episode(
            episode_id="test-1",
            query="Test query",
            tools_used=["tool1", "tool2"],
            success=True,
            duration=10.5,
            findings_quality=0.85
        )
        
        stats = memory_system.episodic.get_statistics()
        assert stats["total_episodes"] == 1
        assert stats["successful_episodes"] == 1


class TestEvaluationFramework:
    """Test evaluation framework"""
    
    def test_framework_initialization(self):
        """Test framework initialization"""
        framework = EvaluationFramework()
        
        assert len(framework.challenges) == 8
        assert all(c.difficulty >= 1 for c in framework.challenges)
        assert all(c.difficulty <= 8 for c in framework.challenges)
    
    def test_challenge_scoring(self):
        """Test challenge scoring"""
        framework = EvaluationFramework()
        challenge = framework.challenges[0]
        
        # Test perfect score
        response = {
            "report": "company name sector market cap employees headquarters",
            "hallucination_rate": 0,
        }
        score = challenge.evaluate_response(response)
        assert score > 0.5  # Should be high score
        
        # Test with hallucination
        response = {
            "report": "company name sector",
            "hallucination_rate": 0.5,
        }
        score = challenge.evaluate_response(response)
        assert score < 0.8  # Should be penalized


class TestAgentResearch:
    """Test agent research execution"""
    
    @pytest.mark.asyncio
    async def test_execute_research_structure(self, agent):
        """Test research execution returns correct structure"""
        # Mock the Bedrock client
        with patch('src.agents.research_agent.get_bedrock_client'):
            with patch.object(agent.tool_registry, 'execute_tool', return_value=AsyncMock()):
                result = await agent.execute_research("Test query")
                
                assert "status" in result
                assert "query" in result
                assert result["query"] == "Test query"


class TestErrorHandling:
    """Test error handling functionality"""
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery mechanism"""
        from src.utils.error_handler import ErrorHandler
        
        handler = ErrorHandler()
        strategy, fallback = await handler.handle_tool_error(
            "test_tool",
            Exception("Connection timeout"),
            attempt=1
        )
        
        # Should recommend retry on first attempt
        from src.utils.error_handler import ErrorRecoveryStrategy
        assert strategy in [
            ErrorRecoveryStrategy.RETRY,
            ErrorRecoveryStrategy.FALLBACK_TOOL,
            ErrorRecoveryStrategy.SKIP_STEP,
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
