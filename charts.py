import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# ── Colours (must match app.py) ──────────────────────────
LIGHT_BROWN  = "#C8A882"
SAGE_GREEN   = "#7D9B76"
CREAM        = "#FAF3E8"
DARK_BROWN   = "#5C3D2E"
MUTED_GOLD   = "#D4A857"
SOFT_SAGE    = "#B2C9AD"
BORDER_COLOR = "#D4B896"
CARD_BG      = "#F5ECD7"

PALETTE_MAIN = [SAGE_GREEN, LIGHT_BROWN, MUTED_GOLD, SOFT_SAGE,
                "#A0826D", "#8FBC8F", "#C49A6C", "#6B8F71",
                "#BFA980", "#4E7C59"]

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

# ── Helper: convert fig to PNG bytes for download ────────
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()

# ── Helper: render title, chart, description, download ───
def chart_card(title, description, fig, fname):
    st.markdown(
        f'<p style="font-family:Playfair Display,serif;font-size:1.15rem;'
        f'font-weight:700;color:#D4744A;margin:0 0 6px 0;">'
        f'{title}</p>', unsafe_allow_html=True
    )
    st.pyplot(fig)
    st.markdown(
        f'<p style="font-size:0.9rem;color:#D4744A;font-style:italic;'
        f'font-weight:500;line-height:1.75;margin:6px 0 10px 0;">'
        f'{description}</p>', unsafe_allow_html=True
    )
    st.download_button(
        label="⬇ Download Chart", data=fig_to_bytes(fig),
        file_name=fname, mime="image/png", key=f"dl_{fname}",
    )
    plt.close(fig)

# ════════════════════════════════════════════════════════
# CHART FUNCTIONS — one function per chart
# ════════════════════════════════════════════════════════

def chart_top_genres(df2):
    genre_counts = df2.explode('genres')['genres'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(genre_counts.index[::-1], genre_counts.values[::-1],
                   color=PALETTE_MAIN[:len(genre_counts)])
    ax.set_xlabel("Number of Movies"); ax.set_title("Top 10 Movie Genres")
    ax.bar_label(bars, padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card("🎭 Top 10 Genres",
               "Most common genres in the filtered dataset. Drama and Comedy dominate due to "
               "broad audience appeal and lower production costs.",
               fig, "top_genres.png")


def chart_rating_distribution(df2):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(df2['vote_average'], bins=20, kde=True, ax=ax,
                 color=SAGE_GREEN, edgecolor=CREAM, linewidth=0.5)
    if ax.lines: ax.lines[0].set_color(DARK_BROWN)
    ax.set_xlabel("Vote Average (0–10)"); ax.set_title("Rating Distribution")
    fig.tight_layout()
    chart_card("⭐ Rating Distribution",
               "Distribution of audience ratings. Most films cluster between 5.5 and 7.5; "
               "very few score above 8 or below 4.",
               fig, "rating_distribution.png")


def chart_revenue_vs_rating(df2):
    sample = df2.sample(min(500, len(df2)), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    sc = ax.scatter(sample['vote_average'], sample['revenue']/1e6,
                    c=sample['revenue']/1e6, cmap='YlOrBr', alpha=0.7,
                    edgecolors=BORDER_COLOR, linewidths=0.3, s=40)
    plt.colorbar(sc, ax=ax, label="Revenue (M$)")
    ax.set_xlabel("Vote Average"); ax.set_ylabel("Revenue (Million $)")
    ax.set_title("Revenue vs Rating")
    fig.tight_layout()
    chart_card("💰 Revenue vs Rating",
               "Each dot is a movie; colour intensity shows revenue size. "
               "Higher-rated films tend to earn more, but many low-rated blockbusters succeed on spectacle alone.",
               fig, "revenue_vs_rating.png")


def chart_runtime_by_rating(df2):
    df2 = df2.copy()
    df2['rating_bin'] = pd.cut(df2['vote_average'], bins=[0, 5, 7, 8.5, 10],
                                labels=['Low (0–5)', 'Med (5–7)', 'High (7–8.5)', 'Top (8.5–10)'])
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=df2, x='rating_bin', y='runtime', ax=ax,
                   palette=[PALETTE_MAIN[i] for i in [0, 2, 1, 3]], inner='box')
    ax.set_xlabel("Rating Bracket"); ax.set_ylabel("Runtime (minutes)")
    ax.set_title("Runtime by Rating Category")
    fig.tight_layout()
    chart_card("⏱️ Runtime by Rating Category",
               "Violin plots show runtime distributions per rating bracket. "
               "Top-rated films (8.5+) have a higher median runtime (~120 min).",
               fig, "runtime_by_rating.png")


def chart_movies_per_year(df2):
    year_counts = df2['release_year'].value_counts().sort_index().tail(30)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(year_counts.index, year_counts.values, alpha=0.3, color=SAGE_GREEN)
    ax.plot(year_counts.index, year_counts.values, marker='o', color=DARK_BROWN,
            linewidth=1.8, markersize=5)
    ax.set_xlabel("Release Year"); ax.set_ylabel("Number of Movies")
    ax.set_title("Movies Released per Year (last 30 yrs)")
    plt.xticks(rotation=45)
    fig.tight_layout()
    chart_card("📅 Movies per Year",
               "How many movies were released each year. The steep rise from the 1990s reflects "
               "the global expansion of cinema and digital filmmaking.",
               fig, "movies_per_year.png")


def chart_budget_vs_revenue(df2):
    bdf = df2[df2['budget'] > 0].sample(min(500, len(df2[df2['budget'] > 0])), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    sc2 = ax.scatter(bdf['budget']/1e6, bdf['revenue']/1e6,
                     c=bdf['vote_average'], cmap='copper', alpha=0.7,
                     edgecolors=BORDER_COLOR, linewidths=0.3, s=40)
    plt.colorbar(sc2, ax=ax, label="Rating")
    ax.set_xlabel("Budget (Million $)"); ax.set_ylabel("Revenue (Million $)")
    ax.set_title("Budget vs Revenue")
    fig.tight_layout()
    chart_card("💵 Budget vs Revenue",
               "Dot colour indicates rating. Higher budgets generally correlate with higher revenues, "
               "but scatter reveals many high-budget flops and low-budget successes.",
               fig, "budget_vs_revenue.png")


def chart_popularity_vs_rating(df2):
    sample2 = df2.sample(min(500, len(df2)), random_state=42)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(sample2['vote_average'], sample2['popularity'],
               color=LIGHT_BROWN, edgecolors=DARK_BROWN, linewidths=0.3, alpha=0.7, s=40)
    ax.set_xlabel("Vote Average"); ax.set_ylabel("Popularity Score")
    ax.set_title("Popularity vs Rating")
    fig.tight_layout()
    chart_card("🔥 Popularity vs Rating",
               "Popularity and rating are loosely correlated. "
               "Niche critically acclaimed films can have low popularity; blockbusters score high on both.",
               fig, "popularity_vs_rating.png")


def chart_vote_count(df2):
    fig, ax = plt.subplots(figsize=(6, 4))
    xlim_max = df2['vote_count'].quantile(0.95)
    data_clip = df2[df2['vote_count'] <= xlim_max]['vote_count']
    sns.histplot(data_clip, bins=30, ax=ax, color=MUTED_GOLD, edgecolor=CREAM, linewidth=0.4)
    ax.set_xlabel("Vote Count (95th-pct clip)"); ax.set_title("Vote Count Distribution")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    chart_card("🗳️ Vote Count Distribution",
               "Most movies receive fewer than 1,000 votes. The distribution is heavily right-skewed — "
               "blockbusters accumulate tens of thousands of votes while indie films are rarely reviewed.",
               fig, "vote_count_distribution.png")


def chart_top_languages(df2):
    lang_counts = df2['original_language'].value_counts().head(10)
    lang_labels = [LANGUAGE_NAMES.get(c, c.upper()) for c in lang_counts.index]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars2 = ax.barh(lang_labels[::-1], lang_counts.values[::-1],
                    color=PALETTE_MAIN[:len(lang_counts)])
    ax.set_xlabel("Number of Movies"); ax.set_title("Top 10 Languages")
    ax.bar_label(bars2, padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card("🌐 Top 10 Original Languages",
               "English dominates (Hollywood bias in TMDB). French, Spanish, and Japanese follow.",
               fig, "top_languages.png")


def chart_revenue_by_year(df2):
    yearly_rev = df2.groupby('release_year')['revenue'].sum().tail(30) / 1e9
    fig, ax = plt.subplots(figsize=(6, 4))
    x_pos = np.arange(len(yearly_rev))
    bars3 = ax.bar(x_pos, yearly_rev.values,
                   color=[SAGE_GREEN if v >= yearly_rev.median() else LIGHT_BROWN
                          for v in yearly_rev.values])
    ax.set_xticks(x_pos[::2])
    ax.set_xticklabels(yearly_rev.index.astype(int)[::2], rotation=45, ha='right', fontsize=9)
    ax.set_xlabel("Year"); ax.set_ylabel("Total Revenue (Billion $)")
    ax.set_title("Total Revenue by Year")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}B"))
    fig.tight_layout()
    chart_card("📈 Revenue by Year",
               "Total box-office revenue per year (last 30 years). Green = above median. "
               "Upward trend reflects inflation, global expansion, and the franchise blockbuster era.",
               fig, "revenue_by_year.png")


def chart_avg_rating_by_genre(df2):
    genre_rating = (df2.explode('genres')
                       .groupby('genres')['vote_average'].mean()
                       .sort_values(ascending=False).head(12))
    fig, ax = plt.subplots(figsize=(6, 4))
    colors_gr = [SAGE_GREEN if v >= genre_rating.median() else LIGHT_BROWN
                 for v in genre_rating.values]
    bars4 = ax.barh(genre_rating.index[::-1], genre_rating.values[::-1], color=colors_gr[::-1])
    ax.set_xlabel("Average Rating"); ax.set_title("Avg Rating by Genre")
    ax.set_xlim(0, 10)
    ax.bar_label(bars4, fmt='%.2f', padding=4, color=DARK_BROWN, fontsize=9)
    fig.tight_layout()
    chart_card("🏆 Average Rating by Genre",
               "Documentary and History genres often score highest because their audiences are "
               "self-selected enthusiasts. Horror and Comedy face wider, more critical audiences.",
               fig, "avg_rating_by_genre.png")


def chart_budget_distribution(df2):
    budget_fil = df2[df2['budget'] > 1e6]['budget'] / 1e6
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(budget_fil, bins=30, ax=ax, color=MUTED_GOLD,
                 edgecolor=CREAM, linewidth=0.4, kde=True)
    if ax.lines: ax.lines[0].set_color(DARK_BROWN)
    ax.set_xlabel("Budget (Million $)"); ax.set_title("Budget Distribution (>$1M films)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    fig.tight_layout()
    chart_card("💸 Budget Distribution",
               "Spread of movie budgets (films with >$1M only). Right-skewed: most films operate "
               "modestly while a small number of blockbusters consume enormous resources.",
               fig, "budget_distribution.png")


def render_all_charts(df2):
    """Call this from app.py to render all 12 charts in 6 rows of 2."""
    c1, c2 = st.columns(2)
    with c1: chart_top_genres(df2)
    with c2: chart_rating_distribution(df2)

    c3, c4 = st.columns(2)
    with c3: chart_revenue_vs_rating(df2)
    with c4: chart_runtime_by_rating(df2)

    c5, c6 = st.columns(2)
    with c5: chart_movies_per_year(df2)
    with c6: chart_budget_vs_revenue(df2)

    c7, c8 = st.columns(2)
    with c7: chart_popularity_vs_rating(df2)
    with c8: chart_vote_count(df2)

    c9, c10 = st.columns(2)
    with c9:  chart_top_languages(df2)
    with c10: chart_revenue_by_year(df2)

    c11, c12 = st.columns(2)
    with c11: chart_avg_rating_by_genre(df2)
    with c12: chart_budget_distribution(df2)