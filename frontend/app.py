import streamlit as st
import sys
import os
import json
from pathlib import Path

# Configurar path para módulos internos e INFRA
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(Path(__file__).parent.parent))

from src.core.hyde_engine import HyDEEngine
from src.core.hyde_retriever import HyDERetriever
from shared.infra.lib.observatory import MetricsTracker

st.set_page_config(page_title="GARE | PRJ-08 HyDE RAG", layout="wide")

# Inicializar Tracker e Motores
tracker = MetricsTracker()
from seletor_llm import selecionar_motor  # mesma pasta do app (Streamlit poe no path)
_provider, _modelo = selecionar_motor()

hyde_engine = HyDEEngine(model_name=_modelo, tracker=tracker, provider=_provider)
retriever = HyDERetriever(tracker=tracker)

st.title("🛡️ GIULIA AI | HyDE RAG: Tradutor de Intenção")
st.markdown("""
Esta interface demonstra o uso de **Hypothetical Document Embeddings**. 
O sistema gera uma resposta 'ideal' fictícia para sua pergunta e a usa para buscar documentos reais.
""")

with st.sidebar:
    st.header("⚙️ Configurações")
    # O modelo agora vem do seletor de motor no topo da barra lateral,
    # que lista os modelos realmente instalados no Ollama. A lista fixa
    # que existia aqui oferecia llama3.1:8b, que nem estava instalado.
    k_results = st.slider("Resultados (K)", 1, 5, 3)
    
    st.divider()
    st.header("💾 Ingestão de Teste")
    demo_text = st.text_area("Texto para Ingerir", 
        "A Norma ISO 14001 define requisitos para um Sistema de Gestão Ambiental (SGA). "
        "A alta direção deve demonstrar liderança e comprometimento. "
        "O planejamento deve incluir riscos e oportunidades. "
        "A organização deve estabelecer, implementar e manter os processos necessários para atender aos requisitos ambientais."
    )
    if st.button("Ingerir Dados"):
        with st.spinner("Indexando..."):
            retriever.ingest([demo_text])
            st.success("Dados indexados!")

# Main UI
query = st.text_input("Sua Pergunta:", placeholder="Ex: O que a alta direção deve fazer?")

if query:
    tab1, tab2 = st.tabs(["🔍 Busca HyDE", "📊 Observabilidade"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 1. Geração Hipotética")
            with st.spinner("Gerando documento ideal..."):
                hypothetical_doc = hyde_engine.generate_document(query)
                st.info(hypothetical_doc)
        
        with col2:
            st.subheader("📄 2. Documentos Recuperados")
            with st.spinner("Buscando no VectorDB..."):
                results = retriever.retrieve(hypothetical_doc, k=k_results)
                if results:
                    for i, doc in enumerate(results):
                        st.markdown(f"**Resultado {i+1}:**")
                        st.write(doc.page_content)
                else:
                    st.warning("Nenhum documento encontrado.")

    with tab2:
        st.subheader("⏱️ Telemetria em Tempo Real")
        metrics = tracker.get_current_metrics()
        
        if metrics:
            cols = st.columns(len(metrics))
            for i, (step, time) in enumerate(metrics.items()):
                cols[i].metric(step.replace("_", " ").title(), f"{time:.3f}s")
        
        st.divider()
        st.subheader("📜 Histórico de Performance")
        if os.path.exists(tracker.log_path):
            with open(tracker.log_path, 'r') as f:
                log_data = [json.loads(line) for line in f]
                st.json(log_data[-5:]) # Mostrar os últimos 5 logs
