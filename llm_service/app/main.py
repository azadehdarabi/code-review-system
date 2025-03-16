from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import logging
from dotenv import load_dotenv
from .services import LLMProvider, OpenAIProvider, DeepseekProvider, LocalProvider
from .config import Settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
settings = Settings()

# Log environment setup
logger.info(f"LLM_PROVIDER set to: {os.getenv('LLM_PROVIDER', 'openai')}")
logger.info("OpenAI API key is set" if settings.openai_api_key else "OpenAI API key is NOT set")

app = FastAPI(title="LLM Service", description="AI Gateway for Code Review System")

class FunctionAnalysisRequest(BaseModel):
    function_code: str

class AnalysisSuggestion(BaseModel):
    suggestions: List[str]

def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    logger.info(f"Using LLM provider: {provider}")
    if provider == "openai":
        return OpenAIProvider(settings)
    elif provider == "deepseek":
        return DeepseekProvider(settings)
    elif provider == "local":
        return LocalProvider(settings)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

@app.post("/analyze", response_model=AnalysisSuggestion)
async def analyze_function(request: FunctionAnalysisRequest) -> AnalysisSuggestion:
    try:
        logger.info("Received analyze request")
        provider = get_llm_provider()
        suggestions = await provider.analyze_code(request.function_code)
        logger.info("Successfully analyzed code")
        return AnalysisSuggestion(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Error in analyze_function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 