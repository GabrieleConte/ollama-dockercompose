from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.ollama import Ollama as LlamaOllama
from llama_index.core.llms.function_calling import FunctionCallingLLM
from collections.abc import AsyncGenerator
import debugpy


app = FastAPI()
# Allow all origins for CORS (you can customize this based on your requirements)
origins = ["*"]

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


async def run_llm(question: str, llm: FunctionCallingLLM) -> AsyncGenerator:
    response_iter = llm.stream_complete(question)
    for response in response_iter:
        yield response.delta


@app.post("/chat")
async def chat(message: str):
    llm = LlamaOllama(
        base_url="http://host.docker.internal:7869",
        model="llama3.1",
        context_window=8000,
        request_timeout=360,
    )
    # message = ChatMessage(content=message)
    return StreamingResponse(run_llm(message, llm), media_type="text/event-stream")
