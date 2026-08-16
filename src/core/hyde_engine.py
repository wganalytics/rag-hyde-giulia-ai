import os
from typing import Optional
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from shared.infra.lib.observatory import MetricsTracker, track_step

from .llm_factory import get_llm, resolve_model, resolve_provider

load_dotenv()

class HyDEEngine:
    """
    Motor responsável por gerar documentos hipotéticos (ideal answers) 
    para expandir a semântica da busca.
    """
    def __init__(self, model_name: str = None, tracker: Optional[MetricsTracker] = None,
                 provider: str = None):
        self.tracker = tracker
        # provider/modelo vêm da fábrica: sem argumento, usa LLM_PROVIDER do .env.
        self.provider = resolve_provider(provider)
        self.model_name = resolve_model(self.provider, model_name)
        self.llm = get_llm(self.provider, self.model_name, temperature=0.0)
        
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
