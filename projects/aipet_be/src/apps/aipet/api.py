from ninja import Router
from ninja.errors import HttpError
from typing import Optional

from .dependencies import get_openrouter_client

router = Router(
    tags=["Aipet"],
)


@router.get("/action")
async def get_aipet(request):
    return {"message": "Hello, World!"}


@router.post("/chat")
async def chat_with_llm(
    request,
    prompt: str,
    system_message: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
):
    """
    Chat with an LLM using OpenRouter.
    
    Args:
        prompt: The user's prompt
        system_message: Optional system message to set context
        model: Model to use (defaults to configured default)
        temperature: Controls randomness (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
    """
    try:
        client = get_openrouter_client()
        response = await client.simple_chat(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {"response": response}
    except Exception as e:
        raise HttpError(500, f"Error communicating with LLM: {str(e)}")


@router.post("/chat/completion")
async def chat_completion(
    request,
    messages: list[str],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False
):
    """
    Make a full chat completion request to OpenRouter.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model to use (defaults to configured default)
        temperature: Controls randomness (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
    """
    try:
        client = get_openrouter_client()
        response = await client.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        return response
    except Exception as e:
        raise HttpError(500, f"Error communicating with LLM: {str(e)}")


@router.get("/models")
async def get_available_models(request):
    """
    Get available models from OpenRouter.
    """
    try:
        client = get_openrouter_client()
        models = await client.get_models()
        return {"models": models}
    except Exception as e:
        raise HttpError(500, f"Error fetching models: {str(e)}")
