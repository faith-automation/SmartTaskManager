from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import date

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

        # check if passwords match
        if password != confirm_password:
          return "Passwords do not match"

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))

        connection.commit()
        connection.close()

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(query,(username,))
        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]   # IMPORTANT LINE

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

from datetime import datetime, date
import calendar
from collections import defaultdict
from flask import request

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    today = date.today()

    if not month:
        month = today.month
    if not year:
        year = today.year

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE user_id=%s"
    cursor.execute(query, (session["user_id"],))
    tasks = cursor.fetchall()

    connection.close()

    tasks_by_date = defaultdict(list)

    for task in tasks:

        if isinstance(task["due_date"], str):
            task["due_date"] = datetime.strptime(task["due_date"], "%Y-%m-%d").date()

        # only tasks for selected month
        if task["due_date"].month == month and task["due_date"].year == year:
            tasks_by_date[task["due_date"]].append(task)

    first_weekday, num_days = calendar.monthrange(year, month)
    first_weekday = (first_weekday + 1) % 7

    return render_template(
        "index.html",
        tasks=tasks,
        today=today,
        username=session["username"],
        tasks_by_date=tasks_by_date,
        current_year=year,
        current_month=month,
        num_days=num_days,
        first_weekday=first_weekday,
        filter_status=None
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

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO tasks (title, description, status, user_id, due_date)
    VALUES (%s, %s, 'Pending', %s, %s)
    """

    cursor.execute(query, (title, description, session["user_id"], due_date))

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
    cursor = connection.cursor()

    query = "UPDATE tasks SET status = 'Completed' WHERE id = %s"
    cursor.execute(query, (task_id,))

    connection.commit()
    connection.close()

    return redirect("/")


# -----------------------------
# DELETE TASK
# -----------------------------
@app.route("/delete/<int:task_id>")
def delete_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))

    connection.commit()
    connection.close()

    return redirect("/")


# -----------------------------
# EDIT TASK
# -----------------------------
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]

        query = """
        UPDATE tasks
        SET title=%s, description=%s, due_date=%s
        WHERE id=%s
        """

        cursor.execute(query, (title, description, due_date, task_id))

        connection.commit()
        connection.close()

        return redirect("/")

    # GET request (load task for editing)
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()

    connection.close()

    return render_template("edit.html", task=task)

from datetime import datetime, date
import calendar
from collections import defaultdict
from flask import request

@app.route("/filter/<status>")
def filter_tasks(status):

    if "user_id" not in session:
        return redirect("/login")

    # Get month/year from query parameters (for next/prev navigation)
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    today = date.today()
    if not month:
        month = today.month
    if not year:
        year = today.year

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE status = %s AND user_id = %s"
    cursor.execute(query, (status, session["user_id"]))
    tasks = cursor.fetchall()
    connection.close()

    # Convert due_date string to date object and group tasks by date
    tasks_by_date = defaultdict(list)
    for task in tasks:
        if isinstance(task["due_date"], str):
            task["due_date"] = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        tasks_by_date[task["due_date"]].append(task)

    # Calendar calculations
    first_weekday, num_days = calendar.monthrange(year, month)
    first_weekday = (first_weekday + 1) % 7  # Sunday=0

    return render_template(
        "index.html",
        tasks=tasks,
        today=today,
        username=session["username"],
        tasks_by_date=tasks_by_date,
        current_year=year,
        current_month=month,
        num_days=num_days,
        first_weekday=first_weekday,
        filter_status=status  # pass current filter to template
    )


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)