from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()


# Define a Pydantic model for the request body
class GenerateRequest(BaseModel):
    prompt: str


# Load the GPT2 model
generator = pipeline("text-generation", model="gpt2")


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    output = generator(request.prompt, max_new_tokens=50, num_return_sequences=1)
    return {"generated_text": output[0]["generated_text"]}
