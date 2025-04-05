FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install fastapi uvicorn transformers torch
# Copy the application code
COPY app ./app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]