from sklearn.ensemble import IsolationForest
import joblib
import pandas as pd
from preprocess_data import preprocess_data

def train_isolation_forest():
    X, y = preprocess_data()
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    joblib.dump(model, "fraud_model.pkl")
    print("Model trained and saved as fraud_model.pkl")

    # Test on Mary's transactions
    test_cases = pd.DataFrame([
        {"amount": 200, "hour": 10, "is_new_recipient": 0},  # Normal
        {"amount": 2000, "hour": 2, "is_new_recipient": 1},  # Fraud
    ])
    predictions = model.predict(test_cases)
    for i, pred in enumerate(predictions):
        status = "Fraud" if pred == -1 else "Normal"
        print(f"Test {i+1}: {test_cases.iloc[i].to_dict()} -> {status}")
    return model

if __name__ == "__main__":
    model = train_isolation_forest()