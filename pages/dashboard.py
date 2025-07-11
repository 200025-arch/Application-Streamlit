import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


#configuration de la page
st.set_page_config(page_title="Tableau de bord Vehicule electrique", layout="wide")

# Utiliser la connexion DuckDB page Home
con = st.session_state.get("duckdb_conn")

# --- TOPBAR ---
st.markdown("""<div class="topbar"><h1>Tableau de bord</h1></div>""", unsafe_allow_html=True)

if con is not None:

    # --- SIDEBAR ---
    with st.sidebar:
        df = con.execute(""" SELECT * FROM VES """).fetchdf()
        st.sidebar.header("Filtres")
        brands = st.sidebar.multiselect("Marque", options=df["brand"].unique(), default=df["brand"].unique())
        min_range = st.sidebar.slider("Autonomie minimale (km)", min_value=0, max_value=int(df["range_km"].dropna().astype(int).max()), value=0)
        min_battery = st.sidebar.slider("Capacité batterie min (kWh)", min_value=0.0, max_value=float(df["battery_capacity_kWh"].dropna().astype(float).max()), value=0.0)
        body_type = st.sidebar.multiselect("Type de carrosserie", options=df["car_body_type"].unique(), default=df["car_body_type"].unique())