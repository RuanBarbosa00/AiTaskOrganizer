import joblib
from src.preprocessing import clean_text
import os

# Load model and vectorizer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # AI Project/
model = joblib.load(os.path.join(BASE_DIR, "models", "model.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "models", "vectorizer.pkl"))


def classify_task(text: str) -> str:
    """
    Classifies a task description into a task type.
    Returns:
        exam, quiz, assignment, project, reading, exercise, etc.
    """
    clean = clean_text(text)
    X = vectorizer.transform([clean])
    prediction = model.predict(X)[0]
    return prediction
