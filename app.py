import streamlit as st
import json
import os

st.set_page_config(page_title="Learning Assistant", page_icon="📘")
st.title("📚 Your Daily Topic")

# --- Load topics ---
def load_all_topics(include_generated=True):
    base = {}
    if os.path.exists("topics.json"):
        with open("topics.json", "r", encoding="utf-8") as f:
            base = json.load(f)
    else:
        st.error("⚠️ 'topics.json' not found. Please upload it to your app directory.")
        st.stop()

    if include_generated and os.path.exists("new_topics.json"):
        with open("new_topics.json", "r", encoding="utf-8") as f:
            generated = json.load(f)
        base.update(generated)

    return base

# --- User Login ---
st.sidebar.markdown("### 👤 User Login")
username = st.sidebar.text_input("Enter your name", value="guest").strip().lower()

if not username:
    st.warning("Please enter a valid username.")
    st.stop()

st.sidebar.success(f"Logged in as: {username.capitalize()}")

# --- Load topics ---
include_generated = st.sidebar.checkbox("🧠 Include AI-Generated Topics", value=True)
topics = load_all_topics(include_generated=include_generated)

topic_keys = list(topics.keys())

# --- Load user-specific progress ---
progress_file = f"progress_{username}.json"
if not os.path.exists(progress_file):
    with open(progress_file, "w") as f:
        json.dump({"last_index": -1, "completed": []}, f)

with open(progress_file, "r") as f:
    progress = json.load(f)

# --- Sidebar for Mode Selection ---
mode = st.sidebar.radio("Select Mode", ["🧠 Daily Learning", "📚 Review Completed Topics", "📈 Progress Dashboard"])

# --- Review Mode ---
if mode == "📚 Review Completed Topics":
    st.title("📚 Review Mode")

    if not progress.get("completed"):
        st.info("You haven't completed any topics yet.")
        st.stop()

    review_topic = st.selectbox("Choose a topic to review:", progress["completed"])
    topic = topics[review_topic]

    st.subheader(f"{topic['title']} ({topic['track']})")
    st.markdown("### 📟 Summary")
    st.markdown(topic["summary"])

    st.markdown("---")
    st.markdown("### 🧪 Retake Quiz")

    score = 0
    for i, q in enumerate(topic["quiz"], 1):
        answer = st.radio(
            f"{i}. {q['question']}",
            q["options"],
            key=f"review_{username}_{i}",
            index=None
        )

        if answer:
            if answer == q["answer"]:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")

    st.markdown(f"🎯 **Your Score: {score} / {len(topic['quiz'])}**")
    st.stop()

# --- Daily Learning Mode ---
if mode == "🧠 Daily Learning":
    current_index = progress.get("last_index", -1) + 1

    if current_index >= len(topic_keys):
        st.title("🎉 You've completed all topics!")
        st.markdown("Switch to **Review Mode** in the sidebar.")
        st.stop()

    topic_key = topic_keys[current_index]
    topic = topics[topic_key]

    st.subheader(f"{topic['title']} ({topic['track']})")
    st.markdown("### 📟 Summary")
    st.markdown(topic["summary"])

    st.markdown("---")
    st.markdown("### 🧪 Quiz Time")

    score = 0
    for i, q in enumerate(topic["quiz"], 1):
        answer_key = f"daily_{username}_{topic_key}_{i}"

        user_answer = st.session_state.get(answer_key, None)
        if user_answer is None:
            user_answer = st.radio(
                f"{i}. {q['question']}",
                q["options"],
                key=answer_key,
                index=None
            )
        else:
            st.radio(
                f"{i}. {q['question']}",
                q["options"],
                index=q["options"].index(user_answer) if user_answer in q["options"] else 0,
                key=answer_key,
                disabled=True
            )

        if user_answer and user_answer != "":
            if user_answer == q["answer"]:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")

    st.markdown(f"🎯 **Your Score: {score} / {len(topic['quiz'])}**")

    if st.button("✅ Mark as complete and move to next topic"):
        progress["last_index"] = current_index
        if topic_key not in progress.get("completed", []):
            progress["completed"].append(topic_key)
        with open(progress_file, "w") as f:
            json.dump(progress, f, indent=2)
        st.rerun()

# --- Progress Dashboard ---
if mode == "📈 Progress Dashboard":
    st.title("📈 Your Progress Dashboard")

    completed_keys = progress.get("completed", [])
    total_topics = len(topics)
    completed_count = len(completed_keys)
    percent_complete = round((completed_count / total_topics) * 100) if total_topics > 0 else 0
    estimated_minutes = completed_count * 15

    st.markdown(f"✅ **Topics Completed:** {completed_count} / {total_topics} ({percent_complete}%)")
    st.markdown(f"⏱️ **Estimated Time Spent:** {estimated_minutes} minutes")

    # --- Track-wise breakdown ---
    st.markdown("### 📊 Track-wise Breakdown")
    track_stats = {}
    for key in completed_keys:
        track = topics[key]["track"]
        track_stats[track] = track_stats.get(track, 0) + 1

    for track, count in track_stats.items():
        st.markdown(f"- **{track}**: {count} topics completed")

    # --- Score Summary ---
    st.markdown("### 🧠 Score Summary")
    total_score = 0
    total_possible = 0

    for key in completed_keys:
        for q in topics[key]["quiz"]:
            total_possible += 1
            # Assume they got all right for now unless storing per-question accuracy
            total_score += 1

    avg_score_pct = round((total_score / total_possible) * 100) if total_possible > 0 else 0
    st.markdown(f"📘 **Estimated Quiz Accuracy:** {avg_score_pct}% (based on completion only)")

    st.stop()
