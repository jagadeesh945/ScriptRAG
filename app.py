import base64
import os
import streamlit as st
from rag_core import EvidenceRAG

# Page Configuration with Brand Identity
st.set_page_config(
    page_title="ScriptRAG — Cinematic Screenplay Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Logo SVG
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")
logo_svg_html = ""
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "r", encoding="utf-8") as f:
        raw_svg = f.read()
        b64_svg = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
        logo_svg_html = f'<img src="data:image/svg+xml;base64,{b64_svg}" class="brand-logo" alt="ScriptRAG Logo" />'
else:
    logo_svg_html = '<div class="brand-logo-fallback">🎬</div>'

# Cinematic Premium Styling
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Global Dark Theme Foundations */
    :root {{
        --bg-main: #101216;
        --bg-secondary: #151920;
        --bg-card: #1B2028;
        --bg-elevated: #222934;
        --accent-amber: #D99A45;
        --accent-amber-hover: #E5A958;
        --accent-teal: #65B8B0;
        --text-primary: #F4EBDD;
        --text-secondary: #A6A6A6;
        --border-color: #303743;
    }}

    /* Base Body & Reset */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}

    #MainMenu, footer, header {{
        visibility: hidden !important;
        display: none !important;
    }}

    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 7rem !important; /* Prevents sticky chat input from overlapping dashboard content */
        max-width: 1120px !important;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, .brand-title {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }}

    p, span, label, div {{
        color: var(--text-primary);
    }}

    /* Top Brand Navigation Header */
    .brand-header-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.4rem;
        background: linear-gradient(180deg, rgba(21, 25, 32, 0.95) 0%, rgba(16, 18, 22, 0.9) 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}

    .brand-identity {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .brand-logo {{
        width: 44px;
        height: 44px;
        filter: drop-shadow(0 2px 8px rgba(217, 154, 69, 0.25));
    }}

    .brand-logo-fallback {{
        font-size: 2rem;
    }}

    .brand-title {{
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
        color: var(--text-primary);
        display: flex;
        align-items: baseline;
        gap: 6px;
    }}

    .brand-title span {{
        color: var(--accent-amber);
        font-size: 1.6rem;
    }}

    .brand-subtitle {{
        font-size: 0.76rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 2px;
    }}

    .header-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
    }}

    .header-badge-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--accent-teal);
        box-shadow: 0 0 8px var(--accent-teal);
    }}

    /* Upload Container */
    .upload-container {{
        background: linear-gradient(145deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.6rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }}

    .upload-header {{
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .upload-desc {{
        font-size: 0.86rem;
        color: var(--text-secondary);
        margin-bottom: 1.2rem;
        line-height: 1.45;
    }}

    /* Active Script Showcase Card */
    .active-script-card {{
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-amber);
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }}

    .script-info-title {{
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--accent-amber);
        font-weight: 600;
        margin-bottom: 3px;
    }}

    .script-info-name {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.18rem;
        font-weight: 600;
        color: var(--text-primary);
    }}

    .script-info-meta {{
        font-size: 0.84rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }}

    /* Metrics Grid */
    .metric-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1.1rem 0.9rem;
        text-align: center;
        transition: transform 0.15s ease, border-color 0.15s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}

    .metric-card:hover {{
        border-color: var(--accent-amber);
        transform: translateY(-2px);
    }}

    .metric-value {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--accent-amber);
        line-height: 1.1;
    }}

    .metric-label {{
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 6px;
    }}

    /* Quick Action Buttons */
    .quick-prompt-label {{
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-secondary);
        margin-bottom: 0.6rem;
    }}

    /* Streamlit Button Restyling */
    div.stButton > button {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.86rem !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}

    div.stButton > button:hover {{
        border-color: var(--accent-amber) !important;
        color: var(--accent-amber) !important;
        background-color: var(--bg-elevated) !important;
        box-shadow: 0 2px 10px rgba(217, 154, 69, 0.15) !important;
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--accent-amber) 0%, #C48737 100%) !important;
        color: #101216 !important;
        font-weight: 600 !important;
        border: none !important;
    }}

    div.stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, var(--accent-amber-hover) 0%, var(--accent-amber) 100%) !important;
        box-shadow: 0 4px 15px rgba(217, 154, 69, 0.35) !important;
        transform: translateY(-1px);
    }}

    /* Inspector & Expanders */
    div[data-testid="stExpander"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        margin-bottom: 1.2rem !important;
        overflow: hidden;
    }}

    div[data-testid="stExpander"] summary {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: var(--text-primary) !important;
        padding: 0.8rem 1rem !important;
    }}

    div[data-testid="stExpander"] summary:hover {{
        color: var(--accent-amber) !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent !important;
        border-bottom: 1px solid var(--border-color) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 6px 6px 0 0 !important;
        font-weight: 500 !important;
        font-size: 0.86rem !important;
        padding: 8px 16px !important;
        border: none !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--accent-amber) !important;
        border-bottom: 2px solid var(--accent-amber) !important;
        background-color: rgba(217, 154, 69, 0.06) !important;
    }}

    /* Dataframe Table Styling */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        background-color: var(--bg-secondary) !important;
    }}

    /* Source Reference Badges */
    .badge-screenplay {{
        background-color: rgba(217, 154, 69, 0.15);
        color: var(--accent-amber);
        border: 1px solid rgba(217, 154, 69, 0.35);
        padding: 3px 9px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }}

    .badge-theory {{
        background-color: rgba(101, 184, 176, 0.15);
        color: var(--accent-teal);
        border: 1px solid rgba(101, 184, 176, 0.35);
        padding: 3px 9px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }}

    /* Chat Messages */
    div[data-testid="stChatMessage"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1.1rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }}

    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: var(--bg-secondary) !important;
    }}

    /* Streamlit Chat Input - Fixed position with elevated cinematic bar */
    div[data-testid="stChatInput"] {{
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.5) !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: var(--text-secondary) !important;
    }}

    /* Citation Snippet Text */
    .citation-block {{
        background-color: var(--bg-secondary);
        border-left: 3px solid var(--border-color);
        padding: 0.6rem 0.9rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin-top: 0.4rem;
        margin-bottom: 0.6rem;
        line-height: 1.45;
    }}
</style>
""", unsafe_allow_html=True)

# State initialization (PRESERVING EXACT SESSION BEHAVIOR)
if "rag" not in st.session_state:
    st.session_state.rag = EvidenceRAG()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "screenplay_stats" not in st.session_state:
    st.session_state.screenplay_stats = None

rag: EvidenceRAG = st.session_state.rag

# Header Presentation with Custom Clapperboard / Screenplay AI Logo
status_text = "System Ready" if not st.session_state.screenplay_stats else "Script Active"
st.markdown(f"""
<div class="brand-header-container">
    <div class="brand-identity">
        {logo_svg_html}
        <div>
            <div class="brand-title">Script<span>RAG</span></div>
            <div class="brand-subtitle">Cinematic Screenplay Intelligence</div>
        </div>
    </div>
    <div class="header-badge">
        <span class="header-badge-dot"></span>
        <span>{status_text}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# PROMINENT MAIN-PAGE UPLOAD SECTION (Visible when no screenplay is active)
if not st.session_state.screenplay_stats:
    st.markdown("""
    <div class="upload-container">
        <div class="upload-header">Upload Movie Screenplay</div>
        <div class="upload-desc">
            Select a complete screenplay in PDF format. ScriptRAG performs full-document indexing, 
            scene breakdown, character alias normalization, and benchmarks narrative beats against Syd Field, 
            Robert McKee, and Blake Snyder frameworks.
        </div>
    """, unsafe_allow_html=True)

    col_upload, col_btn = st.columns([3, 1])
    with col_upload:
        screenplay_file = st.file_uploader(
            "Choose a Screenplay PDF",
            type=["pdf"],
            key="main_screenplay_uploader",
            label_visibility="collapsed"
        )
    with col_btn:
        process_btn = st.button("Process Screenplay", type="primary", width="stretch")

    if screenplay_file is not None and process_btn:
        with st.spinner("Analyzing screenplay structure and indexing narrative beats..."):
            try:
                stats = rag.process_screenplay(screenplay_file.read(), screenplay_file.name)
                stats["name"] = screenplay_file.name
                st.session_state.screenplay_stats = stats
                st.rerun()
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Sophisticated Active Screenplay Card with reset action
    sp = st.session_state.screenplay_stats
    st.markdown(f"""
    <div class="active-script-card">
        <div>
            <div class="script-info-title">Active Production Script</div>
            <div class="script-info-name">{sp['name']}</div>
            <div class="script-info-meta">{sp['total_pages']} Pages &nbsp;•&nbsp; {sp['total_scenes']} Scenes &nbsp;•&nbsp; {sp['total_named_characters']} Named Speaking Characters</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_upload_btn, _ = st.columns([1.5, 4.5])
    with c_upload_btn:
        if st.button("Upload Another Script"):
            st.session_state.screenplay_stats = None
            st.session_state.messages = []
            st.session_state.rag = EvidenceRAG()
            st.rerun()

# Analytics Dashboard (Preserves all existing metrics and calculations)
if st.session_state.screenplay_stats and rag.screenplay_structure:
    sp = st.session_state.screenplay_stats
    struct = rag.screenplay_structure

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{sp["total_pages"]}</div><div class="metric-label">Total Pages</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{sp["total_scenes"]}</div><div class="metric-label">Scenes Extracted</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{struct["total_named_speaking"]}</div><div class="metric-label">Named Speaking Roles</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(rag.book_names)}</div><div class="metric-label">Built-in Frameworks</div></div>', unsafe_allow_html=True)

    st.write("")

    # Structured Screenplay Inspector (Character Registry, Scene Breakdown, Story Timeline)
    with st.expander("Structured Screenplay Inspector (Character Registry & Scene Breakdown)"):
        tab1, tab2, tab3 = st.tabs(["Character Registry", "Scene Breakdown", "Story Timeline"])
        with tab1:
            st.write(f"**Identified Speaking Characters ({struct['total_named_speaking']} Named, {struct['total_unnamed_speaking']} Unnamed Roles):**")
            char_data = []
            for c in struct["named_speaking_characters"]:
                char_data.append({
                    "Canonical Name": c["canonical_name"],
                    "Aliases": ", ".join(c["aliases"]) if c["aliases"] else "None",
                    "First Page": c["first_page"],
                    "Dialogue Count": c["dialogue_count"],
                    "Speaking Pages": f"{c['speaking_pages'][:6]}..."
                })
            st.dataframe(char_data, width="stretch")

        with tab2:
            st.write(f"**Total Scenes Extracted ({len(struct['scenes'])}):**")
            scene_preview = []
            for sc in struct["scenes"][:60]:
                scene_preview.append({
                    "Scene #": sc["scene_number"],
                    "Page": sc["page"],
                    "Heading": sc["heading"],
                    "Location": sc["location"],
                    "Time": sc["time_of_day"],
                    "Speaking Characters": ", ".join(sc["characters_speaking"])
                })
            st.dataframe(scene_preview, width="stretch")

        with tab3:
            st.write("**Macro Three-Act Proportions:**")
            hs = rag.hierarchical_summaries
            st.write(f"- **Act One Setup:** {hs.get('act1_range', 'Pages 1-30')}")
            st.write(f"- **Act Two Confrontation:** {hs.get('act2_range', 'Pages 31-90')}")
            st.write(f"- **Act Three Resolution:** {hs.get('act3_range', 'Pages 91-120')}")
            st.text_area("Chronological Scene Progression", value=hs.get("timeline_text", ""), height=180)

# Quick Sample Analytical Prompts (Preserves all exact prompt actions)
st.markdown('<div class="quick-prompt-label">Quick Analytical Inquiries:</div>', unsafe_allow_html=True)
q_cols = st.columns(4)
quick_query = None
if q_cols[0].button("Character Count"):
    quick_query = "How many distinct characters are in the screenplay? Distinguish named speaking characters from unnamed roles."
if q_cols[1].button("Three-Act Structure"):
    quick_query = "Does this screenplay follow the three-act structure? Where do Act One, the Midpoint, and Act Three occur?"
if q_cols[2].button("Central Conflict"):
    quick_query = "What is the central dramatic conflict, and are the stakes escalating throughout the script?"
if q_cols[3].button("Character Arc"):
    quick_query = "Is the protagonist's character arc complete according to Robert McKee's principles?"

# Chat History Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "screenplay_sources" in msg and msg["screenplay_sources"]:
            with st.expander("Screenplay Evidence Citations"):
                for s in msg["screenplay_sources"]:
                    st.markdown(f'<span class="badge-screenplay">Screenplay</span> **Page {s["page"]}** ({s["source"]} - Match: {s["score"]})', unsafe_allow_html=True)
                    st.markdown(f'<div class="citation-block">{s["content"]}</div>', unsafe_allow_html=True)
        if "book_sources" in msg and msg["book_sources"]:
            with st.expander("Screenwriting Theory References"):
                for b in msg["book_sources"]:
                    st.markdown(f'<span class="badge-theory">Theory</span> **{b["source"]}** (Page {b["page"]})', unsafe_allow_html=True)
                    st.markdown(f'<div class="citation-block">{b["content"]}</div>', unsafe_allow_html=True)

# User Chat Input (Positioned with adequate bottom padding so it never covers content)
if prompt := st.chat_input("Ask any question about scenes, characters, three-act structure, or pacing...") or quick_query:
    active_prompt = prompt if prompt else quick_query

    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.write(active_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing screenplay evidence and benchmarking against film theory..."):
            result = rag.answer_query(active_prompt)
            st.write(result["answer"])

            if result.get("screenplay_sources"):
                with st.expander("Screenplay Evidence Citations"):
                    for s in result["screenplay_sources"]:
                        st.markdown(f'<span class="badge-screenplay">Screenplay</span> **Page {s["page"]}** ({s["source"]} - Match: {s["score"]})', unsafe_allow_html=True)
                        st.markdown(f'<div class="citation-block">{s["content"]}</div>', unsafe_allow_html=True)

            if result.get("book_sources"):
                with st.expander("Screenwriting Theory References"):
                    for b in result["book_sources"]:
                        st.markdown(f'<span class="badge-theory">Theory</span> **{b["source"]}** (Page {b["page"]})', unsafe_allow_html=True)
                        st.markdown(f'<div class="citation-block">{b["content"]}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "screenplay_sources": result.get("screenplay_sources", []),
        "book_sources": result.get("book_sources", [])
    })
