"""
Base tool class and tool registry for ARA-1 agent
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
from src.config.logger import log
 

class ToolStatus(str, Enum):
    """Status of a tool execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ToolParameter(BaseModel):
    """Definition of a tool parameter"""
    name: str
    type: str  # "string", "integer", "float", "boolean", "array", "object"
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class ToolSchema(BaseModel):
    """JSON schema for tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = Field(default_factory=list)


class ToolResult(BaseModel):
    """Result of tool execution"""
    tool_name: str
    status: ToolStatus
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0  # Confidence level of result (0-1)


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, name: str, description: str, parameters: List[ToolParameter]):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.call_count = 0
        self.error_count = 0
        self.success_count = 0
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> ToolSchema:
        """Get JSON schema representation of tool"""
        properties = {}
        required_fields = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required_fields.append(param.name)
        
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": properties,
                "required": required_fields,
            },
            required=required_fields,
        )
    
    def get_bedrock_schema(self) -> Dict[str, Any]:
        """Get Bedrock-compatible tool schema"""
        schema = self.get_schema()
        return {
            "toolSpec": {
                "name": schema.name,
                "description": schema.description,
                "inputSchema": schema.parameters,
            }
        }
    
    def record_success(self):
        """Record successful tool execution"""
        self.call_count += 1
        self.success_count += 1
    
    def record_error(self):
        """Record tool execution error"""
        self.call_count += 1
        self.error_count += 1
    
    def get_efficiency(self) -> float:
        """Get tool efficiency score (0-1)"""
        if self.call_count == 0:
            return 1.0
        return self.success_count / self.call_count


class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_aliases: Dict[str, str] = {}  # Aliases for tools
        log.info("Initialized ToolRegistry")
    
    def register_tool(self, tool: BaseTool, aliases: Optional[List[str]] = None):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
        if aliases:
            for alias in aliases:
                self.tool_aliases[alias] = tool.name
        log.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name or alias"""
        # Check aliases first
        if tool_name in self.tool_aliases:
            tool_name = self.tool_aliases[tool_name]
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[BaseTool]:
        """Get list of all registered tools"""
        return list(self.tools.values())
    
    def get_bedrock_tools_spec(self) -> List[Dict[str, Any]]:
        """Get all tools in Bedrock format"""
        return [tool.get_bedrock_schema() for tool in self.tools.values()]
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all tools"""
        descriptions = ["Available Tools:"]
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILURE,
                data=None,
                error=f"Tool '{tool_name}' not found in registry",
            )
        
        try:
            log.info(f"Executing tool: {tool_name} with kwargs: {kwargs}")
            result = await tool.execute(**kwargs)
            
            if result.status == ToolStatus.SUCCESS:
                tool.record_success()
            else:
                tool.record_error()
            
            return result
            
        except Exception as e:
            tool.record_error()
            log.error(f"Error executing tool {tool_name}: {str(e)}")
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILURE,
                data=None,
                error=str(e),
            )
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage"""
        stats = {
            "total_tools": len(self.tools),
            "tools": {}
        }
        
        for tool_name, tool in self.tools.items():
            stats["tools"][tool_name] = {
                "call_count": tool.call_count,
                "success_count": tool.success_count,
                "error_count": tool.error_count,
                "efficiency": tool.get_efficiency(),
            }
        
        return stats


# Global tool registry instance
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
