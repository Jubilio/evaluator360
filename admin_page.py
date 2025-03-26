import streamlit as st
import pandas as pd
import altair as alt
from components import to_excel, clear_responses, get_evaluations_db

def suggest_mentors(variable: str, responses_df: pd.DataFrame, top_n: int = 3):
    """
    Agrupa as avaliações por 'evaluated' e calcula a média da variável selecionada.
    Sugere, para cada avaliado com desempenho abaixo da média geral, os top_n com melhores resultados nessa variável.
    """
    grouped = responses_df.groupby("evaluated")[variable].mean().reset_index()
    overall_avg = grouped[variable].mean()
    low_perf = grouped[grouped[variable] < overall_avg]
    high_perf = grouped[grouped[variable] >= overall_avg].sort_values(by=variable, ascending=False)
    
    suggestions = {}
    for _, row in low_perf.iterrows():
        evaluated = row["evaluated"]
        mentors = high_perf[high_perf["evaluated"] != evaluated].head(top_n)
        suggestions[evaluated] = mentors
    return suggestions, overall_avg

def admin_page():
    st.title("Dashboard Administrativo")
    st.markdown("Esta página é restrita. Informe a senha de acesso.")
    
    admin_password = st.text_input("Senha de Admin", type="password", key="admin_password")
    if admin_password != "admin123":
        st.error("Senha incorreta!")
        st.stop()
    
    st.success("Acesso permitido!")
    
    # Exibe informações do avaliador, se disponíveis
    if "evaluator_name" in st.session_state and "evaluator_position" in st.session_state:
        st.markdown(f"### Avaliações realizadas por: **{st.session_state.evaluator_name} - {st.session_state.evaluator_position}**")
    
    # Botão para limpar os dados (ex: para testes)
    if st.button("Remover dados de teste"):
        clear_responses()
        st.success("Dados removidos com sucesso.")
    
    st.markdown("### Respostas das Avaliações")
    
    responses_df = get_evaluations_db()
    if responses_df.empty:
        st.warning("Nenhuma avaliação encontrada.")
    else:
        st.dataframe(responses_df, use_container_width=True)
        
        numeric_cols = ["recomendacao", "produtividade", "proatividade", "criticas"]
        existing_cols = [col for col in numeric_cols if col in responses_df.columns]
        if existing_cols:
            avg_df = responses_df[existing_cols].mean().reset_index()
            avg_df.columns = ["Métrica", "Média"]
            st.markdown("### Médias das Avaliações")
            st.table(avg_df)
        
        st.markdown("### Análises Gráficas")
        chart_recomendacao = alt.Chart(responses_df).mark_bar().encode(
            x=alt.X("recomendacao:Q", bin=alt.Bin(maxbins=10), title="Recomendação (0 a 10)"),
            y=alt.Y("count()", title="Contagem")
        ).properties(title="Distribuição da Recomendação")
        st.altair_chart(chart_recomendacao, use_container_width=True)
        
        chart_qualidade = alt.Chart(responses_df).mark_bar().encode(
            x=alt.X("qualidade:N", title="Qualidade do Trabalho"),
            y=alt.Y("count()", title="Contagem"),
            color=alt.Color("qualidade:N")
        ).properties(title="Distribuição da Qualidade do Trabalho")
        st.altair_chart(chart_qualidade, use_container_width=True)
        
        chart_produtividade = alt.Chart(responses_df).mark_bar().encode(
            x=alt.X("produtividade:Q", bin=alt.Bin(maxbins=5), title="Produtividade (1 a 5)"),
            y=alt.Y("count()", title="Contagem")
        ).properties(title="Distribuição da Produtividade")
        st.altair_chart(chart_produtividade, use_container_width=True)
        
        st.markdown("### Sugestão de Mentores")
        var_options = ["produtividade", "proatividade", "recomendacao", "criticas"]
        variable = st.selectbox("Selecione a variável para análise de mentoria:", var_options, key="mentor_var")
        suggestions, overall_avg = suggest_mentors(variable, responses_df, top_n=3)
        st.write(f"Média geral de **{variable}**: {overall_avg:.2f}")
        for evaluated, mentors_df in suggestions.items():
            st.markdown(f"**{evaluated}**:")
            if mentors_df.empty:
                st.write("Nenhum mentor sugerido.")
            else:
                st.write(mentors_df)
        
        excel_data = to_excel(responses_df)
        st.download_button(
            label="Baixar respostas em Excel",
            data=excel_data,
            file_name="avaliacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
