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

