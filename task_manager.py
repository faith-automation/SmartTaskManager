import mysql.connector

# Connect to database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="F@ithDev26", 
    database="smart_task_manager"
)

cursor = connection.cursor()

def add_task():
    title = input("Enter task title: ")
    description = input("Enter task description: ")

    query = "INSERT INTO tasks (title, description) VALUES (%s, %s)"
    cursor.execute(query, (title, description))
    connection.commit()

    print("Task added successfully!\n")


def view_tasks():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    print("\n--- ALL TASKS ---")

    for task in tasks:
        print(f"""
ID: {task[0]}
Title: {task[1]}
Description: {task[2]}
Status: {task[3]}
Created At: {task[4]}
-------------------------
        """)

def mark_completed():
    task_id = input("Enter Task ID to mark as completed: ")

    query = "UPDATE tasks SET status = 'Completed' WHERE id = %s"
    cursor.execute(query, (task_id,))
    connection.commit()

    print("Task marked as completed!\n")

def delete_task():
    task_id = input("Enter Task ID to delete: ")

    query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))
    connection.commit()

    print("Task deleted successfully!\n")
while True:
    print("""
SMART TASK MANAGER
1. Add Task
2. View Tasks
3. Mark Task as Completed
4. Delete Task
5. Exit
    """)

    choice = input("Choose an option: ")

    if choice == "1":
        add_task()
    elif choice == "2":
        view_tasks()
    elif choice == "3":
        mark_completed()
    elif choice == "4":
        delete_task()
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Try again.\n") 