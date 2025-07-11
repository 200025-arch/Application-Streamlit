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

# === Partie gauche : Upload ===
with col2:
    afficher_logo("./Logoc.png")
    st.markdown("### Upload du fichier de données")
    uploaded_file = st.file_uploader("Selectionné un fichier CSV", type="csv", label_visibility="collapsed")

    if uploaded_file is not None:
        with st.spinner("Chargement du fichier..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_csv_path = tmp_file.name

            con = duckdb.connect(database=':memory:')
            con.execute(f"CREATE TABLE VES AS SELECT * FROM read_csv_auto('{tmp_csv_path}')")

            # Stocker les objets nécessaires
            st.session_state["duckdb_conn"] = con
            st.session_state["VEHS"] = "VES"

            # Convertir toute la table en DataFrame et stocker
            df = con.execute("SELECT * FROM VES").fetchdf()
            st.session_state["df"] = df

            preview = df.head(3)

            st.success(" Données chargées.")
            st.markdown("###  Aperçu :")
            st.dataframe(preview, use_container_width=True)

            # Bouton pour accéder au dashboard
            st.markdown(" Passez à l'onglet **Dashboard** pour continuer.")
            st.page_link("pages/dashboard.py", label="Accéder au Dashboard")

# === Partie droite : Présentation ===
with col1:
    st.markdown('<span style="text-align:center; color:#D80536; font-size:50px;font-weight:bold ;"><b><u>Projet Streamlit</u></b></span>', unsafe_allow_html=True)
    st.markdown('<span style="text-align:center; color:#8D9AAE; font-size:20px;font-weight:bold ;"><b><i>(Etude des specifications des vehicules electrique)</i></b></span>', unsafe_allow_html=True)
    st.markdown('<span style="text-align:center; color:#37040E; font-size:30px;font-weight:bold ;"><b><u>Contexte</u></b></span>', unsafe_allow_html=True)
    st.markdown("""
    La transition vers les véhicules électriques (VE) transforme profondément le secteur de la mobilité.Contrairement aux véhicules thermiques, les VE présentent des spécificités : autonomie limitée, 
    dépendance aux infrastructures de recharge, usure des batteries,impact du climat et des trajets sur la performance.

    Ce projet data vise à exploiter ces particularités pour analyser et optimiser l’usage des VE à partir de données 
    réelles. 
    L’objectif est de développer des visualisations pour :
    .Mieux comprendre les comportements de recharge et de conduite,
                
    .Évaluer l’impact des trajets et conditions sur l’autonomie,
                
    .Optimiser l’implantation des bornes,
                
    .Anticiper la dégradation des batteries.
                
    Ce projet s’inscrit dans une logique de mobilité durable, d’innovation technologique et d’aide à la décision pour les acteurs du secteur (constructeurs, opérateurs, collectivités).
    """)
    st.markdown('<span style="text-align:center; color:#37040E; font-size:30px;font-weight:bold ;"><b><u>Membre du groupe</u></b></span>', unsafe_allow_html=True)
    st.markdown("""
    .Eva Debora ASSY
                
    .Tonny MVOUMBI
                
    .Ange Muriel KAMGUEM
    """)