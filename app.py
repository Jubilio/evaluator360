import streamlit as st
from components import inject_css, load_sidebar_logo, init_session_state
from evaluation_page import evaluation_page
from admin_page import admin_page

st.set_page_config(page_title="Avaliação 360°", layout="wide")

# Inicializa as variáveis de sessão
init_session_state()

# Injeta o CSS customizado
inject_css()

# Carrega o logo na sidebar
load_sidebar_logo("acted.png", 300)

# Navegação na sidebar
page = st.sidebar.radio("Menu", options=["Avaliação", "Dashboard Admin"])

if page == "Avaliação":
    evaluation_page()
elif page == "Dashboard Admin":
    admin_page()
