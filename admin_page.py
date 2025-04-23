import streamlit as st
import pandas as pd
import altair as alt
from components import to_excel, clear_responses, get_evaluations_db
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(Paragraph('Relatório de Avaliações', styles['Heading1']))
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()


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
    st.markdown("Esta página é restrita ao RH. Insira a senha para continuar.")
    password = st.sidebar.text_input("Senha do RH", type="password")
    if password != "admin123":
        st.error("Senha incorreta! Acesso negado.")
        return
    st.success("Acesso autorizado para RH.")

    if st.sidebar.button("Remover dados de teste"):
        clear_responses()
        st.success("Dados removidos com sucesso.")

    st.sidebar.markdown("---")
    st.sidebar.write("**Filtros**")
    responses_df = get_evaluations_db()
    if responses_df.empty:
        st.warning("Nenhuma avaliação disponível.")
        return

    responses_df['timestamp'] = pd.to_datetime(responses_df['timestamp'])
    min_date = responses_df['timestamp'].min().date()
    max_date = responses_df['timestamp'].max().date()
    date_range = st.sidebar.date_input("Período", [min_date, max_date])
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        responses_df = responses_df[(responses_df['timestamp'] >= start) & (responses_df['timestamp'] <= end)]

    st.markdown("### Respostas das Avaliações")
    st.dataframe(responses_df, use_container_width=True)

    st.markdown("### Tendência de Métricas")
    present_numeric = [c for c in responses_df.columns if pd.api.types.is_numeric_dtype(responses_df[c]) and c not in ['id']]
    metric_trend = st.selectbox("Selecione métrica para tendência", present_numeric)
    # Agrupamento mensal sem usar resample para evitar erro de frequência
    trend_df = (
        responses_df
        .groupby(pd.Grouper(key='timestamp', freq='M'))
        [metric_trend]
        .mean()
        .reset_index()
    )
    line = alt.Chart(trend_df).mark_line(point=True).encode(
        x=alt.X('timestamp:T', title='Data'),
        y=alt.Y(f'{metric_trend}:Q', title=metric_trend.replace('_', ' ').title())
    ).properties(title=f'Tendência de {metric_trend.replace('_', ' ').title()}')
    st.altair_chart(line, use_container_width=True)

    if st.button("Exportar relatório em PDF"):
        pdf_bytes = generate_pdf(responses_df)
        st.download_button("Baixar PDF", pdf_bytes, file_name="relatorio_avaliacoes.pdf", mime="application/pdf")

    st.markdown("### Análise de Texto nos Comentários")
    texts = pd.concat([responses_df['pontos_positivos'], responses_df['pontos_melhoria']]).dropna()
    words = texts.str.cat(sep=' ').lower().split()
    freq = pd.Series(words).value_counts().head(10).reset_index()
    freq.columns = ['Palavra', 'Frequência']
    st.table(freq)

    st.markdown("### Rankings & Badges")
    top_eval = responses_df['evaluated'].value_counts().head(5).reset_index()
    top_eval.columns = ['Colaborador', 'Número de Avaliações']
    st.markdown("**Top 5 Colaboradores mais avaliados**")
    st.table(top_eval)
    avg_rec = responses_df.groupby('evaluated')['recomendacao'].mean().reset_index()
    badge_winners = avg_rec[avg_rec['recomendacao'] >= 8]
    st.markdown("**Badges (Recomendação >= 8)**")
    if badge_winners.empty:
        st.write("Nenhum colaborador com recomendação média >= 8.")
    else:
        st.write(badge_winners)

    excel_data = to_excel(responses_df)
    st.download_button(
        label="Baixar respostas em Excel",
        data=excel_data,
        file_name="avaliacoes_filtro.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
