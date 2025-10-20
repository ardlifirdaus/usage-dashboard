import plotly.express as px
import streamlit as st

def pie_chart(df, service_col, total_col, color_map, title):
    pie_data = df.groupby(service_col)[total_col].sum().reset_index()
    fig = px.pie(
        pie_data,
        names=service_col,
        values=total_col,
        hole=0.4,
        color=service_col,
        color_discrete_map=color_map
    )
    fig.update_traces(textinfo="percent+label", textposition="inside")
    st.subheader(title)
    st.plotly_chart(fig, config={"responsive": True})

def bar_chart(df_melt, service_col, color_map, title):
    fig = px.bar(
        df_melt,
        x="bulan",
        y="jumlah",
        color=service_col,
        barmode="stack",
        color_discrete_map=color_map
    )
    st.subheader(title)
    st.plotly_chart(fig, config={"responsive": True})

