import streamlit as st
import pandas as pd

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

def render_filters(df):
    """Render all sidebar filters and return filtered dataframe + filter state."""

    # ── Pre-compute defaults (must happen BEFORE widgets are drawn) ──
    min_date        = df['release_date'].min().date()
    max_date        = df['release_date'].max().date()
    budget_max_raw  = float(df['budget'].max())
    revenue_max_raw = float(df['revenue'].max())
    pop_min_raw     = float(df['popularity'].min())
    pop_max_raw     = float(df['popularity'].max())
    rt_min_raw      = int(df['runtime'].min())
    rt_max_raw      = int(df['runtime'].max())

    # ── Reset flag: apply defaults BEFORE any widget is rendered ──────
    # Streamlit forbids setting a widget's key after it has been drawn.
    # So we set the session_state values here (before drawing), then clear the flag.
    if st.session_state.pop("_do_reset", False):
        st.session_state["start_date"]   = min_date
        st.session_state["end_date"]     = max_date
        st.session_state["search_movie"] = []
        st.session_state["lang_filter"]  = []
        st.session_state["genre_filter"] = []
        st.session_state["rating_min"]   = 0.0
        st.session_state["rating_max"]   = 10.0
        st.session_state["budget_min"]   = 0.0
        st.session_state["budget_max"]   = round(budget_max_raw / 1e6, 1)
        st.session_state["rev_min"]      = 0.0
        st.session_state["rev_max"]      = round(revenue_max_raw / 1e6, 1)
        st.session_state["pop_min"]      = round(pop_min_raw, 1)
        st.session_state["pop_max"]      = round(pop_max_raw, 1)
        st.session_state["rt_min"]       = rt_min_raw
        st.session_state["rt_max"]       = rt_max_raw

    st.sidebar.markdown("## 🔍 Filters")
    st.sidebar.markdown("All filters apply to **every chart simultaneously**.")

    # 1. DATE RANGE
    st.sidebar.markdown("### 📅 Date Range")
    start_date = st.sidebar.date_input("Start Date", value=min_date,
                                        min_value=min_date, max_value=max_date,
                                        key="start_date")
    end_date   = st.sidebar.date_input("End Date", value=max_date,
                                        min_value=min_date, max_value=max_date,
                                        key="end_date")
    start_ts = pd.Timestamp(start_date)
    end_ts   = pd.Timestamp(end_date)

    # 2. SEARCH
    st.sidebar.markdown("### 🔎 Search Movie")
    all_titles = sorted(df['title'].dropna().unique().tolist())
    selected_movie = st.sidebar.multiselect(
        "Search & Select Movies", options=all_titles, default=[],
        placeholder="Type to search movies…", key="search_movie"
    )

    # 3. LANGUAGE
    st.sidebar.markdown("### 🌐 Original Language")
    all_lang_codes = sorted(df['original_language'].dropna().unique().tolist())
    lang_opts = {LANGUAGE_NAMES.get(c, c.upper()) + f" ({c})": c for c in all_lang_codes}
    sel_lang_labels = st.sidebar.multiselect(
        "Filter by Language", sorted(lang_opts.keys()), default=[], key="lang_filter"
    )
    selected_languages = [lang_opts[l] for l in sel_lang_labels]

    # 4. GENRES
    st.sidebar.markdown("### 🎭 Genre")
    all_genres = sorted({g for sub in df['genres'] for g in sub})
    selected_genres = st.sidebar.multiselect("Select Genres", all_genres, key="genre_filter")

    # 5. NUMERICAL RANGES
    st.sidebar.markdown("### ⭐ Rating Range")
    rc1, rc2 = st.sidebar.columns(2)
    min_rating = rc1.number_input("Min Rating", 0.0, 10.0, 0.0, 0.1, format="%.1f", key="rating_min")
    max_rating = rc2.number_input("Max Rating", 0.0, 10.0, 10.0, 0.1, format="%.1f", key="rating_max")

    st.sidebar.markdown("### 💰 Budget (Million $)")
    bc1, bc2 = st.sidebar.columns(2)
    budget_min = bc1.number_input("Min Budget", 0.0, value=0.0, step=1.0, key="budget_min")
    budget_max = bc2.number_input("Max Budget", 0.0, value=round(budget_max_raw/1e6,1), step=1.0, key="budget_max")

    st.sidebar.markdown("### 🎯 Revenue (Million $)")
    rv1, rv2 = st.sidebar.columns(2)
    rev_min = rv1.number_input("Min Revenue", 0.0, value=0.0, step=1.0, key="rev_min")
    rev_max = rv2.number_input("Max Revenue", 0.0, value=round(revenue_max_raw/1e6,1), step=1.0, key="rev_max")

    st.sidebar.markdown("### 🔥 Popularity")
    pp1, pp2 = st.sidebar.columns(2)
    pop_min = pp1.number_input("Min Pop", 0.0, value=round(pop_min_raw,1), step=1.0, key="pop_min")
    pop_max = pp2.number_input("Max Pop", 0.0, value=round(pop_max_raw,1), step=1.0, key="pop_max")

    st.sidebar.markdown("### ⏱️ Runtime (min)")
    rt1, rt2 = st.sidebar.columns(2)
    rt_min = rt1.number_input("Min Runtime", 0, value=rt_min_raw, step=1, key="rt_min")
    rt_max = rt2.number_input("Max Runtime", 0, value=rt_max_raw, step=1, key="rt_max")

    st.sidebar.divider()
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True, key="reset_btn"):
        # Set the flag — defaults are applied at the TOP of the next run, before widgets render
        st.session_state["_do_reset"] = True
        st.rerun()

    # APPLY FILTERS
    df2 = df[
        (df['release_date'] >= start_ts) & (df['release_date'] <= end_ts) &
        (df['vote_average'] >= min_rating) & (df['vote_average'] <= max_rating) &
        (df['budget']  >= budget_min * 1e6) & (df['budget']  <= budget_max * 1e6) &
        (df['revenue'] >= rev_min    * 1e6) & (df['revenue'] <= rev_max    * 1e6) &
        (df['popularity'] >= pop_min) & (df['popularity'] <= pop_max) &
        (df['runtime'] >= rt_min) & (df['runtime'] <= rt_max)
    ].copy()

    if selected_genres:    df2 = df2[df2['genres'].apply(lambda x: any(g in x for g in selected_genres))]
    if selected_languages: df2 = df2[df2['original_language'].isin(selected_languages)]
    if selected_movie:     df2 = df2[df2['title'].isin(selected_movie)]

    # Filter state for badge
    filter_state = {
        "selected_movie": selected_movie,
        "selected_languages": selected_languages,
        "selected_genres": selected_genres,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_max_raw": budget_max_raw,
        "revenue_max_raw": revenue_max_raw,
        "language_names": LANGUAGE_NAMES,
    }

    return df2, filter_state