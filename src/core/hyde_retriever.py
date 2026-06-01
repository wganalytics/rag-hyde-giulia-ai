import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from INFRA.lib.observatory import MetricsTracker, track_step

load_dotenv()

class HyDERetriever:
    """
    Retriever que utiliza vetores de documentos hipotéticos para busca semântica.
    """
    def __init__(self, tracker: Optional[MetricsTracker] = None):
        self.tracker = tracker
        self.embedding_model = OllamaEmbeddings(
            model=os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text:latest"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        
        persist_directory = os.path.join(os.path.dirname(__file__), "../../data/vector_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding_model,
            collection_name="hyde_collection"
        )

    def ingest(self, texts: List[str]):
        """Ingere documentos na base."""
        self.vector_db.add_texts(texts)

    @track_step("retrieve_hyde")
    def retrieve(self, hypothetical_doc: str, k: int = 3) -> List[Document]:
        """Realiza a busca usando o embedding do documento hipotético."""
        return self.vector_db.similarity_search(hypothetical_doc, k=k)
    
    @track_step("retrieve_standard")
    def retrieve_standard(self, query: str, k: int = 3) -> List[Document]:
        """Busca padrão (para comparação)."""
        return self.vector_db.similarity_search(query, k=k)
