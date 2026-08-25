import pandas as pd
import json
import streamlit as st

DATA = "data/"

REGION_COLORS = {
    "Maritime": "#1b9e77",
    "Plateaux": "#d95f02",
    "Centrale": "#7570b3",
    "Kara": "#e7298a",
    "Savanes": "#66a61e",
}

VILLES_ORDRE = ["Lomé", "Tabligbo", "Atakpamé", "Kouma konda", "Sotouboua",
                "Sokodé", "Kara", "Niamtougou", "Dapaong", "Mango"]


@st.cache_data
def load_wb():
    return pd.read_csv(DATA + "wb_indicators.csv")


@st.cache_data
def load_ges_2018():
    return pd.read_csv(DATA + "ges_secteur_2018.csv")


@st.cache_data
def load_temperatures():
    df = pd.read_csv(DATA + "temperatures.csv", parse_dates=["date"])
    df["ville"] = pd.Categorical(df["ville"], categories=VILLES_ORDRE, ordered=True)
    return df


@st.cache_data
def load_renewables_combustible():
    return pd.read_csv(DATA + "renewables_combustible.csv")


@st.cache_data
def load_co2_power_long():
    return pd.read_csv(DATA + "co2_power_long.csv")


@st.cache_data
def load_forets_table():
    return pd.read_csv(DATA + "forets_table.csv")


@st.cache_data
def load_forets_geojson():
    with open(DATA + "forets.geojson") as f:
        return json.load(f)


def kpi_card(col, label, value, help_text=None, delta=None):
    col.metric(label, value, delta=delta, help=help_text)
