import streamlit as st
from components import inject_light_theme, inject_dark_theme, load_sidebar_logo, init_session_state
from evaluation_page import evaluation_page
from admin_page import admin_page

st.set_page_config(page_title="Avaliação 360°", layout="wide")
init_session_state()
load_sidebar_logo("acted.png", 200)

# Opção para escolher o tema na sidebar
theme = st.sidebar.selectbox("Selecione o tema", ["Claro", "Escuro"], key="theme_select")
if theme == "Claro":
    inject_light_theme()
else:
    inject_dark_theme()

# Seleção de idioma na sidebar (default: Português)
if "language" not in st.session_state:
    st.session_state.language = "Português"

st.session_state.language = st.sidebar.selectbox("Selecione o idioma", ["Português", "English"], key="language_select")

page = st.sidebar.radio("Menu", options=["Avaliação", "Dashboard Admin"])

if page == "Avaliação":
    evaluation_page()
elif page == "Dashboard Admin":
    admin_page()
