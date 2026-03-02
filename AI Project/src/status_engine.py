from datetime import datetime

def calculate_status(due_date):
    """
    Returns the status of a task based on its due date.

    Possible outputs:
        - OVERDUE
        - DUE TODAY
        - DUE TOMORROW
        - COMING UP
        - FUTURE
        - NO DATE
    """

    if due_date is None or due_date == "":
        return "NO DATE"

    today = datetime.now().date()

    # Convert to date if datetime
    if hasattr(due_date, "date"):
        due_date = due_date.date()

    delta = (due_date - today).days

    if delta < 0:
        return "OVERDUE"
    elif delta == 0:
        return "DUE TODAY"
    elif delta == 1:
        return "DUE TOMORROW"
    elif delta <= 7:
        return "COMING UP"
    else:
        return "FUTURE"
