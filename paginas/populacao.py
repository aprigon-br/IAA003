"""Painel 1: análise descritiva da população (as 5.124 buscas)."""

import streamlit as st

import painel_comum as pc

pc.titulo_colorido("Painel 1 · Análise descritiva da população", pc.AZUL, "titulo_painel1")  # azul da população
st.markdown(
    "As **5.124 buscas** monitoradas pelo Observatório (extração de 11/11/2026). Como temos a população inteira, "
    "os números desta página são **parâmetros**: os valores reais, calculados diretamente, sem estimativa. "
    "Eles servem de gabarito para avaliar a amostra nos painéis 2 e 3."
)

escolha = pc.filtro_publico("filtro_populacao")
df = pc.aplicar_filtro(pc.dados_populacao(), escolha)
if escolha != "Todos":
    st.caption(f"Mostrando só **{escolha}**: {pc.br(len(df), 0)} buscas.")

pc.secoes_descritivas(df, "População")
