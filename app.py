import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_wb, load_ges_2018, load_temperatures, load_renewables_combustible,
    load_co2_power_long, load_forets_table, load_forets_geojson,
    REGION_COLORS, VILLES_ORDRE
)

st.set_page_config(
    page_title="Énergie & Environnement au Togo",
    page_icon="⚡",
    layout="wide",
)

# ---------- CSS léger ----------
st.markdown("""
<style>
.big-title {font-size: 2rem; font-weight: 700; margin-bottom:0;}
.subtitle {color: #6b7280; font-size: 1.05rem; margin-top:0;}
div[data-testid="stMetricValue"] {font-size: 1.6rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Données ----------
wb = load_wb()
ges = load_ges_2018()
temp = load_temperatures()
renew_combust = load_renewables_combustible()
co2_long = load_co2_power_long()
forets = load_forets_table()
forets_geojson = load_forets_geojson()

# ---------- En-tête ----------
st.markdown('<p class="big-title">⚡ Énergie, Climat & Forêts au Togo</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Électrifier les villages, développer les énergies propres, protéger les forêts — '
    'objectif national : accès universel à l\'électricité d\'ici 2030</p>',
    unsafe_allow_html=True
)

# ---------- KPIs globaux ----------
last = wb.dropna(subset=["elec_access_national"]).iloc[-1]
last_year = int(last["year"])
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Accès électricité (national)", f"{last['elec_access_national']:.1f}%", help=f"Année {last_year}")
c2.metric("Accès électricité (rural)", f"{wb.dropna(subset=['elec_access_rural']).iloc[-1]['elec_access_rural']:.1f}%")
c3.metric("Accès électricité (urbain)", f"{wb.dropna(subset=['elec_access_urban']).iloc[-1]['elec_access_urban']:.1f}%")
c4.metric("Superficie forestière", f"{wb.dropna(subset=['forest_area_pct']).iloc[-1]['forest_area_pct']:.1f}%", help="% du territoire")
c5.metric("Forêts classées cartographiées", f"{len(forets)}")

st.divider()

tabs = st.tabs([
    "🔌 Accès à l'électricité",
    "🔥 Énergie des ménages",
    "🏭 Émissions polluantes",
    "🌡️ Climat",
    "🌳 Aires protégées",
    "💡 Recommandations",
])

# ================= ONGLET 1 : ACCES ELECTRICITE =================
with tabs[0]:
    st.subheader("Évolution de l'accès à l'électricité : villes vs villages")

    df_e = wb.dropna(subset=["elec_access_national"], how="all")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_urban"], name="Urbain",
                              line=dict(color="#d95f02", width=3)))
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_rural"], name="Rural",
                              line=dict(color="#1b9e77", width=3)))
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_national"], name="National",
                              line=dict(color="#666666", width=2, dash="dot")))
    fig.add_hline(y=100, line_dash="dash", line_color="lightgray",
                  annotation_text="Objectif 2030 : 100%", annotation_position="top left")
    fig.update_layout(
        yaxis_title="% de la population avec accès", xaxis_title="Année",
        legend=dict(orientation="h", y=1.1), height=450,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    gap = df_e.dropna(subset=["elec_access_urban", "elec_access_rural"]).iloc[-1]
    ecart = gap["elec_access_urban"] - gap["elec_access_rural"]
    st.warning(
        f"⚠️ **Écart ville-campagne : {ecart:.1f} points** en {int(gap['year'])} "
        f"({gap['elec_access_urban']:.1f}% en ville contre {gap['elec_access_rural']:.1f}% en zone rurale). "
        "Cet écart s'est peu résorbé depuis 10 ans malgré la progression nationale."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Fiabilité du réseau : entreprises touchées par des coupures**")
        df_out = wb.dropna(subset=["firms_outages_pct"])[["year", "firms_outages_pct"]]
        fig2 = px.bar(df_out, x="year", y="firms_outages_pct",
                      labels={"firms_outages_pct": "% d'entreprises touchées", "year": "Année"},
                      color_discrete_sequence=["#d95f02"])
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("**Délai et coût de raccordement électrique**")
        df_conn = wb.dropna(subset=["elec_connection_days"])[["year", "elec_connection_days"]]
        if not df_conn.empty:
            fig3 = px.bar(df_conn, x="year", y="elec_connection_days",
                          labels={"elec_connection_days": "Jours nécessaires", "year": "Année"},
                          color_discrete_sequence=["#7570b3"])
            fig3.update_layout(height=350)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Données de délai de raccordement non disponibles sur la période.")

# ================= ONGLET 2 : ENERGIE DES MENAGES =================
with tabs[1]:
    st.subheader("Dépendance au bois et au charbon de bois pour la cuisson")

    df_cook = wb.dropna(subset=["cook_wood_pct"], how="all")
    if not df_cook.empty:
        cook_cols = ["cook_wood_pct", "cook_charcoal_pct", "cook_lpg_pct", "cook_electricity_pct"]
        labels = {"cook_wood_pct": "Bois", "cook_charcoal_pct": "Charbon de bois",
                  "cook_lpg_pct": "Gaz (LPG)", "cook_electricity_pct": "Électricité"}
        melted = df_cook.melt(id_vars="year", value_vars=cook_cols, var_name="combustible", value_name="pct")
        melted["combustible"] = melted["combustible"].map(labels)
        fig4 = px.bar(melted, x="year", y="pct", color="combustible", barmode="group",
                      color_discrete_map={"Bois": "#8c510a", "Charbon de bois": "#333333",
                                          "Gaz (LPG)": "#1b9e77", "Électricité": "#377eb8"},
                      labels={"pct": "% des ménages", "year": "Année", "combustible": "Combustible principal"})
        fig4.update_layout(height=420)
        st.plotly_chart(fig4, use_container_width=True)

        last_cook = df_cook.iloc[-1]
        bois_charbon = last_cook["cook_wood_pct"] + last_cook["cook_charcoal_pct"]
        st.error(
            f"🔥 **{bois_charbon:.0f}% des ménages** utilisent encore le bois ou le charbon de bois pour cuisiner "
            f"(données {int(last_cook['year'])}), contre seulement **{last_cook['cook_lpg_pct']:.1f}%** au gaz."
        )
    else:
        st.info("Données de combustible de cuisson limitées à 2 points de mesure (2014, 2017).")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Accès aux modes de cuisson propres : ville vs village**")
        df_clean = wb.dropna(subset=["clean_cooking_national"], how="all")
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=df_clean["year"], y=df_clean["clean_cooking_urban"], name="Urbain", line=dict(color="#d95f02")))
        fig5.add_trace(go.Scatter(x=df_clean["year"], y=df_clean["clean_cooking_rural"], name="Rural", line=dict(color="#1b9e77")))
        fig5.update_layout(yaxis_title="% population", height=380, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.markdown("**Recul de la superficie forestière**")
        df_forest = wb.dropna(subset=["forest_area_sqkm"])[["year", "forest_area_sqkm"]]
        fig6 = px.area(df_forest, x="year", y="forest_area_sqkm",
                       labels={"forest_area_sqkm": "Superficie (km²)", "year": "Année"},
                       color_discrete_sequence=["#1b9e77"])
        fig6.update_layout(height=380)
        st.plotly_chart(fig6, use_container_width=True)
        perte = df_forest.iloc[0]["forest_area_sqkm"] - df_forest.iloc[-1]["forest_area_sqkm"]
        st.caption(f"Perte de **{perte:,.0f} km²** de forêt entre {int(df_forest.iloc[0]['year'])} et {int(df_forest.iloc[-1]['year'])}.")

# ================= ONGLET 3 : EMISSIONS =================
with tabs[2]:
    st.subheader("Bilan des émissions de gaz à effet de serre (2018)")

    ges_total = ges[(ges["secteur"] != "Total") & (ges["gaz"] == "Total")].sort_values("value", ascending=False)
    fig7 = px.bar(ges_total, x="value", y="secteur", orientation="h",
                  labels={"value": "Émissions (Gg)", "secteur": ""},
                  color="secteur",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig7.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig7, use_container_width=True)

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown("**Répartition par type de gaz et par secteur**")
        ges_detail = ges[(ges["secteur"] != "Total") & (ges["gaz"] != "Total")]
        fig8 = px.bar(ges_detail, x="secteur", y="value", color="gaz", barmode="stack",
                      labels={"value": "Émissions (Gg)", "secteur": "", "gaz": "Gaz"},
                      color_discrete_map={"Dioxyde de carbone (CO2)": "#555555",
                                          "Méthane(CH4)": "#1b9e77",
                                          "Protoxyde d'azote (N2O)": "#d95f02"})
        fig8.update_layout(height=420, xaxis_tickangle=-20)
        st.plotly_chart(fig8, use_container_width=True)

    with col2:
        energie_pct = ges_total[ges_total["secteur"] == "Energie"]["value"].values[0] / ges_total["value"].sum() * 100
        st.metric("Part du secteur Énergie dans les émissions totales", f"{energie_pct:.1f}%")
        st.caption(
            "Le secteur **Agriculture, Foresterie et Affectation des Terres (AFAT)** domine largement "
            "le bilan togolais — principalement lié au recul forestier et aux pratiques agricoles, "
            "et non à la production d'électricité elle-même."
        )

    st.markdown("**Évolution longue des émissions CO₂ du secteur électrique (production d'énergie)**")
    fig9 = px.area(co2_long.dropna(), x="year", y="co2_power_industry_long",
                   labels={"co2_power_industry_long": "Émissions CO₂ (Mt CO2e)", "year": "Année"},
                   color_discrete_sequence=["#d95f02"])
    fig9.update_layout(height=350)
    st.plotly_chart(fig9, use_container_width=True)
    st.caption("La hausse depuis 2014 reflète le développement du parc de production électrique national.")

# ================= ONGLET 4 : CLIMAT =================
with tabs[3]:
    st.subheader("Variations climatiques du Sud au Nord (2013-2019)")

    col1, col2 = st.columns([1, 3])
    with col1:
        type_temp = st.radio("Type de température", ["Températures maximales", "Températures minimales"])
        villes_sel = st.multiselect("Villes", VILLES_ORDRE, default=VILLES_ORDRE)

    with col2:
        df_t = temp[(temp["type_temp"] == type_temp) & (temp["ville"].isin(villes_sel))]
        fig10 = px.line(df_t, x="date", y="value", color="ville",
                        category_orders={"ville": VILLES_ORDRE},
                        labels={"value": "Température (°C)", "date": ""},
                        color_discrete_sequence=px.colors.sequential.Turbo)
        fig10.update_layout(height=420, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig10, use_container_width=True)

    st.markdown("**Température moyenne par ville (Sud → Nord)**")
    avg_by_ville = temp[temp["type_temp"] == type_temp].groupby("ville", observed=True)["value"].mean().reindex(VILLES_ORDRE).reset_index()
    fig11 = px.bar(avg_by_ville, x="ville", y="value",
                   labels={"value": "Température moyenne (°C)", "ville": ""},
                   color="value", color_continuous_scale="OrRd")
    fig11.update_layout(height=350, coloraxis_showscale=False)
    st.plotly_chart(fig11, use_container_width=True)

    ecart_climat = avg_by_ville["value"].max() - avg_by_ville["value"].min()
    st.info(
        f"🌡️ Écart moyen de **{ecart_climat:.1f}°C** entre les villes les plus chaudes du Nord (Dapaong, Mango) "
        "et le Sud côtier. Les zones les plus chaudes accentuent la pression sur le bois-énergie pour la cuisson "
        "et augmentent les besoins en réfrigération/ventilation électrique."
    )

# ================= ONGLET 5 : FORETS / CARTE =================
with tabs[4]:
    st.subheader("Cartographie des 53 forêts classées et aires protégées")

    col1, col2 = st.columns([1, 3])
    with col1:
        regions_sel = st.multiselect("Régions", sorted(forets["region"].unique()),
                                      default=sorted(forets["region"].unique()))
        st.markdown("**Répartition par région**")
        counts = forets["region"].value_counts().reindex(sorted(forets["region"].unique())).fillna(0)
        for r, n in counts.items():
            st.caption(f"🟢 {r} : {int(n)} forêts")

    with col2:
        forets_f = forets[forets["region"].isin(regions_sel)]
        geojson_f = {
            "type": "FeatureCollection",
            "features": [f for f in forets_geojson["features"] if f["properties"]["region"] in regions_sel]
        }

        fig_map = go.Figure()
        fig_map.add_trace(go.Choroplethmapbox(
            geojson=geojson_f,
            locations=[f["properties"]["nom"] for f in geojson_f["features"]],
            z=[1] * len(geojson_f["features"]),
            featureidkey="properties.nom",
            colorscale=[[0, "#1b9e77"], [1, "#1b9e77"]],
            showscale=False,
            marker_opacity=0.6,
            marker_line_width=1,
            marker_line_color="#0b6b4f",
            text=[f["properties"]["nom"] for f in geojson_f["features"]],
            hovertemplate="%{text}<extra></extra>",
        ))
        fig_map.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=6.2,
            mapbox_center={"lat": 8.6, "lon": 1.0},
            height=550,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("**Forêts par région et ancienneté de classement**")
    forets_display = forets_f[["nom", "region", "prefecture", "commune", "creation"]].rename(
        columns={"nom": "Nom", "region": "Région", "prefecture": "Préfecture",
                 "commune": "Commune", "creation": "Année de création"}
    )
    st.dataframe(forets_display, use_container_width=True, hide_index=True)

    st.warning(
        "⚠️ La région **Savanes**, la plus chaude et la plus soumise à la déforestation pour le bois-énergie, "
        "ne compte que **4 forêts classées** sur les 53 — la couverture de protection y est la plus faible "
        "alors que la pression climatique y est la plus forte."
    )

# ================= ONGLET 6 : RECOMMANDATIONS =================
with tabs[5]:
    st.subheader("Recommandations stratégiques")

    st.markdown("""
Sur la base des constats du dashboard, trois axes d'action se dégagent pour tenir l'objectif d'accès
universel à l'électricité en 2030 tout en protégeant les forêts.
    """)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("#### ☀️ Électrifier les villages")
        st.markdown("""
- Kits solaires individuels et mini-réseaux solaires villageois dans les zones rurales les plus isolées (écart de 71 points avec les villes)
- Prioriser les régions Savanes et Kara, où l'accès rural est le plus faible et le climat le plus rude
- Réduire les délais et coûts de raccordement pour lever un frein direct à l'adoption
        """)
    with r2:
        st.markdown("#### 🔥 Cuisson propre")
        st.markdown("""
- Subventionner les foyers améliorés à bois/charbon (réduction 30-50% de la consommation de bois)
- Développer la filière gaz butane (LPG) en zone rurale, aujourd'hui quasi absente hors des villes
- Sensibiliser dans les zones à forte dépendance au bois-énergie, en particulier au Nord
        """)
    with r3:
        st.markdown("#### 🌳 Protéger les forêts")
        st.markdown("""
- Renforcer la surveillance et le reboisement dans les régions Plateaux et Savanes, les plus exposées
- Étendre le réseau de forêts classées dans la région Savanes, sous-représentée (4 sur 53)
- Lier explicitement les projets d'électrification rurale à des clauses de réduction de la coupe de bois
        """)

    st.divider()
    st.markdown("""
**Constat clé reliant les trois axes** : tant que l'électricité n'atteint pas les villages, les ménages
restent dépendants du bois pour cuisiner — ce qui alimente la déforestation, laquelle aggrave à son tour
la hausse locale des températures observée notamment au Nord. Électrification rurale, cuisson propre et
protection forestière doivent donc être traitées comme un seul programme intégré, et non trois politiques séparées.
    """)
