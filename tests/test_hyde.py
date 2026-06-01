import sys
import os
from pathlib import Path

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(Path(__file__).parent.parent))

from src.core.hyde_engine import HyDEEngine
from src.core.hyde_retriever import HyDERetriever

def test_hyde_pipeline():
    print("🚀 Iniciando teste do pipeline HyDE...")
    
    # 1. Setup
    engine = HyDEEngine()
    retriever = HyDERetriever()
    
    # 2. Ingestão de dados de teste
    test_texts = [
        "A política ambiental deve ser comunicada a todos os colaboradores.",
        "O escopo do sistema de gestão ambiental deve estar disponível como informação documentada.",
        "A organização deve determinar as competências necessárias das pessoas que realizam trabalho sob seu controle."
    ]
    retriever.ingest(test_texts)
    print("✅ Dados de teste ingeridos.")
    
    # 3. Geração de Documento Hipotético
    query = "Onde o escopo deve ficar?"
    print(f"❓ Query: {query}")
    
    hypothetical_doc = engine.generate_document(query)
    print(f"🧠 Doc Hipotético: {hypothetical_doc[:100]}...")
    
    assert len(hypothetical_doc) > 20
    print("✅ Documento hipotético gerado com sucesso.")
    
    # 4. Recuperação
    results = retriever.retrieve(hypothetical_doc, k=1)
    assert len(results) > 0
    print(f"📄 Resultado Recuperado: {results[0].page_content}")
    assert "escopo" in results[0].page_content.lower()
    print("✅ Recuperação HyDE validada.")

if __name__ == "__main__":
    try:
        test_hyde_pipeline()
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        sys.exit(1)
