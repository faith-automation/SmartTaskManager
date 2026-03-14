from asyncio import tasks
from multiprocessing import connection
from re import search

from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import date, datetime
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="F@ithDev26",
        database="smart_task_manager"
    )


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        connection.commit()
        connection.close()

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")

    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -----------------------------
# HOMEPAGE
# -----------------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Search functionality
    search = request.args.get("search")
    if search:
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id=%s AND title LIKE %s",
            (session["user_id"], f"%{search}%")
        )
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (session["user_id"],))
    tasks = cursor.fetchall()

    today = date.today()

    filter_type = request.args.get("filter")

    if filter_type == "completed":
         tasks = [t for t in tasks if t["status"] == "Completed"]

    elif filter_type == "pending":
         tasks = [t for t in tasks if t["status"] == "Pending"]

    elif filter_type == "overdue":
        tasks = [ t for t in tasks if t["status"] == "Pending" and datetime.strptime(str(t["due_date"]), "%Y-%m-%d").date() < today
        ]

    # Ensure correct capitalization from DB
    for task in tasks:
        task["status"] = task["status"].capitalize() if "status" in task else "Pending"
        task["priority"] = task["priority"].capitalize() if "priority" in task else "Low"
        task["due_date"] = task["due_date"]  # Ensure datetime.date or string YYYY-MM-DD

    # Dashboard stats
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["status"] == "Completed"])
    pending_tasks = len([t for t in tasks if t["status"] == "Pending"])
    overdue_tasks = len([
        t for t in tasks
        if t["status"] == "Pending" and datetime.strptime(str(t["due_date"]), "%Y-%m-%d").date() < today
    ])
    
    # TASK REMINDERS
    due_today = []
    due_tomorrow = []

    for t in tasks:
         if t["due_date"]:  # make sure due_date exists
          task_date = datetime.strptime(str(t["due_date"]), "%Y-%m-%d").date()

         if t["status"] == "Pending":
            if task_date == today:
                due_today.append(t)
            elif task_date == today + timedelta(days=1):
                due_tomorrow.append(t)

    # Group tasks by date for calendar
    tasks_by_date = defaultdict(list)
    for t in tasks:
        task_date = datetime.strptime(str(t["due_date"]), "%Y-%m-%d").date()
        tasks_by_date[task_date].append(t)

    # Calendar variables
    current_year = request.args.get("year", default=today.year, type=int)
    current_month = request.args.get("month", default=today.month, type=int)
    first_weekday, num_days = calendar.monthrange(current_year, current_month)

    connection.close()

    return render_template(
        "index.html",
        tasks=tasks,
        tasks_by_date=tasks_by_date,
        today=today,
        current_year=current_year,
        current_month=current_month,
        first_weekday=first_weekday,
        num_days=num_days,
        username=session["username"],
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        search_query=search,
        due_today=due_today,
        due_tomorrow=due_tomorrow,
    )

#-----------------------------
# ANALYTICS ROUTE
#-----------------------------
@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (session["user_id"],))
    tasks = cursor.fetchall()

    # Priority counts
    high_priority = len([t for t in tasks if t["priority"] == "High"])
    medium_priority = len([t for t in tasks if t["priority"] == "Medium"])
    low_priority = len([t for t in tasks if t["priority"] == "Low"])

    # Monthly completed tasks
    monthly_completed = defaultdict(int)

    for t in tasks:
        if t["status"] == "Completed" and t["due_date"]:
            month = t["due_date"].month
            monthly_completed[month] += 1

    months = []
    completed_counts = []

    for i in range(1, 13):
        months.append(calendar.month_abbr[i])
        completed_counts.append(monthly_completed[i])

    # Task status statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["status"] == "Completed"])
    pending_tasks = len([t for t in tasks if t["status"] == "Pending"])
    overdue_tasks = len([
        t for t in tasks
        if t["status"] == "Pending" and t["due_date"] < date.today()
    ])
    from datetime import timedelta
    today = date.today()
    week_end = today + timedelta(days=7)

    due_this_week = len([
          t for t in tasks
          if t["due_date"] and today <= t["due_date"] <= week_end
    ])

    connection.close()

    return render_template(
        "analytics.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,

        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,

        months=months,
        completed_counts=completed_counts,

        due_this_week=due_this_week,

        username=session["username"]
    )
   

# -----------------------------
# FILTER TASKS
# -----------------------------
@app.route("/filter/<status>")
def filter_tasks(status):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT * FROM tasks WHERE status=%s AND user_id=%s",
        (status, session["user_id"])
    )
    tasks = cursor.fetchall()
    connection.close()

    # Group tasks by date
    tasks_by_date = defaultdict(list)
    for task in tasks:
        task_date = datetime.strptime(str(task['due_date']), "%Y-%m-%d").date()
        tasks_by_date[task_date].append(task)

    # Calendar
    today = date.today()
    current_year = request.args.get("year", default=today.year, type=int)
    current_month = request.args.get("month", default=today.month, type=int)
    first_weekday, num_days = calendar.monthrange(current_year, current_month)

    return render_template(
        "index.html",
        tasks=tasks,
        tasks_by_date=tasks_by_date,
        today=today,
        current_year=current_year,
        current_month=current_month,
        first_weekday=first_weekday,
        num_days=num_days,
        username=session["username"],
        filter_status=status
    )


# -----------------------------
# ADD TASK
# -----------------------------
@app.route("/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"]
    priority = request.form["priority"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, description, status, user_id, due_date, priority)
        VALUES (%s, %s, 'Pending', %s, %s, %s)
        """,
        (title, description, session["user_id"], due_date, priority)
    )

    connection.commit()
    connection.close()

    return redirect("/")


# -----------------------------
# COMPLETE TASK
# -----------------------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=%s", (task_id,))
    connection.commit()
    connection.close()

    # Return to previous page (filtered or homepage)
    referrer = request.referrer or "/"
    return redirect(referrer)


# -----------------------------
# DELETE TASK
# -----------------------------
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    connection.commit()
    connection.close()

    referrer = request.referrer or "/"
    return redirect(referrer)


# -----------------------------
# EDIT TASK
# -----------------------------
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE tasks
            SET title=%s, description=%s, due_date=%s, priority=%s, status=%s
            WHERE id=%s AND user_id=%s
        """, (title, description, due_date, priority, status, task_id, session["user_id"]))

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM tasks WHERE id=%s AND user_id=%s",
        (task_id, session["user_id"])
    )

    task = cursor.fetchone()
    connection.close()

    return render_template("edit.html", task=task)


if __name__ == "__main__":
    app.run(debug=True)