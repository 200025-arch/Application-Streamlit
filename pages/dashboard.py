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

    #Creation de la clause Where pour les filtres
    #Espace Requetes
    def format_sql_list(values):
            if not values:
                return "('')"
            if len(values) == 1:
                return f"('{values[0]}')"
            return str(tuple(values))

    where_clauses = []
    if brands:
       where_clauses.append(f"brand IN {format_sql_list(brands)}")
    if body_type:
       where_clauses.append(f"car_body_type IN {format_sql_list(body_type)}")
       where_clauses.append(f"CAST(range_km AS DOUBLE) >= {min_range}")
       where_clauses.append(f"CAST(battery_capacity_kWh AS DOUBLE) >= {min_battery}")
       where_sql = " AND ".join(where_clauses)  

    #Gestion des KPI
    query = f"""
        SELECT 
            AVG(CAST(range_km AS DOUBLE)) AS avg_range,
            FROM VES
            WHERE {where_sql}
        """
    query2 = f"""
        SELECT model, brand, MAX(CAST(range_km AS DOUBLE)) AS autonomie_max
            FROM VES
            WHERE {where_sql}
            AND  range_km IS NOT NULL
            GROUP BY model, brand
            ORDER BY autonomie_max DESC
            LIMIT 1
        """
    query3 = f"""
        SELECT car_body_type, COUNT(*) AS total
            FROM VES
            WHERE {where_sql} 
            AND car_body_type IS NOT NULL
            GROUP BY car_body_type
            ORDER BY total DESC
            LIMIT 1;
        """

    query4 = f"""
        SELECT brand, MAX(CAST(fast_charging_power_kw_dc AS DOUBLE)) AS max_charge
            FROM VES
            WHERE {where_sql} 
            AND fast_charging_power_kw_dc IS NOT NULL
            GROUP BY brand
            ORDER BY max_charge DESC
            LIMIT 1;
        """
    query5 = f"""
        SELECT brand, COUNT(*) AS total_vehicules
            FROM VES
            WHERE {where_sql} 
            AND brand IS NOT NULL
            GROUP BY brand
            ORDER BY total_vehicules DESC
            LIMIT 1;
        """
 

    dfkpi = con.execute(query).df().iloc[0]
    dfkpi2 = con.execute(query2).df().iloc[0]
    dfkpi3 = con.execute(query3).df().iloc[0]
    dfkpi4 = con.execute(query4).df().iloc[0]
    dfkpi5 = con.execute(query5).df().iloc[0]

#Affichage KPI
    st.title(" ")
    col1, col2, col3, col4, col5 = st.columns(5)

    def kpi_card(title, value, suffix=""):
        st.markdown(f""" <div class="kpi-card"> <div class="kpi-title">{title}</div><div class="kpi-value">{value} {suffix}</div></div>""", unsafe_allow_html=True)

    def kpi_cards(title, nom,valeur, suffix=""):
        st.markdown(f"""<div class='kpi-card' ><div class="kpi-title">{title}</div><div class="kpi-value">{nom}<span style='color:#2e8b57; font-size:20px;'> |{valeur} {suffix}</span></div></div>""", unsafe_allow_html=True)
    def kpi_cardSs(title, nom,valeur, suffix=""):
        st.markdown(f"""<div class='kpi-card' ><div class="kpi-title">{title}</div><div class="kpi-value">{nom}<span style='color:#D80536; font-size:20px;'> |{valeur} {suffix}</span></div></div>""", unsafe_allow_html=True)


    with col1:
        kpi_card("Autonomie moyenne", round(dfkpi["avg_range"], 0), "km")
    with col2:
        kpi_cards("Model Econome", dfkpi2["model"], dfkpi2["autonomie_max"],"Wh/km")            
    with col3:
        kpi_cards("Vehicule dominant", dfkpi3["car_body_type"],dfkpi3["total"],"Ves")

    with col4:
        kpi_cards("Marque/PC rapide", dfkpi4["brand"],dfkpi4["max_charge"],"Puiss.")

    with col5:
        kpi_cardSs("Marque La Moins utilsé", dfkpi5["brand"],dfkpi5["total_vehicules"],"Ves")
