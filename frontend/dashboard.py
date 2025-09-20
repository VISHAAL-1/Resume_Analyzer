import streamlit as st
import requests
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import time

# --- Page Config & Custom CSS ---
st.set_page_config(layout="wide", page_title="Resume Checker", page_icon="📄")

# Define a single dark, vibrant color palette
primary_color = "#FF4B4B"
secondary_color = "#FF8C00"
background_color = "#121212"
text_color = "#FFFFFF"
button_bg = "#333333"

# Custom CSS for styling and animations
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {primary_color};
    }}
    .stButton > button {{
        color: {text_color};
        background-color: {button_bg};
        border-radius: 5px;
        border: 1px solid {primary_color};
        padding: 10px 20px;
        font-weight: normal;
        transition: all 0.3s ease-in-out;
    }}
    .stButton > button:hover {{
        background-color: {primary_color};
        color: {background_color};
        border-color: {secondary_color};
        box-shadow: 0px 0px 10px {primary_color};
    }}
    /* Main container for initial screen to center content */
    .main-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100%;
        animation: fadeIn 1s ease-in-out;
    }}
    /* Fade in animation for transitions */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Constants & State Management ---
API_BASE = "http://localhost:8000"
USER_FILE = Path(__file__).parent / "users.json"

def setup_users():
    if not USER_FILE.exists():
        sample_users = {
            "admin": {"password": "admin123", "role": "admin"},
            "user": {"password": "user123", "role": "user"}
        }
        USER_FILE.write_text(json.dumps(sample_users))
    with open(USER_FILE, "r") as f:
        return json.load(f)

USERS = setup_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.admin_page = "main"
    st.session_state.view_candidate_name = None
    st.session_state.user_page = "main"
    st.session_state.view_evaluation_id = None

def login_form():
    with st.form("login_form"):
        st.subheader("🔐 Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            try:
                resp = requests.post(f"{API_BASE}/login/", data={"username": username, "password": password})
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = data.get("role")
                    with st.spinner("Logging in..."):
                        time.sleep(1)
                    st.success(f"Welcome back, {username}! 👋")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend API. Make sure it's running.")

def signup_form():
    with st.form("signup_form"):
        st.subheader("📝 Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        signup_submitted = st.form_submit_button("Create Account")
        if signup_submitted:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            else:
                try:
                    resp = requests.post(f"{API_BASE}/signup/", data={"username": new_username, "password": new_password})
                    if resp.status_code == 200:
                        st.success("Account created successfully! Please log in.")
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Failed to create account."))
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend API. Make sure it's running.")
                    
def main_login_page():
    st.title("📄 Resume Relevance Checker")
    st.write("---")
    st.header("Make your resume stand out.")
    st.write("Intelligently evaluate your resume against job descriptions using AI to get actionable feedback and improve your chances.")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Login")
        login_form()
    with col2:
        st.header("Sign Up")
        signup_form()

# --- Admin Portal ---
def show_admin_portal():
    if st.session_state.admin_page == "main":
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.title("Admin Dashboard")
        st.write("Welcome, Admin. Please select an action.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View All Submissions"):
                st.session_state.admin_page = "submissions"
                st.rerun()
        with col2:
            if st.button("➕ Create a New Job"):
                st.session_state.admin_page = "create_job"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        with st.sidebar:
            st.button("📊 View All Submissions", on_click=lambda: st.session_state.update(admin_page="submissions", view_candidate_name=None))
            st.button("➕ Create a New Job", on_click=lambda: st.session_state.update(admin_page="create_job"))
            st.button("Logout", on_click=lambda: st.session_state.update(logged_in=False, username="", role="", admin_page="main"))

        if st.session_state.admin_page == "create_job":
            st.header("➕ Create New Job Description")
            with st.form("job_form"):
                title = st.text_input("Job Title")
                must_have = st.text_input("Must-have skills (comma separated)", help="e.g. python, sql, ml")
                good_to_have = st.text_input("Good-to-have skills (comma separated)")
                qualifications = st.text_area("Qualifications / Notes (optional)")
                submitted = st.form_submit_button("Create Job")
                if submitted:
                    params = {"username": st.session_state.username}
                    resp = requests.post(f"{API_BASE}/jobs/", params=params, data={"title": title, "must_have": must_have, "good_to_have": good_to_have, "qualifications": qualifications})
                    if resp.status_code == 200:
                        st.success("Job created: " + str(resp.json()))
                    else:
                        st.error(f"Failed: {resp.status_code} - {resp.text}")

        elif st.session_state.admin_page == "submissions":
            st.header("📊 All Candidate Submissions")
            try:
                params = {"username": st.session_state.username}
                evs = requests.get(f"{API_BASE}/evaluations/", params=params).json()
                if not evs:
                    st.info("No evaluations found.")
                    return
                df = pd.DataFrame(evs)
                candidates = df.groupby('candidate_name')['job_title'].apply(list).reset_index()
                st.subheader("Candidate List")
                for _, row in candidates.iterrows():
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown(f"**{row['candidate_name']}**")
                    with col2:
                        st.button("View Submissions", key=f"view_admin_{row['candidate_name']}", on_click=lambda name=row['candidate_name']: st.session_state.update(admin_page="view_candidate_submissions", view_candidate_name=name))
            except Exception as e:
                st.error(f"Failed to fetch evaluations: {e}")

        elif st.session_state.admin_page == "view_candidate_submissions":
            st.header(f"Submissions for {st.session_state.view_candidate_name}")
            st.button("⬅️ Back to All Candidates", on_click=lambda: st.session_state.update(admin_page="submissions", view_candidate_name=None))
            try:
                params = {"username": st.session_state.username}
                evs = requests.get(f"{API_BASE}/evaluations/", params=params).json()
                candidate_evals = [ev for ev in evs if ev.get('candidate_name') == st.session_state.view_candidate_name]
                if not candidate_evals:
                    st.info("No submissions found for this candidate.")
                    return
                for ev in candidate_evals:
                    with st.container(border=True):
                        st.subheader(f"Job: {ev['job_title']}")
                        st.metric(label="Overall Score", value=f"{ev['score']}%")
                        verdict_color = "red" if ev['verdict'] == "Low" else "orange" if ev['verdict'] == "Medium" else "green"
                        st.markdown(f"**Verdict:** <span style='color:{verdict_color};'>**{ev['verdict']}**</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(f"**LLM Summary:** {ev['summary']}")
                        with st.expander("Show Detailed Feedback"):
                            st.markdown(f"**Missing skills:** {', '.join(ev.get('missing_skills', []))}")
                            st.write("---")
                            st.markdown(f"**Feedback:** {ev['feedback']}")
            except Exception as e:
                st.error(f"Failed to fetch candidate submissions: {e}")

# --- User Portal ---
def show_user_portal():
    if st.session_state.user_page == "main":
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.title("User Dashboard")
        st.write("Welcome, User. Please select an action.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Upload Resume"):
                st.session_state.user_page = "upload"
                st.rerun()
        with col2:
            if st.button("📂 My Submissions"):
                st.session_state.user_page = "my_submissions"
                st.session_state.view_evaluation_id = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        with st.sidebar:
            st.button("📄 Upload Resume", on_click=lambda: st.session_state.update(user_page="upload"))
            st.button("📂 My Submissions", on_click=lambda: st.session_state.update(user_page="my_submissions", view_evaluation_id=None))
            st.button("Logout", on_click=lambda: st.session_state.update(logged_in=False, username="", role="", user_page="main"))
            
        if st.session_state.user_page == "upload":
            st.header("📄 Upload Your Resume")
            try:
                jobs = requests.get(f"{API_BASE}/jobs/").json()
            except Exception:
                jobs = []
            if jobs:
                job_titles = {j['title']: j['id'] for j in jobs}
                selected_job_title = st.selectbox("Select a Job to Apply for", list(job_titles.keys()))
                job_id = job_titles[selected_job_title]
            else:
                st.info("No jobs found. Please contact an admin.")
                return

            with st.form("resume_form"):
                name = st.text_input("Your Name", value=st.session_state.username)
                email = st.text_input("Your Email")
                uploaded_file = st.file_uploader("Upload resume (pdf/docx)", type=["pdf", "docx"])
                submit_resume = st.form_submit_button("Upload & Evaluate")
                if submit_resume:
                    if not uploaded_file:
                        st.error("Please upload a resume file")
                    else:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        data = {"job_id": str(job_id), "name": name or "", "email": email or ""}
                        try:
                            with st.spinner("Analyzing your resume..."):
                                resp = requests.post(f"{API_BASE}/upload_resume/", data=data, files=files, timeout=120)
                                if resp.status_code == 200:
                                    st.success("Evaluation complete!")
                                    st.session_state.user_page = "my_submissions"
                                    st.rerun()
                                else:
                                    st.error(f"Error: {resp.status_code} - {resp.text}")
                        except Exception as e:
                            st.error(f"Request failed: {e}")

        elif st.session_state.user_page == "my_submissions":
            st.header("📂 My Submissions")
            try:
                params = {"username": st.session_state.username} 
                resp = requests.get(f"{API_BASE}/my_evaluations/", params=params)
                if resp.status_code == 200:
                    my_evals = resp.json()
                else:
                    st.error(f"Failed to fetch submissions: {resp.status_code} - {resp.text}")
                    return
                if not my_evals:
                    st.info("You have no submissions yet. Upload a resume to get started!")
                    return
                for ev in my_evals:
                    with st.container(border=True):
                        st.markdown(f"**Job:** {ev['job_title']} - **Score:** {ev['score']}%")
                        verdict_color = "red" if ev['verdict'] == "Low" else "orange" if ev['verdict'] == "Medium" else "green"
                        st.markdown(f"**Verdict:** <span style='color:{verdict_color};'>**{ev['verdict']}**</span>", unsafe_allow_html=True)
                        st.button("View Details", key=f"view_user_{ev['evaluation_id']}", on_click=lambda eval_id=ev['evaluation_id']: st.session_state.update(user_page="view_single_submission", view_evaluation_id=eval_id))
            except Exception as e:
                st.error(f"Failed to fetch submissions: {e}")

        elif st.session_state.user_page == "view_single_submission":
            st.header("Submission Details")
            st.button("⬅️ Back to My Submissions", on_click=lambda: st.session_state.update(user_page="my_submissions", view_evaluation_id=None))
            try:
                params = {"username": st.session_state.username}
                resp = requests.get(f"{API_BASE}/my_evaluations/", params=params)
                if resp.status_code == 200:
                    my_evals = resp.json()
                    selected_eval = next((ev for ev in my_evals if ev.get('evaluation_id') == st.session_state.view_evaluation_id), None)
                else:
                    st.error(f"Failed to fetch submissions: {resp.status_code} - {resp.text}")
                    return
                if not selected_eval:
                    st.error("Submission not found.")
                    return
                st.subheader(f"Job: {selected_eval['job_title']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Overall Score", value=f"{selected_eval['score']}%")
                with col2:
                    verdict_color = "red" if selected_eval['verdict'] == "Low" else "orange" if selected_eval['verdict'] == "Medium" else "green"
                    st.markdown(f"**Verdict:** <span style='color:{verdict_color}; font-size: 24px; font-weight: bold;'>{selected_eval['verdict']}</span>", unsafe_allow_html=True)
                score_fig = go.Figure(go.Indicator(
                    mode="gauge",
                    gauge={'shape': "angular",
                           'bar': {'color': "lightgreen" if selected_eval['score'] > 75 else "orange" if selected_eval['score'] > 50 else "red"},
                           'axis': {'range': [0, 100], 'tickvals': [0, 50, 75, 100]},
                           'steps': [{'range': [0, 50], 'color': "lightpink"},
                                     {'range': [50, 75], 'color': "lightgray"},
                                     {'range': [75, 100], 'color': "lightgreen"}],
                           'threshold': {'line': {'color': 'black', 'width': 4}, 'thickness': 0.75, 'value': selected_eval['score']}},
                    value=selected_eval['score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Your Score"}
                ))
                score_fig.update_layout(height=400)
                st.plotly_chart(score_fig, use_container_width=True)
                st.markdown("---")
                st.subheader("LLM Analysis")
                st.markdown(f"**LLM Summary:** {selected_eval['summary']}")
                st.markdown(f"**Suggestions for Improvement:**")
                st.write(selected_eval['feedback'])
                st.markdown("---")
                st.subheader("Score Breakdown")
                hard_score = selected_eval.get('hard_score', 0.0)
                semantic_score = selected_eval.get('semantic_score', 0.0)
                df_scores = pd.DataFrame({"Metric": ["Hard Match Score", "Semantic Match Score"], "Score": [hard_score, semantic_score]})
                st.bar_chart(df_scores, x="Metric", y="Score", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to fetch submission details: {e}")

# --- Main Logic ---
if not st.session_state.logged_in:
    main_login_page()
else:
    st.sidebar.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
    
    if st.session_state.role == "admin":
        show_admin_portal()
    elif st.session_state.role == "user":
        show_user_portal()
    else:
        st.warning("Invalid role. Please contact support.")