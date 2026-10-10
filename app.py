import html
import os
import tempfile

import streamlit as st

from logic import generate_project_plan


# =========================
# Page configuration
# =========================

st.set_page_config(
    page_title="AI Project Planner",
    page_icon="📋",
    layout="wide",
)


# =========================
# Styling
# =========================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500&display=swap');

    :root {
        --ink: #14213D;
        --muted: #5B6B85;
        --paper: #F4F7FB;
        --card: #FFFFFF;
        --line: #DCE3EE;
        --accent: #3A5BD9;
        --accent-soft: #E8EDFC;
        --teal: #0FA3B1;
        --teal-soft: #E0F5F7;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }
    .stApp { background: var(--paper); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 1050px; padding-top: 2rem; padding-bottom: 4rem; }

    h1, h2, h3, .hero h1 { font-family: 'Sora', sans-serif; letter-spacing: -0.02em; }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, #14213D 0%, #274690 60%, #3A5BD9 100%);
        color: #fff;
        padding: 3rem 2.8rem;
        border-radius: 24px;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 32px rgba(20, 33, 61, .18);
    }
    .hero::before {
        content: ''; position: absolute; right: -60px; top: -60px;
        width: 260px; height: 260px; border-radius: 50%;
        background: rgba(15, 163, 177, .35);
    }
    .hero::after {
        content: ''; position: absolute; right: 110px; bottom: -90px;
        width: 200px; height: 200px; border-radius: 50%;
        background: rgba(255, 255, 255, .08);
    }
    .hero > * { position: relative; z-index: 1; }
    .hero h1 {
        color: #fff;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 .8rem 0;
        padding: 0;
    }
    .hero p { color: #C9D6F5; font-size: 1.1rem; line-height: 1.6; margin: 0; max-width: 560px; }

    /* Input labels */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] *,
    .stFileUploader label,
    .stNumberInput label {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        color: var(--ink) !important;
        letter-spacing: -0.01em;
    }
    [data-testid="stWidgetLabel"] {
        margin-bottom: .5rem;
    }

    /* Input card */
    div[data-testid="stFileUploader"] section {
        background: var(--card);
        border: 2px dashed var(--line);
        border-radius: 14px;
        padding: 1.4rem;
    }
    div[data-testid="stFileUploader"] section:hover { border-color: var(--accent); }

    div[data-testid="stNumberInput"] input {
        border-radius: 10px;
        font-weight: 500;
    }

    .stButton > button, .stDownloadButton > button {
        background: var(--accent);
        color: #fff;
        border: none;
        border-radius: 12px;
        padding: .7rem 1.6rem;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        width: 100%;
        transition: background .15s ease, transform .1s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #2B47B3;
        color: #fff;
        border: none;
    }
    .stButton > button:active { transform: scale(.98); }
    .stButton > button:focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; }

    /* Metrics */
    .stats { display: flex; gap: 1rem; margin: 1.6rem 0 1rem 0; flex-wrap: wrap; }
    .stat {
        flex: 1; min-width: 140px;
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.2rem;
    }
    .stat b { display: block; font-family: 'Sora', sans-serif; font-size: 1.7rem; color: var(--accent); }
    .stat span { color: var(--muted); font-size: .9rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        border-radius: 10px 10px 0 0;
        padding: .6rem 1.1rem;
    }
    .stTabs [aria-selected="true"] { color: var(--accent); }

    /* Description */
    .panel {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        line-height: 1.7;
        max-width: 78ch;
    }

    /* Skill chips */
    .chips { display: flex; flex-wrap: wrap; gap: .6rem; }
    .chip {
        background: var(--accent-soft);
        color: var(--accent);
        border-radius: 999px;
        padding: .45rem 1rem;
        font-weight: 500;
        font-size: .93rem;
    }

    /* Badges (task titles, role names, week ranges) */
    .badge {
        display: inline-block;
        background: var(--teal-soft);
        color: var(--teal);
        border-radius: 999px;
        padding: .2rem .8rem;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: .85rem;
    }
    .badge-blue { background: var(--accent-soft); color: var(--accent); }
    .sub { color: var(--muted); font-size: .93rem; margin-top: .4rem; line-height: 1.55; }

    /* Tasks */
    .task {
        display: flex; gap: .8rem; align-items: flex-start;
        background: var(--card);
        border: 1px solid var(--line);
        border-left: 4px solid var(--teal);
        border-radius: 10px;
        padding: .85rem 1.1rem;
        margin-bottom: .6rem;
    }
    .task i {
        width: 18px; height: 18px; flex: none; margin-top: 3px;
        border: 2px solid var(--teal); border-radius: 5px;
    }

    /* Roles */
    .roles { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: .9rem; }
    .role {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        display: flex; gap: .8rem; align-items: flex-start;
    }
    .avatar {
        flex: none; width: 38px; height: 38px; border-radius: 50%;
        background: var(--teal-soft); color: var(--teal);
        display: grid; place-items: center;
        font-family: 'Sora', sans-serif; font-weight: 700;
    }

    /* Timeline (a real sequence, so it gets numbered steps) */
    .timeline { position: relative; padding-left: 2.6rem; }
    .timeline::before {
        content: ''; position: absolute; left: 15px; top: 6px; bottom: 6px;
        width: 2px; background: var(--line);
    }
    .step { position: relative; margin-bottom: 1rem; }
    .step .dot {
        position: absolute; left: -2.6rem; top: 0;
        width: 32px; height: 32px; border-radius: 50%;
        background: var(--accent); color: #fff;
        display: grid; place-items: center;
        font-family: 'Sora', sans-serif; font-weight: 600; font-size: .85rem;
    }
    .step .body {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: .8rem 1.1rem;
    }

    @media (max-width: 640px) {
        .hero { padding: 2rem 1.4rem; }
        .hero h1 { font-size: 2.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Helpers
# =========================

def esc(value) -> str:
    return html.escape(str(value))


def split_title(text):
    # Splits "Title: details" into its two parts.
    title, sep, rest = str(text).partition(":")
    if not sep or not rest.strip():
        return str(text).strip(), ""
    return title.strip(), rest.strip()


def badge_block(text, css_class="badge") -> str:
    # Title as a badge, details below it.
    title, rest = split_title(text)
    sub = f'<div class="sub">{esc(rest)}</div>' if rest else ""
    return f'<div><span class="{css_class}">{esc(title)}</span>{sub}</div>'


# =========================
# Hero
# =========================

st.markdown(
    """
    <div class="hero">
        <h1>📋 AI Project Planner</h1>
        <p>Upload a project brief and get tasks, team roles, and a week-by-week
        timeline sized to your team.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# User inputs
# =========================

left, right = st.columns([3, 2], gap="large")

with left:
    uploaded_file = st.file_uploader(
        "Project description (PDF)",
        type=["pdf"],
    )

with right:
    team_size = st.number_input("Team members", min_value=1, value=4, step=1)
    duration = st.number_input("Project duration (weeks)", min_value=1, value=12, step=1)
    generate = st.button("Generate project plan")


# =========================
# Generate project plan
# =========================

if generate:
    if uploaded_file is None:
        st.warning("Upload a PDF to continue.")
    else:
        tmp_path = None
        try:
            # Save the uploaded PDF to a temporary file.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            with st.spinner("Reading your brief and building the plan..."):
                st.session_state["plan"] = generate_project_plan(
                    tmp_path, team_size, duration
                )
                st.session_state["meta"] = (team_size, duration)
        except Exception as exc:
            st.error(f"Couldn't generate the plan: {exc}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)


# =========================
# Display results
# =========================

plan = st.session_state.get("plan")

if plan:
    team, weeks = st.session_state.get("meta", (team_size, duration))

    st.markdown(
        f"""
        <div class="stats">
            <div class="stat"><b>{len(plan.tasks)}</b><span>Tasks</span></div>
            <div class="stat"><b>{len(plan.required_skills)}</b><span>Skills needed</span></div>
            <div class="stat"><b>{team}</b><span>Team members</span></div>
            <div class="stat"><b>{weeks}</b><span>Weeks</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_overview, tab_tasks, tab_team, tab_timeline = st.tabs(
        ["Overview", "Tasks", "Team", "Timeline"]
    )

    with tab_overview:
        st.markdown(
            f'<div class="panel">{esc(plan.description)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("#### Required skills")
        chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in plan.required_skills)
        st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)

    with tab_tasks:
        tasks = "".join(
            f'<div class="task"><i></i>{badge_block(t)}</div>' for t in plan.tasks
        )
        st.markdown(tasks, unsafe_allow_html=True)

    with tab_team:
        roles = "".join(
            f'<div class="role"><div class="avatar">{n}</div>'
            f"{badge_block(r)}</div>"
            for n, r in enumerate(plan.team_roles, start=1)
        )
        st.markdown(f'<div class="roles">{roles}</div>', unsafe_allow_html=True)

    with tab_timeline:
        steps = "".join(
            f'<div class="step"><div class="dot">{n}</div>'
            f'<div class="body">{badge_block(item, "badge badge-blue")}</div></div>'
            for n, item in enumerate(plan.timeline, start=1)
        )
        st.markdown(f'<div class="timeline">{steps}</div>', unsafe_allow_html=True)


# in the terminal, run: streamlit run app.py