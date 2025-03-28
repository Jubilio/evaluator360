import streamlit as st
from components import get_employees_data, save_evaluation_db

# Dicionário com textos para cada idioma
texts = {
    "Português": {
        "intro": """
**Por favor, dedique alguns minutos para preencher este inquérito**

Esta é uma ferramenta essencial para fortalecer o desempenho individual e da equipa, promovendo um ambiente colaborativo e eficiente. Por meio do feedback dos colegas, identificamos pontos de melhoria, valorizamos contribuições e estimulamos o desenvolvimento profissional. Pedimos que as respostas sejam sinceras, imparciais e focadas no crescimento coletivo. Todas as informações serão tratadas com confidencialidade e utilizadas para aprimorar continuamente o nosso trabalho.

Esta é uma ferramenta chave para fortalecer o desempenho individual e da equipe, promovendo um ambiente colaborativo e eficiente.
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
        "q5": "5. Quão proativo é este(a) colega? (1 a 5)",
        "q6": "6. Quão bem este(a) colega resolve problemas de forma independente?",
        "q7": "7. Como este(a) colega lida com as críticas ao seu trabalho? (1 a 5)",
        "q8": "8. Quão bem se adapta este(a) colega às mudanças de prioridades?",
        "q9": "9. Liste as áreas em que este(a) colega apresenta bom desempenho. Seja específico.",
        "q10": "10. Liste as áreas que podem ser melhoradas para este(a) colega. Seja específico.",
        # Novas questões
        "q11": "11. Como você avalia a capacidade de comunicação deste colega? (1 a 5)",
        "q12": "12. Como você avalia a iniciativa deste colega para propor melhorias? (1 a 5)",
        "submit": "Next / Próximo",
        "fill_required": "Por favor, responda todas as perguntas. Os campos 'Pontos Positivos' e 'Áreas para Melhoria' são obrigatórios.",
        "evaluation_success": "Avaliação registrada!"
    },
    "English": {
        "intro": """
**Please take a few minutes to complete this survey**

This tool is essential to strengthen individual and team performance, fostering a collaborative and efficient work environment. Through colleague feedback, we identify areas for improvement, value contributions, and encourage professional development. We ask that responses be honest, impartial, and focused on collective growth. All information will be kept confidential and used to continuously improve our work.

This is a key tool for strengthening individual and team performance, fostering a collaborative and efficient work environment.
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
        "evaluator_defined": "Evaluator defined. Proceed with the evaluations.",
        "you_selected": "You selected:",
        "total_to_evaluate": "Total colleagues to evaluate:",
        "evaluating": "Evaluating:",
        "questions": "Questions:",
        # Questions
        "q1": "1. How likely are you to recommend this colleague for a specific activity? (0 to 10)",
        "q2": "2. How good is the quality of this colleague's work?",
        "q3": "3. How productive is this colleague? (1 to 5)",
        "q4": "4. How well does this colleague work with others?",
        "q5": "5. How proactive is this colleague? (1 to 5)",
        "q6": "6. How well does this colleague solve problems independently?",
        "q7": "7. How does this colleague handle criticism of their work? (1 to 5)",
        "q8": "8. How well does this colleague adapt to changing priorities?",
        "q9": "9. List the areas in which this colleague performs well. Be specific.",
        "q10": "10. List the areas that could be improved for this colleague. Be specific.",
        # Additional questions
        "q11": "11. How would you rate this colleague's communication skills? (1 to 5)",
        "q12": "12. How would you rate this colleague's initiative in proposing improvements? (1 to 5)",
        "submit": "Next / Next",
        "fill_required": "Please answer all questions. The 'Positive Points' and 'Areas for Improvement' fields are required.",
        "evaluation_success": "Evaluation recorded!"
    }
}

def evaluation_page():
    # Escolhe o idioma com base no session_state (configurado no app.py)
    language = st.session_state.get("language", "Português")
    t = texts[language]  # Alias para facilitar
    
    st.title("Avaliação 360°")
    st.markdown(t["intro"])
    st.markdown(t["instructions"])
    
    df = get_employees_data()
    if df.empty:
        st.stop()
    
    # Caso o avaliador ainda não tenha sido definido
    if st.session_state.evaluator_selected is None:
        st.subheader(t["name_input"])
        typed_name = st.text_input(t["name_input"], key="typed_name")
        
        matching_names = []
        if typed_name.strip():
            matching_names = [n for n in df["name"].unique() if typed_name.lower() in n.lower()]
        
        if matching_names:
            selected_name = st.selectbox("Matching Names:", matching_names, key="selected_name")
        else:
            selected_name = None
        
        confirmar_button = st.button(t["confirm"])
        if confirmar_button:
            if not selected_name:
                st.error(t["no_match"])
            else:
                evaluator_record = df[df["name"] == selected_name].iloc[0]
                st.session_state.evaluator_record = evaluator_record
                st.session_state.evaluator_name = evaluator_record["name"]
                st.session_state.evaluator_position = evaluator_record["position"]
                st.session_state.evaluator_selected = True

                if evaluator_record["months"] < 3:
                    st.error(t["not_eligible"])
                else:
                    df_to_evaluate = df[df["name"] != evaluator_record["name"]].copy()
                    evaluator_position_norm = evaluator_record["position"].strip().lower()
                    df_to_evaluate["position_clean"] = df_to_evaluate["position"].apply(lambda x: x.strip().lower())
                    if evaluator_position_norm == "distribution project officer":
                        df_to_evaluate = df_to_evaluate[df_to_evaluate["position_clean"] != "meal officer"]
                    elif evaluator_position_norm == "meal officer":
                        df_to_evaluate = df_to_evaluate[df_to_evaluate["position_clean"] != "distribution project officer"]
                    df_to_evaluate = df_to_evaluate[df_to_evaluate["months"] >= 3].reset_index(drop=True)
                    st.session_state.df_to_evaluate = df_to_evaluate
                    st.session_state.current_index = 0
                    st.success(t["evaluator_defined"])

    # Se o avaliador já foi definido
    if st.session_state.evaluator_selected is not None and "evaluator_record" in st.session_state:
        evaluator_record = st.session_state.evaluator_record
        if evaluator_record["months"] < 3:
            st.error(t["not_eligible"])
        else:
            evaluator_name = st.session_state.evaluator_name
            evaluator_position = st.session_state.evaluator_position
            df_to_evaluate = st.session_state.df_to_evaluate
            total_avaliacoes = len(df_to_evaluate)
            st.markdown(f"**{t['you_selected']}** {evaluator_name} - {evaluator_position}")
            st.markdown(f"**{t['total_to_evaluate']}** {total_avaliacoes}")
            
            if st.session_state.current_index < total_avaliacoes:
                current_row = df_to_evaluate.iloc[st.session_state.current_index]
                evaluated_name = current_row["name"]
                st.markdown("---")
                st.subheader(f"{t['evaluating']} {evaluated_name} - {current_row['position']}")
                with st.form(key=f"avaliacao_{evaluated_name}"):
                    st.markdown(f"**{t['questions']}**")
                    resposta = {}
                    resposta["recomendacao"] = st.slider(
                        t["q1"],
                        min_value=0, max_value=10, value=5, key=f"recomendacao_{evaluated_name}"
                    )
                    resposta["qualidade"] = st.radio(
                        t["q2"],
                        options=["Excelente", "Muito Bom", "Bom", "Regular", "Ruim"],
                        key=f"qualidade_{evaluated_name}"
                    )
                    resposta["produtividade"] = st.slider(
                        t["q3"],
                        min_value=1, max_value=5, value=3, key=f"produtividade_{evaluated_name}"
                    )
                    resposta["trabalho_em_equipe"] = st.radio(
                        t["q4"],
                        options=["Excelente", "Muito Bom", "Bom", "Regular", "Ruim"],
                        key=f"trabalho_em_equipe_{evaluated_name}"
                    )
                    resposta["proatividade"] = st.slider(
                        t["q5"],
                        min_value=1, max_value=5, value=3, key=f"proatividade_{evaluated_name}"
                    )
                    resposta["resolucao"] = st.radio(
                        t["q6"],
                        options=["Excelente", "Muito Bem", "Bem", "Regular", "Ruim"],
                        key=f"resolucao_{evaluated_name}"
                    )
                    resposta["criticas"] = st.slider(
                        t["q7"],
                        min_value=1, max_value=5, value=3, key=f"criticas_{evaluated_name}"
                    )
                    resposta["adaptabilidade"] = st.radio(
                        t["q8"],
                        options=["Excelente", "Muito Bem", "Bem", "Regular", "Ruim"],
                        key=f"adaptabilidade_{evaluated_name}"
                    )
                    resposta["pontos_positivos"] = st.text_area(
                        t["q9"],
                        key=f"pontos_positivos_{evaluated_name}"
                    )
                    resposta["pontos_melhoria"] = st.text_area(
                        t["q10"],
                        key=f"pontos_melhoria_{evaluated_name}"
                    )
                    # Novas questões
                    resposta["comunicacao"] = st.slider(
                        t["q11"],
                        min_value=1, max_value=5, value=3, key=f"comunicacao_{evaluated_name}"
                    )
                    resposta["iniciativa"] = st.slider(
                        t["q12"],
                        min_value=1, max_value=5, value=3, key=f"iniciativa_{evaluated_name}"
                    )
                    
                    submit = st.form_submit_button(t["submit"])
                    if submit:
                        if not resposta["pontos_positivos"].strip() or not resposta["pontos_melhoria"].strip():
                            st.error(t["fill_required"])
                        else:
                            evaluation_record = {"evaluated": evaluated_name, **resposta}
                            from components import save_evaluation_db
                            save_evaluation_db(
                                evaluator=st.session_state.evaluator_name,
                                evaluator_position=st.session_state.evaluator_position,
                                evaluated=evaluated_name,
                                evaluation_data=evaluation_record
                            )
                            st.session_state.avaliacoes[evaluated_name] = resposta
                            st.session_state.current_index += 1
                            st.success(t["evaluation_success"])
            else:
                st.success("Você completou todas as avaliações!")
                st.markdown("### Resumo das Avaliações Realizadas")
                for _, row in df_to_evaluate.iterrows():
                    evaluated_name = row["name"]
                    if evaluated_name in st.session_state.avaliacoes:
                        avaliacao = st.session_state.avaliacoes[evaluated_name]
                        st.markdown(f"#### {row['name']} - {row['position']}")
                        st.write(f"**1. Recomendação (0 a 10):** {avaliacao['recomendacao']}")
                        st.write(f"**2. Qualidade do trabalho:** {avaliacao['qualidade']}")
                        st.write(f"**3. Produtividade (1 a 5):** {avaliacao['produtividade']}")
                        st.write(f"**4. Trabalho em equipe:** {avaliacao['trabalho_em_equipe']}")
                        st.write(f"**5. Proatividade (1 a 5):** {avaliacao['proatividade']}")
                        st.write(f"**6. Resolução de problemas:** {avaliacao['resolucao']}")
                        st.write(f"**7. Lidar com críticas (1 a 5):** {avaliacao['criticas']}")
                        st.write(f"**8. Adaptação:** {avaliacao['adaptabilidade']}")
                        st.write(f"**9. Pontos Positivos:** {avaliacao['pontos_positivos']}")
                        st.write(f"**10. Áreas para Melhoria:** {avaliacao['pontos_melhoria']}")
                        st.write(f"**11. Comunicação:** {avaliacao['comunicacao']}")
                        st.write(f"**12. Iniciativa:** {avaliacao['iniciativa']}")
