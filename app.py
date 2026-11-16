"""
Painéis do trabalho final de Probabilidade e Estatística para IA (IAA003).

Rodar localmente:
    .venv\\Scripts\\streamlit.exe run app.py

Cada painel tem um endereço próprio: /populacao, /amostra e /inferencia.
Página extra (análise exploratória, vinda da pasta EDA): /onde-anunciar.
"""

import streamlit as st

st.set_page_config(page_title="Buscas do Google: população × amostra", page_icon=":material/query_stats:",
                   layout="wide", initial_sidebar_state="expanded")

paginas = st.navigation({
    "Trabalho final": [
        st.Page("paginas/inicio.py", title="Início: a base de dados", icon=":material/home:", default=True),
        st.Page("paginas/populacao.py", title="1. População", icon=":material/groups:", url_path="populacao"),
        st.Page("paginas/amostra.py", title="2. Amostra", icon=":material/filter_alt:", url_path="amostra"),
        st.Page("paginas/inferencia.py", title="3. Inferência", icon=":material/functions:", url_path="inferencia"),
    ],
    "Análise exploratória": [
        # Dashboard da pasta EDA, adaptado para ler o mesmo dataset.txt
        st.Page("paginas/onde_anunciar.py", title="Onde vale a pena anunciar?", icon=":material/search:",
                url_path="onde-anunciar"),
    ],
})

with st.sidebar:
    st.caption("Trabalho final · Probabilidade e Estatística para IA (IAA003)")
    st.caption("Dados: Google Ads Keyword Planner, via Observatório Lucro Digital (extração de 11/11/2026)")

paginas.run()
