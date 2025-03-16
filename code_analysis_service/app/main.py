from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .tasks import clone_repository
from .code_analyzer import analyze_function
from .config import Settings

app = FastAPI(title="Code Analysis Service", description="Code Analysis Service for Code Review System")
settings = Settings()

class AnalyzeStartRequest(BaseModel):
    repo_url: str

class AnalyzeStartResponse(BaseModel):
    job_id: str

class AnalyzeFunctionRequest(BaseModel):
    job_id: str
    function_name: str

class AnalyzeFunctionResponse(BaseModel):
    suggestions: list[str]

@app.post("/analyze/start", response_model=AnalyzeStartResponse)
async def start_analysis(request: AnalyzeStartRequest) -> AnalyzeStartResponse:
    try:
        # Start background task to clone repository
        job_id = clone_repository.delay(request.repo_url)
        return AnalyzeStartResponse(job_id=str(job_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/function", response_model=AnalyzeFunctionResponse)
async def analyze_function_endpoint(request: AnalyzeFunctionRequest) -> AnalyzeFunctionResponse:
    try:
        suggestions = await analyze_function(request.job_id, request.function_name)
        return AnalyzeFunctionResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 