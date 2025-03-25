import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt
import os

# Injeta CSS customizado (fundo branco e cores definidas)
def inject_css():
    custom_css = """
    <style>
    :root {
        --primary-color: R27-V20-B100;
        --secondary-color-1: R75-V178-B114;
        --secondary-color-2: R84-V84-B84;
    }
    body {
        background-color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        background-color: grey;
    }
    h1, h2, h3, h4 {
        color: var(--secondary-color-2);
    }
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border: none;
    }
    .stTextInput>div>input {
        border: 2px solid var(--primary-color);
    }
    .sidebar .sidebar-content {
        background-color: var(--secondary-color-1);
        color: white;
    }
    .sidebar .sidebar-content a {
        color: white;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Carrega o logo na sidebar
def load_sidebar_logo(path="acted.png", width=200):
    if os.path.exists(path):
        st.sidebar.image(path, width=width)
    else:
        st.sidebar.markdown(
            "<h3 style='text-align: center; color: var(--primary-color);'>LOGO DA EMPRESA</h3>",
            unsafe_allow_html=True
        )

# Converte um DataFrame em arquivo Excel
def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Avaliações')
    writer.close()
    return output.getvalue()

# Carrega os dados dos funcionários a partir de um CSV
import os
import pandas as pd
import streamlit as st

def get_employees_data() -> pd.DataFrame:
    csv_path = "employees.csv"
    if os.path.exists(csv_path):
        try:
            # Carrega o CSV, ignorando espaços iniciais
            df = pd.read_csv(csv_path, skipinitialspace=True)
            # Remove espaços dos cabeçalhos e converte para minúsculas
            df.columns = df.columns.str.strip().str.lower()
            # Agora o CSV deve conter as colunas: id, name, position, months
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o CSV: {e}")
            return pd.DataFrame([])
    else:
        st.error("Arquivo 'employees.csv' não encontrado. Coloque o arquivo na pasta do app.")
        return pd.DataFrame([])

# Inicializa as variáveis de sessão necessárias
def init_session_state():
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "avaliacoes" not in st.session_state:
        st.session_state.avaliacoes = {}
    if "evaluator_selected" not in st.session_state:
        st.session_state.evaluator_selected = None
    if "evaluator_record" not in st.session_state:
        st.session_state.evaluator_record = None
