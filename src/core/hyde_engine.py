import os
from typing import Optional
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from INFRA.lib.observatory import MetricsTracker, track_step

load_dotenv()

class HyDEEngine:
    """
    Motor responsável por gerar documentos hipotéticos (ideal answers) 
    para expandir a semântica da busca.
    """
    def __init__(self, model_name: str = None, tracker: Optional[MetricsTracker] = None):
        self.tracker = tracker
        self.model_name = model_name or os.getenv("HYDE_MODEL_NAME", "llama3.2:3b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = ChatOllama(
            model=self.model_name,
            base_url=base_url,
            temperature=0.0
        )
        
        # Prompt para geração do documento hipotético
        self.hyde_prompt = ChatPromptTemplate.from_template(
            "Você é um especialista técnico. Por favor, escreva um parágrafo que responda "
            "diretamente e detalhadamente à pergunta abaixo. Escreva como se estivesse "
            "retirando este parágrafo de um manual técnico oficial ou artigo especializado.\n\n"
            "Pergunta: {question}\n\n"
            "Resposta Ideal Hipotética:"
        )
        
        self.chain = self.hyde_prompt | self.llm | StrOutputParser()

    @track_step("generate_hypothetical_document")
    def generate_document(self, query: str) -> str:
        """Gera o documento hipotético baseado na query do usuário."""
        return self.chain.invoke({"question": query})
