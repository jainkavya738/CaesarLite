from typing import TypedDict, List, Annotated
from langchain_groq import ChatGroq
import operator
from dotenv import load_dotenv
load_dotenv()

class PlannerState(TypedDict):
    timetable: str
    syllabus_topics: List[dict]
    free_slots: List[str]
    history_context: str
    current_plan: List[dict]
    week_number: int

def timetable_node(state: PlannerState):
    raw_timetable = state['timetable']

    llm = ChatGroq(model="llama-3.3-70b-versatile")

    prompt = f"Analyse this fixed timetable: {raw_timetable}. Extract ALL free time slots excluding class/lab timings. Return structured JSON."
    response = llm.invoke(prompt)

    return {"free_slots": response.content}

import sqlite3

def memory_node(state: PlannerState):
    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()

    current_week = state.get("week_number", 1)
    prev_week = current_week - 1

    if prev_week <= 0:
        performance = 100
        backlog_topics = []
    else:
        cursor.execute("""
            SELECT S.topic_name
            FROM Planner P
            JOIN Syllabus S ON P.topic_id = S.id
            WHERE P.week_number=? AND P.status!='Done'
        """, (prev_week,))
        backlog_topics = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT COUNT(*) FROM Planner WHERE week_number=?", 
            (prev_week,)
        )
        total_row = cursor.fetchone()
        total = total_row[0] if total_row else 0

        cursor.execute(
            "SELECT COUNT(*) FROM Planner WHERE week_number=? AND status='Done'", 
            (prev_week,)
        )
        done_row = cursor.fetchone()
        done = done_row[0] if done_row else 0

        performance = int((done / total) * 100) if total > 0 else 100

    conn.close()

    history_msg = f"""
    Last week performance: {performance}%.
    Backlogs: {', '.join(backlog_topics) if backlog_topics else 'None'}.
    Adjust difficulty and workload accordingly.
    """

    return {"history_context": history_msg}

def planner_node(state: PlannerState):
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    prompt = f"""
        You are an academic planning agent.

        TASK:
        Generate a weekly study plan.

        RULES (VERY IMPORTANT):
        - Return ONLY valid JSON
        - Do NOT include explanations outside JSON
        - Do NOT include markdown
        - Do NOT include backticks
        - Do NOT include extra text

        CONTEXT:
        Syllabus Topics: {state['syllabus_topics']}
        Free Slots: {state['free_slots']}
        History Context: {state['history_context']}

        FORMAT:
        [
        {{
            "day": "Monday",
            "time": "10:00 - 11:00",
            "topic": "Recursion",
            "reasoning": "Backlog topic scheduled in free slot"
        }}
        ]
    """

    response = llm.invoke(prompt)
    return {"current_plan": response.content}


import json

def save_plan_to_db(plan_json, week):
    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()

    for entry in json.loads(plan_json):
        cursor.execute("""
                INSERT INTO Planner (week_number, scheduled_time, explanation)
                VALUES (?, ?, ?)
            """, (week, f"{entry['day']} {entry['time']}", entry['reasoning']))

    conn.commit()
    conn.close()

def calculate_weekly_progress(week_num):
    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Planner WHERE week_number=?", (week_num,))
    total_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Planner WHERE week_number=? AND status='Done'", (week_num,))
    completed_tasks = cursor.fetchone()[0]

    conn.close()

    if total_tasks == 0: return 100

    progress_percentage = (completed_tasks / total_tasks) * 100
    print(f"Weekly Progress: {progress_percentage:.2f}%")

    return progress_percentage

def finalize_plan_to_db(state: PlannerState):
    """
    Saves the final accepted plan into SQLite for persistent memory.
    """

    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()
    week = state['week_number']

    plan_data = json.loads(state['current_plan'])

    for entry in plan_data:
        cursor.execute("""
            INSERT INTO Planner (week_number, scheduled_time, explanation, status) 
            VALUES (?, ?, ?, 'Pending')
        """, (week, f"{entry['day']} {entry['time']}", entry['reasoning']))

    conn.commit()
    conn.close()

    print("Finalized plan saved to SQLite.")


def feedback_agent_checkoff(week_num):
    """
    Allows the student to manually mark tasks as completed in the .ipynb.
    """

    conn = sqlite3.connect("study_planner.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, topic_id, scheduled_time FROM Planner WHERE week_number=?", (week_num,))
    tasks = cursor.fetchall()

    print(f"--- Week {week_num} Progress Tracking ---")
    for task in tasks:
        status = input(f"Task: {task[2]} (ID: {task[0]}). Did you complete it? (y/n): ")
        new_status = 'Done' if status.lower() == 'y' else 'Backlog'

        cursor.execute("UPDATE Planner SET status=? WHERE id=?", (new_status, task[0]))

    conn.commit()
    conn.close()

    print("Progress updated in persistent memory.")

from langgraph.types import interrupt

def human_review(state: PlannerState):
    """
    Pauses execution and waits for human input (Approve, Modify, Reject).
    """

    review_input = interrupt({
        'question': "Please review the generated study plan",
        'plan': state['current_plan']
    })

    return {
        'user_decision': review_input['decision'],
        'student_comments': review_input.get("comments", "")  ###
    }

def workload_reduction_node(state: PlannerState):
    """
    Automatically simplifies the next week's plan if progress was low.
    """

    return{
        "history_context": state['history_context'] + "\nPriority: Reduce hours by 20% to avoid burnout. Lessen the overburdening!"
    }

def route_after_review(state: PlannerState):
    """
    Determines if we finish, re-plan, or reduce workload.
    """

    decision = state.get('user_decision')
    progress_score = state.get("weekly_progress_score",100)

    if progress_score < 50:
        return 'workload_reduction_node'
    if decision == "Reject" or decision == "Modify":
        return 'replan'

    return "finalize"