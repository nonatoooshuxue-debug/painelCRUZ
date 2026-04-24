import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Acompanhamento de Inadimplência")
@st.cache_data
def painel():
    df = pd.read_excel("PAINEL DE CR CRUZ.xlsx", skiprows=6)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df["DIAS"] = pd.to_numeric(df["DIAS"], errors = "coerce")
    df["VALOR"] = (df["VALOR"].astype(str).str.replace("R$", "", regex=False).str.replace(",", ".", regex=False).str.strip())
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
    df["RN"] = df["RN"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df


df_painel = painel()
gv_op = sorted(df_painel["NOME DO GC/GV"].dropna().astype(str).unique())
gv_sel = st.sidebar.selectbox("Escolha o GV/GC:", gv_op)

df_filtrado = df_painel[df_painel["NOME DO GC/GV"] == gv_sel]
rn_op = sorted(df_filtrado["RN"].dropna().astype(str).unique())
rn_sel = st.sidebar.multiselect("Escolha o(s) RN(s):", options=rn_op, default=rn_op)
df_filtrado2 = df_filtrado[df_filtrado["RN"].isin(rn_sel)]

faturamento = 3974115.00
meta_inad = 0.0030

df_inad = df_filtrado2[(df_filtrado2["DIAS"] <= -1) & (df_filtrado2["DIAS"] >= -30)]
valor_inad = df_inad["VALOR"].sum()
porcentagem_gv = (valor_inad / faturamento) if faturamento > 0 else 0

df_pdd = df_filtrado2[(df_filtrado2["DIAS"] <= -45) & (df_filtrado2["DIAS"] >= -75)]
valor_pdd = df_pdd["VALOR"].sum()
meta_pdd = 0.0012 
porcentagem_pdd = (valor_pdd / faturamento) if faturamento > 0 else 0

col1, col2 = st.columns(2)

with col1:
    variacao_inad = porcentagem_gv - meta_inad
    st.metric(
        label=f"INAD (1-30 dias) - {gv_sel}", 
        value=f"{porcentagem_gv:.2%}", 
        delta=f"{variacao_inad:.2%} vs meta", 
        delta_color="inverse"
    )
    st.caption(f"Valor: R$ {valor_inad:,.2f}")

with col2:
    variacao_pdd = porcentagem_pdd - meta_pdd
    st.metric(
        label=f"PDD (45-75 dias) - {gv_sel}", 
        value=f"{porcentagem_pdd:.2%}", 
        delta=f"{variacao_pdd:.2%} vs meta", 
        delta_color="inverse"
    )
    st.caption(f"Valor: R$ {valor_pdd:,.2f}")

st.divider()

st.subheader(f"Análise por Setores: {gv_sel}")
gv1, gv2 = st.columns(2)
with gv1:
    fig_inad = px.bar(df_inad, x="RN", y="VALOR", title=f"INAD (1-30 dias) por Setor: {gv_sel}", color_discrete_sequence=["#FF4B4B"]
    )
    st.plotly_chart(fig_inad, use_container_width=True)

with gv2:
    fig_pdd = px.bar(df_pdd, x="RN", y="VALOR", title=f"PDD (45-75 dias) por Setor: {gv_sel}", color_discrete_sequence=["#FF4B4B"]
    )
    st.plotly_chart(fig_pdd, use_container_width=True)


with st.expander("Visualizar Dados Filtrados"):
    st.dataframe(df_filtrado2, use_container_width=True)



