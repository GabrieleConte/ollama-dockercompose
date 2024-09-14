from llama_index.core import VectorStoreIndex, Document
from llama_index.readers.file import UnstructuredReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core
class Rag:
    
    def __init__(self,llm,  embedding,documents:list[Document]) -> None:
        