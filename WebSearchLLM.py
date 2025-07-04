import os
from dotenv import load_dotenv
import json
from openai import AsyncOpenAI
import time
import asyncio
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

client_openai = AsyncOpenAI(api_key= os.getenv("OPENAI_API_KEY"))

# Retry decorator with exponential backoff for async functions
def async_retry_with_exponential_backoff(
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 5,
    retry_status_codes: tuple = (429, 500, 502),
):
    """Retry an async function with exponential backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay
            
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Check if it's a status code error we should retry
                    status_code = getattr(e, "status_code", None)
                    if status_code in retry_status_codes and num_retries < max_retries:
                        num_retries += 1
                        retry_after = getattr(e, "headers", {}).get("retry-after")
                        
                        if retry_after and retry_after.isdigit():
                            # Use the retry-after header value if available
                            delay = float(retry_after)
                        else:
                            # Calculate backoff with jitter
                            delay = exponential_base ** num_retries * initial_delay
                            if jitter:
                                delay *= (1 + random.random())
                        
                        logger.warning(
                            f"Rate limit or server error ({status_code}) hit. Retrying in {delay:.2f} seconds. "
                            f"Retry {num_retries}/{max_retries}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        # Either not a retryable error or max retries exceeded
                        logger.error(f"API request failed: {str(e)}")
                        raise
        return wrapper
    return decorator

async def llm_contact_search(business_info):
    structured_result = await openai_completion_with_backoff(business_info)
    json_result = json.loads(structured_result)
    return json_result
    
@async_retry_with_exponential_backoff()
async def openai_completion_with_backoff(prompt):
    response = await client_openai.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
            "role": "system",
            "content": [
                {
                "type": "input_text",
                "text": "You are a web search agent. You will be given a business name or  business address or business web page and you have to return contact numbers of the business by searching web. You have to provide 100% accurate information. (If you find multiple contact numbers, list them all)"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "input_text",
                "text": prompt
                }
            ]
            }
        ],
        text={
            "format": {
            "type": "json_schema",
            "name": "business_info",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                "business_name": {
                    "type": "string",
                    "description": "The name of the business."
                },
                "business_address": {
                    "type": "string",
                    "description": "The address where the business is located."
                },
                "contact_numbers": {
                    "type": "array",
                    "description": "A list of contact numbers for the business.",
                    "items": {
                    "type": "string",
                    "description": "A single contact number for the business."
                    }
                },
                "search_resources": {
                    "type": "string",
                    "description": "Resources available for searching related business information."
                }
                },
                "required": [
                "business_name",
                "business_address",
                "contact_numbers",
                "search_resources"
                ],
                "additionalProperties": False
            }
            }
        },
        reasoning={},
        tools=[
            {
            "type": "web_search_preview",
            "search_context_size": "high",
            "user_location": {
                "type": "approximate",
                # "city": null,
                "country": "US",
                # "region": null,
                # "timezone": null
            }
            }
        ],
        tool_choice="required",
        temperature=1,
        max_output_tokens=2048,
        top_p=1,
        store=True,
        background=True,
        )
    
    print(f"Initial status: {response.status}")
    
    while response.status in {"queued", "in_progress"}:
        await asyncio.sleep(2)
        response = await client_openai.responses.retrieve(response.id)
        
    if response.status == "completed":
        return response.output[1].content[0].text
    else:
        error_msg = f"Request failed with status: {response.status}"
        if hasattr(response, 'error'):
            error_msg += f" - Error: {response.error}"
        # raise Exception(error_msg)
        print(error_msg)
        return {"business_name": "", "business_address": "", "contact_numbers": [], "search_resources": ""}
    





