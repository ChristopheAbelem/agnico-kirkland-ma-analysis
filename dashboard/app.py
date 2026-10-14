from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data"

COLORS = {"AEM": "#1f77b4", "NEM": "#ff7f0e", "B": "#7f7f7f"}

st.set_page_config(page_title="AEM–KL Merger Post-Mortem", layout="wide")


@st.cache_data
def load(name, **kwargs):
    return pd.read_csv(DATA / f"{name}.csv", **kwargs)


st.title("Agnico Eagle & Kirkland Lake Gold: Merger Post-Mortem")
st.caption("All-stock merger of equals announced September 28, 2021, closed February 8, 2022.")

tabs = st.tabs(["Overview", "Deal & Synergies", "Market Reaction", "Operations", "Valuation", "Limitations"])

with tabs[0]:
    windows = load("stock_windows", index_col="Window")
    aisc = load("aisc", index_col="Year")
    syn = load("synergies")
    pe = load("pe_table", index_col="Year")

    # KPIs computed from the exported tables
    after = windows.loc["After announcement"]
    peers_ret = after[["NEM", "B"]].mean()

    aisc_chg = (aisc.loc[2025] / aisc.loc[2022] - 1) * 100
    peers_aisc = aisc_chg[["NEM", "B"]].mean()

    reported = syn.loc[syn["Type"] != "Target", "USD_M"].sum()
    target = syn.loc[syn["Type"] == "Target", "USD_M"].sum()

    pe25 = pe.loc[2025]
    peers_pe = pe25[["NEM_PE", "B_PE"]].mean()
    pe_prem = (pe25["AEM_PE"] / peers_pe - 1) * 100

    st.subheader("Verdict")
    st.write(
        "Partially. Agnico Eagle kept unit-cost growth below its peers' and its stock moved from "
        "lagging them before the announcement to leading them after. But the reported synergies "
        "explain only a small part of the cost advantage, margin expansion follows the gold price, "
        "and other events (such as the 2023 Yamana acquisition) happened in the same period. "
        "The data cannot isolate how much of the outperformance is due to the merger."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AEM return since announcement", f"{after['AEM']:.0f}%",
              f"{after['AEM'] - peers_ret:+.0f} pts vs peers")
    c2.metric("AISC growth 2022–2025", f"{aisc_chg['AEM']:.0f}%",
              f"{aisc_chg['AEM'] - peers_aisc:+.0f} pts vs peers", delta_color="inverse")
    c3.metric("Reported synergies through 2023", f"~${round(reported, -1):.0f}M",
              f"of ${target:.0f}M 5-year target", delta_color="off", delta_arrow="off")
    c4.metric("P/E premium vs peers (2025)", f"{pe_prem:.0f}%",
              f"{pe25['AEM_PE']:.1f}x vs {peers_pe:.1f}x", delta_color="off", delta_arrow="off")

    st.caption(
        "Peers: Newmont (NEM) and Barrick (B). Returns are dividend-adjusted, Sep 28, 2021 to "
        "Aug 14, 2026. AISC as reported by each company. Synergies include about $90M of 2023 "
        "guidance, not actuals. Full analysis in the notebook."
    )

with tabs[1]:
    st.subheader("Deal terms")
    terms = pd.DataFrame({
        "Item": ["Structure", "Exchange ratio", "Implied price", "Premium", "Announced", "Closed"],
        "Detail": [
            "All-stock merger of equals",
            "0.7935 AEM shares per KL share",
            "C$50.63 per KL share (deal value about C$13.5B / US$10.7B)",
            "9% discount to the Sep 27, 2021 close; about 1% above the 10-day VWAP",
            "September 28, 2021",
            "February 8, 2022",
        ],
    })
    st.dataframe(terms, hide_index=True, use_container_width=True)

    st.subheader("Reported synergies vs 5-year target")
    syn = load("synergies")
    syn["Group"] = syn["Type"].map(lambda t: "5-year target" if t == "Target" else "Reported through 2023")

    fig = px.bar(
        syn, x="USD_M", y="Group", color="Type", orientation="h",
        hover_data={"Item": True, "USD_M": True, "Group": False, "Type": False},
        color_discrete_map={"Realized": "#2e7d32", "Guidance": "#a5d6a7", "Target": "#9e9e9e"},
        labels={"USD_M": "USD millions (pre-tax)", "Group": ""},
    )
    fig.update_layout(barmode="stack", height=280, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Realized: about $40M corporate by mid-2022 and $22M operational in 2022. Guidance: about "
        "$50M corporate and $40M operational for 2023 (not actuals). No company totals after 2023 "
        "were found, and the five-year window has not ended. At full run-rate, operational synergies "
        "are estimated at up to $30–40 per ounce, about 4–5% of unit cash costs."
    )

with tabs[2]:
    prices = load("prices", parse_dates=["Date"], index_col="Date")

    st.subheader("Share price, indexed to 100")
    col1, col2 = st.columns([1, 2])
    tickers = col1.multiselect("Companies", ["AEM", "NEM", "B"], default=["AEM", "NEM", "B"])
    start, end = col2.slider(
        "Period",
        min_value=prices.index.min().date(),
        max_value=prices.index.max().date(),
        value=(prices.index.min().date(), prices.index.max().date()),
        format="YYYY-MM",
    )

    view = prices.loc[str(start):str(end), tickers]
    if tickers and len(view) > 1:
        indexed = view / view.iloc[0] * 100
        fig = px.line(indexed, color_discrete_map=COLORS,
                      labels={"value": "Index (start = 100)", "Date": "", "variable": ""})
        ann = pd.Timestamp("2021-09-28")
        if view.index.min() <= ann <= view.index.max():
            fig.add_vline(x=ann, line_dash="dash", line_color="gray")
            fig.add_annotation(x=ann, y=1, yref="paper", text="Announcement",
                               showarrow=False, xanchor="left", yanchor="top")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one company and a longer period.")
    st.caption("Dividend-adjusted (total return). The index starts at 100 on the first day of the selected period.")

    left, right = st.columns(2)

    event = load("announcement_reaction")
    ev = event.melt(id_vars="Ticker", var_name="Window", value_name="Return (%)")
    ev["Window"] = ev["Window"].str.replace(" (%)", "", regex=False)
    fig2 = px.bar(ev, x="Window", y="Return (%)", color="Ticker", barmode="group",
                  color_discrete_map=COLORS, text_auto=".1f", labels={"Window": "", "Ticker": ""})
    left.subheader("Announcement reaction")
    left.plotly_chart(fig2, use_container_width=True)
    left.caption(
        "Return from the Sep 27, 2021 close. AEM fell 1.6% on day 0 while peers rose about 1%, then "
        "outperformed by 3.6 points at +5 days and 5.7 at +20. Only day 0 is a clean read of the announcement."
    )

    win = load("stock_windows")
    w = win.melt(id_vars="Window", var_name="Ticker", value_name="Return (%)")
    fig3 = px.bar(w, x="Window", y="Return (%)", color="Ticker", barmode="group",
                  color_discrete_map=COLORS, text_auto=".1f", labels={"Window": "", "Ticker": ""})
    right.subheader("Before vs after the announcement")
    right.plotly_chart(fig3, use_container_width=True)
    right.caption(
        "Before: Jan 2, 2019 to Sep 27, 2021. After: Sep 28, 2021 to Aug 14, 2026. Dividend-adjusted. "
        "The before window covers a different gold cycle and excludes Kirkland Lake."
    )

with tabs[3]:
    # Row 1: margins vs peers | AEM margin detail
    c1, c2 = st.columns(2)

    pm = load("peer_margins", index_col="Year")
    metric = c1.radio("Metric", ["Operating margin", "Cost ratio"], horizontal=True)
    suffix = "Operating_Margin" if metric == "Operating margin" else "Cost_Ratio"
    m = pm[[f"{t}_{suffix}" for t in ["AEM", "NEM", "B"]]]
    m.columns = ["AEM", "NEM", "B"]
    fig = px.line(m, markers=True, color_discrete_map=COLORS,
                  labels={"value": f"{metric} (%)", "Year": "", "variable": ""})
    fig.update_xaxes(dtick=1)
    c1.subheader("Margins vs peers")
    c1.plotly_chart(fig, use_container_width=True)
    c1.caption(
        "Operating margin rose 28 points at AEM, 35 at Newmont and 20 at Barrick (2022–2025): the "
        "expansion is shared across the sector. Cost ratio = cost of revenue / revenue (lower is better). "
        "Newmont's figures include the Newcrest acquisition from late 2023."
    )

    am = load("aem_margins", index_col="Year")
    am.columns = ["Operating margin", "EBITDA margin", "Net margin", "Cost ratio"]
    fig = px.line(am, markers=True, labels={"value": "%", "Year": "", "variable": ""})
    fig.update_xaxes(dtick=1)
    c2.subheader("AEM margin detail")
    c2.plotly_chart(fig, use_container_width=True)
    c2.caption(
        "EBITDA = operating income + depreciation. Net margin includes non-operating items. The 2022 "
        "cost ratio includes a $158.5M non-cash inventory adjustment from merger accounting (about 2.8 points)."
    )

    # Row 2: gold check | AISC
    c3, c4 = st.columns(2)

    g = load("gold_index", index_col="Year")
    g.columns = ["Gold price (avg)", "AEM revenue", "AEM cost of revenue"]
    fig = px.line(g, markers=True, labels={"value": "Index (2022 = 100)", "Year": "", "variable": ""},
                  color_discrete_map={"Gold price (avg)": "#d4a017", "AEM revenue": "#1f77b4",
                                      "AEM cost of revenue": "#d62728"})
    fig.update_xaxes(dtick=1)
    c3.subheader("Gold price vs AEM revenue and costs")
    c3.plotly_chart(fig, use_container_width=True)
    c3.caption(
        "From 2022 to 2025 gold rose about 92%, AEM's revenue about 107% and its cost of revenue about "
        "33%: margins widened because revenue grew much faster than costs. Gold is the COMEX futures "
        "average, a proxy for AEM's realized price."
    )

    aisc = load("aisc", index_col="Year")
    base = load("aisc_baseline", index_col="Year").rename(columns={"AEM (pro forma)": "AEM"})
    c4.subheader("All-in sustaining cost (AISC) per ounce")
    show2021 = c4.checkbox("Include 2021 pro forma baseline (estimate)")
    scale = c4.radio("Scale", ["USD/oz", "Rebased to 100"], horizontal=True)
    data = pd.concat([base.loc[[2021]], aisc]) if show2021 else aisc
    if scale == "Rebased to 100":
       data = data / data.iloc[0] * 100
    y_label = "AISC (USD/oz)" if scale == "USD/oz" else "Index (base year = 100)"
    fig = px.line(data, markers=True, color_discrete_map=COLORS,
                  labels={"value": y_label, "Year": "", "variable": ""})
    fig.update_xaxes(tickmode="array", tickvals=list(data.index))
    c4.plotly_chart(fig, use_container_width=True)
    c4.caption(
        "AEM's AISC rose 23% from 2022 to 2025 against 33% at Newmont and 34% at Barrick (about "
        "$150–165 per ounce less cost growth). Reported synergies ($30–40 per ounce at full run-rate) "
        "explain at most a fifth to a quarter of that gap. Definitions differ across companies, so "
        "compare changes, not levels. The 2021 AEM value combines AEM and Kirkland Lake (estimate)."
    )

    # Row 3: Detour Lake
    st.subheader("Detour Lake: plan vs actual")
    d = load("detour_lake", index_col="Year")[["Detour_Actual_TCC", "Detour_Plan_Jul2022_TCC", "AEM_Company_TCC"]]
    d.columns = ["Detour Lake, actual", "Detour Lake, July 2022 plan", "AEM company-wide"]
    fig = px.line(d, markers=True, labels={"value": "Total cash cost (USD/oz)", "Year": "", "variable": ""},
                  color_discrete_map={"Detour Lake, actual": "#2e7d32",
                                      "Detour Lake, July 2022 plan": "#2e7d32",
                                      "AEM company-wide": "#1f77b4"})
    fig.for_each_trace(lambda t: t.update(line_dash="dash") if "plan" in t.name else None)
    fig.update_xaxes(tickmode="array", tickvals=[2022, 2023, 2024, 2025])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Detour Lake is the largest mine AEM inherited from Kirkland Lake. Its total cash costs rose 34% "
        "from 2022 to 2025, against 23% company-wide, and ended 46% above the July 2022 plan, which "
        "assumed $1,500 gold (higher gold prices raise royalties). The reported Detour synergy (about "
        "$15–22 per ounce) is too small to be visible here, so this test is uninformative about synergies."
    )

with tabs[4]:
    st.subheader("P/E ratio (year-end price / diluted EPS)")
    pe = load("pe_table", index_col="Year")
    pe_long = pe[["AEM_PE", "NEM_PE", "B_PE"]].rename(columns=lambda c: c.replace("_PE", ""))

    show_all = st.checkbox("Show 2022–2023 (distorted by merger costs and negative EPS)")
    if not show_all:
        pe_long = pe_long.loc[[2024, 2025]]

    pe_long = pe_long.reset_index().melt(id_vars="Year", var_name="Ticker", value_name="P/E")
    pe_long["Year"] = pe_long["Year"].astype(str)
    fig = px.bar(pe_long, x="Year", y="P/E", color="Ticker", barmode="group",
                 color_discrete_map=COLORS, text_auto=".1f", labels={"Year": "", "Ticker": ""})
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "In 2024–2025 AEM traded at 19–21 times earnings against 13–16 for Newmont and Barrick, a premium "
        "of roughly 60% in 2024 and 20–30% in 2025, consistent with its larger stock gain. The data cannot "
        "show whether the premium comes from the merger or from other factors such as asset quality and "
        "jurisdiction. Newmont's P/E is blank in 2022–2023 because its EPS was negative. Prices are not "
        "dividend-adjusted here."
    )

with tabs[5]:
    st.subheader("Limitations")
    st.markdown(
        """
- **No counterfactual**: there is no way to observe what AEM would have achieved without the merger.
- **Confounding events**: the 2023 acquisition of Yamana's Canadian assets and asset-level factors occurred in the same period.
- **Imperfect peers**: Newmont acquired Newcrest in 2023, and Barrick's production fell in 2025.
- **Short financial history**: yfinance provides only 2022–2025, so there are no pre-merger margins.
- **Synergy data**: no company totals after 2023 were found, the 2023 amounts are guidance rather than actuals, and the five-year window has not yet ended.
- **Cost definitions**: AISC definitions differ across companies; the 2021 pro forma baseline is an estimate based on Kirkland Lake's nine-month figure.
- **Proxies**: gold is the COMEX futures average, not AEM's realized price; P/E uses reported diluted EPS, which includes one-time items.
- **Stock windows**: the pre-announcement window (2019–2021) covers a different gold cycle and excludes Kirkland Lake, which is not available in yfinance.
"""
    )
    st.caption("Full methodology, sources and calculations are in the notebook.")