from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.ollama import Ollama as LlamaOllama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms.function_calling import FunctionCallingLLM
from collections.abc import AsyncGenerator
from pydantic import BaseModel

# Define the expected request body structure
class MessageRequest(BaseModel):
    message: str
    
llm= LlamaOllama(
    base_url="http://ollama:11434",
    model="llama3.2:3b",
    context_window=16000,
    request_timeout=360,
)

embedding = OllamaEmbedding(
    base_url="http://ollama:11434",
    model_name="nomic-embed-text",
    request_timeout=360,
)


app = FastAPI()
# Allow all origins for CORS (you can customize this based on your requirements)
origins = ["frontend,ollama"]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# debugpy.listen(("0.0.0.0", 5678))
 

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Read the content of your HTML file
    with open("./src/index.html", "r") as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)


async def run_llm(question: str) -> AsyncGenerator:
    response_iter = llm.stream_complete(question)
    for response in response_iter:
        yield response.delta
        
    #yield str(len(embedding.get_text_embedding(question)))


@app.post("/chat")
async def chat(request: MessageRequest):
    
    message = request.message
    # message = ChatMessage(content=message)
    return StreamingResponse(run_llm(message), media_type="text/event-stream")



