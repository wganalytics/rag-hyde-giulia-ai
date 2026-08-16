"""Seletor de motor de LLM compartilhado pelas telas do ecossistema."""

# ── Seletor de motor de LLM (gerado pelo padrão do ecossistema) ────────────
import streamlit as _st
from src.core.llm_factory import (
    PROVIDERS as _PROVIDERS, PROVIDER_LABELS as _LABELS,
    LLMConfigError as _LLMErro, probe_provider as _probe,
    modelos_ollama as _modelos_locais, resolve_model as _resolve_model,
    resolve_provider as _resolve_provider,
)

_SUGESTOES = {
    "sem_credito": "Adicione crédito no painel do provider — a chave está correta.",
    "chave_invalida": "Gere uma nova chave e atualize o .env.",
    "limite_taxa": "Aguarde um pouco antes de tentar de novo.",
    "modelo_inexistente": "Confira o nome do modelo no .env.",
}


def _icone(s):
    if not s.available:
        return "⛔"
    return {True: "✅", False: "⛔"}.get(s.verified, "⚙️")


@_st.cache_resource(show_spinner="Testando os motores de LLM...")
def _motores():
    """Testa cada provider uma vez por processo, para o seletor já oferecer
    somente o que responde."""
    out = []
    for nome in _PROVIDERS:
        try:
            out.append(_probe(nome))
        except _LLMErro:
            pass
    return out


def selecionar_motor(sidebar=True):
    """Desenha o seletor e devolve (provider, modelo)."""
    alvo = _st.sidebar if sidebar else _st
    status = {s.provider: s for s in _motores()}
    funcionais = [p for p, s in status.items() if s.verified is True]
    quebrados = [p for p, s in status.items() if s.verified is not True]

    mostrar_todos = alvo.checkbox("Mostrar motores indisponíveis", value=not funcionais)
    ofertados = list(status) if mostrar_todos else funcionais
    if not ofertados:
        alvo.error("Nenhum motor de LLM está funcionando.")
        for s in status.values():
            alvo.write(f"{_icone(s)} **{s.provider}** — {s.reason}")
        _st.stop()

    padrao = _resolve_provider()
    provider = alvo.selectbox(
        "🧠 Motor de LLM", options=ofertados,
        index=ofertados.index(padrao) if padrao in ofertados else 0,
        format_func=lambda p: _LABELS[p],
    )

    # No Ollama a máquina sabe quais modelos existem: oferecer a lista evita
    # errar o nome e só descobrir na primeira pergunta.
    locais = _modelos_locais() if provider == "ollama" else []
    padrao_modelo = _resolve_model(provider)
    if locais:
        if padrao_modelo not in locais:
            locais = [padrao_modelo] + locais
        modelo = alvo.selectbox("Modelo", options=locais, index=locais.index(padrao_modelo),
                                help="Modelos instalados no Ollama desta máquina.")
    else:
        modelo = alvo.text_input("Modelo", value=padrao_modelo)

    s = status[provider]
    if s.verified is True:
        alvo.success("Respondeu ao teste")
    else:
        alvo.error(s.reason)
        if s.categoria in _SUGESTOES:
            alvo.caption(_SUGESTOES[s.categoria])
    if quebrados:
        alvo.caption(f"Fora do seletor: {', '.join(quebrados)}")
    if alvo.button("🔄 Testar motores de novo", use_container_width=True):
        _motores.clear()
        _st.rerun()

    return provider, modelo
