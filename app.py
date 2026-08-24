"""
RiSk UnSolvd Credit Risk Training App
Streamlit application with 5 topic modules.
Flow: Select module → Watch / mark videos complete → Unlock Semi-Pro / Pro / Legend stages
Each stage: 10 randomly sampled questions. Difficulty increases substantially across stages.
Pass threshold: 7/10 to unlock next stage.
Logo integrated.
"""

import streamlit as st
import random
from pathlib import Path

# -----------------------------------------------------------------------------
# Load resources
# -----------------------------------------------------------------------------
RESOURCES_PATH = Path(__file__).parent / "resources.txt"

def load_resources():
    raw = RESOURCES_PATH.read_text(encoding="utf-8")
    namespace = {}
    exec(raw, namespace)
    return namespace["MODULES"], namespace["QUESTIONS"]

MODULES, QUESTIONS = load_resources()

# -----------------------------------------------------------------------------
# Session state initialisation
# -----------------------------------------------------------------------------
def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_module" not in st.session_state:
        st.session_state.selected_module = None
    if "video_completed" not in st.session_state:
        st.session_state.video_completed = {}
    if "stage_unlocked" not in st.session_state:
        st.session_state.stage_unlocked = {}
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = None
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "stage_passed" not in st.session_state:
        st.session_state.stage_passed = {}

init_state()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
STAGES = ["Semi-Pro", "Pro", "Legend"]
PASS_THRESHOLD = 7

def get_module_by_id(mid):
    for m in MODULES:
        if m["id"] == mid:
            return m
    return None

def ensure_module_state(mid):
    if mid not in st.session_state.video_completed:
        st.session_state.video_completed[mid] = False
    if mid not in st.session_state.stage_unlocked:
        st.session_state.stage_unlocked[mid] = {
            "Semi-Pro": False,
            "Pro": False,
            "Legend": False
        }
    if mid not in st.session_state.stage_passed:
        st.session_state.stage_passed[mid] = {
            "Semi-Pro": False,
            "Pro": False,
            "Legend": False
        }

def start_quiz(mid, stage):
    bank = QUESTIONS.get(mid, {}).get(stage, [])
    if len(bank) < 10:
        st.error(f"Insufficient questions for {stage} in this module. Found {len(bank)}.")
        return
    selected = random.sample(bank, 10)
    st.session_state.quiz_questions = selected
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.score = 0
    st.session_state.current_stage = stage
    st.session_state.page = "quiz"

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
def page_home():
    st.title("RiSk UnSolvd — Credit Risk Training App")
    st.markdown("""
    This application supports structured self-study of credit-risk topics aligned with the  
    **RiSk UnSolvd** public curriculum. It is designed for postgraduate students and practitioners  
    in public administration, economics, and quantitative social science.

    **Learning pathway for each module**
    1. Review the recommended video lectures (external YouTube links).
    2. Confirm completion of video training.
    3. Progress through three successive expertise stages:  
       **Semi-Pro → Pro → Legend**.  
       Conceptual difficulty and required reasoning depth increase substantially at each stage.
    4. Each stage presents **10 questions drawn at random** from a verified item bank.  
       Pass threshold: **7 out of 10**. Successful completion unlocks the next stage.
    """)
    st.divider()
    st.subheader("Select a Module")
    for m in MODULES:
        with st.container():
            st.markdown(f"### {m['id']}. {m['name']}")
            st.caption(m["description"])
            if st.button(f"Enter Module {m['id']}", key=f"enter_{m['id']}"):
                st.session_state.selected_module = m["id"]
                ensure_module_state(m["id"])
                st.session_state.page = "module"
                st.rerun()
            st.divider()

def page_module():
    mid = st.session_state.selected_module
    m = get_module_by_id(mid)
    ensure_module_state(mid)

    if st.session_state.stage_passed[mid]["Semi-Pro"]:
        st.session_state.stage_unlocked[mid]["Pro"] = True
    if st.session_state.stage_passed[mid]["Pro"]:
        st.session_state.stage_unlocked[mid]["Legend"] = True

    st.title(f"Module {mid}: {m['name']}")
    st.markdown(m["description"])

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.subheader("1. Video Training")
    st.markdown(
        "Review the recommended lectures (links open externally). "
        "After completing the viewing, confirm below to unlock the first assessment stage."
    )

    for i, v in enumerate(m["videos"], 1):
        st.markdown(f"{i}. [{v['title']}]({v['url']})")

    completed = st.session_state.video_completed[mid]
    if not completed:
        if st.checkbox("I confirm that I have completed the video training for this module", key=f"vid_{mid}"):
            st.session_state.video_completed[mid] = True
            st.session_state.stage_unlocked[mid]["Semi-Pro"] = True
            st.success("Video training recorded as complete. Semi-Pro stage is now unlocked.")
            st.rerun()
    else:
        st.success("Video training completed.")

    st.subheader("2. Expertise Stages")
    st.markdown(
        "Each stage draws 10 questions at random from a verified item bank. "
        "Conceptual demand and required analytical depth increase markedly from Semi-Pro to Legend. "
        "A score of 7/10 or higher is required to unlock the subsequent stage."
    )

    for stage in STAGES:
        unlocked = st.session_state.stage_unlocked[mid][stage]
        passed = st.session_state.stage_passed[mid][stage]
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if passed:
                status = "Passed"
            elif unlocked:
                status = "Unlocked — ready to attempt"
            else:
                status = "Locked"
            st.markdown(f"**{stage}** — {status}")
        with col2:
            if unlocked and not passed:
                if st.button(f"Start {stage}", key=f"start_{mid}_{stage}"):
                    start_quiz(mid, stage)
                    st.rerun()
        with col3:
            if passed:
                st.markdown("✓")

def page_quiz():
    mid = st.session_state.selected_module
    stage = st.session_state.current_stage
    m = get_module_by_id(mid)
    questions = st.session_state.quiz_questions

    st.title(f"{m['name']} — {stage} Assessment")
    st.caption(
        "Ten questions drawn at random from the verified item bank for this stage. "
        "Select one option for each question. Pass threshold: 7/10."
    )

    if not st.session_state.quiz_submitted:
        with st.form("quiz_form"):
            for idx, q in enumerate(questions):
                st.markdown(f"**Question {idx+1}**")
                st.markdown(q["q"])
                choice = st.radio(
                    "Select the most accurate answer:",
                    options=list(range(len(q["options"]))),
                    format_func=lambda i, opts=q["options"]: opts[i],
                    key=f"q_{idx}",
                    index=None
                )
                if choice is not None:
                    st.session_state.quiz_answers[idx] = choice
                st.divider()

            submitted = st.form_submit_button("Submit answers")
            if submitted:
                score = 0
                for idx, q in enumerate(questions):
                    if st.session_state.quiz_answers.get(idx) == q["answer"]:
                        score += 1
                st.session_state.score = score
                st.session_state.quiz_submitted = True
                if score >= PASS_THRESHOLD:
                    st.session_state.stage_passed[mid][stage] = True
                    if stage == "Semi-Pro":
                        st.session_state.stage_unlocked[mid]["Pro"] = True
                    elif stage == "Pro":
                        st.session_state.stage_unlocked[mid]["Legend"] = True
                st.rerun()
    else:
        score = st.session_state.score
        st.subheader(f"Result: {score} / 10")
        if score >= PASS_THRESHOLD:
            st.success(
                f"Stage passed. "
                + ("The next stage is now unlocked." if stage != "Legend" else "Module stage sequence completed.")
            )
        else:
            st.warning(
                f"Score below the required threshold of {PASS_THRESHOLD}/10. "
                "You may retry the stage; a new random draw will be presented."
            )

        st.subheader("Detailed review")
        for idx, q in enumerate(questions):
            user_ans = st.session_state.quiz_answers.get(idx)
            correct = q["answer"]
            is_correct = user_ans == correct
            st.markdown(f"**Question {idx+1}**")
            st.markdown(q["q"])
            user_text = q["options"][user_ans] if user_ans is not None else "No answer selected"
            st.markdown(f"- Your selection: {user_text}")
            st.markdown(f"- Correct answer: {q['options'][correct]}")
            if is_correct:
                st.markdown("Result: Correct")
            else:
                st.markdown("Result: Incorrect")
            st.caption(f"Explanation: {q.get('explanation', 'No explanation recorded.')}")
            st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Return to module overview"):
                st.session_state.page = "module"
                st.session_state.quiz_submitted = False
                st.rerun()
        with col2:
            if score < PASS_THRESHOLD:
                if st.button("Retry this stage (new random draw)"):
                    start_quiz(mid, stage)
                    st.rerun()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="RiSk UnSolvd Training",
        page_icon="📊",
        layout="wide"
    )

    # ---------- LOGO ----------
    logo_path = Path(__file__).parent / "logo.jpg"
    if logo_path.exists():
        st.logo(str(logo_path), size="large")
    else:
        # Fallback text if logo file is missing
        st.sidebar.markdown("### RiSk UnSolvd")

    st.sidebar.title("RiSk UnSolvd")
    st.sidebar.markdown("Credit Risk Training App")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Pathway**  \n"
        "Module selection → Video training →  \n"
        "Semi-Pro → Pro → Legend"
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "All assessment items are drawn from verified regulatory and industry sources "
        "(IFRS 9, Basel IRB, Federal Reserve CCAR guidance, standard scorecard methodology). "
        "No unverified claims are included."
    )

    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "module":
        page_module()
    elif st.session_state.page == "quiz":
        page_quiz()
    else:
        page_home()

if __name__ == "__main__":
    main()