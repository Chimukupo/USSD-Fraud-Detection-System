import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from database import User, Transaction, SessionLocal

def preprocess_data(csv_file="transactions.csv"):
    df = pd.read_csv(csv_file)
    # Compute is_new_recipient
    def is_new_recipient(row):
        db = SessionLocal()
        recent_txs = db.query(Transaction).filter(Transaction.user_id == row["user_id"]).all()
        known_recipients = {t.recipient for t in recent_txs}
        db.close()
        return 1 if row["recipient"] not in known_recipients else 0

    df["is_new_recipient"] = df.apply(is_new_recipient, axis=1)
    # Features for ML
    features = ["amount", "hour", "is_new_recipient"]
    X = df[features]
    return X, df["is_fraud"]

if __name__ == "__main__":
    X, y = preprocess_data()
    print(f"Processed {len(X)} records with {sum(y)} frauds")