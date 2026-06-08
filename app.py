import streamlit as st
import pandas as pd
import yaml
import re
from io import StringIO

st.set_page_config(page_title="Data Quality Agent", layout="wide", page_icon="✦")

from auth.database import (
    create_user, verify_user, save_upload, save_validation,
    save_cleaned_file, save_uploaded_csv, save_cleaned_csv,
    get_history, get_issues,
)
from agent.autofix import auto_fix
from agent.validator import validate
from agent.llm_helper import generate_fix
from agent.ai_summary import generate_dataset_summary
from agent.ai_chat import ask_dataset_question
from agent.quality_score import calculate_quality_score
from agent.ai_insights import generate_root_cause_analysis

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ========== AUTH SHARED ANIMATIONS ========== */
@keyframes dqa-orb-float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50%       { transform: translateY(-22px) scale(1.06); }
}
@keyframes dqa-orb-drift {
    0%, 100% { transform: translateX(0px) scale(1); }
    50%       { transform: translateX(18px) scale(1.04); }
}
@keyframes dqa-orb-spin {
    0%, 100% { transform: translateY(0px) translateX(0px) scale(1); }
    33%       { transform: translateY(-14px) translateX(10px) scale(1.05); }
    66%       { transform: translateY(8px) translateX(-8px) scale(0.97); }
}
@keyframes dqa-card-in {
    0%   { opacity: 0; transform: translateY(36px) scale(0.97); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes dqa-fade-up {
    0%   { opacity: 0; transform: translateY(14px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes dqa-dot-pulse {
    0%, 100% { transform: scale(1);   opacity: 0.5; }
    50%       { transform: scale(1.5); opacity: 1; }
}
@keyframes slideDown {
    from { opacity: 0; transform: translateY(-14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Floating orbs ── */
.dqa-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    z-index: 0;
}
.dqa-orb-1 {
    width: 420px; height: 420px;
    background: rgba(167, 139, 250, 0.25);
    top: -100px; left: -120px;
    animation: dqa-orb-float 9s ease-in-out infinite;
}
.dqa-orb-2 {
    width: 300px; height: 300px;
    background: rgba(196, 181, 253, 0.22);
    bottom: -80px; right: -80px;
    animation: dqa-orb-drift 11s ease-in-out infinite;
    animation-delay: 3s;
}
.dqa-orb-3 {
    width: 200px; height: 200px;
    background: rgba(139, 92, 246, 0.15);
    top: 40%; left: 65%;
    animation: dqa-orb-spin 7s ease-in-out infinite;
    animation-delay: 5s;
}

/* ── Pulsing dots ── */
.dqa-dots {
    display: flex; gap: 8px; justify-content: center;
    margin-bottom: 20px;
    animation: dqa-fade-up 0.5s 0.05s both;
}
.dqa-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: #a78bfa;
    animation: dqa-dot-pulse 1.6s ease-in-out infinite;
}
.dqa-dot:nth-child(2) { animation-delay: 0.2s; background: #8b5cf6; }
.dqa-dot:nth-child(3) { animation-delay: 0.4s; background: #7c3aed; }

/* ── Auth titles ── */
.auth-title {
    font-size: 2.6rem;
    font-weight: 800;
    text-align: center;
    color: #3b0764;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
    animation: slideDown 0.55s ease both;
    position: relative; z-index: 2;
}
.auth-sub {
    text-align: center;
    font-size: 0.95rem;
    color: #6b21a8;
    margin-bottom: 32px;
    font-weight: 400;
    animation: slideDown 0.65s ease both;
    position: relative; z-index: 2;
}

/* ── Auth input wrapper ── */
.auth-col-wrap {
    position: relative; z-index: 2;
    animation: dqa-card-in 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

/* Input fields — no card, open style */
.auth-col-wrap .stTextInput {
    margin-bottom: 8px;
    animation: dqa-fade-up 0.6s both;
}
.auth-col-wrap .stTextInput:nth-of-type(1) { animation-delay: 0.25s; }
.auth-col-wrap .stTextInput:nth-of-type(2) { animation-delay: 0.35s; }
.auth-col-wrap .stTextInput:nth-of-type(3) { animation-delay: 0.45s; }

.auth-col-wrap .stTextInput label {
    color: #4c1d95 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

.auth-col-wrap .stTextInput > div > div > input {
    background: rgba(237, 233, 254, 0.55) !important;
    border: 1.5px solid rgba(167, 139, 250, 0.35) !important;
    border-radius: 14px !important;
    color: #2e1065 !important;
    font-size: 0.95rem !important;
    padding: 13px 16px !important;
    transition: border-color 0.25s, box-shadow 0.25s, background 0.25s, transform 0.18s !important;
}
.auth-col-wrap .stTextInput > div > div > input:focus {
    background: rgba(255, 255, 255, 0.85) !important;
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.18) !important;
    transform: translateY(-1px) !important;
    outline: none !important;
}
.auth-col-wrap .stTextInput > div > div > input::placeholder {
    color: rgba(109, 40, 217, 0.35) !important;
}

/* Primary auth button */
.auth-col-wrap .stButton > button {
    background: linear-gradient(135deg, #6a3de8 0%, #a855f7 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 14px 24px !important;
    width: 100% !important;
    margin-top: 10px !important;
    box-shadow: 0 6px 28px rgba(106, 61, 232, 0.45) !important;
    transition: transform 0.2s, box-shadow 0.2s, opacity 0.15s !important;
    animation: dqa-fade-up 0.6s 0.5s both;
}
.auth-col-wrap .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 36px rgba(106, 61, 232, 0.58) !important;
    opacity: 0.94 !important;
}
.auth-col-wrap .stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 3px 12px rgba(106, 61, 232, 0.3) !important;
}

/* Divider line under button */
.auth-divider {
    border: none;
    border-top: 1px solid rgba(167, 139, 250, 0.3);
    margin: 20px 0 16px;
}

/* Footer */
.auth-footer {
    text-align: center;
    animation: dqa-fade-up 0.6s 0.65s both;
    position: relative; z-index: 2;
}
.auth-footer p {
    color: rgba(88, 28, 135, 0.6);
    font-size: 0.85rem;
    margin-bottom: 8px;
}

/* Footer button — rounded pill style matching screenshot */
.auth-footer-col .stButton > button {
    background: linear-gradient(135deg, #6a3de8 0%, #a855f7 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 28px !important;
    box-shadow: 0 4px 16px rgba(106, 61, 232, 0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    width: 100% !important;
}
.auth-footer-col .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(106, 61, 232, 0.5) !important;
}

/* ══ DASHBOARD CSS (untouched) ══ */
.stApp { background: #f5f4ff; }
.metric-row { display: flex; gap: 16px; margin-bottom: 24px; }
.metric-card {
    flex: 1; border-radius: 16px; padding: 22px 24px;
    color: #fff; transition: transform .2s, box-shadow .2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,.15); }
.metric-card .val { font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-card .lbl { font-size: .8rem; opacity: .85; margin-top: 4px; }
.mc-1 { background: linear-gradient(135deg, #6366f1, #818cf8); }
.mc-2 { background: linear-gradient(135deg, #a855f7, #c084fc); }
.mc-3 { background: linear-gradient(135deg, #ec4899, #f472b6); }
.card {
    background: #fff; border: 1px solid #e5e2ff;
    border-radius: 16px; padding: 24px; margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(99,102,241,.06);
}
.card-title {
    font-size: 1rem; font-weight: 600; color: #1e1b4b;
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.issue-item {
    border-left: 3px solid #f472b6; background: #fdf4ff;
    border-radius: 0 10px 10px 0; padding: 12px 16px;
    margin-bottom: 12px; font-size: .88rem; color: #4c1d95;
}
section[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e5e2ff; }
.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 8px 0 20px; }
.sidebar-brand .icon {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    color: #fff; width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700;
}
.sidebar-brand .name { font-weight: 600; color: #1e1b4b; font-size: .95rem; }
.user-pill {
    background: #f5f4ff; border: 1px solid #e5e2ff; border-radius: 30px;
    padding: 6px 14px; font-size: .78rem; color: #6366f1;
    margin-bottom: 16px; word-break: break-all;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 500 !important;
    transition: opacity .2s, transform .2s !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
[data-testid="stDownloadButton"] button { background: linear-gradient(135deg, #10b981, #34d399) !important; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
hr { border-color: #e5e2ff !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers (dashboard only) ──────────────────────────────────────────────────
def metric_cards(rows, cols, issues):
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card mc-1"><div class="val">{rows}</div><div class="lbl">Total Rows</div></div>
      <div class="metric-card mc-2"><div class="val">{cols}</div><div class="lbl">Total Columns</div></div>
      <div class="metric-card mc-3"><div class="val">{issues}</div><div class="lbl">Issues Found</div></div>
    </div>""", unsafe_allow_html=True)

def card_open(icon, title):
    st.markdown(f'<div class="card"><div class="card-title">{icon} {title}</div>', unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in and st.session_state.page == "login":

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 35%, #e9d5ff 65%, #f3e8ff 100%) !important;
        min-height: 100vh;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; display: none !important; }
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
        max-width: 560px !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating orbs
    st.markdown("""
    <div class="dqa-orb dqa-orb-1"></div>
    <div class="dqa-orb dqa-orb-2"></div>
    <div class="dqa-orb dqa-orb-3"></div>
    """, unsafe_allow_html=True)

    # Dots + title + subtitle
    st.markdown("""
    <div class="dqa-dots">
        <div class="dqa-dot"></div>
        <div class="dqa-dot"></div>
        <div class="dqa-dot"></div>
    </div>
    <div class="auth-title">Welcome back</div>
    <div class="auth-sub">Sign in to continue to your workspace</div>
    """, unsafe_allow_html=True)

    # Fields + button
    st.markdown('<div class="auth-col-wrap">', unsafe_allow_html=True)
    email    = st.text_input("Email address", placeholder="hello@example.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
    login_clicked = st.button("Sign in", use_container_width=True, key="login_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-footer">
        <p>New to Data Quality Agent?</p>
    </div>
    """, unsafe_allow_html=True)
    _, fc, _ = st.columns([1, 1, 1])
    with fc:
        st.markdown('<div class="auth-footer-col">', unsafe_allow_html=True)
        signup_clicked = st.button("Create an account", use_container_width=True, key="go_signup")
        st.markdown("</div>", unsafe_allow_html=True)

    # Logic
    if login_clicked:
        if verify_user(email, password):
            for k in ["login_email", "login_password"]:
                st.session_state.pop(k, None)
            st.session_state.logged_in  = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

    if signup_clicked:
        st.session_state.page = "signup"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SIGNUP PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "signup":

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 35%, #e9d5ff 65%, #f3e8ff 100%) !important;
        min-height: 100vh;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; display: none !important; }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 560px !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating orbs
    st.markdown("""
    <div class="dqa-orb dqa-orb-1"></div>
    <div class="dqa-orb dqa-orb-2"></div>
    <div class="dqa-orb dqa-orb-3"></div>
    """, unsafe_allow_html=True)

    # Dots + title + subtitle
    st.markdown("""
    <div class="dqa-dots">
        <div class="dqa-dot"></div>
        <div class="dqa-dot"></div>
        <div class="dqa-dot"></div>
    </div>
    <div class="auth-title">Create an account</div>
    <div class="auth-sub">Start cleaning your data in minutes</div>
    """, unsafe_allow_html=True)

    # Fields + button
    st.markdown('<div class="auth-col-wrap">', unsafe_allow_html=True)
    email    = st.text_input("Email address", placeholder="hello@example.com", key="signup_email")
    password = st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_password")
    confirm  = st.text_input("Confirm password", type="password", placeholder="Confirm your password", key="signup_confirm_password")
    create_clicked = st.button("Get started", use_container_width=True, key="signup_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-footer">
        <p>Already have an account?</p>
    </div>
    """, unsafe_allow_html=True)
    _, fc, _ = st.columns([1, 1, 1])
    with fc:
        st.markdown('<div class="auth-footer-col">', unsafe_allow_html=True)
        back_clicked = st.button("Sign in", use_container_width=True, key="go_login")
        st.markdown("</div>", unsafe_allow_html=True)

    # Logic
    if create_clicked:
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(pattern, email):
            st.error("Invalid email format.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            with st.spinner("Creating account…"):
                import time; time.sleep(3)
            if create_user(email, password):
                st.success("Account created! Please sign in.")
                for k in ["signup_email", "signup_password", "signup_confirm_password"]:
                    st.session_state.pop(k, None)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Email already exists.")

    if back_clicked:
        for k in ["signup_email", "signup_password", "signup_confirm_password"]:
            st.session_state.pop(k, None)
        st.session_state.page = "login"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in:

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
          <div class="icon">✦</div>
          <div class="name">DQ Agent</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            f'<div class="user-pill">📧 {st.session_state.get("user_email","")}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page      = "login"
            st.rerun()

    st.markdown("## ✦ Data Quality Agent")
    st.caption("Upload a CSV, detect issues, and auto-fix your dataset.")
    st.divider()

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")

    if uploaded_file:

        if st.session_state.get("last_file") != uploaded_file.name:
            st.session_state.last_file = uploaded_file.name
            for k in ["upload_id", "validation_saved", "clean_saved"]:
                st.session_state.pop(k, None)

        if "upload_id" not in st.session_state:
            upload_id = save_upload(st.session_state.user_email, uploaded_file.name)
            st.session_state.upload_id = upload_id
            df = pd.read_csv(uploaded_file)
            save_uploaded_csv(upload_id, df.to_csv(index=False))
        else:
            upload_id = st.session_state.upload_id
            df = pd.read_csv(uploaded_file)

        with open("rules/checks.yaml", "r") as f:
            rules = yaml.safe_load(f)
        failures = validate(df, rules)
        
        # Generate root cause analysis
        root_cause_analysis = generate_root_cause_analysis(df, failures)
        
        # Calculate quality scores
        scores = calculate_quality_score(df, failures)
        
        ai_summary = generate_dataset_summary(
            df,
            failures,
            scores
        )

        metric_cards(len(df), len(df.columns), len(failures))

        # Data Quality Score card
        card_open("📈", "Data Quality Score")
        
        st.metric(
            "Overall Quality Score",
            f"{scores['overall']}/100"
        )
        
        st.progress(scores["overall"] / 100)
        
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric(
            "Completeness",
            f"{scores['completeness']}%"
        )
        
        c2.metric(
            "Validity",
            f"{scores['validity']}%"
        )
        
        c3.metric(
            "Uniqueness",
            f"{scores['uniqueness']}%"
        )
        
        c4.metric(
            "Consistency",
            f"{scores['consistency']}%"
        )
        
        card_close()

        # AI Data Quality Summary card
        card_open("🤖", "AI Data Quality Summary")
        st.info(ai_summary)
        card_close()

        # AI Root Cause & Business Impact card
        card_open("🚨", "AI Root Cause & Business Impact")
        st.markdown(root_cause_analysis)
        card_close()

        # Ask AI About Your Dataset card
        card_open("💬", "Ask AI About Your Dataset")
        question = st.text_input(
            "Ask a question",
            placeholder="Which column has the most errors?"
        )
        if st.button(
            "Ask AI",
            key="ask_ai_btn"
        ):
            if question:
                with st.spinner("AI is analyzing dataset..."):
                    answer = ask_dataset_question(
                        df,
                        question
                    )
                    st.markdown(answer)
        card_close()

        # Dataset Preview card
        card_open("📄", "Dataset Preview")
        st.dataframe(df, use_container_width=True)
        card_close()

        # Validation Report card
        card_open("📊", "Validation Report")
        if not failures:
            st.success("✅ No issues found — your dataset looks clean!")
        else:
            st.error(f"❌  {len(failures)} issue(s) detected")
            if "validation_saved" not in st.session_state:
                for f in failures:
                    save_validation(upload_id, f["issue"], generate_fix(f["issue"]))
                st.session_state.validation_saved = True
            for failure in failures:
                st.markdown(
                    f'<div class="issue-item">🔴 <strong>Issue:</strong> {failure["issue"]}</div>',
                    unsafe_allow_html=True,
                )
                with st.expander("View affected rows & AI suggestion"):
                    st.dataframe(failure["rows"], use_container_width=True)
                    st.caption("AI-suggested fix:")
                    st.code(generate_fix(failure["issue"]), language="python")
        card_close()

        # Auto Fix card
        card_open("🛠", "Auto Fix")
        if st.button("Fix Dataset", use_container_width=False):
            fixed_df = auto_fix(df.copy())
            if "clean_saved" not in st.session_state:
                save_cleaned_csv(upload_id, fixed_df.to_csv(index=False))
                save_cleaned_file(upload_id, "clean_data.csv")
                st.session_state.clean_saved = True
            st.success("✅ Dataset fixed successfully!")
            c1, c2 = st.columns(2)
            c1.metric("Records Before", len(df))
            c2.metric("Records After",  len(fixed_df))
            st.dataframe(fixed_df, use_container_width=True)
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=fixed_df.to_csv(index=False),
                file_name="clean_data.csv",
                mime="text/csv",
            )
        card_close()

    st.divider()
    st.markdown("### 📜 Validation History")

    history = get_history(st.session_state.user_email)

    if history:
        for row in history:
            upload_id, upload_time, file_name, original_csv, cleaned_csv = row

            with st.expander(f"📁  {file_name}  ·  {upload_time}"):
                st.caption(f"Upload ID: {upload_id}")

                issues = get_issues(upload_id)

                if issues:
                    st.markdown("**🚨 Issues Detected**")
                    for issue in issues:
                        st.markdown(
                            f'<div class="issue-item">{issue[0]}</div>',
                            unsafe_allow_html=True,
                        )

                if original_csv:
                    st.markdown("**📄 Original Dataset**")
                    st.dataframe(
                        pd.read_csv(StringIO(original_csv)),
                        use_container_width=True
                    )

                if cleaned_csv:
                    st.markdown("**✅ Cleaned Dataset**")
                    st.dataframe(
                        pd.read_csv(StringIO(cleaned_csv)),
                        use_container_width=True
                    )
    else:
        st.info("No validation history yet. Upload a CSV to get started.")