from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks ORDER BY due_date ASC")
    tasks = c.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)",
                  (title, description, due_date))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_task.html')

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

import os

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import schedule
import time
import threading

def check_due_tasks():
    today = datetime.now().date()
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT title, due_date FROM tasks WHERE status='Pending'")
    tasks = c.fetchall()
    for task in tasks:
        title, due_date_str = task
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date == today:
                print(f"🔔 Reminder: '{title}' is due today!")
    conn.close()

def start_scheduler():
    schedule.every(60).seconds.do(check_due_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the scheduler in a background thread
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()
