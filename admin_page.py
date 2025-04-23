import streamlit as st
import pandas as pd
import altair as alt
from components import to_excel, clear_responses, get_evaluations_db


def suggest_mentors(variable: str, responses_df: pd.DataFrame, top_n: int = 3):
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
    st.markdown("**Acesso restrito ao RH**")

    # Inicializa estado de login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Campo de senha
    password = st.sidebar.text_input("Senha do RH", type="password", key="admin_pwd")

    # Processa login
    if not st.session_state.logged_in:
        if st.sidebar.button("Entrar"):
            if password == "admin123":
                st.session_state.logged_in = True
                st.sidebar.success("Acesso autorizado para RH.")
            else:
                st.sidebar.error("Senha incorreta! Acesso negado.")
        else:
            st.sidebar.info("Digite a senha e clique em Entrar para acessar o dashboard.")
            return

    # Botão para limpar dados de teste
    if st.sidebar.button("Remover dados de teste"):
        clear_responses()
        st.sidebar.success("Dados removidos com sucesso.")

    # Carrega todas as avaliações e exibe
    df_all = get_evaluations_db()
    if df_all.empty:
        st.warning("Nenhuma avaliação disponível.")
        return
    st.markdown("### Todas as Respostas das Avaliações")
    st.dataframe(df_all, use_container_width=True)

    # Filtros por período
    st.sidebar.markdown("---")
    st.sidebar.header("Filtros por período")
    df = df_all.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    date_range = st.sidebar.date_input(
        label="Selecione o período", 
        value=[min_date, max_date],
        label_visibility="visible"
    )
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        if not filtered.empty:
            df = filtered
        else:
            st.warning(
                "Nenhum registro no período selecionado. "
                "Exibindo todas as avaliações."  
            )

    # Cálculo de médias
    numeric_cols = [
        'recomendacao','produtividade','proatividade',
        'adaptabilidade','autonomia','gestao_equipa',
        'operacionalizacao','comunicacao_eficaz',
        'tarefa_atempada','qualidade_resultados'
    ]
    available = [c for c in numeric_cols if c in df.columns]
    if available:
        avg_df = df[available].mean().reset_index()
        avg_df.columns = ['Métrica','Média']
        st.markdown("### Médias Gerais")
        st.table(avg_df)

    # Gráfico de tendência mensal
    if available:
        st.markdown("### Tendência de Métricas (Mensal)")
        metric = st.selectbox("Selecione métrica para tendência", available, key="trend_metric")
        trend_df = (
            df.groupby(pd.Grouper(key='timestamp', freq='ME'))
              [metric]
              .mean()
              .reset_index()
        )
        if not trend_df.empty:
            chart = alt.Chart(trend_df).mark_line(point=True).encode(
                x=alt.X('timestamp:T', title='Mês'),
                y=alt.Y(f'{metric}:Q', title=metric.replace('_',' ').title())
            ).properties(title=f'Tendência de {metric.replace('_',' ').title()}')
            st.altair_chart(chart, use_container_width=True)

    # Nuvem de palavras
    st.markdown("### Nuvem de Palavras (Comentários)")
    if 'pontos_positivos' in df.columns and 'pontos_melhoria' in df.columns:
        texts = pd.concat([df['pontos_positivos'], df['pontos_melhoria']]).dropna()
        if not texts.empty:
            words = texts.str.cat(sep=' ').lower().split()
            freq = pd.Series(words).value_counts().head(10).reset_index()
            freq.columns = ['Palavra','Frequência']
            st.table(freq)

    # Sugestão de mentores
    if available:
        st.markdown("### Sugestão de Mentores")
        var = st.selectbox("Variável para mentoria", available, key='mentor_var')
        suggestions, overall = suggest_mentors(var, df)
        st.write(f"Média geral de **{var.replace('_',' ').title()}**: {overall:.2f}")
        for avaliado, mentors in suggestions.items():
            st.markdown(f"**{avaliado}**")
            if not mentors.empty:
                st.dataframe(mentors)
            else:
                st.write("Nenhum mentor sugerido.")

    # Rankings & Badges
    st.markdown("### Rankings & Badges")
    top5 = df['evaluated'].value_counts().head(5).reset_index()
    top5.columns = ['Colaborador','Avaliações']
    st.markdown("**Top 5 Avaliados**")
    st.table(top5)
    rec_avg = df.groupby('evaluated')['recomendacao'].mean().reset_index()
    badges = rec_avg[rec_avg['recomendacao'] >= 8]
    st.markdown("**Badges (Recomendação >= 8)**")
    if not badges.empty:
        st.table(badges)

    # Exportação Excel
    st.markdown("### Exportar Dados")
    excel = to_excel(df)
    st.download_button(
        "Download Excel", excel, "avaliacoes_filtradas.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
