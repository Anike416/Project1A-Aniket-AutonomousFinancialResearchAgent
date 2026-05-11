"""
Error handling and recovery mechanisms for the agent
""" 
from typing import Any, Dict, Optional, Callable
from enum import Enum
from src.config.logger import log
from src.config.settings import settings


class ErrorType(str, Enum):
    """Types of errors that can occur"""
    API_UNAVAILABLE = "api_unavailable"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    MALFORMED_RESPONSE = "malformed_response"
    TIMEOUT = "timeout"
    HALLUCINATION = "hallucination"
    LOGICAL_ERROR = "logical_error"
    UNKNOWN = "unknown"


class ErrorRecoveryStrategy(str, Enum):
    """Strategies for recovering from errors"""
    RETRY = "retry"
    FALLBACK_TOOL = "fallback_tool"
    SKIP_STEP = "skip_step"
    DEGRADED_MODE = "degraded_mode"
    ABORT = "abort"


class ErrorHandler:
    """Handles error recovery and graceful degradation"""
    
    def __init__(self):
        self.error_count: Dict[ErrorType, int] = {error_type: 0 for error_type in ErrorType}
        self.recovery_attempts: Dict[ErrorType, int] = {error_type: 0 for error_type in ErrorType}
        self.fallback_chains: Dict[str, list] = self._build_fallback_chains()
        log.info("Initialized ErrorHandler")
    
    def _build_fallback_chains(self) -> Dict[str, list]:
        """Build tool fallback chains"""
        return {
            "sec_filing_search": [
                "vector_db_search",  # Try vector DB first
                "web_search",        # Then web search
                "company_profile",   # Then basic profile
            ],
            "financial_data_api": [
                "vector_db_search",
                "web_search",
            ],
            "earnings_transcript": [
                "web_search",
                "news_sentiment",
            ],
            "web_search": [
                "vector_db_search",
            ],
        }
    
    async def handle_tool_error(
        self,
        tool_name: str,
        error: Exception,
        attempt: int = 1,
    ) -> tuple[ErrorRecoveryStrategy, Optional[str]]:
        """
        Handle a tool execution error
        
        Args:
            tool_name: Name of the tool that failed
            error: The exception that occurred
            attempt: Current attempt number
            
        Returns:
            Tuple of (recovery_strategy, fallback_tool_name)
        """
        error_type = self._classify_error(error)
        self.error_count[error_type] += 1
        
        log.warning(f"Tool error: {tool_name} - {error_type}: {str(error)}")
        
        # Determine recovery strategy
        if attempt < settings.max_retries:
            # Retry with exponential backoff
            self.recovery_attempts[error_type] += 1
            return ErrorRecoveryStrategy.RETRY, None
        
        elif tool_name in self.fallback_chains:
            # Try fallback tool
            fallback_chain = self.fallback_chains[tool_name]
            if attempt - 1 < len(fallback_chain):
                fallback = fallback_chain[attempt - 1]
                self.recovery_attempts[ErrorType.API_UNAVAILABLE] += 1
                log.info(f"Using fallback tool: {fallback}")
                return ErrorRecoveryStrategy.FALLBACK_TOOL, fallback
        
        # Check if we can degrade gracefully
        if self._can_degrade_gracefully(tool_name):
            log.info(f"Entering degraded mode for {tool_name}")
            return ErrorRecoveryStrategy.DEGRADED_MODE, None
        
        # Skip this step
        if attempt < settings.fallback_chain_depth:
            log.info(f"Skipping step with {tool_name}")
            return ErrorRecoveryStrategy.SKIP_STEP, None
        
        # Abort
        log.error(f"Aborting - max recovery attempts reached for {tool_name}")
        return ErrorRecoveryStrategy.ABORT, None
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type"""
        error_str = str(error).lower()
        
        if "unavailable" in error_str or "connection" in error_str:
            return ErrorType.API_UNAVAILABLE
        elif "rate" in error_str or "quota" in error_str:
            return ErrorType.RATE_LIMIT
        elif "auth" in error_str or "unauthorized" in error_str:
            return ErrorType.AUTH_ERROR
        elif "malformed" in error_str or "parse" in error_str:
            return ErrorType.MALFORMED_RESPONSE
        elif "timeout" in error_str:
            return ErrorType.TIMEOUT
        elif "hallucination" in error_str:
            return ErrorType.HALLUCINATION
        
        return ErrorType.UNKNOWN
    
    def _can_degrade_gracefully(self, tool_name: str) -> bool:
        """Check if tool can degrade gracefully"""
        # Tools that have graceful degradation options
        degradable_tools = [
            "web_search",
            "news_sentiment",
            "peer_comparison",
            "sec_filing_search",
        ]
        return tool_name in degradable_tools
    
    def detect_hallucination(self, claim: str, sources: list) -> bool:
        """
        Detect potential hallucinations
        
        Args:
            claim: The claim to verify
            sources: List of sources to verify against
            
        Returns:
            True if hallucination detected
        """
        # Simple heuristic: if claim contains specific numbers or entities
        # but no sources mention them, it might be hallucination
        
        import re
        
        # Extract numbers and entities from claim
        numbers = re.findall(r'\d+(?:\.\d+)?', claim)
        
        # Check if numbers appear in sources
        for num in numbers:
            found = any(num in str(source) for source in sources)
            if not found:
                log.warning(f"Potential hallucination detected: number {num} not in sources")
                return True
        
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = sum(self.error_count.values())
        total_recoveries = sum(self.recovery_attempts.values())
        
        return {
            "total_errors": total_errors,
            "total_recoveries": total_recoveries,
            "recovery_rate": total_recoveries / total_errors if total_errors > 0 else 0,
            "errors_by_type": {str(k): v for k, v in self.error_count.items()},
            "recoveries_by_type": {str(k): v for k, v in self.recovery_attempts.items()},
        }


class CircuitBreaker:
    """Circuit breaker pattern for handling cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        log.info(f"Initialized CircuitBreaker (threshold={failure_threshold})")
    
    def record_success(self):
        """Record successful operation"""
        if self.state == "half-open":
            self.state = "closed"
            self.failure_count = 0
            log.info("Circuit breaker closed after successful operation")
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        from datetime import datetime
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            log.error(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "closed":
            return True
        
        elif self.state == "open":
            from datetime import datetime, timedelta
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.reset_timeout):
                self.state = "half-open"
                self.failure_count = 0
                log.info("Circuit breaker transitioning to half-open")
                return True
            return False
        
        else:  # half-open
            return True
