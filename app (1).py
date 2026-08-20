import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Premier League Player Stats",
    page_icon="⚽",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Strip stray whitespace from column names, just in case
    df.columns = [c.strip() for c in df.columns]
    return df


DATA_PATH = "players.csv"  # place the CSV next to this script, or change the path
df = load_data(DATA_PATH)

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.header("Filters")

clubs = sorted(df["Club"].dropna().unique())
positions = sorted(df["Position"].dropna().unique())
nationalities = sorted(df["Nationality"].dropna().unique())

selected_clubs = st.sidebar.multiselect("Club", clubs, default=[])
selected_positions = st.sidebar.multiselect("Position", positions, default=[])
selected_nationalities = st.sidebar.multiselect("Nationality", nationalities, default=[])

min_age, max_age = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age range", min_age, max_age, (min_age, max_age))

min_apps, max_apps = int(df["Appearances"].min()), int(df["Appearances"].max())
min_appearances = st.sidebar.slider("Minimum appearances", min_apps, max_apps, 0)

name_search = st.sidebar.text_input("Search player name")

# Apply filters
filtered = df.copy()
if selected_clubs:
    filtered = filtered[filtered["Club"].isin(selected_clubs)]
if selected_positions:
    filtered = filtered[filtered["Position"].isin(selected_positions)]
if selected_nationalities:
    filtered = filtered[filtered["Nationality"].isin(selected_nationalities)]
filtered = filtered[
    (filtered["Age"] >= age_range[0]) & (filtered["Age"] <= age_range[1])
]
filtered = filtered[filtered["Appearances"] >= min_appearances]
if name_search:
    filtered = filtered[filtered["Name"].str.contains(name_search, case=False, na=False)]

st.sidebar.markdown(f"**{len(filtered)}** players match your filters")

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("⚽ Premier League Player Stats Dashboard")
st.caption("Dataset: 2020-21 season player statistics")

# ----------------------------------------------------------------------------
# KPI row
# ----------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Players", f"{len(filtered):,}")
col2.metric("Clubs", filtered["Club"].nunique())
col3.metric("Total Goals", int(filtered["Goals"].sum()))
col4.metric("Total Assists", int(filtered["Assists"].sum()))
col5.metric("Avg. Age", f"{filtered['Age'].mean():.1f}" if len(filtered) else "—")

st.divider()

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_overview, tab_leaders, tab_compare, tab_explorer = st.tabs(
    ["📊 Overview", "🏆 Leaderboards", "🆚 Player Comparison", "🔍 Data Explorer"]
)

# ---- Overview tab -----------------------------------------------------------
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Goals by Club")
        goals_by_club = (
            filtered.groupby("Club", as_index=False)["Goals"].sum().sort_values("Goals", ascending=False)
        )
        fig = px.bar(goals_by_club, x="Club", y="Goals", color="Goals", color_continuous_scale="Reds")
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Players by Position")
        pos_counts = filtered["Position"].value_counts().reset_index()
        pos_counts.columns = ["Position", "Count"]
        fig = px.pie(pos_counts, names="Position", values="Count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Age Distribution")
        fig = px.histogram(filtered, x="Age", nbins=20, color="Position")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Top Nationalities")
        nat_counts = filtered["Nationality"].value_counts().head(10).reset_index()
        nat_counts.columns = ["Nationality", "Count"]
        fig = px.bar(nat_counts, x="Count", y="Nationality", orientation="h")
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

# ---- Leaderboards tab -------------------------------------------------------
with tab_leaders:
    st.subheader("Top performers")

    numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
    default_metric = "Goals" if "Goals" in numeric_cols else numeric_cols[0]
    metric = st.selectbox("Rank by metric", numeric_cols, index=numeric_cols.index(default_metric))
    top_n = st.slider("Show top N", 5, 30, 10)

    leaderboard = (
        filtered[["Name", "Club", "Position", metric]]
        .dropna(subset=[metric])
        .sort_values(metric, ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        leaderboard.sort_values(metric),
        x=metric,
        y="Name",
        color="Club",
        orientation="h",
        text=metric,
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(leaderboard.reset_index(drop=True), use_container_width=True)

# ---- Comparison tab ----------------------------------------------------------
with tab_compare:
    st.subheader("Compare players head-to-head")

    all_names = sorted(df["Name"].dropna().unique())
    default_players = all_names[:2] if len(all_names) >= 2 else all_names
    chosen = st.multiselect("Pick players to compare", all_names, default=default_players, max_selections=5)

    if chosen:
        compare_df = df[df["Name"].isin(chosen)]

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        default_metrics = [m for m in ["Goals", "Assists", "Appearances", "Passes"] if m in numeric_cols]
        metrics = st.multiselect(
            "Metrics to compare", numeric_cols, default=default_metrics or numeric_cols[:4]
        )

        if metrics:
            radar_df = compare_df.set_index("Name")[metrics].fillna(0)
            # Normalize each metric 0-1 across the full dataset for fair radar comparison
            norm_df = radar_df.copy()
            for m in metrics:
                col_max = df[m].max()
                norm_df[m] = radar_df[m] / col_max if col_max else 0

            radar_plot_df = norm_df.reset_index().melt(id_vars="Name", var_name="Metric", value_name="Value")
            fig = px.line_polar(
                radar_plot_df, r="Value", theta="Metric", color="Name", line_close=True
            )
            fig.update_traces(fill="toself")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(compare_df.set_index("Name")[metrics], use_container_width=True)
    else:
        st.info("Select at least one player above.")

# ---- Explorer tab -------------------------------------------------------------
with tab_explorer:
    st.subheader("Raw data explorer")
    st.dataframe(filtered, use_container_width=True, height=500)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv,
        file_name="filtered_players.csv",
        mime="text/csv",
    )
