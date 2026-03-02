import easyocr
from src.predict import classify_task
from src.date_extractor import extract_date

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(path):
    results = reader.readtext(path, detail=0)
    return results

def merge_into_lines(words):
    lines = []
    buffer = []

    for w in words:
        if not isinstance(w, str):
            continue

        w = w.strip()
        if not w:
            continue

        if any(w.startswith(m) for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
            if buffer:
                lines.append(" ".join(buffer))
                buffer = []
            buffer.append(w)
        else:
            buffer.append(w)

    if buffer:
        lines.append(" ".join(buffer))

    return lines

def looks_like_task(line):
    keywords = [
        "exam", "quiz", "test",
        "assignment", "project", "paper", "essay",
        "reading", "read", "chapter",
        "exercise", "problem", "homework",
        "presentation", "report", "meeting"
    ]
    line_low = line.lower()
    return any(k in line_low for k in keywords)

def extract_tasks_from_image(path):
    raw_words = extract_text_from_image(path)
    lines = merge_into_lines(raw_words)

    tasks = []

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        if not looks_like_task(clean):
            continue

        due_dt = extract_date(clean)
        due_str = due_dt.strftime("%Y-%m-%d") if due_dt else ""

        task_type = classify_task(clean)

        tasks.append({
            "name": clean,
            "type": task_type,
            "due": due_str
        })

    return tasks
