from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.ollama import Ollama as LlamaOllama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core import Settings,load_index_from_storage
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient
from collections.abc import AsyncGenerator
from pydantic import BaseModel
from fastapi import UploadFile, File
import os
import tempfile

# creates a persistant index to disk
client = QdrantClient(url="http://qdrant", port=6333)
aclient = AsyncQdrantClient(url="http://qdrant", port=6333)

# create our vector store with hybrid indexing enabled
# batch_size controls how many nodes are encoded with sparse vectors at once
vector_store = QdrantVectorStore(
    "llama2_paper",
    client=client,
    aclient=aclient,
    enable_hybrid=True,
    batch_size=20,
)
data_dir = os.path.join(os.path.dirname(__file__), "data")
storage_dir = os.path.join(data_dir,"storage")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(data_dir,"storage"),exist_ok=True)
if os.path.exists(os.path.join(data_dir,"storage","index_store.json")):
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir,vector_store=vector_store)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Define the expected request body structure
class MessageRequest(BaseModel):
    message: str


llm = LlamaOllama(
    base_url="http://ollama:11434",
    model="llama3.2:3b",
    context_window=8000,
    request_timeout=360,
)


embedding = OllamaEmbedding(
    base_url="http://ollama:11434",
    model_name="nomic-embed-text",
    request_timeout=360,
)

Settings.llm=llm
Settings.embed_model=embedding
Settings.chunk_size=512


app = FastAPI()
# Allow all origins for CORS (you can customize this based on your requirements)
origins = ["frontend,ollama,qdrant"]

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

    # yield str(len(embedding.get_text_embedding(question)))


@app.post("/chat")
async def chat(request: MessageRequest):
    index = load_index_from_storage(storage_context=storage_context, index_id="vector_id",store_nodes_override=True)
    query_engine = index.as_query_engine(similarity_top_k=2, sparse_top_k=12, vector_store_query_mode="hybrid")
    response = await query_engine.aquery(request.message)
    return {"response": response}
    


@app.post("/index_pdf/")
async def index_pdf(file: UploadFile = File(...)):
    # Create the data directory if it doesn't exist

    # Create a temporary file in the data directory
    with tempfile.NamedTemporaryFile(
        delete=True, dir=data_dir, suffix=".pdf"
    ) as temp_file:
        temp_file.name=file.filename
        temp_file.write(await file.read())
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            store_nodes_override=True
        )
        index.set_index_id("vector_id")
        index.storage_context.persist(storage_dir)
    temp_file.close()
    
    
    