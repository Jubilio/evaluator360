import streamlit as st
from components import get_employees_data, save_evaluation_db

# Dicionário com textos para cada idioma
texts = {
    "Português": {
        "intro": """
**Por favor, dedique alguns minutos para preencher este inquérito**

Esta é uma ferramenta essencial para fortalecer o desempenho individual e da equipa, promovendo um ambiente colaborativo e eficiente. Por meio do feedback dos colegas, identificamos pontos de melhoria, valorizamos contribuições e estimulamos o desenvolvimento profissional. Pedimos que as respostas sejam sinceras, imparciais e focadas no crescimento coletivo. Todas as informações serão tratadas com confidencialidade e utilizadas para aprimorar continuamente o nosso trabalho.
        """,
        "instructions": """
### Instruções
**Passos:**
1. Digite parte do seu nome e selecione o resultado correto.
2. Se você tiver pelo menos 3 meses de trabalho, avalie cada colega (exceto você mesmo) respondendo às perguntas numeradas.

**Observações:**
- Funcionários com menos de 3 meses **não podem realizar a avaliação**.
- Se você for **Distribution Project Officer**, não poderá avaliar funcionários na posição **MEAL Officer** e vice-versa.
        """,
        "name_input": "Seu nome (busca parcial):",
        "confirm": "Confirmar",
        "no_match": "Nenhum nome correspondente. Verifique a grafia e tente novamente.",
        "not_eligible": "Não pode realizar a avaliação devido ao tempo de trabalho com os colegas.",
        "evaluator_defined": "Avaliador definido. Prossiga para as avaliações.",
        "you_selected": "Você selecionou:",
        "total_to_evaluate": "Total de colegas a avaliar:",
        "evaluating": "Avaliando:",
        "questions": "Perguntas:",
        # Questões da avaliação
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
        "q14": "14. Liste as áreas que podem ser melhoradas para este(a) colega. Seja específico.",
        "submit": "Next / Próximo",
        "fill_required": "Por favor, responda todas as perguntas obrigatórias.",
        "evaluation_success": "Avaliação registrada!"
    },
    "English": {
        "intro": """
**Please take a few minutes to complete this survey**

This tool is essential to strengthen individual and team performance, fostering a collaborative and efficient work environment. Through colleague feedback, we identify areas for improvement, value contributions, and encourage professional development. We ask that responses be honest, impartial, and focused on collective growth. All information will be kept confidential and used to continuously improve our work.
        """,
        "instructions": """
### Instructions
**Steps:**
1. Type part of your name and select the correct match.
2. If you have been working for at least 3 months, evaluate each colleague (except yourself) by answering the numbered questions.

**Notes:**
- Employees with less than 3 months of work **cannot perform the evaluation**.
- If you are a **Distribution Project Officer**, you cannot evaluate colleagues with the position **MEAL Officer**, and vice versa.
        """,
        "name_input": "Your name (partial search):",
        "confirm": "Confirm",
        "no_match": "No matching name found. Check the spelling and try again.",
        "not_eligible": "You are not eligible to perform the evaluation due to your work duration with colleagues.",
        "evaluator_defined": "Evaluator defined. Proceed to evaluations.",
        "you_selected": "You selected:",
        "total_to_evaluate": "Total colleagues to evaluate:",
        "evaluating": "Evaluating:",
        "questions": "Questions:",
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
        "q14": "14. List the areas that could be improved for this colleague. Be specific.",
        "submit": "Next / Next",
        "fill_required": "Please answer all required questions.",
        "evaluation_success": "Evaluation recorded!"
    }
}

def evaluation_page():
    language = st.session_state.get("language", "Português")
    t = texts[language]

    st.title("Avaliação 360°")
    st.markdown(t["intro"])
    st.markdown(t["instructions"])

    df = get_employees_data()
    if df.empty:
        st.stop()

    if st.session_state.get("evaluator_selected") is None:
        st.subheader(t["name_input"])
        typed_name = st.text_input(t["name_input"], key="typed_name")
        matching = [n for n in df["name"].unique() if typed_name.lower() in n.lower()] if typed_name.strip() else []
        selected = st.selectbox("", matching, key="selected_name") if matching else None
        if st.button(t["confirm"]):
            if not selected:
                st.error(t["no_match"])
            else:
                rec = df[df["name"] == selected].iloc[0]
                st.session_state.evaluator_record = rec
                st.session_state.evaluator_name = rec["name"]
                st.session_state.evaluator_position = rec["position"]
                st.session_state.evaluator_selected = True
                if rec["months"] < 2:
                    st.error(t["not_eligible"])
                else:
                    ev = rec["position"].strip().lower()
                    de = df[df["name"] != rec["name"]].copy()
                    de["pos_clean"] = de["position"].str.strip().str.lower()
                    if ev == "distribution project officer":
                        de = de[de["pos_clean"] != "meal officer"]
                    elif ev == "meal officer":
                        de = de[de["pos_clean"] != "distribution project officer"]
                    de = de[de["months"] >= 3].reset_index(drop=True)
                    st.session_state.df_to_evaluate = de
                    st.session_state.current_index = 0
                    st.success(t["evaluator_defined"])

    if st.session_state.get("evaluator_selected"):
        rec = st.session_state.evaluator_record
        if rec["months"] < 2:
            st.error(t["not_eligible"])
            return
        df2 = st.session_state.df_to_evaluate
        st.markdown(f"**{t['you_selected']}** {st.session_state.evaluator_name} - {st.session_state.evaluator_position}")
        st.markdown(f"**{t['total_to_evaluate']}** {len(df2)}")
        idx = st.session_state.current_index
        if idx < len(df2):
            row = df2.iloc[idx]
            name = row["name"]
            st.markdown("---")
            st.subheader(f"{t['evaluating']} {name} - {row['position']}")
            with st.form(key=f"form_{name}"):
                ans = {}
                ans['recomendacao'] = st.slider(t['q1'], 0, 10, 5, key=f"rec_{name}")
                ans['qualidade'] = st.radio(t['q2'], ["Excelente","Muito Bom","Bom","Regular","Ruim"], key=f"qual_{name}")
                ans['produtividade'] = st.slider(t['q3'], 1, 5, 3, key=f"prod_{name}")
                ans['trabalho_equipa'] = st.radio(t['q4'], ["Excelente","Muito Bom","Bom","Regular","Ruim"], key=f"team_{name}")
                ans['proatividade'] = st.slider(t['q5'], 1, 5, 3, key=f"proativo_{name}")
                ans['adaptabilidade'] = st.slider(t['q6'], 1, 5, 3, key=f"adapt_{name}")
                ans['autonomia'] = st.slider(t['q7'], 1, 5, 3, key=f"auto_{name}")
                ans['gestao_equipa'] = st.slider(t['q8'], 1, 5, 3, key=f"gestao_{name}")
                ans['operacionalizacao'] = st.slider(t['q9'], 1, 5, 3, key=f"opera_{name}")
                ans['comunicacao_eficaz'] = st.slider(t['q10'], 1, 5, 3, key=f"eficaz_{name}")
                ans['tarefa_atempada'] = st.slider(t['q11'], 1, 10, 5, key=f"time_{name}")
                ans['qualidade_resultados'] = st.slider(t['q12'], 1, 5, 3, key=f"resul_{name}")
                ans['pontos_positivos'] = st.text_area(t['q13'], key=f"pos_{name}")
                ans['pontos_melhoria'] = st.text_area(t['q14'], key=f"melhoria_{name}")
                if st.form_submit_button(t['submit']):
                    if not ans['pontos_positivos'].strip() or not ans['pontos_melhoria'].strip():
                        st.error(t['fill_required'])
                    else:
                        save_evaluation_db(
                            st.session_state.evaluator_name,
                            st.session_state.evaluator_position,
                            name,
                            ans
                        )
                        st.session_state.avaliacoes[name] = ans
                        st.session_state.current_index += 1
                        st.success(t['evaluation_success'])
        else:
            st.success("Você completou todas as avaliações!")
            st.markdown("### Resumo das Avaliações Realizadas")
            for r in df2.itertuples():
                n = r.name
                if n in st.session_state.avaliacoes:
                    a = st.session_state.avaliacoes[n]
                    st.markdown(f"#### {n} - {r.position}")
                    for k, v in a.items():
                        st.write(f"**{k}:** {v}")
