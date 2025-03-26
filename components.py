import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt
import os
import sqlite3
from datetime import datetime

# Configuração de logging (opcional)
import logging
logging.basicConfig(level=logging.INFO)

DB_FILE = "evaluations.db"

def create_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluator TEXT,
            evaluator_position TEXT,
            evaluated TEXT,
            recomendacao INTEGER,
            qualidade TEXT,
            produtividade INTEGER,
            trabalho_em_equipe TEXT,
            proatividade INTEGER,
            resolucao TEXT,
            criticas INTEGER,
            adaptabilidade TEXT,
            pontos_positivos TEXT,
            pontos_melhoria TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Cria o banco de dados na primeira execução
create_db()

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

@st.cache_data
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

def save_evaluation_db(evaluator, evaluator_position, evaluated, evaluation_data):
    """
    Salva os dados da avaliação no banco de dados SQLite.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Extrai os valores do dicionário
    recomendacao = evaluation_data.get("recomendacao")
    qualidade = evaluation_data.get("qualidade")
    produtividade = evaluation_data.get("produtividade")
    trabalho_em_equipe = evaluation_data.get("trabalho_em_equipe")
    proatividade = evaluation_data.get("proatividade")
    resolucao = evaluation_data.get("resolucao")
    criticas = evaluation_data.get("criticas")
    adaptabilidade = evaluation_data.get("adaptabilidade")
    pontos_positivos = evaluation_data.get("pontos_positivos")
    pontos_melhoria = evaluation_data.get("pontos_melhoria")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO evaluations (
            evaluator, evaluator_position, evaluated, recomendacao, qualidade, produtividade,
            trabalho_em_equipe, proatividade, resolucao, criticas, adaptabilidade,
            pontos_positivos, pontos_melhoria, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (evaluator, evaluator_position, evaluated, recomendacao, qualidade, produtividade,
          trabalho_em_equipe, proatividade, resolucao, criticas, adaptabilidade,
          pontos_positivos, pontos_melhoria, timestamp))
    conn.commit()
    conn.close()

def get_evaluations_db() -> pd.DataFrame:
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM evaluations", conn)
    conn.close()
    return df

def clear_responses():
    """Remove os dados do banco de dados (para testes)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations")
    conn.commit()
    conn.close()
    st.session_state.responses_df = pd.DataFrame()
