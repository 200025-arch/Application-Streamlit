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
        st.markdown(f"""<div class='kpi-card' ><div class="kpi-title">{title}</div><div class="kpi-value">{nom}<span style='color:#2e8b57; font-size:15px;'> |{valeur} {suffix}</span></div></div>""", unsafe_allow_html=True)
    def kpi_cardSs(title, nom,valeur, suffix=""):
        st.markdown(f"""<div class='kpi-card' ><div class="kpi-title">{title}</div><div class="kpi-value">{nom}<span style='color:#D80536; font-size:15px;'> |{valeur} {suffix}</span></div></div>""", unsafe_allow_html=True)


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




    #Visualisation
    #graphe 1
    dfV1 = f"""
    SELECT brand, AVG(CAST(range_km AS DOUBLE)) AS autonomie_moy
    FROM VES
    WHERE {where_sql}
    GROUP BY brand
    ORDER BY autonomie_moy DESC
    LIMIT 10
    """
    dfviz = con.execute(dfV1).df()
    fig = px.bar(
        dfviz,
        x="autonomie_moy",
        y="brand",
        orientation='h',
        color_discrete_sequence=["#EE2449"],
        title="Autonomie moyenne par marque (Top 10)"
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#EDF2F4",
        font=dict(color="#2B2E42"),
        title_font_size=20,
        xaxis_title="Autonomie (km)",
        yaxis_title="Marque",
        yaxis=dict(categoryorder='total ascending')
    )

    #graphe2
    dfV2 = con.execute(f"""
        SELECT AVG(CAST(efficiency_wh_per_km AS DOUBLE)) AS val
        FROM VES WHERE {where_sql}
    """).fetchone()[0]
    fig1= go.Figure(go.Indicator(
        mode="gauge+number",
        value=dfV2,
        title={'text': "Efficacité moyenne (Wh/km)"},
        gauge={
            'axis': {'range': [100, 200]},
            'bar': {'color': "#EE2449"},
            'steps': [{'range': [100, 140], 'color': "#FDEDEC"},
                    {'range': [140, 200], 'color': "#FADBD8"}]
        }
    ))
    fig1.update_layout(height=300, paper_bgcolor="#EDF2F4", font_color="#2B2E42")


    # graphe 3
    dfV3 = con.execute(f"""
        SELECT car_body_type, COUNT(*) AS count
        FROM VES WHERE {where_sql}
        GROUP BY car_body_type
    """).df()
    fig2 = px.pie(dfV3, names="car_body_type", values="count",
                color_discrete_sequence=["#EE2449", "#D80536", "#8D9AAE", "#2B2E42", "#EDF2F4"],
                title="Répartition par type de carrosserie")
    fig2.update_traces(textinfo='percent+label')
    fig2.update_layout(paper_bgcolor="#EDF2F4", font_color="#2B2E42")

    #Graphe 4
    dfV4 = con.execute(f"""
        SELECT segment, CAST(range_km AS DOUBLE) AS range_km
        FROM VES WHERE {where_sql}
    """).df()
    fig3 = px.box(dfV4, x="segment", y="range_km", color_discrete_sequence=["#EE2449"],
                title="Autonomie par segment")
    fig3.update_layout(paper_bgcolor="#EDF2F4", plot_bgcolor="#FFFFFF", font_color="#2B2E42")

    #Graphe5
    dfV5 = con.execute(f"""
        SELECT brand, CAST(efficiency_wh_per_km AS DOUBLE) AS efficiency
        FROM VES WHERE {where_sql}
        AND brand IN ('Tesla', 'BMW') AND efficiency_wh_per_km IS NOT NULL
    """).df()
    fig4 = px.histogram(dfV5, x="efficiency", color="brand", barmode="overlay",
                            color_discrete_map={"Tesla": "#EE2449", "BMW": "#8D9AAE"},
                            title="Histogramme superposé : efficacité Tesla vs BMW")
    fig4.update_layout(paper_bgcolor="#EDF2F4", font_color="#2B2E42", height=300)

    fig.update_layout(height=350)
    fig1.update_layout(height=350)
    fig2.update_layout(height=350)
    fig3.update_layout(height=350)
    fig4.update_layout(height=350)

    #Affichage des Visuels

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(fig1, use_container_width=True)
    with col3:
        st.plotly_chart(fig2, use_container_width=True)

    col4, col5 = st.columns(2)
    with col4:
        st.plotly_chart(fig3, use_container_width=True)
    with col5:
        st.plotly_chart(fig4, use_container_width=True)

else:
    st.title(" ")
    st.error(" Aucune connexion détectée.\n\nVeuillez recharger le fichier pour initialiser correctement les données.")
    st.info("Redirection vers la page d’accueil...")




# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
/* Supprimer le menu et le footer Streamlit */
#MainMenu, footer {visibility: hidden;}
html, body, .main, .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* Topbar*/
.topbar {
    width: 100%;
    background-color: #2B2E42;
    padding: 0.25rem 1rem;
    height: 50px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #ccc;
    z-index: 999;
    position: fixed;
    top: 0;
}
.topbar h1 {
    font-size: 20px;
    color: #8D9AAE;
    margin: 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #8D9AAE;
    color: white;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)
# CSS pour  KPI
st.markdown("""
    <style>
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        overflow-x: auto;
    }
    .kpi-card {
        background-color: white;
        padding: 1.5rem 1.5rem 1.2rem 1rem;
        border-radius: 12px;
        border-left: 5px solid #EE2449;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        transition: 0.2s ease-in-out;
        min-width: 200px;
        flex: 1;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .kpi-title {
        font-size: 15px;
        color: #7f8c8d;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-value {
        font-size: 30px;
        font-weight: 600;
        color: #111827;
    }
    .kpi-icon {
        font-size: 32px;
        color: #EE2449;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)