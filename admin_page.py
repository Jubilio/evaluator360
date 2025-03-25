import streamlit as st
import pandas as pd
import altair as alt
from components import to_excel

def admin_page():
    st.title("Dashboard Administrativo")
    st.markdown("Esta página é restrita. Informe a senha de acesso.")
    
    admin_password = st.text_input("Senha de Admin", type="password", key="admin_password")
    if admin_password != "admin123":
        st.error("Senha incorreta!")
        st.stop()
    
    st.success("Acesso permitido!")
    st.markdown("### Respostas das Avaliações")
    
    if "avaliacoes" not in st.session_state or "df_to_evaluate" not in st.session_state:
        st.warning("Nenhuma avaliação encontrada. Certifique-se de que as avaliações foram registradas na página de Avaliação.")
    else:
        df_to_evaluate = st.session_state.df_to_evaluate.copy()
        avaliacoes = st.session_state.avaliacoes
        data_list = []
        for idx, row in df_to_evaluate.iterrows():
            col_id = row["id"]
            if col_id in avaliacoes:
                resposta = avaliacoes[col_id]
                data_list.append({
                    "Nome": row["name"],
                    "Posição": row["position"],
                    "Recomendação (0 a 10)": resposta.get("recomendacao"),
                    "Qualidade": resposta.get("qualidade"),
                    "Produtividade (1 a 5)": resposta.get("produtividade"),
                    "Trabalho em Equipe": resposta.get("trabalho_em_equipe"),
                    "Proatividade (1 a 5)": resposta.get("proatividade"),
                    "Resolução de Problemas": resposta.get("resolucao"),
                    "Lidar com Críticas (1 a 5)": resposta.get("criticas"),
                    "Adaptação": resposta.get("adaptabilidade"),
                    "Pontos Positivos": resposta.get("pontos_positivos"),
                    "Áreas para Melhoria": resposta.get("pontos_melhoria")
                })
        if data_list:
            df_respostas = pd.DataFrame(data_list)
            st.dataframe(df_respostas, use_container_width=True)
            
            st.markdown("### Análises Gráficas")
            chart_recomendacao = alt.Chart(df_respostas).mark_bar().encode(
                x=alt.X("Recomendação (0 a 10):Q", bin=alt.Bin(maxbins=10), title="Recomendação (0 a 10)"),
                y=alt.Y("count()", title="Contagem")
            ).properties(title="Distribuição da Recomendação")
            st.altair_chart(chart_recomendacao, use_container_width=True)
            
            chart_qualidade = alt.Chart(df_respostas).mark_bar().encode(
                x=alt.X("Qualidade:N", title="Qualidade do Trabalho"),
                y=alt.Y("count()", title="Contagem"),
                color=alt.Color("Qualidade:N")
            ).properties(title="Distribuição da Qualidade do Trabalho")
            st.altair_chart(chart_qualidade, use_container_width=True)
            
            chart_produtividade = alt.Chart(df_respostas).mark_bar().encode(
                x=alt.X("Produtividade (1 a 5):Q", bin=alt.Bin(maxbins=5), title="Produtividade (1 a 5)"),
                y=alt.Y("count()", title="Contagem")
            ).properties(title="Distribuição da Produtividade")
            st.altair_chart(chart_produtividade, use_container_width=True)
            
            excel_data = to_excel(df_respostas)
            st.download_button(
                label="Baixar respostas em Excel",
                data=excel_data,
                file_name="avaliacoes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Nenhuma resposta registrada ainda.")
