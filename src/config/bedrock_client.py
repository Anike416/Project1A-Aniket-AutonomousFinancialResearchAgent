"""
AWS Bedrock client wrapper for LLM operations
"""
import boto3
import json
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config.settings import settings
from src.config.logger import log


class BedrockClient:
    """Wrapper for AWS Bedrock API interactions"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self.model_id = settings.bedrock_model_id
        self.embedding_model = settings.bedrock_embedding_model
        log.info(f"Initialized Bedrock client with model: {self.model_id}")
    
    @retry(stop=stop_after_attempt(settings.max_retries), wait=wait_exponential(multiplier=settings.retry_backoff_factor))
    def invoke_model(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Invoke Bedrock model with messages and optional tools
        
        Args:
            messages: List of message dictionaries
            system_prompt: System prompt for the model
            tools: Optional list of tool definitions
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Response from Bedrock API
        """
        temperature = temperature or settings.agent_temperature
        max_tokens = max_tokens or settings.bedrock_max_tokens
        
        # Check if using Meta Llama model
        if "llama" in self.model_id.lower():
            # Meta Llama model format - requires prompt as a single string
            llama_max_tokens = min(max_tokens, 2048)  # Llama has lower limits
            
            # Build simple prompt format
            prompt_text = ""
            if system_prompt:
                prompt_text += f"System: {system_prompt}\n\n"
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role.lower() == "user":
                    prompt_text += f"User: {content}\n"
                else:
                    prompt_text += f"Assistant: {content}\n"
            
            prompt_text += "Assistant:"
            
            request_body = {
                "prompt": prompt_text,
                "temperature": temperature,
                "max_gen_len": llama_max_tokens,
                "top_p": settings.agent_top_p,
            }
        # Check if using Nova model
        elif "nova" in self.model_id.lower():
            # Nova model format - uses maxTokens (camelCase) and maxTokens must be reasonable
            # Nova has lower max limits, cap at 4096
            nova_max_tokens = min(max_tokens, 4096)
            
            nova_messages = []
            for msg in messages:
                nova_msg = {
                    "role": msg.get("role", "user"),
                    "content": [{"text": msg.get("content", "")}]
                }
                nova_messages.append(nova_msg)
            
            request_body = {
                "messages": nova_messages,
                "inferenceConfig": {
                    "maxTokens": nova_max_tokens,
                    "temperature": temperature,
                },
            }
            if system_prompt:
                request_body["system"] = [{"text": system_prompt}]
        else:
            # Claude model format (default)
            request_body = {
                "anthropic_version": "bedrock-2023-06-01",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }
            if system_prompt:
                request_body["system"] = system_prompt
            if tools:
                request_body["tools"] = tools
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
            )
            
            result = json.loads(response["body"].read())
            log.debug(f"Bedrock raw response keys: {list(result.keys()) if isinstance(result, dict) else 'not dict'}")
            log.debug(f"Bedrock response: {result}")
            return result
            
        except Exception as e:
            log.error(f"Error invoking Bedrock model: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(settings.max_retries), wait=wait_exponential(multiplier=settings.retry_backoff_factor))
    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings from Bedrock Titan embeddings model
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        request_body = {
            "inputText": text,
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.embedding_model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
            
            result = json.loads(response["body"].read())
            embedding = result.get("embedding", [])
            
            log.debug(f"Generated embedding of dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            log.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def create_agent(self, agent_name: str, agent_description: str, tools: List[Dict[str, Any]]) -> str:
        """
        Create a Bedrock Agent
        
        Args:
            agent_name: Name of the agent
            agent_description: Description of agent
            tools: List of tool definitions
            
        Returns:
            Agent ID
        """
        agents_client = boto3.client(
            "bedrock-agent",
            region_name=settings.aws_region,
        )
        
        try:
            response = agents_client.create_agent(
                agentName=agent_name,
                agentRoleArn=f"arn:aws:iam::ACCOUNT_ID:role/BedrockAgentRole",  # Replace with actual ARN
                description=agent_description,
                idleSessionTTLInSeconds=900,
            )
            
            agent_id = response["agent"]["agentId"]
            log.info(f"Created Bedrock Agent: {agent_id}")
            return agent_id
            
        except Exception as e:
            log.error(f"Error creating Bedrock Agent: {str(e)}")
            raise


# Global Bedrock client instance
bedrock_client = None


def get_bedrock_client() -> BedrockClient:
    """Get or create global Bedrock client"""
    global bedrock_client
    if bedrock_client is None:
        bedrock_client = BedrockClient()
    return bedrock_client
