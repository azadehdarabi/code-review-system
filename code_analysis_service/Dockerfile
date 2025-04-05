FROM python:3.9-slim

WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app ./app

# Ensure git is available
ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

# Create directory for repo storage
RUN mkdir -p /tmp/repos

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
