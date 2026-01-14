import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import os

# Configuration
DATA_PATH = r'd:\project ai\data\emotions_combined.csv'
MODEL_PATH = r'd:\project ai\data\emotion_model.pkl'
VECTORIZER_PATH = r'd:\project ai\data\tfidf_vectorizer.pkl'

def train_model():
    print("Loading data...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Check for missing values
    df.dropna(subset=['text', 'label'], inplace=True)
    
    print(f"Data Loaded: {len(df)} records")
    print("Label distribution:")
    print(df['label'].value_counts())

    # Split data
    X = df['text']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Vectorization
    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model Training
    print("Training Logistic Regression model...")
    # Using Logistic Regression as it's efficient and effective for text classification
    model = LogisticRegression(max_iter=1000, solver='lbfgs') 
    model.fit(X_train_vec, y_train)

    # Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save Model and Vectorizer
    print("Saving model and vectorizer...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")

if __name__ == "__main__":
    train_model()
