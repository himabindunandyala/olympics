# ============================================================
# Dashboard Type: ANALYTICAL
# This is an analytical dashboard designed for sports analysts
# and Olympic historians to discover patterns, compare country
# performance over time, and explore medal distributions across
# Summer Olympics history (not real-time operational monitoring).
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config (MUST be first Streamlit call) ──────────────
st.set_page_config(
    page_title="🏅 Summer Olympics Dashboard",
    page_icon="🏅",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp                           { background-color: #0f172a; }
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    div[data-testid="metric-container"] {
        background-color : #1e293b;
        border           : 1px solid #334155;
        border-radius    : 12px;
        padding          : 18px 14px;
    }
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.6rem !important;
    }
    h1, h2, h3      { color: #f8fafc !important; }
    .stMarkdown p   { color: #94a3b8; }
    hr              { border-color: #334155; }
</style>
""", unsafe_allow_html=True)

# ── Color constants ──────────────────────────────────────────
GOLD     = "#FBBF24"
SILVER   = "#94A3B8"
BRONZE   = "#D97706"
BLUE     = "#38BDF8"
PLOT_BG  = "#1e293b"
PAPER_BG = "#0f172a"
FONT_C   = "#f8fafc"
GRID_C   = "#334155"

def base_layout(title_text=""):
    return dict(
        paper_bgcolor = PAPER_BG,
        plot_bgcolor  = PLOT_BG,
        font          = dict(color=FONT_C, family="Arial, sans-serif"),
        margin        = dict(l=16, r=16, t=50, b=16),
        xaxis         = dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(color=FONT_C)),
        yaxis         = dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(color=FONT_C)),
        legend        = dict(bgcolor=PLOT_BG, font=dict(color=FONT_C), bordercolor=GRID_C, borderwidth=1),
        title         = dict(text=title_text, font=dict(color=FONT_C, size=15), x=0.01),
    )

# ── Load & clean data ────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("SummerOlympics_medals.csv")
    df.columns = df.columns.str.strip()
    for col in ["Year", "Golds", "Silvers", "Bronzes", "Medals", "Rank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Drop actual float NaN in Country BEFORE converting to string
    df = df.dropna(subset=["Country"])
    df["Country"] = df["Country"].astype(str).str.strip()
    # Remove any leftover nan/none/empty strings
    df = df[~df["Country"].str.lower().isin(["nan","none","","n/a"])]
    df = df.dropna(subset=["Year", "Medals"])
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏅 Olympics Filter Panel")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    year_range = st.select_slider(
        "📅 Year Range",
        options=years,
        value=(years[0], years[-1]),
    )

    top_n = st.slider("🔢 Top N Countries", min_value=5, max_value=25, value=10, step=5)

    all_countries = sorted(df["Country"].unique())
    defaults = [c for c in ["United States", "China", "United Kingdom", "Germany", "Australia"]
                if c in all_countries]
    selected_countries = st.multiselect(
        "🌍 Spotlight Countries (trend chart)",
        options=all_countries,
        default=defaults,
    )

    medal_type = st.radio(
        "🥇 Medal Type",
        ["Golds", "Silvers", "Bronzes", "Medals"],
        index=3,
    )

    st.markdown("---")
    st.caption("Summer Olympics medal records")

# ── Apply filters ────────────────────────────────────────────
dff = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])].copy()

# ── Page header ──────────────────────────────────────────────
st.markdown("# 🏅 Summer Olympics Medal Dashboard")
st.markdown(
    "**For sports analysts and Olympic historians** — explore which nations have dominated "
    "the Summer Games, how medal tallies shifted across eras, and which countries convert "
    "the most golds."
)
st.markdown("---")

# ── KPI cards ────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("🗓️ Games Covered",   dff["Year"].nunique())
k2.metric("🌍 Nations",         dff["Country"].nunique())
k3.metric("🏅 Total Medals",    f"{int(dff['Medals'].sum()):,}")
k4.metric("👑 All-Time Leader", dff.groupby("Country")["Medals"].sum().idxmax())

st.markdown("---")

# ════════════════════════════════════════════════════════════
# ROW 1 — Bar chart  +  Stacked bar
# ════════════════════════════════════════════════════════════
c1, c2 = st.columns(2)

# ── Chart 1: Horizontal bar ──────────────────────────────────
with c1:
    st.markdown(f"### 🏆 Top {top_n} Countries — {medal_type}")
    bar_df = (
        dff.groupby("Country")[medal_type]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values(medal_type, ascending=True)
    )
    end_color = {"Golds": GOLD, "Silvers": SILVER, "Bronzes": BRONZE}.get(medal_type, BLUE)
    fig1 = go.Figure(go.Bar(
        x=bar_df[medal_type],
        y=bar_df["Country"],
        orientation="h",
        marker=dict(
            color=bar_df[medal_type],
            colorscale=[[0, "#1d4ed8"], [1, end_color]],
            showscale=False,
        ),
        text=bar_df[medal_type],
        textposition="outside",
        textfont=dict(color=FONT_C, size=11),
    ))
    layout1 = base_layout(f"Top {top_n} by {medal_type}")
    layout1["xaxis"]["title"] = dict(text=medal_type, font=dict(color=FONT_C))
    layout1["yaxis"]["title"] = ""
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, width='stretch')

# ── Chart 2: Stacked bar ─────────────────────────────────────
with c2:
    st.markdown(f"### 🥇🥈🥉 Medal Breakdown — Top {top_n}")
    top_names = dff.groupby("Country")["Medals"].sum().nlargest(top_n).index
    comp_df = (
        dff[dff["Country"].isin(top_names)]
        .groupby("Country")[["Golds", "Silvers", "Bronzes"]]
        .sum()
        .reset_index()
        .sort_values("Golds", ascending=False)
    )
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=comp_df["Country"], y=comp_df["Golds"],   name="Gold",   marker_color=GOLD))
    fig2.add_trace(go.Bar(x=comp_df["Country"], y=comp_df["Silvers"], name="Silver", marker_color=SILVER))
    fig2.add_trace(go.Bar(x=comp_df["Country"], y=comp_df["Bronzes"], name="Bronze", marker_color=BRONZE))
    layout2 = base_layout("Gold / Silver / Bronze Composition")
    layout2["barmode"] = "stack"
    layout2["xaxis"]["tickangle"] = -40
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, width='stretch')

# ════════════════════════════════════════════════════════════
# ROW 2 — Line chart  +  Bubble scatter
# ════════════════════════════════════════════════════════════
c3, c4 = st.columns(2)

# ── Chart 3: Line trend ──────────────────────────────────────
with c3:
    st.markdown(f"### 📈 {medal_type} Over Time")
    if selected_countries:
        trend_df = (
            dff[dff["Country"].isin(selected_countries)]
            .groupby(["Year", "Country"])[medal_type]
            .sum()
            .reset_index()
        )
        fig3 = px.line(
            trend_df, x="Year", y=medal_type, color="Country",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig3.update_traces(line=dict(width=2.5), marker=dict(size=7))
        layout3 = base_layout(f"{medal_type} per Olympics — Selected Nations")
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, width='stretch')
    else:
        st.info("👆 Select countries in the sidebar to see trends.")

# ── Chart 4: Bubble scatter ──────────────────────────────────
with c4:
    st.markdown("### 🫧 Golds vs Total Medals (size = Bronzes)")
    s_df = (
        dff.groupby("Country")[["Golds", "Silvers", "Bronzes", "Medals"]]
        .sum()
        .reset_index()
    )
    s_df = s_df[s_df["Bronzes"] > 0]
    fig4 = px.scatter(
        s_df, x="Golds", y="Medals",
        size="Bronzes", hover_name="Country",
        color="Golds",
        color_continuous_scale=[[0, "#1d4ed8"], [0.5, BLUE], [1, GOLD]],
        size_max=55,
    )
    fig4.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1, color=PAPER_BG))
    )
    layout4 = base_layout("Gold Efficiency: Golds vs Total Medals")
    layout4["coloraxis_showscale"] = False
    fig4.update_layout(**layout4)
    st.plotly_chart(fig4, width='stretch')

# ════════════════════════════════════════════════════════════
# ROW 3 — Heatmap (full width)
# ════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🌡️ Medal Heatmap — Top 20 Nations × Decade")

dff["Decade"] = (dff["Year"] // 10 * 10).astype(str) + "s"
top20_idx = dff.groupby("Country")["Medals"].sum().nlargest(20).index
heat_df = (
    dff[dff["Country"].isin(top20_idx)]
    .groupby(["Country", "Decade"])["Medals"]
    .sum()
    .unstack(fill_value=0)
)
# Sort by total medals descending
row_order = dff[dff["Country"].isin(top20_idx)].groupby("Country")["Medals"].sum().sort_values(ascending=False).index
heat_df = heat_df.reindex(row_order)

fig5 = px.imshow(
    heat_df,
    color_continuous_scale=[[0, PLOT_BG], [0.1, "#1d4ed8"], [0.55, BLUE], [1, GOLD]],
    aspect="auto",
    text_auto=True,
    labels=dict(color="Medals", x="Decade", y="Country"),
)
fig5.update_traces(textfont=dict(color="white", size=10))
layout5 = base_layout("Medal Count per Decade — Top 20 Nations")
layout5["coloraxis_showscale"] = True
fig5.update_layout(**layout5)
st.plotly_chart(fig5, width='stretch')

# ════════════════════════════════════════════════════════════
# ROW 4 — Pie  +  Gold conversion rate bar
# ════════════════════════════════════════════════════════════
st.markdown("---")
c5, c6 = st.columns(2)

# ── Chart 6: Donut pie ───────────────────────────────────────
with c5:
    st.markdown(f"### 🍩 {medal_type} Share — Top 10")
    pie_df = dff.groupby("Country")[medal_type].sum().nlargest(10).reset_index()
    fig6 = px.pie(
        pie_df, names="Country", values=medal_type,
        hole=0.45,
        color_discrete_sequence=[GOLD, BLUE, BRONZE, SILVER,
                                  "#f97316","#a78bfa","#34d399","#fb7185","#60a5fa","#e879f9"],
    )
    fig6.update_traces(
        textinfo="percent+label",
        textfont=dict(color="white", size=11),
        marker=dict(line=dict(color=PAPER_BG, width=2)),
    )
    layout6 = base_layout(f"Share of {medal_type} — Top 10 Nations")
    layout6["showlegend"] = False
    fig6.update_layout(**layout6)
    st.plotly_chart(fig6, width='stretch')

# ── Chart 7: Gold conversion rate ───────────────────────────
with c6:
    st.markdown("### 📊 Gold Conversion Rate (Golds / Total Medals)")
    conv_df = dff.groupby("Country")[["Golds", "Medals"]].sum().reset_index()
    conv_df = conv_df[conv_df["Medals"] >= 20]
    conv_df["Gold %"] = (conv_df["Golds"] / conv_df["Medals"] * 100).round(1)
    conv_df = conv_df.nlargest(top_n, "Gold %").sort_values("Gold %", ascending=True)

    fig7 = go.Figure(go.Bar(
        x=conv_df["Gold %"],
        y=conv_df["Country"],
        orientation="h",
        marker=dict(
            color=conv_df["Gold %"],
            colorscale=[[0, "#1d4ed8"], [1, GOLD]],
            showscale=False,
        ),
        text=[f"{v}%" for v in conv_df["Gold %"]],
        textposition="outside",
        textfont=dict(color=FONT_C, size=11),
    ))
    layout7 = base_layout("% of Total Medals that are Gold")
    layout7["xaxis"]["title"] = dict(text="Gold %", font=dict(color=FONT_C))
    layout7["yaxis"]["title"] = ""
    fig7.update_layout(**layout7)
    st.plotly_chart(fig7, width='stretch')

# ── Raw data expander ────────────────────────────────────────
st.markdown("---")
with st.expander("📋 View Raw Filtered Data"):
    cols = [c for c in ["Year","Country","Rank","Golds","Silvers","Bronzes","Medals"] if c in dff.columns]
    st.dataframe(
        dff[cols].sort_values(["Year", "Rank"]).reset_index(drop=True),
        width='stretch',
        height=320,
    )

st.caption("📌 Data: Summer Olympics medal records | Built with Streamlit & Plotly")
