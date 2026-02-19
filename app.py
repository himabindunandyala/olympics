# Dashboard Type: ANALYTICAL
# This dashboard is an analytical dashboard because it is designed for analysts, historians,
# and sports enthusiasts to discover patterns, compare country performance over time,
# and explore medal distributions across Summer Olympics history — not to monitor real-time
# operations or surface a single KPI for executives.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Summer Olympics Medal Dashboard",
    page_icon="🏅",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0d1117; }
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #161b22; }
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
    }
    /* Headers */
    h1, h2, h3 { color: #f0f6fc; }
    p, label, .stMarkdown { color: #8b949e; }
    /* Divider */
    hr { border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("SummerOlympics_medals.csv")
    df.columns = df.columns.str.strip()
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

# ─── Color Palette ────────────────────────────────────────────────────────────
GOLD   = "#FFD700"
SILVER = "#C0C0C0"
BRONZE = "#CD7F32"
ACCENT = "#58a6ff"
BG     = "#0d1117"
CARD   = "#21262d"

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/320px-Olympic_rings_without_rims.svg.png", use_container_width=True)
st.sidebar.markdown("## 🏅 Filters")

years = sorted(df["Year"].unique())
year_range = st.sidebar.select_slider(
    "Olympic Year Range",
    options=years,
    value=(years[0], years[-1]),
)

top_n = st.sidebar.slider("Top N Countries", min_value=5, max_value=30, value=10, step=5)

all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Spotlight Countries",
    options=all_countries,
    default=["United States", "China", "United Kingdom", "Germany", "Australia"],
)

medal_type = st.sidebar.radio("Medal Type for Charts", ["Golds", "Silvers", "Bronzes", "Medals"], index=3)

# ─── Filter Data ─────────────────────────────────────────────────────────────
mask = (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
dff = df[mask].copy()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 🏅 Summer Olympics Medal Dashboard")
st.markdown(
    "**For sports analysts and Olympic historians** — explore which nations have dominated "
    "the Summer Games, how medal distributions have shifted over time, and which countries "
    "punch above their weight."
)
st.markdown("---")

# ─── KPI Metrics ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_games   = dff["Year"].nunique()
total_nations = dff["Country"].nunique()
total_medals  = dff["Medals"].sum()
top_country   = dff.groupby("Country")["Medals"].sum().idxmax()

col1.metric("🗓️ Olympic Games", total_games)
col2.metric("🌍 Nations Competed", total_nations)
col3.metric("🥇 Total Medals Awarded", f"{total_medals:,}")
col4.metric("👑 All-Time Leader", top_country)

st.markdown("---")

# ─── Chart Row 1 ─────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

# Chart 1 — Horizontal Bar: Top N Countries by selected medal type
with c1:
    st.markdown(f"### 🏆 Top {top_n} Countries — Total {medal_type}")
    top_df = (
        dff.groupby("Country")[medal_type]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values(medal_type)
    )
    fig1 = px.bar(
        top_df, x=medal_type, y="Country", orientation="h",
        color=medal_type,
        color_continuous_scale=[[0, CARD], [1, GOLD if medal_type == "Golds" else ACCENT]],
        template="plotly_dark",
    )
    fig1.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="", xaxis_title=medal_type,
    )
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2 — Stacked Bar: Gold/Silver/Bronze breakdown for top countries
with c2:
    st.markdown(f"### 🥇🥈🥉 Medal Composition — Top {top_n} Countries")
    top_names = dff.groupby("Country")["Medals"].sum().nlargest(top_n).index
    comp_df = (
        dff[dff["Country"].isin(top_names)]
        .groupby("Country")[["Golds", "Silvers", "Bronzes"]]
        .sum()
        .reset_index()
        .sort_values("Golds", ascending=False)
    )
    fig2 = go.Figure()
    fig2.add_bar(x=comp_df["Country"], y=comp_df["Golds"],   name="Gold",   marker_color=GOLD)
    fig2.add_bar(x=comp_df["Country"], y=comp_df["Silvers"], name="Silver", marker_color=SILVER)
    fig2.add_bar(x=comp_df["Country"], y=comp_df["Bronzes"], name="Bronze", marker_color=BRONZE)
    fig2.update_layout(
        barmode="stack",
        paper_bgcolor=BG, plot_bgcolor=BG,
        legend=dict(bgcolor=CARD, font_color="#f0f6fc"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_tickangle=-45,
        template="plotly_dark",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ─── Chart Row 2 ─────────────────────────────────────────────────────────────
c3, c4 = st.columns(2)

# Chart 3 — Line Chart: Medal trend over time for spotlight countries
with c3:
    st.markdown(f"### 📈 {medal_type} Trend Over Time")
    if selected_countries:
        trend_df = (
            dff[dff["Country"].isin(selected_countries)]
            .groupby(["Year", "Country"])[medal_type]
            .sum()
            .reset_index()
        )
        fig3 = px.line(
            trend_df, x="Year", y=medal_type, color="Country",
            markers=True, template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig3.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG,
            legend=dict(bgcolor=CARD, font_color="#f0f6fc"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Select at least one country in the sidebar to view trends.")

# Chart 4 — Scatter: Golds vs Total Medals (bubble = bronzes)
with c4:
    st.markdown("### 🔵 Golds vs Total Medals per Country (bubble = Bronzes)")
    scatter_df = dff.groupby("Country")[["Golds", "Silvers", "Bronzes", "Medals"]].sum().reset_index()
    fig4 = px.scatter(
        scatter_df, x="Golds", y="Medals", size="Bronzes",
        hover_name="Country", color="Golds",
        color_continuous_scale=[[0, "#21262d"], [1, GOLD]],
        template="plotly_dark",
        size_max=50,
    )
    fig4.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ─── Chart 5 — Heatmap ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🗺️ Medal Heatmap — Countries × Decades")

dff["Decade"] = (dff["Year"] // 10 * 10).astype(str) + "s"
top20 = dff.groupby("Country")["Medals"].sum().nlargest(20).index
heat_df = (
    dff[dff["Country"].isin(top20)]
    .groupby(["Country", "Decade"])["Medals"]
    .sum()
    .unstack(fill_value=0)
)
fig5 = px.imshow(
    heat_df,
    color_continuous_scale=[[0, BG], [0.3, "#1f3a5f"], [1, GOLD]],
    aspect="auto",
    template="plotly_dark",
    labels=dict(color="Medals"),
)
fig5.update_layout(
    paper_bgcolor=BG, plot_bgcolor=BG,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Decade", yaxis_title="",
)
st.plotly_chart(fig5, use_container_width=True)

# ─── Raw Data Table ───────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 View Filtered Raw Data"):
    st.dataframe(
        dff.sort_values(["Year", "Rank"]).reset_index(drop=True),
        use_container_width=True,
    )

st.caption("Data source: Summer Olympics medal records. Dashboard built with Streamlit + Plotly.")
