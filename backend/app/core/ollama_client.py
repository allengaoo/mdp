"""
Ollama LLM Client for Chat2App Module.
MDP Platform V3.1

Communicates with local Ollama instance running Llama 3.
"""

import json
from typing import List, Dict, Any, Optional
import httpx
from loguru import logger

from app.core.config import settings


class OllamaServiceUnavailable(Exception):
    """Raised when Ollama service is not accessible."""
    pass


class OllamaClient:
    """Client for communicating with local Ollama LLM."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.temperature = settings.ollama_temperature
    
    async def health_check(self) -> bool:
        """Check if Ollama service is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response from Ollama Llama 3.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            json_mode: If True, force JSON output format
            
        Returns:
            Parsed response from LLM
        """
        # Build request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            }
        }
        
        # Enable JSON mode for Llama 3
        if json_mode:
            payload["format"] = "json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling Ollama API: {self.base_url}/api/chat")
                logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)[:500]}...")
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    raise OllamaServiceUnavailable(
                        f"Ollama returned status {response.status_code}"
                    )
                
                result = response.json()
                
                # Extract content from response
                content = result.get("message", {}).get("content", "")
                
                # Parse JSON if json_mode is enabled
                if json_mode and content:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON response: {e}")
                        return {"raw_content": content, "parse_error": str(e)}
                
                return {"raw_content": content}
                
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama service")
            raise OllamaServiceUnavailable(
                "Please ensure Ollama is running on port 11434. "
                "Start it with: ollama serve"
            )
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise OllamaServiceUnavailable(
                f"Ollama request timed out after {self.timeout} seconds. "
                "The model might be loading or the query is too complex."
            )


# Singleton instance
ollama_client = OllamaClient()
