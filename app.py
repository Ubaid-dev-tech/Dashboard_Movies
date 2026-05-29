import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import ast
import io
from datetime import datetime

# ──────────────────────────────────────────────
# THEME — Light Brown & Sage Green
# ──────────────────────────────────────────────
LIGHT_BROWN   = "#C8A882"
SAGE_GREEN    = "#7D9B76"
CREAM         = "#FAF3E8"
DARK_BROWN    = "#5C3D2E"
MUTED_GOLD    = "#D4A857"
SOFT_SAGE     = "#B2C9AD"
CARD_BG       = "#F5ECD7"
TEXT_COLOR    = "#3B2A1A"
BORDER_COLOR  = "#D4B896"

PALETTE_MAIN  = [SAGE_GREEN, LIGHT_BROWN, MUTED_GOLD, SOFT_SAGE,
                 "#A0826D", "#8FBC8F", "#C49A6C", "#6B8F71",
                 "#BFA980", "#4E7C59"]

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor":  CREAM,
    "axes.facecolor":    "#F0E6D0",
    "axes.edgecolor":    BORDER_COLOR,
    "axes.labelcolor":   DARK_BROWN,
    "xtick.color":       DARK_BROWN,
    "ytick.color":       DARK_BROWN,
    "text.color":        DARK_BROWN,
    "grid.color":        "#E2D5C0",
    "grid.linewidth":    0.6,
    "font.family":       "serif",
    "axes.titleweight":  "bold",
    "axes.titlecolor":   DARK_BROWN,
    "axes.titlesize":    11,
})

# ──────────────────────────────────────────────
# PAGE CONFIG & GLOBAL CSS
# ──────────────────────────────────────────────
st.set_page_config(page_title="🎬 Movie Analytics Dashboard", layout="wide")

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;600&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Lato', sans-serif;
      background-color: {CREAM};
      color: {TEXT_COLOR};
  }}

  /* ── Header banner ── */
  .dashboard-header {{
      background: linear-gradient(135deg, {DARK_BROWN} 0%, {SAGE_GREEN} 100%);
      border-radius: 14px;
      padding: 28px 36px;
      margin-bottom: 20px;
      box-shadow: 0 4px 18px rgba(92,61,46,0.18);
  }}
  .dashboard-header h1 {{
      font-family: 'Playfair Display', serif;
      font-size: 2.2rem;
      color: {CREAM};
      margin: 0 0 6px 0;
  }}
  .dashboard-header p {{
      color: #f0e6d0cc;
      font-size: 0.95rem;
      margin: 0;
  }}

  /* ── Metric cards — equal size ── */
  [data-testid="metric-container"] {{
      background: {CARD_BG};
      border: 1px solid {BORDER_COLOR};
      border-radius: 10px;
      padding: 18px 20px;
      min-height: 100px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(92,61,46,0.08);
  }}
  [data-testid="metric-container"] label {{
      font-family: 'Lato', sans-serif;
      font-weight: 600;
      color: {SAGE_GREEN} !important;
      font-size: 0.82rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
      font-family: 'Playfair Display', serif;
      font-size: 1.7rem !important;
      color: {DARK_BROWN} !important;
  }}

  /* ── Section cards ── */
  .chart-card {{
      background: {CARD_BG};
      border: 1px solid {BORDER_COLOR};
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      box-shadow: 0 2px 10px rgba(92,61,46,0.07);
  }}
  .chart-title {{
      font-family: 'Playfair Display', serif;
      font-size: 1.05rem;
      font-weight: 700;
      color: {DARK_BROWN};
      margin-bottom: 4px;
  }}
  .chart-desc {{
      font-size: 0.82rem;
      color: #8B6E52;
      margin-bottom: 10px;
      font-style: italic;
  }}

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {{
      background: linear-gradient(180deg, #f5ead4 0%, #ecdcc0 100%);
      border-right: 2px solid {BORDER_COLOR};
  }}
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {{
      color: {DARK_BROWN};
      font-family: 'Playfair Display', serif;
  }}

  /* ── Divider ── */
  hr {{ border-color: {BORDER_COLOR} !important; }}

  /* ── Download buttons ── */
  .stDownloadButton > button {{
      background: {SAGE_GREEN};
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 0.78rem;
      padding: 4px 12px;
      margin-top: 4px;
  }}
  .stDownloadButton > button:hover {{
      background: {DARK_BROWN};
  }}

  /* ── DataFrames ── */
  [data-testid="stDataFrame"] {{
      border: 1px solid {BORDER_COLOR};
      border-radius: 8px;
  }}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
  <h1>🎬 Movie Analytics Dashboard</h1>
  <p>
    Explore the <strong>TMDB 5000 Movies</strong> dataset interactively. Analyze ratings, revenue,
    genres, budgets, popularity, and release trends from <strong>1916 to 2017</strong>.
    Use the sidebar to filter by date range, genre, language, budget, revenue, popularity, runtime, and rating.
    Every chart is downloadable. All metric boxes are equal in size for easy comparison.
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADER
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# HELPER — downloadable figure bytes
# ──────────────────────────────────────────────
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()

# ──────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
st.sidebar.markdown("All filters apply to **every chart simultaneously**.")

# 1. DATE RANGE — calendar widget
st.sidebar.markdown("### 📅 Date Range")
min_date = df['release_date'].min().date()
max_date = df['release_date'].max().date()
start_date = st.sidebar.date_input("Start Date", value=min_date,
                                    min_value=min_date, max_value=max_date)
end_date   = st.sidebar.date_input("End Date",   value=max_date,
                                    min_value=min_date, max_value=max_date)
start_ts = pd.Timestamp(start_date)
end_ts   = pd.Timestamp(end_date)

# 2. SEARCH
st.sidebar.markdown("### 🔎 Search Movie")
all_titles = sorted(df['title'].dropna().unique().tolist())
selected_movie = st.sidebar.multiselect("Search & Select Movies", options=all_titles, default=[],
                                         placeholder="Type to search movies…")

# 3. LANGUAGE
st.sidebar.markdown("### 🌐 Original Language")
LANGUAGE_NAMES = {
    'af':'Afrikaans','ar':'Arabic','bn':'Bengali','ca':'Catalan','cn':'Cantonese',
    'cs':'Czech','cy':'Welsh','da':'Danish','de':'German','el':'Greek','en':'English',
    'eo':'Esperanto','es':'Spanish','et':'Estonian','eu':'Basque','fa':'Persian',
    'fi':'Finnish','fr':'French','gl':'Galician','gu':'Gujarati','he':'Hebrew',
    'hi':'Hindi','hr':'Croatian','hu':'Hungarian','hy':'Armenian','id':'Indonesian',
    'is':'Icelandic','it':'Italian','ja':'Japanese','ka':'Georgian','kn':'Kannada',
    'ko':'Korean','lt':'Lithuanian','lv':'Latvian','mk':'Macedonian','ml':'Malayalam',
    'mn':'Mongolian','ms':'Malay','nb':'Norwegian','nl':'Dutch','pa':'Punjabi',
    'pl':'Polish','pt':'Portuguese','ro':'Romanian','ru':'Russian','sh':'Serbo-Croatian',
    'sk':'Slovak','sl':'Slovenian','sr':'Serbian','sv':'Swedish','ta':'Tamil',
    'te':'Telugu','th':'Thai','tl':'Filipino','tr':'Turkish','uk':'Ukrainian',
    'ur':'Urdu','vi':'Vietnamese','zh':'Chinese','zu':'Zulu','xx':'Unknown',
}
all_lang_codes = sorted(df['original_language'].dropna().unique().tolist())
lang_opts = {LANGUAGE_NAMES.get(c, c.upper()) + f" ({c})": c for c in all_lang_codes}
sel_lang_labels = st.sidebar.multiselect("Filter by Language", sorted(lang_opts.keys()), default=[])
selected_languages = [lang_opts[l] for l in sel_lang_labels]

# 4. GENRES
st.sidebar.markdown("### 🎭 Genre")
all_genres = sorted({g for sub in df['genres'] for g in sub})
selected_genres = st.sidebar.multiselect("Select Genres", all_genres)

# 5. NUMERICAL RANGES
budget_max_raw  = float(df['budget'].max())
revenue_max_raw = float(df['revenue'].max())
pop_min_raw     = float(df['popularity'].min())
pop_max_raw     = float(df['popularity'].max())
rt_min_raw      = int(df['runtime'].min())
rt_max_raw      = int(df['runtime'].max())

st.sidebar.markdown("### ⭐ Rating Range")
rc1, rc2 = st.sidebar.columns(2)
min_rating = rc1.number_input("Min", 0.0, 10.0, 0.0, 0.1, format="%.1f")
max_rating = rc2.number_input("Max", 0.0, 10.0, 10.0, 0.1, format="%.1f")

st.sidebar.markdown("### 💰 Budget (Million $)")
bc1, bc2 = st.sidebar.columns(2)
budget_min = bc1.number_input("Min", 0.0, value=0.0, step=1.0)
budget_max = bc2.number_input("Max", 0.0, value=round(budget_max_raw/1e6, 1), step=1.0)

st.sidebar.markdown("### 🎯 Revenue (Million $)")
rv1, rv2 = st.sidebar.columns(2)
rev_min = rv1.number_input("Min", 0.0, value=0.0, step=1.0)
rev_max = rv2.number_input("Max", 0.0, value=round(revenue_max_raw/1e6, 1), step=1.0)

st.sidebar.markdown("### 🔥 Popularity")
pp1, pp2 = st.sidebar.columns(2)
pop_min = pp1.number_input("Min", 0.0, value=round(pop_min_raw, 1), step=1.0)
pop_max = pp2.number_input("Max", 0.0, value=round(pop_max_raw, 1), step=1.0)

st.sidebar.markdown("### ⏱️ Runtime (min)")
rt1, rt2 = st.sidebar.columns(2)
rt_min = rt1.number_input("Min", 0, value=rt_min_raw, step=1)
rt_max = rt2.number_input("Max", 0, value=rt_max_raw, step=1)

st.sidebar.divider()
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    st.rerun()

# ──────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────
df2 = df[
    (df['release_date'] >= start_ts) & (df['release_date'] <= end_ts) &
    (df['vote_average'] >= min_rating) & (df['vote_average'] <= max_rating) &
    (df['budget']   >= budget_min * 1e6) & (df['budget']   <= budget_max * 1e6) &
    (df['revenue']  >= rev_min    * 1e6) & (df['revenue']  <= rev_max    * 1e6) &
    (df['popularity'] >= pop_min) & (df['popularity'] <= pop_max) &
    (df['runtime']  >= rt_min)  & (df['runtime']  <= rt_max)
].copy()

if selected_genres:
    df2 = df2[df2['genres'].apply(lambda x: any(g in x for g in selected_genres))]
if selected_languages:
    df2 = df2[df2['original_language'].isin(selected_languages)]
if selected_movie:
    df2 = df2[df2['title'].isin(selected_movie)]

# ──────────────────────────────────────────────
# ACTIVE FILTER BADGE
# ──────────────────────────────────────────────
active = []
if selected_movie:      active.append(f"🔎 {', '.join(selected_movie)}")
if selected_languages:  active.append(f"🌐 {', '.join(selected_languages)}")
if selected_genres:     active.append(f"🎭 {', '.join(selected_genres)}")
if min_rating > 0 or max_rating < 10: active.append(f"⭐ {min_rating}–{max_rating}")
if budget_min > 0 or budget_max < round(budget_max_raw/1e6, 1):
    active.append(f"💰 ${budget_min}M–${budget_max}M")

if active:
    st.info("**Active Filters:** " + " | ".join(active) + f"  →  **{len(df2):,} movies**")
else:
    st.success(f"No filters active — showing all **{len(df2):,} movies**")

# ──────────────────────────────────────────────
# SEARCH RESULTS PANEL
# ──────────────────────────────────────────────
if selected_movie:
    label = ', '.join(selected_movie)
    st.subheader(f'🔎 Search Results: "{label}"')
    if df2.empty:
        st.warning(f'No movies found matching "{label}".')
    else:
        st.success(f'Found **{len(df2)}** movie(s)')
        dcols = ['title', 'vote_average', 'release_year', 'revenue',
                 'budget', 'popularity', 'runtime', 'original_language']
        dcols = [c for c in dcols if c in df2.columns]
        sd = df2[dcols].copy()
        sd.columns = [c.replace('_', ' ').title() for c in sd.columns]
        sd['Revenue'] = (df2['revenue']/1e6).round(1).astype(str) + 'M'
        sd['Budget']  = (df2['budget']/1e6).round(1).astype(str) + 'M'
        st.dataframe(sd.reset_index(drop=True), use_container_width=True)
    st.divider()

# ──────────────────────────────────────────────
# KPI METRICS  (equal-size boxes via CSS above)
# ──────────────────────────────────────────────
st.markdown("### 📊 Key Metrics")
k1, k2, k3, k4, k5, k6 = st.columns(6)
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

# ──────────────────────────────────────────────
# CHART HELPER  — renders card with title, desc,
# chart, and download button
# ──────────────────────────────────────────────
def chart_card(title, description, fig, fname):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-desc">{description}</div>', unsafe_allow_html=True)
    st.pyplot(fig)
    st.download_button(
        label="⬇ Download Chart",
        data=fig_to_bytes(fig),
        file_name=fname,
        mime="image/png",
        key=fname,
    )
    plt.close(fig)

# ──────────────────────────────────────────────
# ROW 1: Genres  |  Rating Distribution
# ──────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    genre_counts = df2.explode('genres')['genres'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(genre_counts.index[::-1], genre_counts.values[::-1],
                   color=PALETTE_MAIN[:len(genre_counts)])
    ax.set_xlabel("Number of Movies")
    ax.set_title("Top 10 Movie Genres")
    ax.bar_label(bars, padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card(
        "🎭 Top 10 Genres",
        "This chart shows the 10 most common genres in the filtered dataset. "
        "Drama and Comedy usually dominate because they have broader audience appeal and lower production costs.",
        fig, "top_genres.png"
    )

with c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(df2['vote_average'], bins=20, kde=True, ax=ax,
                 color=SAGE_GREEN, edgecolor=CREAM, linewidth=0.5)
    ax.lines[0].set_color(DARK_BROWN)
    ax.set_xlabel("Vote Average (0–10)")
    ax.set_title("Rating Distribution")
    fig.tight_layout()
    chart_card(
        "⭐ Rating Distribution",
        "Distribution of audience ratings across all filtered movies. "
        "The KDE curve shows the overall shape. Most films cluster between 5.5 and 7.5, "
        "with very few movies scoring above 8 or below 4.",
        fig, "rating_distribution.png"
    )

# ──────────────────────────────────────────────
# ROW 2: Revenue vs Rating  |  Runtime by Rating
# ──────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    sample = df2.sample(min(500, len(df2)), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    sc = ax.scatter(sample['vote_average'], sample['revenue']/1e6,
                    c=sample['revenue']/1e6, cmap='YlOrBr', alpha=0.7,
                    edgecolors=BORDER_COLOR, linewidths=0.3, s=40)
    plt.colorbar(sc, ax=ax, label="Revenue (M$)")
    ax.set_xlabel("Vote Average")
    ax.set_ylabel("Revenue (Million $)")
    ax.set_title("Revenue vs Rating")
    fig.tight_layout()
    chart_card(
        "💰 Revenue vs Rating",
        "Each dot is a movie. Colour intensity shows revenue magnitude. "
        "Higher-rated movies tend to earn more, but many low-rated blockbusters succeed purely on spectacle and marketing.",
        fig, "revenue_vs_rating.png"
    )

with c4:
    df2['rating_bin'] = pd.cut(df2['vote_average'],
                                bins=[0, 5, 7, 8.5, 10],
                                labels=['Low (0–5)', 'Med (5–7)', 'High (7–8.5)', 'Top (8.5–10)'])
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=df2, x='rating_bin', y='runtime', ax=ax,
                   palette=[PALETTE_MAIN[i] for i in [0, 2, 1, 3]], inner='box')
    ax.set_xlabel("Rating Bracket")
    ax.set_ylabel("Runtime (minutes)")
    ax.set_title("Runtime by Rating Category")
    fig.tight_layout()
    chart_card(
        "⏱️ Runtime by Rating Category",
        "Violin plots show the full distribution of runtimes for each rating bracket. "
        "Top-rated films (8.5+) have a higher median runtime (~120 min), suggesting audiences "
        "reward depth and storytelling that takes more time to develop.",
        fig, "runtime_by_rating.png"
    )

# ──────────────────────────────────────────────
# ROW 3: Movies per Year  |  Budget vs Revenue
# ──────────────────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    year_counts = df2['release_year'].value_counts().sort_index().tail(30)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(year_counts.index, year_counts.values, alpha=0.3, color=SAGE_GREEN)
    ax.plot(year_counts.index, year_counts.values, marker='o', color=DARK_BROWN,
            linewidth=1.8, markersize=5)
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Movies Released per Year (last 30 yrs)")
    plt.xticks(rotation=45)
    fig.tight_layout()
    chart_card(
        "📅 Movies per Year",
        "Trend of how many movies were released each year. "
        "The steep rise from the 1990s reflects the global expansion of cinema and digital filmmaking, "
        "making production more accessible and affordable.",
        fig, "movies_per_year.png"
    )

with c6:
    bdf = df2[df2['budget'] > 0].sample(min(500, len(df2[df2['budget'] > 0])), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    sc2 = ax.scatter(bdf['budget']/1e6, bdf['revenue']/1e6,
                     c=bdf['vote_average'], cmap='copper', alpha=0.7,
                     edgecolors=BORDER_COLOR, linewidths=0.3, s=40)
    plt.colorbar(sc2, ax=ax, label="Rating")
    ax.set_xlabel("Budget (Million $)")
    ax.set_ylabel("Revenue (Million $)")
    ax.set_title("Budget vs Revenue")
    fig.tight_layout()
    chart_card(
        "💵 Budget vs Revenue",
        "Dot colour indicates rating. Higher budgets generally correlate with higher revenues, "
        "but the scatter shows many high-budget flops and low-budget successes — risk doesn't vanish with money.",
        fig, "budget_vs_revenue.png"
    )

# ──────────────────────────────────────────────
# ROW 4: Popularity vs Rating  |  Vote Count Dist
# ──────────────────────────────────────────────
c7, c8 = st.columns(2)

with c7:
    sample2 = df2.sample(min(500, len(df2)), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(sample2['vote_average'], sample2['popularity'],
               color=LIGHT_BROWN, edgecolors=DARK_BROWN, linewidths=0.3, alpha=0.7, s=40)
    ax.set_xlabel("Vote Average")
    ax.set_ylabel("Popularity Score")
    ax.set_title("Popularity vs Rating")
    fig.tight_layout()
    chart_card(
        "🔥 Popularity vs Rating",
        "Popularity (based on TMDB page views, watchlist adds, etc.) and rating are only loosely correlated. "
        "Some niche critically acclaimed films have low popularity, while mainstream blockbusters score high on both.",
        fig, "popularity_vs_rating.png"
    )

with c8:
    fig, ax = plt.subplots(figsize=(6, 4))
    xlim_max = df2['vote_count'].quantile(0.95)
    data_clipped = df2[df2['vote_count'] <= xlim_max]['vote_count']
    sns.histplot(data_clipped, bins=30, ax=ax, color=MUTED_GOLD,
                 edgecolor=CREAM, linewidth=0.4)
    ax.set_xlabel("Vote Count (95th-percentile clip)")
    ax.set_title("Vote Count Distribution")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    chart_card(
        "🗳️ Vote Count Distribution",
        "Most movies receive fewer than 1,000 votes on TMDB. "
        "The distribution is heavily right-skewed — a handful of blockbusters accumulate tens of thousands of votes, "
        "while the long tail of indie and foreign films are rarely reviewed.",
        fig, "vote_count_distribution.png"
    )

# ──────────────────────────────────────────────
# ROW 5: Languages  |  Revenue by Year
# ──────────────────────────────────────────────
c9, c10 = st.columns(2)

with c9:
    lang_counts = df2['original_language'].value_counts().head(10)
    lang_labels = [LANGUAGE_NAMES.get(c, c.upper()) for c in lang_counts.index]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars2 = ax.barh(lang_labels[::-1], lang_counts.values[::-1],
                    color=PALETTE_MAIN[:len(lang_counts)])
    ax.set_xlabel("Number of Movies")
    ax.set_title("Top 10 Languages")
    ax.bar_label(bars2, padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card(
        "🌐 Top 10 Original Languages",
        "English dominates because the TMDB dataset is heavily skewed toward Hollywood. "
        "French, Spanish, and Japanese follow — reflecting the global industries with the most TMDB coverage.",
        fig, "top_languages.png"
    )

with c10:
    yearly_rev = df2.groupby('release_year')['revenue'].sum().tail(30) / 1e9
    fig, ax = plt.subplots(figsize=(6, 4))
    x_pos = np.arange(len(yearly_rev))
    bars3 = ax.bar(x_pos, yearly_rev.values,
                   color=[SAGE_GREEN if v >= yearly_rev.median() else LIGHT_BROWN
                          for v in yearly_rev.values])
    ax.set_xticks(x_pos[::2])
    ax.set_xticklabels(yearly_rev.index.astype(int)[::2], rotation=45, ha='right', fontsize=9)
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Revenue (Billion $)")
    ax.set_title("Total Revenue by Year")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}B"))
    fig.tight_layout()
    chart_card(
        "📈 Revenue by Year",
        "Total box-office revenue summed by release year (last 30 years). "
        "Green bars are above-median years. The upward trend reflects inflation, global market expansion, "
        "and the blockbuster era driven by Marvel, DC, and franchise films.",
        fig, "revenue_by_year.png"
    )

# ──────────────────────────────────────────────
# ROW 6 (EXTRA): Avg Rating by Genre  |  Budget Distribution
# ──────────────────────────────────────────────
c11, c12 = st.columns(2)

with c11:
    genre_rating = (
        df2.explode('genres')
           .groupby('genres')['vote_average']
           .mean()
           .sort_values(ascending=False)
           .head(12)
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    colors_gr = [SAGE_GREEN if v >= genre_rating.median() else LIGHT_BROWN
                 for v in genre_rating.values]
    bars4 = ax.barh(genre_rating.index[::-1], genre_rating.values[::-1], color=colors_gr[::-1])
    ax.set_xlabel("Average Rating")
    ax.set_title("Avg Rating by Genre")
    ax.set_xlim(0, 10)
    ax.bar_label(bars4, fmt='%.2f', padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card(
        "🏆 Average Rating by Genre",
        "Which genres are rated most highly on average? Documentary and History genres often score high "
        "because their audiences are self-selected enthusiasts, while Horror and Comedy are rated by wider, more critical audiences.",
        fig, "avg_rating_by_genre.png"
    )

with c12:
    budget_df = df2[df2['budget'] > 1e6]['budget'] / 1e6
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(budget_df, bins=30, ax=ax, color=MUTED_GOLD,
                 edgecolor=CREAM, linewidth=0.4, kde=True)
    ax.lines[0].set_color(DARK_BROWN)
    ax.set_xlabel("Budget (Million $)")
    ax.set_title("Budget Distribution (>$1M films)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    fig.tight_layout()
    chart_card(
        "💸 Budget Distribution",
        "Shows how movie budgets are spread across the dataset (films with >$1M budget only). "
        "The right-skewed distribution confirms that most films operate on modest budgets, "
        "while a small number of blockbusters consume enormous resources.",
        fig, "budget_distribution.png"
    )

# ──────────────────────────────────────────────
# DATA TABLES
# ──────────────────────────────────────────────
st.divider()
st.markdown("### 🏆 Top 10 Highest Rated Movies (Filtered)")
dcols = ['title', 'vote_average', 'revenue', 'budget', 'popularity',
         'runtime', 'release_year', 'original_language']
dcols = [c for c in dcols if c in df2.columns]
top10 = df2.nlargest(10, 'vote_average')[dcols].reset_index(drop=True)
top10_display = top10.copy()
top10_display['revenue'] = (top10_display['revenue']/1e6).round(1).astype(str) + 'M'
top10_display['budget']  = (top10_display['budget']/1e6).round(1).astype(str) + 'M'
st.dataframe(top10_display, use_container_width=True)

st.markdown("### 📋 Full Filtered Dataset")
st.caption(f"Showing {len(df2):,} movies matching all current filters")
full_display = df2[dcols].copy()
full_display['revenue'] = (full_display['revenue']/1e6).round(1).astype(str) + 'M'
full_display['budget']  = (full_display['budget']/1e6).round(1).astype(str) + 'M'
st.dataframe(full_display.reset_index(drop=True), use_container_width=True, height=320)

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.divider()
st.markdown(
    f"<p style='text-align:center; color:#A08060; font-size:0.8rem;'>"
    f"🎬 Movie Analytics Dashboard · TMDB 5000 Dataset · "
    f"Built with Streamlit & Matplotlib · Theme: Light Brown & Sage Green</p>",
    unsafe_allow_html=True
)