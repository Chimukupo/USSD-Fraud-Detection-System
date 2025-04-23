import pandas as pd
df = pd.read_csv("transactions.csv")
print(df["is_fraud"].value_counts())
print(df[df["user_id"] == 1]["is_fraud"].value_counts())
print(df[df["is_fraud"] == True][["amount", "hour", "recipient"]].describe())