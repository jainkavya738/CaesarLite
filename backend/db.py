import sqlite3

def init_db(db_name="study_planner.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Schedule(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            component_type TEXT NOT NULL
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Syllabus(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            importance_score FLOAT DEFAULT 1.00,
            is_completed BOOLEAN DEFAULT 0
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Planner(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_number INTEGER NOT NULL,
            topic_id INTEGER,
            scheduled_time TEXT,
            status TEXT CHECK(status IN ('Pending', 'Done', 'Backlog')) DEFAULT 'Pending',
            explanation TEXT, 
            FOREIGN KEY (topic_id) REFERENCES Syllabus(id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Feedback(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            decision TEXT CHECK(decision IN ('Approve', 'Modify', 'Reject')),
            student_comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plan_id) REFERENCES Planner(id)
        )
        '''
    )

    conn.commit()
    conn.close()

    print("Database creation succesfull!")

init_db()