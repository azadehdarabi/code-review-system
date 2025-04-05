import json
import re
from abc import ABC, abstractmethod
from typing import List
import openai
import httpx
import logging
from .config import Settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def analyze_code(self, code: str) -> List[str]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            logger.error("OpenAI API key is not set")
            raise ValueError("OpenAI API key is not set")
        logger.info("Initializing OpenAI provider")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def analyze_code(self, code: str) -> List[str]:
        try:
            logger.info("Sending request to OpenAI API")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a code review expert. Analyze the given Python function and provide a list of suggestions for improvement."},
                    {"role": "user", "content": f"Please review this Python function:\n\n{code}"}
                ]
            )
            logger.info("Successfully received response from OpenAI API")
            suggestions = response.choices[0].message.content.split("\n")
            return [s.strip("- ") for s in suggestions if s.strip()]
        except openai.APIConnectionError as e:
            logger.error(f"Connection error to OpenAI API: {str(e)}")
            raise Exception(f"Failed to connect to OpenAI API: {str(e)}")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Error analyzing code: {str(e)}")


class DeepseekProvider(LLMProvider):
    def __init__(self, settings: Settings):
        if not settings.deepseek_api_key:
            logger.error("Deepseek API key is not set")
            raise ValueError("Deepseek API key is not set")
        logger.info("Initializing Deepseek provider")
        self.api_key = settings.deepseek_api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    async def analyze_code(self, code: str) -> List[str]:
        try:
            logger.info("Sending request to Deepseek API")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system",
                             "content": "You are a code review expert. Analyze the given Python function and provide a list of suggestions for improvement."},
                            {"role": "user", "content": f"Please review this Python function:\n\n{code}"}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )

                if response.status_code != 200:
                    error_msg = f"Deepseek API error: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                logger.info("Successfully received response from Deepseek API")
                result = response.json()
                suggestions = result["choices"][0]["message"]["content"].split("\n")
                return [s.strip("- ") for s in suggestions if s.strip()]

        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with Deepseek API: {str(e)}")
            raise Exception(f"Failed to connect to Deepseek API: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Deepseek provider: {str(e)}")
            raise Exception(f"Deepseek API error: {str(e)}")


class LocalProvider(LLMProvider):
    def __init__(self, settings: Settings):
        logger.info("Initializing Local LLM provider")
        self.base_url = settings.local_model_url

    async def analyze_code(self, code: str) -> List[str]:
        try:
            logger.info("Sending request to Local LLM")
            prompt = f"""You are an AI code reviewer specializing in Python. Your task is to analyze the given function and provide constructive feedback.

            ### Instructions:
            - Identify code quality improvements (e.g., readability, maintainability, efficiency).
            - Check for best practices (e.g., type hints, docstrings, meaningful variable names).
            - Highlight potential bugs or logical errors.
            
            ### Input Function:
            ```python
            {code}
            ```
            """

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={
                        "prompt": prompt
                    }
                )

                if response.status_code != 200:
                    error_msg = f"Local LLM error: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                logger.info("Successfully received response from Local LLM")
                result = response.json()
                logger.info(f"Raw LLM response: {result}")  # Log the full response

                if "generated_text" not in result:
                    logger.error("Missing 'generated_text' in LLM response")
                    raise Exception("Invalid LLM response format")

                text = result["generated_text"]

                if not isinstance(text, str):
                    logger.error(f"Expected string response, got: {type(text)}")
                    raise Exception("Unexpected response format from LLM")

                cleaned_text = ' '.join(text.split())

                # Try to parse the cleaned text as JSON if it's in JSON format
                try:
                    import json
                    json_data = json.loads(cleaned_text)
                    if "suggestions" in json_data:
                        suggestions = json_data["suggestions"]
                    else:
                        suggestions = [cleaned_text]
                except json.JSONDecodeError:
                    suggestions = [cleaned_text]

                logger.info(f"Parsed suggestions: {suggestions}")
                return suggestions
        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with Local LLM: {str(e)}")
            raise Exception(f"Failed to connect to Local LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Local LLM provider: {str(e)}")
            raise Exception(f"Local LLM error: {str(e)}")
