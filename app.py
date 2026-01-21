import streamlit as st
import tempfile
import json
import fitz

from backend.db import init_db
from backend.ingestion import ingestion_agent
from backend.vectorstore import create_vector
from backend.tutor import tutor_agent
from backend.graph import caesar

st.set_page_config(
    page_title="CAESAR Lite – AI Study Planner",
    layout="wide"
)

st.title("📚 CAESAR Lite – Agentic AI Academic Study Planner")

init_db()

page = st.sidebar.radio(
    "Navigate",
    ["Upload Syllabus", "Weekly Planner", "Tutor"]
)

if page == "Upload Syllabus":
    st.header("📄 Upload Syllabus PDF")

    pdf = st.file_uploader("Upload syllabus PDF", type=["pdf"])

    if pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf.read())
            pdf_path = tmp.name

        if st.button("Process Syllabus"):
            with st.spinner("Extracting topics & building knowledge base..."):
                ingestion_agent(pdf_path)

                doc = fitz.open(pdf_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text("text") + "\n"

                create_vector(full_text)

            st.success("✅ Syllabus processed successfully!")

elif page == "Weekly Planner":
    st.header("🗓 Weekly Study Planner")

    timetable = st.text_area(
        "Enter your weekly timetable",
        height=150
    )

    week_number = st.number_input("Week Number", min_value=1, value=1)

    syllabus_topics = st.text_input(
        "Syllabus Topics (comma separated)",
        "Data Structures, Recursion, Sorting Algorithms"
    )

    if st.button("Generate Plan"):
        inputs = {
            "timetable": timetable,
            "week_number": week_number,
            "syllabus_topics": syllabus_topics.split(",")
        }

        thread = {"configurable": {"thread_id": f"week-{week_number}"}}

        with st.spinner("Generating adaptive study plan..."):
            events = list(caesar.stream(inputs, thread))
            final_event = events[-1]

            plan_json = final_event["planner_node"]["current_plan"]
            st.session_state["plan"] = plan_json
    
    raw = ""
    if "plan" in st.session_state:
        st.subheader("📋 Generated Plan")
        raw = st.session_state["plan"].strip()

    if not raw:
        st.error("Planner returned empty response")
        st.stop()

    try:
        plan = json.loads(raw)
    
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1

        if start == -1 or end == -1:
            st.error("Planner output is not valid JSON")
            st.code(raw)
            st.stop()
        
        plan = json.loads(raw[start:end])

    if not isinstance(plan, list):
        st.error("Planner JSON must be a list")
        st.stop()

    for item in plan:
        st.markdown(
                f"""
                **{item['day']} – {item['time']}**  
                📘 Topic: `{item['topic']}`  
                🧠 Reason: _{item['reasoning']}_
                """
            )

    decision = st.radio(
            "Your decision",
            ["Approve", "Modify", "Reject"]
        )

    comments = st.text_area("Comments (optional)")

    if st.button("Submit Review"):
        st.success(f"Plan {decision}ed successfully!")
        st.write("Feedback will affect future plans.")

elif page == "Tutor":
    st.header("🤖 Tutor Agent (Syllabus + Wikipedia RAG)")

    query = st.text_input("Ask your doubt")

    if st.button("Ask Tutor"):
        with st.spinner("Thinking..."):
            answer = tutor_agent(query)

        st.subheader("Answer")
        st.write(answer)
