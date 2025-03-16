# Code Review System

A microservice-based code review system that analyzes Python functions from GitHub repositories using LLMs.

## Architecture

The system consists of three main services:

1. **Local LLM Service**
   - Runs TinyLlama, a lightweight but capable language model
   - Provides code analysis capabilities without cloud dependencies
   - Runs completely locally with no API keys needed

2. **LLM Gateway Service**
   - Provides a unified interface to different LLM providers
   - Can switch between local LLM, OpenAI, or Deepseek
   - Exposes an API for code analysis

3. **Code Analysis Service**
   - Handles GitHub repository processing
   - Manages background jobs for repo downloads
   - Extracts and analyzes Python functions
   - Communicates with the LLM Gateway for analysis

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher (for local development)
- At least 4GB of RAM for running the local LLM
- Git (for cloning repositories)

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd code-review-system
   ```

2. Create Python virtual environment (optional, for local development):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   # For LLM Service
   cd llm_service
   pip install -r requirements.txt

   # For Code Analysis Service
   cd ../code_analysis_service
   pip install -r requirements.txt
   ```

4. Build and start the services:
   ```bash
   docker-compose up --build
   ```

## API Usage

### LLM Gateway Service (port 8000)

Analyze a Python function:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "function_code": "def add(a, b): return a + b"
  }'
```

Example response:
```json
{
  "suggestions": [
    "Add type hints for parameters a and b",
    "Add a docstring describing the function's purpose",
    "Consider adding parameter validation"
  ]
}
```

### Code Analysis Service (port 8001)

1. Start repository analysis:
```bash
curl -X POST http://localhost:8001/analyze/start \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/example/repo"
  }'
```

2. Analyze a specific function:
```bash
curl -X POST http://localhost:8001/analyze/function \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "abc123",
    "function_name": "module_name.add"
  }'
```

## Development

1. Run tests:
   ```bash
   cd llm_service
   pytest

   cd ../code_analysis_service
   pytest
   ```

2. Run style checks:
   ```bash
   pylint app
   mypy app
   black app --check
   ```

## Technology Choices

- **FastAPI**: Modern, fast web framework for building APIs
- **TinyLlama**: Lightweight local LLM for code analysis
- **Celery**: Distributed task queue for handling background jobs
- **Redis**: Message broker for Celery and job status storage
- **Docker**: Containerization and service orchestration
- **Pydantic**: Data validation using Python type annotations

## Design Decisions

1. **Local LLM**: 
   - Eliminates dependency on external API providers
   - No API keys or usage costs
   - Complete privacy of code analysis
   - Predictable performance and availability

2. **Microservice Architecture**:
   - Separates concerns and allows independent scaling
   - Each service can be developed and deployed independently
   - Easy to switch between different LLM providers

3. **Background Processing**:
   - Asynchronous repository processing for better user experience
   - Uses Celery for reliable task queue management
   - Redis for efficient message brokering

4. **Docker Compose**:
   - Simple deployment and development setup
   - Consistent environment across development and production
   - Easy to scale individual services

5. **Environment-based Configuration**:
   - Easy configuration management across environments
   - Flexible LLM provider switching

## Error Handling

The system implements comprehensive error handling:
- Invalid repository URLs
- Non-existent Python functions
- LLM service failures
- Network issues
- Invalid input validation

## Future Improvements

1. Add authentication and rate limiting
2. Implement caching for analyzed functions
3. Add support for more programming languages
4. Implement retry mechanisms for failed API calls
5. Add monitoring and logging infrastructure
6. Support for larger language models
7. GPU acceleration for local LLM 