Smart Task Manager

A full-stack web application that helps users manage tasks efficiently with features like task tracking, calendar view, analytics, and reminders.

---

Features

User Authentication

* Secure user registration and login system
* Passwords hashed using Werkzeug security
* Session-based authentication

Task Management

* Add, edit, delete, and mark tasks as complete
* Set due dates and descriptions
* Assign task priority (Low, Medium, High)

Calendar View

* Monthly calendar displaying tasks by date
* Navigate between months
* Tasks color-coded based on priority and status
* Inline actions (complete, edit, delete)

Smart Search

* Search tasks by title
* Auto-suggestions while typing
* Results filtered per logged-in user

Dashboard Overview

* Total tasks
* Completed tasks
* Pending tasks
* Overdue tasks

Task Reminders

* Alerts for overdue tasks
* Highlights tasks due today or within 7 days

Analytics Dashboard

* Task completion statistics
* Monthly productivity chart
* Priority distribution chart
* Tasks due within the next 7 days
  
 UI/UX

* Clean purple & white professional design
* Responsive 3-column layout
* Hover effects and modern cards
* Scrollable calendar panel

---

Tech Stack

**Frontend**

* HTML
* CSS
* JavaScript (Chart.js for analytics)

**Backend**

* Python (Flask)

**Database**

* MySQL

---

Project Structure

```
SmartTaskManager/
│── app.py
│── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── edit.html
│   ├── analytics.html


---

###Installation & Setup

### 1. Clone the Repository

```
git clone https://github.com/your-username/SmartTaskManager.git
cd SmartTaskManager
```

### 2. Install Dependencies

```
pip install flask mysql-connector-python werkzeug
```

### 3. Setup MySQL Database

Create a database:

```sql
CREATE DATABASE smart_task_manager;
```

Create tables:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password TEXT
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50),
    priority VARCHAR(50),
    due_date DATE,
    user_id INT
);
```

### 4. Update Database Credentials

In `app.py`:

```
user="root"
password="your_password"
database="smart_task_manager"
```

---

###5. Run the App

```
python app.py
```

Open in browser:

### ```
http://127.0.0.1:5000
---


Future Improvements

* Drag-and-drop Kanban board
* Email notifications for reminders
* Mobile responsiveness improvements
* Cloud deployment (Render / Railway)
* Dark Mode



Author
Faith Brigid Andeso Chepkemoi

GitHub: https://github.com/faith-automation

Project Status

✔ Fully functional
✔ Portfolio-ready
✔ Actively improving

 Why This Project Matters

This project demonstrates:

* Full-stack web development
* Database design and integration
* User authentication systems
* Real-world application features (calendar, analytics, reminders)
* Clean UI/UX design principles


✨ *Built with passion to solve real productivity challenges.*
