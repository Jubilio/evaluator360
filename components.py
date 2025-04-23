import streamlit as st
import pandas as pd
import sqlite3
import os
from io import BytesIO
from datetime import datetime

DB_FILE = "evaluations.db"


def create_db():
    """Garante criação da tabela sem apagar dados existentes."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
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
            adaptabilidade INTEGER,
            autonomia INTEGER,
            gestao_equipa INTEGER,
            operacionalizacao INTEGER,
            comunicacao_eficaz INTEGER,
            tarefa_atempada INTEGER,
            qualidade_resultados INTEGER,
            pontos_positivos TEXT,
            pontos_melhoria TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Cria a tabela (sem apagar dados) ao importar o módulo\create_db()


def inject_light_theme():
    light_css = """
    <style>
    :root {
        --primary-color: #4bb272;
        --secondary-color-1: #545454;
        --secondary-color-2: #1b1464;
    }
    body {
        background-color: white !important;
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container { background-color: white; }
    h1, h2, h3, h4 { color: var(--secondary-color-2); }
    .stButton>button { background-color: var(--primary-color); color: white; border: none; }
    .sidebar .sidebar-content { background-color: var(--secondary-color-1); color: white; }
    </style>
    """
    st.markdown(light_css, unsafe_allow_html=True)


def inject_dark_theme():
    dark_css = """
    <style>
    :root {
        --primary-color: #4bb272;
        --secondary-color-1: #545454;
        --secondary-color-2: #1b1464;
    }
    body { background-color: #333333 !important; color: white; font-family: 'Segoe UI', sans-serif; }
    .block-container { background-color: #444444; }
    h1, h2, h3, h4 { color: var(--primary-color); }
    .stButton>button { background-color: var(--primary-color); color: white; border: none; }
    .stTextInput>div>input { border: 2px solid var(--primary-color); background-color: #555555; color: white; }
    .sidebar .sidebar-content { background-color: #222222; color: white; }
    .sidebar .sidebar-content a { color: white; }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)


def load_sidebar_logo(path="acted.png", width=200):
    if os.path.exists(path):
        st.sidebar.image(path, width=width)
    else:
        st.sidebar.markdown(
            "<h3 style='text-align: center; color: var(--primary-color);'>LOGO DA EMPRESA</h3>",
            unsafe_allow_html=True
        )


def init_session_state():
    defaults = {
        "current_index": 0,
        "avaliacoes": {},
        "evaluator_selected": None,
        "evaluator_record": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Avaliações')
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
    else:
        st.error("Arquivo 'employees.csv' não encontrado. Coloque o arquivo na pasta do app.")
    return pd.DataFrame([])


def save_evaluation_db(evaluator, evaluator_position, evaluated, e: dict):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    vals = [
        evaluator,
        evaluator_position,
        evaluated,
        e.get('recomendacao'),
        e.get('qualidade'),
        e.get('produtividade'),
        e.get('trabalho_em_equipe'),
        e.get('proatividade'),
        e.get('adaptabilidade'),
        e.get('autonomia'),
        e.get('gestao_equipa'),
        e.get('operacionalizacao'),
        e.get('comunicacao_eficaz'),
        e.get('tarefa_atempada'),
        e.get('qualidade_resultados'),
        e.get('pontos_positivos'),
        e.get('pontos_melhoria'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
    placeholders = ",".join(["?" for _ in vals])
    cur.execute(
        f"INSERT INTO evaluations (evaluator, evaluator_position, evaluated, recomendacao, qualidade, produtividade, trabalho_em_equipe, proatividade, adaptabilidade, autonomia, gestao_equipa, operacionalizacao, comunicacao_eficaz, tarefa_atempada, qualidade_resultados, pontos_positivos, pontos_melhoria, timestamp) VALUES ({placeholders})",
        vals
    )
    conn.commit()
    conn.close()


def get_evaluations_db() -> pd.DataFrame:
    if not os.path.exists(DB_FILE):
        create_db()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM evaluations", conn)
    conn.close()
    return df


def clear_responses():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM evaluations")
    conn.commit()
    conn.close()
