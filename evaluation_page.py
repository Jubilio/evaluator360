import streamlit as st
import streamlit.components.v1 as components
from components import get_employees_data, save_evaluation_db

# Textos multilíngues
texts = {
    "Português": {
        "intro": """
**Por favor, dedique alguns minutos para preencher este inquérito**

Esta é uma ferramenta essencial para fortalecer o desempenho individual e da equipa, promovendo um ambiente colaborativo e eficiente. Por meio do feedback dos colegas, identificamos pontos de melhoria, valorizamos contribuições e estimulamos o desenvolvimento profissional. Pedimos que as respostas sejam sinceras, imparciais e focadas no crescimento coletivo. Todas as informações serão tratadas com confidencialidade e utilizadas para aprimorar continuamente o nosso trabalho.
""",
        "instructions": """
### Instruções
1. Digite parte do seu nome e selecione o resultado correto.
2. Se você tiver pelo menos 1 meses de trabalho, avalie cada colega (exceto você mesmo).

""",
        "name_input": "Digite seu nome:",
        "confirm": "Confirmar",
        "no_match": "Nenhum nome correspondente.",
        "not_eligible": "Você não é elegível para avaliar.",
        "evaluator_defined": "Avaliador definido! Iniciando avaliações...",
        "you_selected": "Você selecionou:",
        "total_to_evaluate": "Colegas a avaliar:",
        "evaluating": "Avaliando:",
        "submit": "Próximo",
        "send": "Enviar",
        "fill_required": "Por favor, responda todas as perguntas obrigatórias.",
        "success": "Avaliação registrada com sucesso!",
        # Perguntas
        "q1": "1. Qual é a probabilidade de recomendar esse(a) colega para uma atividade específica? (0 a 10)",
        "q2": "2. Quão boa é a qualidade do trabalho deste colega?",
        "q3": "3. Quão produtivo é este(a) colega de trabalho? (1 a 5)",
        "q4": "4. Quão bem trabalha esse(a) colega com os(as) outros(as)?",
        "q5": "5. Quão proativo(a) é este(a) colega? (1 a 5)",
        # Novas variáveis substitutas
        "q6": "6. Adaptabilidade: Como avalia a capacidade deste(a) colega para se adaptar a mudanças, imprevistos ou novos contextos de trabalho? (1 a 5)",
        "q7": "7. Autonomia: Em que medida este(a) colega demonstra iniciativa e capacidade para trabalhar de forma autónoma, sem necessidade de supervisão constante? (1 a 5)",
        "q8": "8. Trabalho em equipa e gestão de equipa: Como descreve a capacidade deste(a) colega para colaborar com colegas e, se aplicável, liderar e motivar a sua equipa? (1 a 5)",
        "q9": "9. Operacionalização: Este(a) colega consegue transformar planos e orientações em ações concretas de forma eficiente? (1 a 5)",
        "q10": "10. Comunicação eficaz: Em que medida este(a) colega comunica de forma clara, respeitosa e apropriada com colegas, parceiros e outras partes interessadas? (1 a 5)",
        # Questões adicionais solicitadas
        "q11": "11. De 1 a 10, como avalia a capacidade do(a) colega em desempenhar de forma atempada as tarefas diárias a ele(a) atribuídas?",
        "q12": "12. Como avalia a qualidade dos resultados das tarefas executadas pelo(a) colega de uma forma geral?",
        # Questões abertas (mantêm-se por último)
        "q13": "13. Liste as áreas em que este(a) colega apresenta bom desempenho. Seja específico.",
        "q14": "14. Liste as áreas que podem ser melhoradas para este(a) colega. Seja específico."
    },
    "English": {
        "intro": """
**Please take a few minutes to complete this survey**

This tool is essential to strengthen individual and team performance, fostering a collaborative and efficient work environment. Through colleague feedback, we identify areas for improvement, value contributions, and encourage professional development. We ask that responses be honest, impartial, and focused on collective growth. All information will be kept confidential and used to continuously improve our work.
""",
        "instructions": """
### Instructions
1. Type part of your name and select the correct match.
2. If you have been working for at least 3 months, evaluate each colleague (except yourself).


""",
        "name_input": "Enter your name:",
        "confirm": "Confirm",
        "no_match": "No matching name found.",
        "not_eligible": "You are not eligible to evaluate.",
        "evaluator_defined": "Evaluator defined! Starting evaluations...",
        "you_selected": "You selected:",
        "total_to_evaluate": "Colleagues to evaluate:",
        "evaluating": "Evaluating:",
        "submit": "Next",
        "send": "Submit",
        "fill_required": "Please answer all required questions.",
        "success": "Evaluation recorded successfully!",
        # Questions
        "q1": "1. How likely are you to recommend this colleague for a specific activity? (0 to 10)",
        "q2": "2. How good is the quality of this colleague's work?",
        "q3": "3. How productive is this colleague? (1 to 5)",
        "q4": "4. How well does this colleague work with others?",
        "q5": "5. How proactive is this colleague? (1 to 5)",
        "q6": "6. Adaptability: How do you rate this colleague's ability to adapt to changes, unexpected events or new work contexts? (1 to 5)",
        "q7": "7. Autonomy: To what extent does this colleague demonstrate initiative and capability to work independently without constant supervision? (1 to 5)",
        "q8": "8. Teamwork and team management: How would you describe this colleague's ability to collaborate with coworkers and, when applicable, lead and motivate their team? (1 to 5)",
        "q9": "9. Operationalization: Does this colleague effectively turn plans and guidelines into concrete actions efficiently? (1 to 5)",
        "q10": "10. Effective communication: To what extent does this colleague communicate clearly, respectfully and appropriately with colleagues, partners and other stakeholders? (1 to 5)",
        "q11": "11. On a scale from 1 to 10, how do you rate this colleague's ability to perform daily tasks assigned to them in a timely manner?",
        "q12": "12. How do you assess the quality of the results of tasks performed by the colleague in general?",
        "q13": "13. List the areas in which this colleague performs well. Be specific.",
        "q14": "14. List the areas that could be improved for this colleague. Be specific."
    }
}


def evaluation_page():
    # Seleciona textos pelo idioma
    lang = st.session_state.get("language", "Português")
    base = texts["Português"]
    t0 = texts.get(lang, {})
    
    def tt(key):
        return t0.get(key, base.get(key, ""))

    # Inicializa estado
    if "step" not in st.session_state:
        st.session_state.step = "intro"
        st.session_state.evaluator = None
        st.session_state.pool = None
        st.session_state.index = 0
        st.session_state.answers = {}

    df = get_employees_data()
    if df.empty:
        st.error(tt("no_match"))
        return

    # Passo 1: Seleção de avaliador
    if st.session_state.step == "intro":
        st.title("Avaliação 360°")
        st.markdown(tt("intro"))
        st.markdown(tt("instructions"))
        name_input = st.text_input(tt("name_input"), key="typed_name")
        matches = [n for n in df["name"] if name_input.lower() in n.lower()] if name_input else []
        selected = st.selectbox(tt("name_input"), matches, key="selected_name") if matches else None
        if st.button(tt("confirm")):
            if not selected:
                st.error(tt("no_match"))
            else:
                rec = df[df["name"] == selected].iloc[0]
                if rec["months"] < 3:
                    st.error(tt("not_eligible"))
                else:
                    pool = df[df["name"] != selected].copy()
                    pos = rec["position"].strip().lower()
                    if pos == "distribution project officer":
                        pool = pool[pool["position"].str.lower() != "meal officer"]
                    elif pos == "meal officer":
                        pool = pool[pool["position"].str.lower() != "distribution project officer"]
                    pool = pool[pool["months"] >= 3].reset_index(drop=True)
                    st.session_state.evaluator = rec
                    st.session_state.pool = pool
                    st.session_state.step = "questions"
                    st.success(tt("evaluator_defined"))
        return

    # Passo 2: Perguntas sequenciais
    components.html('<script>window.scrollTo(0,0);</script>', height=0)
    rec = st.session_state.evaluator
    pool = st.session_state.pool
    idx = st.session_state.index

    st.title(f"{tt('you_selected')} {rec['name']} - {rec['position']}")
    st.markdown(f"**{tt('total_to_evaluate')}** {len(pool)}")

    if idx < len(pool):
        person = pool.iloc[idx]
        st.subheader(f"{tt('evaluating')} {person['name']} - {person['position']}")
        with st.form(key=f"form_{idx}", clear_on_submit=True):
            a1 = st.slider(tt('q1'), 0, 10, 5)
            a2 = st.radio(tt('q2'), ["Excelente","Muito Bom","Bom","Regular","Ruim"])
            a3 = st.slider(tt('q3'), 1, 5, 3)
            a4 = st.radio(tt('q4'), ["Excelente","Muito Bom","Bom","Regular","Ruim"])
            a5 = st.slider(tt('q5'), 1, 5, 3)
            a6 = st.slider(tt('q6'), 1, 5, 3)
            a7 = st.slider(tt('q7'), 1, 5, 3)
            a8 = st.slider(tt('q8'), 1, 5, 3)
            a9 = st.slider(tt('q9'), 1, 5, 3)
            a10 = st.slider(tt('q10'), 1, 5, 3)
            a11 = st.slider(tt('q11'), 1, 10, 5)
            a12 = st.slider(tt('q12'), 1, 5, 3)
            p13 = st.text_area(tt('q13'))
            p14 = st.text_area(tt('q14'))
            label = tt('submit') if idx < len(pool) - 1 else (tt('send') or tt('submit'))
            submitted = st.form_submit_button(label)

        if submitted:
            missing = []
            for key, val in [('q1',a1),('q2',a2),('q3',a3),('q4',a4),('q5',a5),('q6',a6),('q7',a7),('q8',a8),('q9',a9),('q10',a10),('q11',a11),('q12',a12)]:
                if val is None or (isinstance(val,str) and not val.strip()):
                    missing.append(key)
            if not p13.strip(): missing.append('q13')
            if not p14.strip(): missing.append('q14')
            if missing:
                st.error(tt('fill_required'))
            else:
                st.session_state.answers[person['name']] = {
                    'recomendacao': a1,
                    'qualidade': a2,
                    'produtividade': a3,
                    'trabalho_em_equipe': a4,
                    'proatividade': a5,
                    'adaptabilidade': a6,
                    'autonomia': a7,
                    'gestao_equipa': a8,
                    'operacionalizacao': a9,
                    'comunicacao_eficaz': a10,
                    'tarefa_atempada': a11,
                    'qualidade_resultados': a12,
                    'pontos_positivos': p13.strip(),
                    'pontos_melhoria': p14.strip()
                }
                st.session_state.index += 1
                if idx == len(pool) - 1:
                    for name_eval, resp in st.session_state.answers.items():
                        save_evaluation_db(rec['name'], rec['position'], name_eval, resp)
                    st.success(tt('success'))
        return
    else:
        st.info("Nenhum colega para avaliar.")
        return
