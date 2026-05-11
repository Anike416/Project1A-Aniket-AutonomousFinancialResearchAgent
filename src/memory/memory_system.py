"""
Memory system for ARA-1 agent (short-term, long-term, and episodic)
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from src.config.settings import settings
from src.config.logger import log
import json
 

class MemoryEntry(BaseModel):
    """Single memory entry"""
    id: str
    content: str
    timestamp: datetime
    source_type: str  # "session", "research", "error_recovery", etc.
    metadata: Dict[str, Any]
    confidence: float = 1.0
    tags: List[str] = []


class ShortTermMemory:
    """Short-term memory for current session (working memory)"""
    
    def __init__(self, max_tokens: int = None):
        self.max_tokens = max_tokens or settings.short_term_max_tokens
        self.entries: List[MemoryEntry] = []
        self.current_token_count = 0
        log.info(f"Initialized ShortTermMemory with max tokens: {self.max_tokens}")
    
    def add_entry(self, content: str, source_type: str, metadata: Dict[str, Any], tags: List[str] = None):
        """Add entry to short-term memory"""
        entry = MemoryEntry(
            id=f"short-term-{len(self.entries)}",
            content=content,
            timestamp=datetime.now(),
            source_type=source_type,
            metadata=metadata,
            tags=tags or [],
        )
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        token_estimate = len(content) // 4
        
        if self.current_token_count + token_estimate > self.max_tokens:
            # Remove oldest entries until we have space
            self._make_space(token_estimate)
        
        self.entries.append(entry)
        self.current_token_count += token_estimate
        log.debug(f"Added entry to short-term memory. Total tokens: {self.current_token_count}")
    
    def _make_space(self, required_tokens: int):
        """Remove old entries to make space"""
        while self.entries and self.current_token_count + required_tokens > self.max_tokens:
            removed = self.entries.pop(0)
            removed_tokens = len(removed.content) // 4
            self.current_token_count -= removed_tokens
            log.debug(f"Removed old entry from short-term memory")
    
    def get_context(self, limit: Optional[int] = None) -> str:
        """Get formatted context from short-term memory"""
        entries_to_include = self.entries if limit is None else self.entries[-limit:]
        
        context_lines = []
        for entry in entries_to_include:
            context_lines.append(f"[{entry.source_type}] {entry.content}")
        
        return "\n".join(context_lines)
    
    def clear(self):
        """Clear all short-term memory"""
        self.entries.clear()
        self.current_token_count = 0
        log.info("Cleared short-term memory")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        return {
            "entries_count": len(self.entries),
            "token_count": self.current_token_count,
            "max_tokens": self.max_tokens,
            "utilization_percent": (self.current_token_count / self.max_tokens * 100) if self.max_tokens else 0,
        }


class LongTermMemory:
    """Long-term memory backed by vector database (Pinecone)"""
    
    def __init__(self):
        self.vector_db = None
        self._initialize_vector_db()
        log.info("Initialized LongTermMemory with vector database")
    
    def _initialize_vector_db(self):
        """Initialize connection to Pinecone vector database"""
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Create index if it doesn't exist
            try:
                pc.create_index(
                    name=settings.pinecone_index_name,
                    dimension=settings.pinecone_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
                )
                log.info(f"Created Pinecone index: {settings.pinecone_index_name}")
            except Exception as e:
                log.debug(f"Index already exists or error creating index: {str(e)}")
            
            self.vector_db = pc.Index(settings.pinecone_index_name)
            log.info("Connected to Pinecone vector database")
            
        except ImportError:
            log.warning("Pinecone not installed, long-term memory disabled")
            self.vector_db = None
        except Exception as e:
            log.error(f"Error initializing vector database: {str(e)}")
            self.vector_db = None
    
    async def store(
        self,
        content: str,
        embedding: List[float],
        ticker: str,
        source_type: str,
        confidence: float = 1.0,
        verified: bool = False,
    ):
        """Store memory entry in vector database"""
        if not self.vector_db:
            log.warning("Vector database not available, skipping storage")
            return
        
        try:
            metadata = {
                "content": content[:500],  # Store first 500 chars for reference
                "ticker": ticker,
                "source_type": source_type,
                "timestamp": datetime.now().isoformat(),
                "confidence": confidence,
                "verified": verified,
            }
            
            # Vector DB operations are typically synchronous
            # This is a simplified version
            entry_id = f"{ticker}-{source_type}-{int(datetime.now().timestamp())}"
            
            self.vector_db.upsert(
                vectors=[(entry_id, embedding, metadata)]
            )
            
            log.debug(f"Stored long-term memory: {entry_id}")
            
        except Exception as e:
            log.error(f"Error storing in vector database: {str(e)}")
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search long-term memory using vector similarity"""
        if not self.vector_db:
            log.warning("Vector database not available, returning empty results")
            return []
        
        try:
            results = self.vector_db.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
            )
            
            formatted_results = []
            for match in results.get("matches", []):
                formatted_results.append({
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": match.get("metadata", {}),
                })
            
            log.debug(f"Retrieved {len(formatted_results)} results from long-term memory")
            return formatted_results
            
        except Exception as e:
            log.error(f"Error searching long-term memory: {str(e)}")
            return []
    
    async def get_by_ticker(self, ticker: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve all memories for a specific ticker"""
        if not self.vector_db:
            return []
        
        try:
            # This would typically use a metadata filter in Pinecone
            log.debug(f"Retrieved memories for ticker: {ticker}")
            return []  # Placeholder
            
        except Exception as e:
            log.error(f"Error retrieving memories for ticker: {str(e)}")
            return []


class EpisodicMemory:
    """Episodic memory for learning from past experiences and strategies"""
    
    def __init__(self):
        self.episodes: Dict[str, Dict[str, Any]] = {}
        self.strategies: Dict[str, List[str]] = {}  # Query type -> successful strategies
        self.error_patterns: Dict[str, int] = {}  # Error type -> count
        log.info("Initialized EpisodicMemory")
    
    def record_episode(
        self,
        episode_id: str,
        query: str,
        tools_used: List[str],
        success: bool,
        duration: float,
        findings_quality: float,
    ):
        """Record an episode of agent interaction"""
        episode = {
            "query": query,
            "tools_used": tools_used,
            "success": success,
            "duration": duration,
            "findings_quality": findings_quality,
            "timestamp": datetime.now().isoformat(),
        }
        self.episodes[episode_id] = episode
        
        # Record successful strategy
        if success:
            query_type = self._classify_query(query)
            if query_type not in self.strategies:
                self.strategies[query_type] = []
            strategy_key = "-".join(sorted(tools_used))
            if strategy_key not in self.strategies[query_type]:
                self.strategies[query_type].append(strategy_key)
        
        log.debug(f"Recorded episode: {episode_id}")
    
    def record_error(self, error_type: str, recovery_action: str):
        """Record error pattern and recovery action"""
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = 0
        self.error_patterns[error_type] += 1
        log.debug(f"Recorded error pattern: {error_type}")
    
    def get_recommended_tools(self, query: str) -> List[str]:
        """Get recommended tools based on past successful strategies"""
        query_type = self._classify_query(query)
        
        if query_type in self.strategies and self.strategies[query_type]:
            # Return tools from the most commonly successful strategy
            latest_strategy = self.strategies[query_type][-1]
            return latest_strategy.split("-")
        
        return []
    
    def _classify_query(self, query: str) -> str:
        """Classify query type (simplified)"""
        query_lower = query.lower()
        if "risk" in query_lower:
            return "risk_assessment"
        elif "comparison" in query_lower or "vs" in query_lower:
            return "comparative_analysis"
        elif "growth" in query_lower or "trend" in query_lower:
            return "growth_analysis"
        elif "financial" in query_lower or "ratio" in query_lower:
            return "financial_analysis"
        else:
            return "general_research"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get episodic memory statistics"""
        successful_episodes = sum(1 for e in self.episodes.values() if e.get("success"))
        
        return {
            "total_episodes": len(self.episodes),
            "successful_episodes": successful_episodes,
            "success_rate": successful_episodes / len(self.episodes) if self.episodes else 0,
            "error_patterns": self.error_patterns,
            "strategy_count": len(self.strategies),
        }


class AgentMemorySystem:
    """Integrated memory system combining all three memory types"""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        log.info("Initialized AgentMemorySystem")
    
    def get_full_context(self) -> str:
        """Get complete context from all memory sources"""
        context = self.short_term.get_context()
        return context
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get status of all memory components"""
        return {
            "short_term": self.short_term.get_summary(),
            "episodic": self.episodic.get_statistics(),
        }
