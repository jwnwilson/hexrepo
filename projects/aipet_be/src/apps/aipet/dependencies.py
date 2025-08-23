from functools import lru_cache

from adaptor.http import OpenRouterClient


@lru_cache()
def get_openrouter_client() -> OpenRouterClient:
    """
    Dependency function to get an OpenRouter client instance.

    Returns:
        OpenRouterClient instance
    """
    return OpenRouterClient()
