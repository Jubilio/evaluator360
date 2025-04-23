import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime
from io import BytesIO

# Caminho para o banco de dados SQLite
DB_FILE = os.path.join(os.path.dirname(__file__), "evaluations.db")

# Inicializa o banco de dados com o esquema atualizado
def create_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
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
            adaptabilidade INTEGER,
            autonomia INTEGER,
            gestao_equipa INTEGER,
            operacionalizacao INTEGER,
            comunicacao_eficaz INTEGER,
            tarefa_atempada INTEGER,
            qualidade_resultados INTEGER,
            iniciativa INTEGER,
            pontos_positivos TEXT,
            pontos_melhoria TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

create_db()

# Função para salvar uma avaliação no banco de dados
def save_evaluation_db(evaluator: str, evaluator_position: str, evaluated: str, evaluation_data: dict):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    # Monta o dicionário de dados completo
    data = {
        'evaluator': evaluator,
        'evaluator_position': evaluator_position,
        'evaluated': evaluated,
        **evaluation_data,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Colunas e placeholders
    cols = list(data.keys())
    placeholders = ", ".join(["?" for _ in cols])
    sql = f"INSERT INTO evaluations ({', '.join(cols)}) VALUES ({placeholders})"
    cursor.execute(sql, [data[c] for c in cols])
    conn.commit()
    conn.close()

# Função para obter todas as avaliações
def get_evaluations_db() -> pd.DataFrame:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM evaluations", conn)
    conn.close()
    return df

# Limpa todas as avaliações (para testes)
def clear_responses():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations")
    conn.commit()
    conn.close()

# Exporta DataFrame para Excel
def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Avaliações')
    writer.close()
    return output.getvalue()

# Carrega base de funcionários de CSV (com cache)
@st.cache_data
def get_employees_data() -> pd.DataFrame:
    csv_path = os.path.join(os.path.dirname(__file__), 'employees.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Normaliza colunas
        df.columns = df.columns.str.strip().str.lower()
        return df
    else:
        st.error("Arquivo 'employees.csv' não encontrado.")
        return pd.DataFrame([])

# Inicializa variáveis de sessão
def init_session_state():
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'avaliacoes' not in st.session_state:
        st.session_state.avaliacoes = {}
    if 'evaluator_selected' not in st.session_state:
        st.session_state.evaluator_selected = None
    if 'evaluator_record' not in st.session_state:
        st.session_state.evaluator_record = None

# Injeção de CSS customizado (cores)
def inject_css():
    css = '''
    <style>
    :root { --primary-color: #4bb272; --secondary-color-1: #545454; --secondary-color-2: #1b1464; }
    body { background-color: white !important; }
    h1, h2, h3, h4 { color: var(--secondary-color-2); }
    .stButton>button { background-color: var(--primary-color); color: white; border: none; }
    .sidebar .sidebar-content { background-color: var(--secondary-color-1); color: white; }
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

# Carrega logo no sidebar
def load_sidebar_logo(path: str, width: int = 200):
    if os.path.exists(path):
        st.sidebar.image(path, width=width)
    else:
        st.sidebar.markdown('<h3 style="color: var(--primary-color);">LOGO</h3>', unsafe_allow_html=True)
