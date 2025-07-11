import streamlit as st
import duckdb
import tempfile
import base64


st.set_page_config(page_title="Upload de fichier", layout="wide")

st.markdown("""
    <style>
        /* Cache complètement la sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Étend la zone principale sur toute la largeur */
        [data-testid="stAppViewContainer"] > div:first-child {
            padding-left: 0rem;
        }
    </style>
""", unsafe_allow_html=True)
# === Configuration de la page ===
def afficher_logo(path, largeur=100):
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            st.markdown(
                f'<div style="text-align: center;"><img src="data:image/png;base64,{encoded}" width="{largeur}" ></div>',
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        pass

st.markdown("""
    <style>
    /* Conteneur Streamlit Columns */
    .stColumns > div:first-child {
        background-color: #0E3843; /* gris clair */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)
#afficher_logo("./Logoc.png")
# === Mise en page : deux colonnes ===
col1, col2 = st.columns([1, 1])  # gauche (upload), droite (présentation)