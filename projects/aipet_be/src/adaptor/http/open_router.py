import json
import logging
from typing import Any, Dict, List, Optional, Union

import httpx
from ninja.errors import HttpError

from config import config

logger = logging.getLogger(__name__)


class OpenRouterMessage:
    """Represents a message in the OpenRouter API format."""
    
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class OpenRouterClient:
    """Client for making calls to the OpenRouter API."""
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.default_model = config.OPENROUTER_DEFAULT_MODEL
        self.timeout = config.OPENROUTER_TIMEOUT
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aipet.com",  # Replace with your actual domain
            "X-Title": "AIPet Backend"
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the OpenRouter API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to httpx request
        
        Returns:
            API response as a dictionary
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            raise HttpError(e.response.status_code, f"OpenRouter API error: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HttpError(500, f"Request error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HttpError(500, f"Unexpected error: {e}")
    
    async def chat_completion(
        self,
        messages: List[Union[OpenRouterMessage, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to OpenRouter.
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (defaults to OPENROUTER_DEFAULT_MODEL)
            temperature: Controls randomness (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            API response as a dictionary
        """
        if not messages:
            raise ValueError("At least one message is required")
        
        # Convert messages to the correct format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, OpenRouterMessage):
                formatted_messages.append(msg.to_dict())
            elif isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                raise ValueError(f"Invalid message format: {type(msg)}")
        
        payload = {
            "model": model or self.default_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        return await self._make_request("POST", "/chat/completions", json=payload)
    
    async def simple_chat(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simplified chat method for single prompt responses.
        
        Args:
            prompt: The user's prompt
            system_message: Optional system message
            model: Model to use
            temperature: Controls randomness
            max_tokens: Maximum tokens to generate
        
        Returns:
            The generated response text
        """
        messages = []
        
        if system_message:
            messages.append(OpenRouterMessage("system", system_message))
        
        messages.append(OpenRouterMessage("user", prompt))
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from OpenRouter.
        
        Returns:
            List of available models
        """
        data = await self._make_request("GET", "/models")
        return data.get("data", []) 