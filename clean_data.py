import pandas as pd
import numpy as np
import json
from shapely import wkt
from shapely.geometry import mapping

UP = "/mnt/user-data/uploads/"
OUT = "data/"

# ---------- 1. World Bank indicators (fichier 1) ----------
df1 = pd.read_csv(UP + "1787627548703_indicators-tgo.csv", skiprows=[1])
df1 = df1.drop_duplicates()

key_indicators = {
    "Access to electricity (% of population)": "elec_access_national",
    "Access to electricity, rural (% of rural population)": "elec_access_rural",
    "Access to electricity, urban (% of urban population)": "elec_access_urban",
    "Firms experiencing electrical outages (% of firms)": "firms_outages_pct",
    "Value lost due to electrical outages (% of sales for affected firms)": "outages_value_lost_pct",
    "Time required to get electricity (days)": "elec_connection_days",
    "Cost to get electricity connection (% of income per capita)": "elec_connection_cost_pct",
    "Getting electricity (rank)": "elec_getting_rank",
    "Main cooking fuel: wood (% of households)": "cook_wood_pct",
    "Main cooking fuel: charcoal (% of households)": "cook_charcoal_pct",
    "Main cooking fuel: LPG/natural gas/biogas (% of households)": "cook_lpg_pct",
    "Main cooking fuel: electricity  (% of households)": "cook_electricity_pct",
    "Access to clean fuels and technologies for cooking (% of population)": "clean_cooking_national",
    "Access to clean fuels and technologies for cooking, rural (% of rural population)": "clean_cooking_rural",
    "Access to clean fuels and technologies for cooking, urban (% of urban population)": "clean_cooking_urban",
    "Forest area (% of land area)": "forest_area_pct",
    "Forest area (sq. km)": "forest_area_sqkm",
    "Forest rents (% of GDP)": "forest_rents_pct_gdp",
    "Adjusted savings: net forest depletion (current US$)": "forest_depletion_usd",
    "Renewable energy consumption (% of total final energy consumption)": "renewable_energy_pct",
    "Energy intensity level of primary energy (MJ/$2017 PPP GDP)": "energy_intensity",
    "Total greenhouse gas emissions excluding LULUCF (Mt CO2e)": "ghg_total_excl_lulucf",
    "Total greenhouse gas emissions including LULUCF (Mt CO2e)": "ghg_total_incl_lulucf",
    "Total greenhouse gas emissions excluding LULUCF per capita (t CO2e/capita)": "ghg_per_capita",
    "Carbon dioxide (CO2) emissions (total) excluding LULUCF (Mt CO2e)": "co2_total",
    "Carbon dioxide (CO2) emissions from Power Industry (Energy) (Mt CO2e)": "co2_power_industry",
    "Carbon dioxide (CO2) emissions from Building (Energy) (Mt CO2e)": "co2_building_energy",
    "Carbon dioxide (CO2) emissions from Transport (Energy) (Mt CO2e)": "co2_transport",
    "Carbon dioxide (CO2) emissions from Industrial Combustion (Energy) (Mt CO2e)": "co2_industrial_combustion",
    "Carbon dioxide (CO2) net fluxes from LULUCF - Deforestation (Mt CO2e)": "co2_deforestation",
    "Methane (CH4) emissions (total) excluding LULUCF (Mt CO2e)": "ch4_total",
    "Methane (CH4) emissions from Agriculture (Mt CO2e)": "ch4_agriculture",
}

sub = df1[df1["Indicator Name"].isin(key_indicators.keys())].copy()
sub["var"] = sub["Indicator Name"].map(key_indicators)
sub = sub[["var", "Year", "Value"]].drop_duplicates(subset=["var", "Year"])
sub = sub.rename(columns={"Year": "year", "Value": "value"})
wb = sub.pivot(index="year", columns="var", values="value").reset_index().sort_values("year")
wb.to_csv(OUT + "wb_indicators.csv", index=False)
print("wb_indicators:", wb.shape)

# ---------- 2. GES par secteur 2018 (fichier 2) ----------
df2 = pd.read_csv(UP + "1787627706710_observationdata-xorttne.csv")
df2["type"] = df2["type"].replace({"mnooxydes d\u2019azote (N2O)": "Protoxyde d'azote (N2O)"})
df2 = df2.rename(columns={"secteur": "secteur", "type": "gaz", "Value": "value", "Date": "annee"})
df2 = df2[["secteur", "gaz", "annee", "value"]]
df2.to_csv(OUT + "ges_secteur_2018.csv", index=False)
print("ges_secteur_2018:", df2.shape)

# ---------- 3. Temperatures 10 villes (fichier 3) ----------
df3 = pd.read_csv(UP + "1787627927994_observationdata-yvlucze.csv")
df3["annee"] = df3["Date"].str.extract(r"(\d{4})").astype(int)
df3["mois"] = df3["Date"].str.extract(r"M(\d{1,2})").astype(int)
df3["date"] = pd.to_datetime(df3["annee"].astype(str) + "-" + df3["mois"].astype(str) + "-01")
df3 = df3.rename(columns={"libellés": "type_temp", "villes": "ville", "Value": "value"})
df3 = df3[["ville", "type_temp", "annee", "mois", "date", "value"]]

# ordre géographique Sud -> Nord (approx par latitude)
ordre_villes = ["Lomé", "Tabligbo", "Atakpamé", "Kouma konda", "Sotouboua",
                 "Sokodé", "Kara", "Niamtougou", "Dapaong", "Mango"]
df3["ville"] = pd.Categorical(df3["ville"], categories=ordre_villes, ordered=True)
df3.to_csv(OUT + "temperatures.csv", index=False)
print("temperatures:", df3.shape)

# ---------- 4. Combustibles renouvelables (fichier 4) ----------
df4 = pd.read_csv(UP + "1787628157132_energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv")
df4 = df4[["date", "value"]].rename(columns={"date": "year", "value": "combustible_renew_pct"})
df4.to_csv(OUT + "renewables_combustible.csv", index=False)
print("renewables_combustible:", df4.shape)

# ---------- 5. CO2 secteur energie longue serie (fichier 5) ----------
df5 = pd.read_csv(UP + "1787628254613_emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv")
df5 = df5[["date", "value"]].rename(columns={"date": "year", "value": "co2_power_industry_long"})
df5.to_csv(OUT + "co2_power_long.csv", index=False)
print("co2_power_long:", df5.shape)

# ---------- 6. Forets classees (fichier 6a) - conversion geometry WKT -> GeoJSON ----------
df6 = pd.read_csv(UP + "1787628520065_file-zones-protegees-forets-classees-23-12-2024-09-53-17.csv")

features = []
for _, row in df6.iterrows():
    try:
        geom = wkt.loads(row["geometry"])
        centroid = geom.centroid
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "nom": row["etab_nom"],
                "region": row["region_nom_bdd"],
                "prefecture": row["prefecture_nom_bdd"],
                "commune": row["commune_nom_bdd"],
                "canton": row["canton_nom_bdd"],
                "localite": row["nom_localite"],
                "creation": row["etab_creation_date"],
                "lat": centroid.y,
                "lon": centroid.x,
            }
        })
    except Exception as e:
        print("erreur geometry:", row["etab_nom"], e)

geojson = {"type": "FeatureCollection", "features": features}
with open(OUT + "forets.geojson", "w") as f:
    json.dump(geojson, f)

forets_df = pd.DataFrame([{**f["properties"]} for f in features])
forets_df.to_csv(OUT + "forets_table.csv", index=False)
print("forets:", forets_df.shape)

print("\nTerminé.")
