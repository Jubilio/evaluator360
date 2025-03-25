import streamlit as st
from components import get_employees_data, save_evaluation

def evaluation_page():
    st.title("Avaliação 360°")
    st.markdown("""
    **Please take a few minutes to complete this survey / Por favor, dedique alguns minutos para preencher este inquérito**

    Esta é uma ferramenta essencial para fortalecer o desempenho individual e da equipa, promovendo um ambiente colaborativo e eficiente. Por meio do feedback dos colegas, identificamos pontos de melhoria, valorizamos contribuições e estimulamos o desenvolvimento profissional. Pedimos que as respostas sejam sinceras, imparciais e focadas no crescimento coletivo. Todas as informações serão tratadas com confidencialidade e utilizadas para aprimorar continuamente o nosso trabalho.

    This is a key tool for strengthening individual and team performance, fostering a collaborative and efficient work environment. Through feedback from colleagues, we identify areas for improvement, recognize contributions, and encourage professional development.
    """)
    st.markdown("""
    ### Instruções
    **Passos:**
    1. Digite parte do seu nome e selecione o resultado correto.
    2. Se você tiver pelo menos 3 meses de trabalho, avalie cada colega (exceto você mesmo) respondendo às perguntas numeradas.

    **Observações:**
    - Funcionários com menos de 3 meses **não podem realizar a avaliação**.
    - Se você for **Distribution Project Officer**, não poderá avaliar funcionários na posição **MEAL Officer** e vice-versa.
    """)
    
    df = get_employees_data()
    if df.empty:
        st.stop()
    
    # Caso o avaliador ainda não tenha sido definido
    if st.session_state.evaluator_selected is None:
        st.subheader("Digite seu nome e selecione o resultado correto")
        typed_name = st.text_input("Seu nome (busca parcial):", key="typed_name")
        
        matching_names = []
        if typed_name.strip():
            matching_names = [n for n in df["name"].unique() if typed_name.lower() in n.lower()]
        
        if matching_names:
            selected_name = st.selectbox("Nomes encontrados:", matching_names, key="selected_name")
        else:
            selected_name = None
        
        confirmar_button = st.button("Confirmar")
        if confirmar_button:
            if not selected_name:
                st.error("Nenhum nome correspondente. Verifique a grafia e tente novamente.")
            else:
                evaluator_record = df[df["name"] == selected_name].iloc[0]
                st.session_state.evaluator_record = evaluator_record
                st.session_state.evaluator_name = evaluator_record["name"]
                st.session_state.evaluator_position = evaluator_record["position"]
                st.session_state.evaluator_selected = True

                if evaluator_record["months"] < 3:
                    st.error("Não pode realizar a avaliação devido ao tempo de trabalho com os colegas.")
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
                    st.success("Avaliador definido. Prossiga para as avaliações.")

    # Se o avaliador já estiver definido
    if st.session_state.evaluator_selected is not None and "evaluator_record" in st.session_state:
        evaluator_record = st.session_state.evaluator_record
        if evaluator_record["months"] < 3:
            st.error("Você não é elegível para realizar a avaliação, pois possui menos de 3 meses de trabalho com os colegas.")
        else:
            evaluator_name = st.session_state.evaluator_name
            evaluator_position = st.session_state.evaluator_position
            df_to_evaluate = st.session_state.df_to_evaluate
            total_avaliacoes = len(df_to_evaluate)
            st.markdown(f"**Você selecionou:** {evaluator_name} - {evaluator_position}")
            st.markdown(f"**Total de colegas a avaliar:** {total_avaliacoes}")
            
            if st.session_state.current_index < total_avaliacoes:
                current_row = df_to_evaluate.iloc[st.session_state.current_index]
                evaluated_name = current_row["name"]  # Nome do avaliado
                st.markdown("---")
                st.subheader(f"Avaliando: {evaluated_name} - {current_row['position']}")
                with st.form(key=f"avaliacao_{evaluated_name}"):
                    st.markdown("**Perguntas:**")
                    resposta = {}
                    resposta["recomendacao"] = st.slider(
                        "1. Qual é a probabilidade de recomendar esse(a) colega para uma atividade específica? (0 a 10)",
                        min_value=0, max_value=10, value=5, key=f"recomendacao_{evaluated_name}"
                    )
                    resposta["qualidade"] = st.radio(
                        "2. Quão boa é a qualidade do trabalho deste colega?",
                        options=["Excelente", "Muito Bom", "Bom", "Regular", "Ruim"],
                        key=f"qualidade_{evaluated_name}"
                    )
                    resposta["produtividade"] = st.slider(
                        "3. Quão produtivo é este(a) colega de trabalho? (1 a 5)",
                        min_value=1, max_value=5, value=3, key=f"produtividade_{evaluated_name}"
                    )
                    resposta["trabalho_em_equipe"] = st.radio(
                        "4. Quão bem trabalha esse(a) colega com os(as) outros(as)?",
                        options=["Excelente", "Muito Bem", "Bem", "Regular", "Ruim"],
                        key=f"trabalho_em_equipe_{evaluated_name}"
                    )
                    resposta["proatividade"] = st.slider(
                        "5. Quão proativo(a) é este(a) colega? (1 a 5)",
                        min_value=1, max_value=5, value=3, key=f"proatividade_{evaluated_name}"
                    )
                    resposta["resolucao"] = st.radio(
                        "6. Quão bem este(a) colega resolve problemas de forma independente?",
                        options=["Excelente", "Muito Bem", "Bem", "Regular", "Ruim"],
                        key=f"resolucao_{evaluated_name}"
                    )
                    resposta["criticas"] = st.slider(
                        "7. Como este(a) colega lida com as críticas ao seu trabalho? (1 a 5)",
                        min_value=1, max_value=5, value=3, key=f"criticas_{evaluated_name}"
                    )
                    resposta["adaptabilidade"] = st.radio(
                        "8. Quão bem se adapta este(a) colega às mudanças de prioridades?",
                        options=["Excelente", "Muito Bem", "Bem", "Regular", "Ruim"],
                        key=f"adaptabilidade_{evaluated_name}"
                    )
                    resposta["pontos_positivos"] = st.text_area(
                        "9. Liste as áreas em que este(a) colega apresenta bom desempenho. Seja específico.",
                        key=f"pontos_positivos_{evaluated_name}"
                    )
                    resposta["pontos_melhoria"] = st.text_area(
                        "10. Liste as áreas que podem ser melhoradas para este(a) colega. Seja específico.",
                        key=f"pontos_melhoria_{evaluated_name}"
                    )
                    
                    submit = st.form_submit_button("Next / Próximo")
                    if submit:
                        if not resposta["pontos_positivos"].strip() or not resposta["pontos_melhoria"].strip():
                            st.error("Por favor, responda todas as perguntas. Os campos 'Pontos Positivos' e 'Áreas para Melhoria' são obrigatórios.")
                        else:
                            evaluation_record = {"avaliado": evaluated_name, **resposta}
                            from components import save_evaluation
                            save_evaluation(
                                evaluator=st.session_state.evaluator_name,
                                evaluator_position=st.session_state.evaluator_position,
                                evaluated=evaluated_name,
                                evaluation_data=evaluation_record
                            )
                            st.session_state.avaliacoes[evaluated_name] = resposta
                            st.session_state.current_index += 1
                            st.success("Avaliação registrada!")
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
