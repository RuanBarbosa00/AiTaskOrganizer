import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from preprocessing import clean_text

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_dataset(path="data/data.csv"):
    """
    Loads the dataset.
    Expected columns:
        - text
        - label
    """
    df = pd.read_csv(path)

    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain 'text' and 'label' columns.")

    return df


# ---------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------

def train_model():
    print("Loading dataset...")
    df = load_dataset()

    print("Cleaning text...")
    df["clean"] = df["text"].apply(clean_text)

    print("Vectorizing...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["clean"])
    y = df["label"]

    print("Training model...")
    model = LogisticRegression(max_iter=500)
    model.fit(X, y)

    print("Saving model and vectorizer...")
    joblib.dump(model, "models/model.pkl")
    joblib.dump(vectorizer, "models/vectorizer.pkl")

    print("Training complete!")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    train_model()
