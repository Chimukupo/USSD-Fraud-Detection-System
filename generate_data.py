import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ========== Generating Dummy Data ==========
def generate_synthetic_data(n_transactions=10000, mary_user_id=1):
    data = []
    for i in range(n_transactions):
        # ========== Random user (Mary for 20% of transactions) ==========
        user_id = mary_user_id if random.random() < 0.2 else random.randint(2, 100)
        # ========== Normal vs. fraud ==========
        is_fraud = random.random() < 0.1  # ========== 10% fraud ==========
        amount = random.uniform(1000, 5000) if is_fraud else random.uniform(50, 500)
        recipient = "0959876543" if is_fraud else "0961234567"
        hour = random.randint(0, 3) if is_fraud else random.randint(8, 18)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=hour)
        data.append({
            "user_id": user_id,
            "amount": amount,
            "recipient": recipient,
            "timestamp": timestamp,
            "hour": timestamp.hour,
            "is_fraud": is_fraud
        })
    df = pd.DataFrame(data)
    df.to_csv("transactions.csv", index=False)
    print(f"Generated {len(df)} transactions, {sum(df['is_fraud'])} frauds")
    return df

if __name__ == "__main__":
    df = generate_synthetic_data()