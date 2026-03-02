import pickle
from datetime import datetime, timedelta
from src.preprocessing import clean_text
from src.priority_engine import (
    priority_from_type_and_date,
    USER_PRIORITIES,
    USER_ALERT_WINDOWS,
    set_priority,
    set_alert_window
)
from src.date_extractor import extract_date

# Load model and vectorizer
model = pickle.load(open("models/model.pkl", "rb"))
vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))

def analyze_task(text):
    clean = clean_text(text)
    X = vectorizer.transform([clean])
    task_type = model.predict(X)[0]
    due_date = extract_date(text)
    priority = priority_from_type_and_date(task_type, due_date)

    return {
        "task": text,
        "type": task_type,
        "due_date": due_date,
        "priority": priority
    }

def create_exam_reminder(task):
    if task["type"] != "exam" or not task["due_date"]:
        return None

    reminder_due = task["due_date"] - timedelta(days=3)

    return {
        "task": f"Study for {task['task']}",
        "type": "study-reminder",
        "due_date": reminder_due,
        "priority": priority_from_type_and_date("reading", reminder_due)
    }

def create_quiz_reminder(task):
    if task["type"] != "quiz" or not task["due_date"]:
        return None

    reminder_due = task["due_date"] - timedelta(days=2)

    return {
        "task": f"Study for {task['task']}",
        "type": "quiz-reminder",
        "due_date": reminder_due,
        "priority": priority_from_type_and_date("reading", reminder_due)
    }

def priority_value(priority):
    return {"Low":1, "Medium":2, "High":3, "Critical":4}.get(priority, 1)

def safe_due_date(d):
    return d if d else datetime.max

def check_reminder_status(task):
    if not task["due_date"]:
        return "NO DATE"

    today = datetime.now().date()
    delta = (task["due_date"].date() - today).days

    if delta < 0:
        return "OVERDUE"
    if delta == 0:
        return "DUE TODAY"
    if delta == 1:
        return "DUE TOMORROW"
    if delta <= 3:
        return "COMING UP"
    return "FUTURE"

def run_workflow():
    print("AI Task Workflow (Dates in MM/DD format)")
    print("Enter multiple tasks. Type 'done' when finished.\n")

    tasks = []

    while True:
        text = input("Task: ")
        if text.lower() == "done":
            break
        tasks.append(text)

    print("\nProcessing tasks...\n")

    analyzed = []
    for t in tasks:
        info = analyze_task(t)
        analyzed.append(info)

        exam_r = create_exam_reminder(info)
        if exam_r:
            analyzed.append(exam_r)

        quiz_r = create_quiz_reminder(info)
        if quiz_r:
            analyzed.append(quiz_r)

    analyzed.sort(
        key=lambda x: (
            -priority_value(x["priority"]),
            safe_due_date(x["due_date"])
        )
    )

    print("\n--- SORTED TASK LIST ---\n")
    for item in analyzed:
        status = check_reminder_status(item)
        print(f"Task: {item['task']}")
        print(f"Type: {item['type']}")
        print(f"Due date (MM/DD): {item['due_date'].strftime('%m/%d/%Y') if item['due_date'] else 'None'}")
        print(f"Priority: {item['priority']}")
        print(f"Status: {status}")
        print("-------------------------")

if __name__ == "__main__":
    run_workflow()
