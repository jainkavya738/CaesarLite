📚 CAESAR Lite – Agentic AI Academic Study Planner

CAESAR Lite is an Agentic AI-powered academic study planner designed for college students.
It generates a weekly personalized study plan around fixed schedules (classes/labs), provides syllabus-grounded doubt solving (RAG), tracks weekly progress, and adapts future plans using persistent memory (SQLite).

🚀 Key Features

✅ Syllabus PDF Ingestion

Upload syllabus PDF

Extract topics using Groq LLM

Store topics in SQLite (Syllabus table)

✅ Weekly Study Plan Generator (LangGraph Workflow)

Reads timetable input

Extracts free study slots

Plans one topic per free slot

Prioritizes backlog and importance

✅ Human-in-the-Loop (HITL)

Student can Approve / Modify / Reject the generated plan

Feedback influences planning behavior

✅ Tutor Agent (RAG + Self-Correction)

First answers using FAISS + Syllabus embeddings

If not found, falls back to Wikipedia (optional internet)

✅ Persistent Memory with SQLite

Stores plans, statuses, and feedback

Allows history-aware adaptive scheduling

✅ Streamlit Frontend

Easy UI for syllabus upload, planning, and doubt solving

🧠 Tech Stack

Python

Streamlit (Frontend)

LangGraph (Agent workflow)

LangChain + Groq (LLM)

FAISS (Vector Store for RAG)

Sentence Transformers Embeddings (Free local embeddings)

SQLite (Persistent memory)

PyMuPDF / fitz (PDF extraction)

Wikipedia Tool (fallback knowledge)

📁 Project Structure
CAESARLITE/
│
├── backend/
│   ├── __init__.py
│   ├── db.py              # SQLite schema & initialization
│   ├── ingestion.py       # Syllabus extraction + storing topics
│   ├── vectorstore.py     # FAISS vector store creation
│   ├── tutor.py           # RAG tutor agent + Wikipedia fallback
│   ├── planner.py         # Planning nodes + memory logic + HITL nodes
│   └── graph.py           # LangGraph workflow compilation
│
├── app.py                 # Streamlit UI (main entry point)
├── main.ipynb             # Notebook (experiments / dev testing)
├── requirements.txt
├── .env                   # Groq API key (NOT pushed to GitHub)
└── study_planner.db       # SQLite DB (local persistent memory)

⚙️ Setup Instructions (Local Run)
✅ 1) Clone the repository
git clone <your-repo-url>
cd CAESARLITE

✅ 2) Create and activate virtual environment

Windows

python -m venv venv
venv\Scripts\activate


Mac/Linux

python3 -m venv venv
source venv/bin/activate

✅ 3) Install dependencies
pip install -r requirements.txt

✅ 4) Add Groq API key

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here


⚠️ Never upload .env to GitHub.

✅ 5) Run the Streamlit App
streamlit run app.py


It will open in your browser automatically.

🧪 How to Use the App
1️⃣ Upload Syllabus

Go to Upload Syllabus

Upload a PDF syllabus

Click Process Syllabus
✅ Topics are extracted and saved in SQLite
✅ FAISS index is created for Tutor Agent

2️⃣ Generate Weekly Plan

Go to Weekly Planner

Enter timetable

Enter week number

Enter syllabus topics (comma-separated)

Click Generate Plan
✅ You get a weekly plan with reasoning

3️⃣ Ask Tutor Questions

Go to Tutor

Ask a doubt

The agent first searches syllabus context using FAISS

If not in syllabus → it uses Wikipedia fallback (if internet available)

🧠 Agent Workflow (LangGraph)

This project demonstrates:

✅ Sequential workflow:
Memory → Timetable → Planner

✅ Conditional workflow:
If progress is low → Workload reduction plan

✅ HITL (Human-in-the-loop):
Approve / Modify / Reject plan

✅ Persistent Memory:
SQLite stores plan + feedback + backlog

📌 Database Tables Used

Schedule → Fixed academic timetable entries

Syllabus → Subject + topic list (with importance & completion tracking)

Planner → Generated weekly plan + status tracking

Feedback → Student approvals/modifications/rejections

🔐 Environment Variables
Key	Purpose
GROQ_API_KEY	Enables Groq LLM calls via LangChain
⚠️ Common Errors & Fixes
✅ Groq API key error

Error:
GroqError: GROQ_API_KEY not set

✅ Fix: Add this to .env

GROQ_API_KEY=your_key_here

✅ JSON parsing errors during ingestion/planning

LLM output may not always be perfect JSON.
The code includes defensive parsing and structured prompts to improve reliability.

✅ Wikipedia timeout

If Wikipedia is blocked/slow, tutor fallback will automatically handle it and return a safe response.

🌟 Future Improvements (Optional)

Add calendar view for weekly plan

Add progress visualization dashboard (graphs)

Add OpenAlex fallback for academic sources

Add user login + multiple student profiles

Deploy with cloud database (Postgres)

🏁 Final Note

This is not just a chatbot.
CAESAR Lite is a complete agentic system with:

tools

memory

planning

RAG tutor

human supervision

adaptive scheduling

👤 Author

Kavya Jain
First-year CSE student, LNMIIT Jaipur
Project: Mentox Bootcamp GenAI Capstone (CAESAR Lite)