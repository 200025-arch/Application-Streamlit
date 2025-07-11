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
