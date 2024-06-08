from flask import Flask, redirect, render_template, request, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create 'users' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    
    # Create 'tasks' table if it doesn't exist
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
    
    # Create 'done' table if it doesn't exist
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

# User Authentication Routes

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = generate_password_hash(data.get('password'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert new user into 'users' table
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({'success': True}), 201
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return jsonify({'success': True}), 200
        
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

# Task Routes

@app.route('/addTask', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    task = request.json.get('task')
    due_date = request.json.get('due_date')
    priority = request.json.get('priority')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks(task, due_date, priority, user_id) VALUES(?, ?, ?, ?)", 
                   (task, due_date, priority, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 201

@app.route('/getTasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    sort_by = request.args.get('sort_by', 'priority')
    filter_by_date = request.args.get('filter_by_date')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [session['user_id']]
    
    if filter_by_date:
        query += " AND due_date <= ?"
        params.append(filter_by_date)
        
    query += f" ORDER BY {sort_by}"
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    
    cursor.execute("SELECT * FROM done WHERE user_id = ?", (session['user_id'],))
    done = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({'tasks': [dict(task) for task in tasks], 'done': [dict(task) for task in done]}), 200

@app.route('/move-to-done/<int:id>/<string:task_name>', methods=['POST'])
def move_to_done(id, task_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO done(task, task_id, user_id) VALUES(?, ?, ?)", (task_name, id, session['user_id']))
    cursor.execute("DELETE FROM tasks WHERE tid = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/move-to-todo/<int:id>/<string:task_name>', methods=['POST'])
def move_to_todo(id, task_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks(task, user_id) VALUES(?, ?)", (task_name, session['user_id']))
    cursor.execute("DELETE FROM done WHERE did = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/deleteTask/<int:id>', methods=['DELETE'])
def deleteTask(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE tid = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/delete-completed/<int:id>', methods=['DELETE'])
def deleteCompletedTask(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM done WHERE did = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/updateTask/<int:id>', methods=['PUT'])
def updateTask(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    updated_task = request.json.get('updated_task')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET task = ? WHERE tid = ? AND user_id = ?", (updated_task, id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/updateTaskOrder', methods=['PUT'])
def updateTaskOrder():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    task_id = request.json.get('task_id')
    new_index = request.json.get('new_index')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET priority = ? WHERE tid = ? AND user_id = ?", (new_index, task_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/checkAuth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

if __name__ == "__main__":
    initialize_db()  # Ensure the database is initialized before running the app
    app.run(debug=True)
