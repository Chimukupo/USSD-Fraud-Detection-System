Z Mobile Money
  A mobile money fraud detection system, featuring a USSD simulator (*115#), rule-based and ML-powered fraud detection, phishing SMS alerts, and an admin dashboard.
Features

USSD Interface: Mock *115# menu for sending money and responding to fraud alerts (e.g., approve/cancel suspicious transfers).
Fraud Detection:
Rule-based: Flags transfers > ZMW 1,000 or to new recipients.
ML-based: Isolation Forest model detects anomalies (e.g., large amounts, odd hours).


Phishing Protection: Detects scam SMS (e.g., “Send ZMW 100 to win”) using keyword analysis.
Admin Dashboard: Web interface to monitor flagged transactions.
Tech Stack: Python, FastAPI, PostgreSQL, Scikit-learn, Pandas, Jinja2.

Use Case
  Mary, a Lusaka-based user, sends ZMW 200 to a supplier (normal) but is targeted by a ZMW 2,000 fraud and a phishing SMS (“Click for a job offer”). Z Mobile Money flags the fraud, alerts Mary via *115#, lets her cancel, and warns about the SMS.
Setup

Clone the repo:git clone https://github.com/Chimukupo/USSD-Fraud-Detection-System.git
cd USSD-Fraud-Detection-System


Install dependencies:python -m venv zmobile_env
source zmobile_env/bin/activate  # Windows: zmobile_env\Scripts\activate
pip install fastapi uvicorn psycopg2-binary sqlalchemy pandas scikit-learn jinja2


Set up PostgreSQL:
Create database: CREATE DATABASE zmobilemoney;
Update database.py with your Postgres password.


Initialize data:python database.py
python generate_data.py


Run the app:uvicorn main:app --reload


API: http://127.0.0.1:8000
Dashboard: http://127.0.0.1:8000/dashboard



Testing

Normal Transfer: curl -X POST "http://127.0.0.1:8000/transaction" -H "Content-Type: application/json" -d '{"user_id": 1, "amount": 200, "recipient": "0961234567"}'
Fraud Transfer: curl -X POST "http://127.0.0.1:8000/transaction" -H "Content-Type: application/json" -d '{"user_id": 1, "amount": 2000, "recipient": "0959876543"}', then cancel via /ussd_response.
Phishing SMS: curl -X POST "http://127.0.0.1:8000/check_sms" -H "Content-Type: application/json" -d '{"user_id": 1, "sms_text": "Click the link below for a job offer"}'.

## ML Setup
- Generates 10,000 synthetic transactions (~10% fraud, e.g., 972 in initial run).
- Trains Isolation Forest model to detect anomalies (e.g., Mary’s ZMW 2,000 fraud).
- Run: `python generate_data.py && python preprocess_data.py && python train_model.py`

Future Work

Interactive *115# demo (Week 6).
Advanced ML for phishing detection.
Real USSD gateway integration.

Contributors

Chimukupo - Lead Developer
[Partner’s GitHub] - Collaborator (TBD)

License
  MIT License
