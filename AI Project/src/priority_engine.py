from datetime import datetime

# -----------------------------------------
# USER-DEFINED PRIORITIES (DEFAULTS)
# -----------------------------------------

USER_PRIORITIES = {
    "exam": "High",
    "assignment": "Medium",
    "project": "Medium",
    "reading": "Low",
    "exercise": "Low",
    "quiz": "High"
}

# -----------------------------------------
# USER-DEFINED ALERT WINDOWS (DEFAULTS)
# -----------------------------------------

USER_ALERT_WINDOWS = {
    "exam": 7,
    "assignment": 5,
    "project": 5,
    "reading": 2,
    "exercise": 2,
    "quiz": 3
}

# Priority levels in order
LEVELS = ["Low", "Medium", "High", "Critical"]


# -----------------------------------------
# UPDATE FUNCTIONS (USED BY SETTINGS PAGE)
# -----------------------------------------

def set_priority(task_type, priority):
    """Updates the base priority for a task type."""
    USER_PRIORITIES[task_type] = priority


def set_alert_window(task_type, days):
    """Updates the alert window (days before due date)."""
    USER_ALERT_WINDOWS[task_type] = days


# -----------------------------------------
# PRIORITY CALCULATION LOGIC
# -----------------------------------------

def adjust_by_due_date(base_priority, due_date, task_type):
    """
    Adjusts priority based on how close the due date is.
    - If overdue → Critical
    - If within alert window → +1 level
    - If due tomorrow or today → +2 levels
    """

    if due_date is None:
        return base_priority

    today = datetime.now()
    delta = (due_date - today).days

    # Overdue
    if delta < 0:
        return "Critical"

    idx = LEVELS.index(base_priority)
    alert_days = USER_ALERT_WINDOWS.get(task_type, 3)

    # Inside alert window
    if delta <= alert_days:
        idx += 1

    # Due today or tomorrow
    if delta <= 1:
        idx += 1

    # Cap at Critical
    idx = min(idx, len(LEVELS) - 1)

    return LEVELS[idx]


def priority_from_type_and_date(task_type, due_date):
    """
    Returns the final priority for a task based on:
    - Base priority (user-defined)
    - Due date proximity
    - Alert window
    """
    base = USER_PRIORITIES.get(task_type, "Low")
    final = adjust_by_due_date(base, due_date, task_type)
    return final
