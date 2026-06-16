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

    # ── Pre-compute defaults ──────────────────────────────────────────
    min_date        = df['release_date'].min().date()
    max_date        = df['release_date'].max().date()
    budget_max_raw  = float(df['budget'].max())
    revenue_max_raw = float(df['revenue'].max())
    pop_min_raw     = float(df['popularity'].min())
    pop_max_raw     = float(df['popularity'].max())
    rt_min_raw      = int(df['runtime'].min())
    rt_max_raw      = int(df['runtime'].max())

    # ── Default snapshot (what "no filters" looks like) ───────────────
    default_applied = {
        "start_date":   min_date,
        "end_date":     max_date,
        "search_movie": [],
        "lang_filter":  [],
        "genre_filter": [],
        "rating_min":   0.0,
        "rating_max":   10.0,
        "budget_min":   0.0,
        "budget_max":   round(budget_max_raw / 1e6, 1),
        "rev_min":      0.0,
        "rev_max":      round(revenue_max_raw / 1e6, 1),
        "pop_min":      round(pop_min_raw, 1),
        "pop_max":      round(pop_max_raw, 1),
        "rt_min":       rt_min_raw,
        "rt_max":       rt_max_raw,
    }

    # ── Initialise applied snapshot on first run ──────────────────────
    if "applied_filters" not in st.session_state:
        st.session_state["applied_filters"] = default_applied.copy()

    # ── Handle RESET (set widget keys + applied snapshot, then rerun) ─
    if st.session_state.pop("_do_reset", False):
        for k, v in default_applied.items():
            st.session_state[k] = v
        st.session_state["applied_filters"] = default_applied.copy()
        st.rerun()

    # ═════════════════════════════════════════════════════════════════
    # SIDEBAR WIDGETS  (values are pending until Apply is clicked)
    # ═════════════════════════════════════════════════════════════════
    st.sidebar.markdown("## 🔍 Filters")
    st.sidebar.markdown("Adjust filters then click **Apply Filters** to update charts.")

    # 1. DATE RANGE
    st.sidebar.markdown("### 📅 Date Range")
    start_date = st.sidebar.date_input("Start Date", value=st.session_state.get("start_date", min_date),
                                        min_value=min_date, max_value=max_date,
                                        key="start_date")
    end_date   = st.sidebar.date_input("End Date", value=st.session_state.get("end_date", max_date),
                                        min_value=min_date, max_value=max_date,
                                        key="end_date")

    # 2. SEARCH
    st.sidebar.markdown("### 🔎 Search Movie")
    all_titles = sorted(df['title'].dropna().unique().tolist())
    selected_movie = st.sidebar.multiselect(
        "Search & Select Movies", options=all_titles,
        default=st.session_state.get("search_movie", []),
        placeholder="Type to search movies…", key="search_movie"
    )

    # 3. LANGUAGE
    st.sidebar.markdown("### 🌐 Original Language")
    all_lang_codes = sorted(df['original_language'].dropna().unique().tolist())
    lang_opts = {LANGUAGE_NAMES.get(c, c.upper()) + f" ({c})": c for c in all_lang_codes}
    sel_lang_labels = st.sidebar.multiselect(
        "Filter by Language", sorted(lang_opts.keys()),
        default=st.session_state.get("lang_filter", []),
        key="lang_filter"
    )

    # 4. GENRES
    st.sidebar.markdown("### 🎭 Genre")
    all_genres = sorted({g for sub in df['genres'] for g in sub})
    selected_genres = st.sidebar.multiselect(
        "Select Genres", all_genres,
        default=st.session_state.get("genre_filter", []),
        key="genre_filter"
    )

    # 5. NUMERICAL RANGES
    st.sidebar.markdown("### ⭐ Rating Range")
    rc1, rc2 = st.sidebar.columns(2)
    min_rating = rc1.number_input("Min Rating", 0.0, 10.0,
                                   value=float(st.session_state.get("rating_min", 0.0)),
                                   step=0.1, format="%.1f", key="rating_min")
    max_rating = rc2.number_input("Max Rating", 0.0, 10.0,
                                   value=float(st.session_state.get("rating_max", 10.0)),
                                   step=0.1, format="%.1f", key="rating_max")

    st.sidebar.markdown("### 💰 Budget (Million $)")
    bc1, bc2 = st.sidebar.columns(2)
    budget_min = bc1.number_input("Min Budget", 0.0,
                                   value=float(st.session_state.get("budget_min", 0.0)),
                                   step=1.0, key="budget_min")
    budget_max = bc2.number_input("Max Budget", 0.0,
                                   value=float(st.session_state.get("budget_max", round(budget_max_raw/1e6, 1))),
                                   step=1.0, key="budget_max")

    st.sidebar.markdown("### 🎯 Revenue (Million $)")
    rv1, rv2 = st.sidebar.columns(2)
    rev_min = rv1.number_input("Min Revenue", 0.0,
                                value=float(st.session_state.get("rev_min", 0.0)),
                                step=1.0, key="rev_min")
    rev_max = rv2.number_input("Max Revenue", 0.0,
                                value=float(st.session_state.get("rev_max", round(revenue_max_raw/1e6, 1))),
                                step=1.0, key="rev_max")

    st.sidebar.markdown("### 🔥 Popularity")
    pp1, pp2 = st.sidebar.columns(2)
    pop_min = pp1.number_input("Min Pop", 0.0,
                                value=float(st.session_state.get("pop_min", round(pop_min_raw, 1))),
                                step=1.0, key="pop_min")
    pop_max = pp2.number_input("Max Pop", 0.0,
                                value=float(st.session_state.get("pop_max", round(pop_max_raw, 1))),
                                step=1.0, key="pop_max")

    st.sidebar.markdown("### ⏱️ Runtime (min)")
    rt1, rt2 = st.sidebar.columns(2)
    rt_min = rt1.number_input("Min Runtime", 0,
                               value=int(st.session_state.get("rt_min", rt_min_raw)),
                               step=1, key="rt_min")
    rt_max = rt2.number_input("Max Runtime", 0,
                               value=int(st.session_state.get("rt_max", rt_max_raw)),
                               step=1, key="rt_max")

    st.sidebar.divider()

    # ── APPLY & RESET buttons ──────────────────────────────────────────
    btn_col1, btn_col2 = st.sidebar.columns(2)

    with btn_col1:
        if st.button("✅ Apply Filters", use_container_width=True, key="apply_btn",
                     type="primary"):
            st.session_state["applied_filters"] = {
                "start_date":   start_date,
                "end_date":     end_date,
                "search_movie": selected_movie,
                "lang_filter":  sel_lang_labels,
                "genre_filter": selected_genres,
                "rating_min":   min_rating,
                "rating_max":   max_rating,
                "budget_min":   budget_min,
                "budget_max":   budget_max,
                "rev_min":      rev_min,
                "rev_max":      rev_max,
                "pop_min":      pop_min,
                "pop_max":      pop_max,
                "rt_min":       rt_min,
                "rt_max":       rt_max,
            }
            st.rerun()

    with btn_col2:
        if st.button("🔄 Reset", use_container_width=True, key="reset_btn"):
            st.session_state["_do_reset"] = True
            st.rerun()

    # ═════════════════════════════════════════════════════════════════
    # APPLY FILTERS using the SAVED snapshot (not live widget values)
    # ═════════════════════════════════════════════════════════════════
    af = st.session_state["applied_filters"]

    start_ts = pd.Timestamp(af["start_date"])
    end_ts   = pd.Timestamp(af["end_date"])

    # Resolve language codes from saved label list
    applied_languages = [lang_opts[l] for l in af["lang_filter"] if l in lang_opts]

    df2 = df[
        (df['release_date'] >= start_ts) & (df['release_date'] <= end_ts) &
        (df['vote_average'] >= af["rating_min"]) & (df['vote_average'] <= af["rating_max"]) &
        (df['budget']  >= af["budget_min"] * 1e6) & (df['budget']  <= af["budget_max"] * 1e6) &
        (df['revenue'] >= af["rev_min"]    * 1e6) & (df['revenue'] <= af["rev_max"]    * 1e6) &
        (df['popularity'] >= af["pop_min"]) & (df['popularity'] <= af["pop_max"]) &
        (df['runtime'] >= af["rt_min"]) & (df['runtime'] <= af["rt_max"])
    ].copy()

    if af["genre_filter"]:    df2 = df2[df2['genres'].apply(lambda x: any(g in x for g in af["genre_filter"]))]
    if applied_languages:     df2 = df2[df2['original_language'].isin(applied_languages)]
    if af["search_movie"]:    df2 = df2[df2['title'].isin(af["search_movie"])]

    # Filter state for badge
    filter_state = {
        "selected_movie":    af["search_movie"],
        "selected_languages": applied_languages,
        "selected_genres":   af["genre_filter"],
        "min_rating":        af["rating_min"],
        "max_rating":        af["rating_max"],
        "budget_min":        af["budget_min"],
        "budget_max":        af["budget_max"],
        "budget_max_raw":    budget_max_raw,
        "revenue_max_raw":   revenue_max_raw,
        "language_names":    LANGUAGE_NAMES,
    }

    return df2, filter_state