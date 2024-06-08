import sqlite3

def initialize_db():
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        tid INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        due_date DATE,
        priority INTEGER,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS done (
        did INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        task_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY(task_id) REFERENCES tasks(tid),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_db()
