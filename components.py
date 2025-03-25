import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt
import os
from datetime import datetime

def inject_css():
    custom_css = """
    <style>
    :root {
        --primary-color: #4bb272;
        --secondary-color-1: #545454;
        --secondary-color-2: #1b1464;
    }
    body {
        background-color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        background-color: white;
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

def load_sidebar_logo(path="acted.png", width=200):
    if os.path.exists(path):
        st.sidebar.image(path, width=width)
    else:
        st.sidebar.markdown(
            "<h3 style='text-align: center; color: var(--primary-color);'>LOGO DA EMPRESA</h3>",
            unsafe_allow_html=True
        )

def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Avaliações')
    writer.close()
    return output.getvalue()

def get_employees_data() -> pd.DataFrame:
    csv_path = "employees.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, skipinitialspace=True)
            df.columns = df.columns.str.strip().str.lower()
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o CSV: {e}")
            return pd.DataFrame([])
    else:
        st.error("Arquivo 'employees.csv' não encontrado. Coloque o arquivo na pasta do app.")
        return pd.DataFrame([])

def init_session_state():
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "avaliacoes" not in st.session_state:
        st.session_state.avaliacoes = {}
    if "evaluator_selected" not in st.session_state:
        st.session_state.evaluator_selected = None
    if "evaluator_record" not in st.session_state:
        st.session_state.evaluator_record = None

def save_evaluation(evaluator, evaluator_position, evaluated, evaluation_data):
    """
    Salva os dados da avaliação no arquivo 'responses.csv'.
    Acrescenta o nome do avaliador, sua posição, o nome do avaliado e o timestamp.
    """
    evaluation_data["evaluator"] = evaluator
    evaluation_data["evaluator_position"] = evaluator_position
    evaluation_data["avaliado"] = evaluated
    evaluation_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    df = pd.DataFrame([evaluation_data])
    csv_file = "responses.csv"
    if not os.path.exists(csv_file):
        df.to_csv(csv_file, index=False, mode='w')
    else:
        df.to_csv(csv_file, index=False, mode='a', header=False)

def clear_responses():
    """Remove o arquivo de respostas (se existir) e limpa a variável de sessão."""
    csv_file = "responses.csv"
    if os.path.exists(csv_file):
        os.remove(csv_file)
    st.session_state.responses_df = pd.DataFrame()
