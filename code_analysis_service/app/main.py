import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
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
    suggestions: List[str]


@app.post("/analyze/start", response_model=AnalyzeStartResponse)
async def start_analysis(request: AnalyzeStartRequest) -> AnalyzeStartResponse:
    try:
        # Start background task to clone repository
        task = clone_repository.delay(request.repo_url)
        return AnalyzeStartResponse(job_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/function", response_model=AnalyzeFunctionResponse)
async def analyze_function_endpoint(request: AnalyzeFunctionRequest) -> AnalyzeFunctionResponse:
    try:
        job_id = request.job_id
        repo_path = os.path.join(settings.repo_storage_path, job_id)

        # Debugging output
        print(f"Checking repository at: {repo_path}")
        print(f"Exists: {os.path.exists(repo_path)}, Contents: {os.listdir(repo_path) if os.path.exists(repo_path) else 'N/A'}")

        if not os.path.exists(repo_path) or not os.listdir(repo_path):
            raise Exception(f"Repository {job_id} is still being cloned or failed.")

        suggestions = await analyze_function(job_id, request.function_name)
        return AnalyzeFunctionResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
