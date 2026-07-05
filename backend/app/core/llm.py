"""LLM integration using Pollinations AI keyless API."""

import httpx
import json
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger()

async def generate_text(messages: List[Dict[str, str]], system_prompt: str = None) -> str:
    """Generate text using the open-source Llama model via Pollinations AI."""
    url = "https://text.pollinations.ai/"
    
    formatted_messages = []
    if system_prompt:
        formatted_messages.append({"role": "system", "content": system_prompt})
    
    formatted_messages.extend(messages)
    
    payload = {
        "messages": formatted_messages,
        "model": "openai"  # Maps to a high-quality model on Pollinations
    }
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, timeout=45.0)
            if r.status_code == 200:
                result = r.text.strip()
                if result:
                    return result
                logger.warning("llm_empty_response", status_code=r.status_code)
                return ""
            else:
                logger.error("llm_generation_failed", status_code=r.status_code, body=r.text[:200])
                return ""
    except httpx.TimeoutException:
        logger.warning("llm_timeout", url=url)
        return ""
    except httpx.ConnectError as e:
        logger.error("llm_connection_error", error=str(e))
        return ""
    except Exception as e:
        logger.error("llm_generation_error", error=str(e))
        return ""
