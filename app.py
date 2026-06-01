import streamlit as st
import pandas as pd
import ast
import seaborn as sns
import matplotlib.pyplot as plt

from filters import render_filters, LANGUAGE_NAMES
from charts  import render_all_charts

# ─────────────────────────────────────────────
# THEME COLOURS
# ─────────────────────────────────────────────
LIGHT_BROWN  = "#C8A882"
SAGE_GREEN   = "#7D9B76"
CREAM        = "#FAF3E8"
DARK_BROWN   = "#5C3D2E"
MUTED_GOLD   = "#D4A857"
CARD_BG      = "#F5ECD7"
BORDER_COLOR = "#D4B896"

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": CREAM, "axes.facecolor": "#F0E6D0",
    "axes.edgecolor": BORDER_COLOR, "axes.labelcolor": DARK_BROWN,
    "xtick.color": DARK_BROWN, "ytick.color": DARK_BROWN,
    "text.color": DARK_BROWN, "grid.color": "#E2D5C0",
    "grid.linewidth": 0.6, "font.family": "serif",
    "axes.titleweight": "bold", "axes.titlecolor": DARK_BROWN,
    "axes.titlesize": 11,
})

# ─────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="🎬 Movie Analytics Dashboard", layout="wide")

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] {{ font-family: 'Lato', sans-serif; }}

  .dashboard-header {{
      background: linear-gradient(135deg, {DARK_BROWN} 0%, {SAGE_GREEN} 100%);
      border-radius: 14px; padding: 28px 36px; margin-bottom: 20px;
      box-shadow: 0 4px 18px rgba(92,61,46,0.18);
  }}
  .dashboard-header h1 {{
      font-family: 'Playfair Display', serif; font-size: 2.2rem;
      color: {CREAM}; margin: 0 0 6px 0;
  }}
  .dashboard-header p {{ color: #f0e6d0cc; font-size: 0.95rem; margin: 0; }}

  [data-testid="metric-container"] {{
      background: {CARD_BG}; border: 1px solid {BORDER_COLOR};
      border-radius: 10px; padding: 18px 20px; min-height: 100px;
      display: flex; flex-direction: column; justify-content: center;
      box-shadow: 0 2px 8px rgba(92,61,46,0.08);
  }}
  [data-testid="metric-container"] label {{
      font-weight: 700; color: {SAGE_GREEN} !important;
      font-size: 0.82rem; letter-spacing: 0.05em; text-transform: uppercase;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
      font-family: 'Playfair Display', serif;
      font-size: 1.7rem !important; color: {DARK_BROWN} !important;
  }}

  section[data-testid="stSidebar"] {{
      background: linear-gradient(180deg, #f2e4c8 0%, #e8d5a8 100%);
      border-right: 3px solid {DARK_BROWN};
  }}
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] div,
  section[data-testid="stSidebar"] li,
  section[data-testid="stSidebar"] small,
  section[data-testid="stSidebar"] strong {{ color: #7A3B3B !important; font-weight: 600 !important; }}
  section[data-testid="stSidebar"] h2 {{
      font-family: 'Playfair Display', serif !important;
      color: #7A3B3B !important; font-size: 1.35rem !important; font-weight: 700 !important;
      border-bottom: 2px solid {SAGE_GREEN}; padding-bottom: 6px; margin-bottom: 10px;
  }}
  section[data-testid="stSidebar"] h3 {{
      font-family: 'Playfair Display', serif !important;
      color: #7A3B3B !important; font-size: 1.0rem !important; font-weight: 700 !important;
      background: linear-gradient(90deg, {SAGE_GREEN}33, transparent);
      border-left: 4px solid {SAGE_GREEN}; padding: 5px 10px;
      border-radius: 0 5px 5px 0; margin: 12px 0 6px 0;
  }}
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
      color: #7A3B3B !important; font-weight: 700 !important; font-size: 0.9rem !important;
  }}
  section[data-testid="stSidebar"] [data-baseweb="select"] span,
  section[data-testid="stSidebar"] [data-baseweb="select"] div,
  section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
      color: #7A3B3B !important; font-weight: 600 !important;
  }}
  /* Placeholder text in search/select dropdowns */
  section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
  section[data-testid="stSidebar"] input::placeholder {{
      color: #D4744A !important; font-weight: 600 !important;
  }}
  section[data-testid="stSidebar"] [aria-placeholder],
  section[data-testid="stSidebar"] [placeholder] {{
      color: #D4744A !important;
  }}
  /* Target the actual placeholder text in multiselect */
  section[data-testid="stSidebar"] [data-baseweb="select"] > div > div[aria-expanded] span[aria-live],
  section[data-testid="stSidebar"] [data-baseweb="select"] .css-1wa3eu0-placeholder,
  section[data-testid="stSidebar"] [class*="placeholder"] {{
      color: #D4744A !important; font-weight: 600 !important;
  }}
  section[data-testid="stSidebar"] input {{
      background: #fffaf2 !important; border: 1.5px solid {BORDER_COLOR} !important;
      color: #7A3B3B !important; font-weight: 600 !important; border-radius: 6px !important;
  }}
  section[data-testid="stSidebar"] .stButton > button {{
      background: {DARK_BROWN} !important; color: {CREAM} !important;
      font-weight: 700 !important; border-radius: 8px !important;
      border: none !important; padding: 10px !important; font-size: 0.9rem !important;
  }}
  section[data-testid="stSidebar"] .stButton > button p,
  section[data-testid="stSidebar"] .stButton > button span,
  section[data-testid="stSidebar"] .stButton > button div {{
      color: {CREAM} !important; font-weight: 700 !important;
  }}
  section[data-testid="stSidebar"] .stButton > button:hover {{ background: {SAGE_GREEN} !important; }}
  section[data-testid="stSidebar"] .stButton > button:hover p,
  section[data-testid="stSidebar"] .stButton > button:hover span,
  section[data-testid="stSidebar"] .stButton > button:hover div {{
      color: {CREAM} !important;
  }}

  .stDownloadButton > button {{
      background: {SAGE_GREEN}; color: white; border: none;
      border-radius: 6px; font-size: 0.78rem; padding: 4px 12px; margin-top: 4px;
  }}
  .stDownloadButton > button:hover {{ background: {DARK_BROWN}; }}
  hr {{ border-color: {BORDER_COLOR} !important; }}
  [data-testid="stDataFrame"] {{ border: 1px solid {BORDER_COLOR}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
  <h1>🎬 Movie Analytics Dashboard</h1>
  <p>
    Explore the <strong>TMDB 5000 Movies</strong> dataset interactively.
    Analyze ratings, revenue, genres, budgets, popularity, and release trends from <strong>1916 to 2017</strong>.
    Use the sidebar to filter by date range, genre, language, budget, revenue, popularity, runtime, and rating.
    Every chart is downloadable.
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("tmdb_5000_movies.csv")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    for col in ['revenue', 'budget', 'runtime', 'popularity', 'vote_count']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['genres'] = df['genres'].apply(
        lambda x: [i['name'] for i in ast.literal_eval(x)] if pd.notna(x) else [])
    df['keywords_list'] = df['keywords'].apply(
        lambda x: [i['name'] for i in ast.literal_eval(x)] if pd.notna(x) else []
    ) if 'keywords' in df.columns else [[] for _ in range(len(df))]
    df = df.dropna(subset=['vote_average', 'revenue', 'release_year',
                           'budget', 'popularity', 'runtime', 'release_date'])
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS  (from filters.py)
# ─────────────────────────────────────────────
df2, filter_state = render_filters(df)

# ─────────────────────────────────────────────
# ACTIVE FILTER BADGE
# ─────────────────────────────────────────────
active = []
if filter_state["selected_movie"]:     active.append(f"🔎 {', '.join(filter_state['selected_movie'])}")
if filter_state["selected_languages"]: active.append(f"🌐 {', '.join(filter_state['selected_languages'])}")
if filter_state["selected_genres"]:    active.append(f"🎭 {', '.join(filter_state['selected_genres'])}")
if filter_state["min_rating"] > 0 or filter_state["max_rating"] < 10:
    active.append(f"⭐ {filter_state['min_rating']}–{filter_state['max_rating']}")
if filter_state["budget_min"] > 0 or filter_state["budget_max"] < round(filter_state["budget_max_raw"]/1e6, 1):
    active.append(f"💰 ${filter_state['budget_min']}M–${filter_state['budget_max']}M")

if active:
    st.info("**Active Filters:** " + " | ".join(active) + f"  →  **{len(df2):,} movies**")
else:
    st.success(f"No filters active — showing all **{len(df2):,} movies**")

# ─────────────────────────────────────────────
# SEARCH RESULTS PANEL
# ─────────────────────────────────────────────
if filter_state["selected_movie"]:
    label = ', '.join(filter_state["selected_movie"])
    st.subheader(f'🔎 Search Results: "{label}"')
    if df2.empty:
        st.warning(f'No movies found matching "{label}".')
    else:
        st.success(f'Found **{len(df2)}** movie(s)')
        dcols = ['title','vote_average','release_year','revenue','budget',
                 'popularity','runtime','original_language']
        dcols = [c for c in dcols if c in df2.columns]
        sd = df2[dcols].copy()
        sd.columns = [c.replace('_',' ').title() for c in sd.columns]
        sd['Revenue'] = (df2['revenue']/1e6).round(1).astype(str) + 'M'
        sd['Budget']  = (df2['budget']/1e6).round(1).astype(str)  + 'M'
        st.dataframe(sd.reset_index(drop=True), use_container_width=True)
    st.divider()

# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
st.markdown("### 📊 Key Metrics")
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Total Movies",   f"{len(df2):,}")
k2.metric("Avg Rating",     f"{df2['vote_average'].mean():.2f}" if len(df2) else "N/A")
k3.metric("Total Revenue",  f"${df2['revenue'].sum()/1e9:.2f}B" if len(df2) else "N/A")
k4.metric("Avg Runtime",    f"{df2['runtime'].mean():.0f} min"  if len(df2) else "N/A")
k5.metric("Avg Budget",     f"${df2['budget'].mean()/1e6:.1f}M" if len(df2) else "N/A")
k6.metric("Avg Popularity", f"{df2['popularity'].mean():.1f}"   if len(df2) else "N/A")
st.divider()

if df2.empty:
    st.warning("⚠️ No movies match the current filters. Please adjust the sidebar filters.")
    st.stop()

# ─────────────────────────────────────────────
# ALL CHARTS  (from charts.py)
# ─────────────────────────────────────────────
render_all_charts(df2)

# ─────────────────────────────────────────────
# DATA TABLES
# ─────────────────────────────────────────────
st.divider()
st.markdown("### 🏆 Top 10 Highest Rated Movies (Filtered)")
dcols = ['title','vote_average','revenue','budget','popularity',
         'runtime','release_year','original_language']
dcols = [c for c in dcols if c in df2.columns]
top10 = df2.nlargest(10,'vote_average')[dcols].reset_index(drop=True).copy()
top10['revenue'] = (top10['revenue']/1e6).round(1).astype(str) + 'M'
top10['budget']  = (top10['budget']/1e6).round(1).astype(str)  + 'M'
st.dataframe(top10, use_container_width=True)

st.markdown("### 📋 Full Filtered Dataset")
st.caption(f"Showing {len(df2):,} movies matching all current filters")
full_d = df2[dcols].copy().reset_index(drop=True)
full_d['revenue'] = (df2['revenue'].values/1e6).round(1).astype(str)
full_d['budget']  = (df2['budget'].values/1e6).round(1).astype(str)
st.dataframe(full_d, use_container_width=True, height=320)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="background:{CARD_BG};padding:28px 36px;border-radius:14px;
            border-left:5px solid {SAGE_GREEN};margin-top:10px;
            box-shadow:0 2px 10px rgba(92,61,46,0.08);">
  <h4 style="color:{DARK_BROWN};margin-top:0;font-family:'Playfair Display',serif;font-size:1.25rem;">
      📋 Dashboard Information
  </h4>
  <div style="color:{DARK_BROWN};font-size:14px;line-height:2.3;">
      <b>Dataset:</b> TMDB 5000 Movies (1916–2017)<br>
      <b>Total Records Available:</b> {len(df):,} movies<br>
      <b>Currently Displayed:</b> {len(df2):,} movies<br>
      <b>Files:</b> app.py · charts.py · filters.py<br>
      <b>Theme:</b> Light Brown &amp; Sage Green · Built with Streamlit &amp; Matplotlib
  </div>
  <div style="margin-top:16px;border-top:1px solid {BORDER_COLOR};padding-top:14px;">
      <b style="color:{DARK_BROWN};font-size:14px;">📊 Charts in this Dashboard:</b>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 24px;margin-top:8px;font-size:13px;color:{DARK_BROWN};">
          <span>🎭 Top 10 Genres</span>
          <span>⭐ Rating Distribution</span>
          <span>💰 Revenue vs Rating</span>
          <span>⏱️ Runtime by Rating Category</span>
          <span>📅 Movies per Year</span>
          <span>💵 Budget vs Revenue</span>
          <span>🔥 Popularity vs Rating</span>
          <span>🗳️ Vote Count Distribution</span>
          <span>🌐 Top 10 Original Languages</span>
          <span>📈 Revenue by Year</span>
          <span>🏆 Average Rating by Genre</span>
          <span>💸 Budget Distribution</span>
      </div>
  </div>
</div>
""", unsafe_allow_html=True)