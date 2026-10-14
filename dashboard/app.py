from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="AEM–KL Merger Post-Mortem", layout="wide")


@st.cache_data
def load(name, **kwargs):
    return pd.read_csv(DATA / f"{name}.csv", **kwargs)


st.title("Agnico Eagle & Kirkland Lake Gold: Merger Post-Mortem")
st.caption("All-stock merger of equals announced September 28, 2021, closed February 8, 2022.")

tabs = st.tabs(["Overview", "Deal & Synergies", "Market Reaction", "Operations", "Valuation", "Limitations"])

with tabs[0]:
    st.write("Overview — coming next.")

with tabs[1]:
    st.write("Deal & Synergies — coming next.")

with tabs[2]:
    st.write("Market Reaction — coming next.")

with tabs[3]:
    st.write("Operations — coming next.")

with tabs[4]:
    st.write("Valuation — coming next.")

with tabs[5]:
    st.write("Limitations — coming next.")