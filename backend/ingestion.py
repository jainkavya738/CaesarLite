import json
import fitz
from langchain_groq import ChatGroq
import sqlite3
from dotenv import load_dotenv
load_dotenv()

def ingestion_agent(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"

    llm = ChatGroq(model="llama-3.3-70b-versatile")

    response = llm.invoke(f"""
        You are a data extraction agent.

        TASK:
        Extract academic topics from the syllabus text below.

        RULES (VERY IMPORTANT):
        - Return ONLY valid JSON
        - Do NOT include explanations
        - Do NOT include markdown
        - Do NOT include backticks
        - Do NOT include any text outside JSON

        FORMAT:
        [
        {{"subject": "...", "topic": "..."}},
        {{"subject": "...", "topic": "..."}}
        ]

        SYLLABUS TEXT:
        {full_text[:4000]}
    """
    )
    
    raw = response.content.strip()

    if not raw:
        raise ValueError("LLM returned empty response")

    try:
        data = json.loads(raw)
    
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        
        if start == -1 or end == -1:
            raise ValueError(f"Invalid JSON from LLM:\n{raw}")
        
        data = json.loads(raw[start:end])

    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()

    for item in data:
        cursor.execute(
            "INSERT INTO Syllabus(subject_name, topic_name) VALUES (?, ?)",
            (item["subject"], item["topic"])
        )

    conn.commit()
    conn.close()

    print("Topics extracted successfully!")