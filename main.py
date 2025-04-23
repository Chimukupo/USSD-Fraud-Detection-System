from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, User, Transaction
from datetime import datetime
import joblib
import pandas as pd
import regex as re
from mock_ussd import send_ussd

app = FastAPI(title="Z Mobile Money")
templates = Jinja2Templates(directory="templates")
model = joblib.load("fraud_model.pkl")  # ========== Load ML model ==========

# ========== Pydantic models ==========
class TransactionCreate(BaseModel):
    user_id: int
    amount: float
    recipient: str

class USSDResponse(BaseModel):
    tx_id: int
    response: str

class SMSCheck(BaseModel):
    user_id: int
    sms_text: str

# ========== Database dependency ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to Z Mobile Money!"}

@app.post("/transaction")
async def create_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == tx.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ========== Rule-based fraud detection ==========
    recent_txs = db.query(Transaction).filter(Transaction.user_id == tx.user_id).all()
    known_recipients = {t.recipient for t in recent_txs}
    is_new_recipient = tx.recipient not in known_recipients
    is_rule_flagged = tx.amount > 1000 or is_new_recipient

    # ========== ML-based fraud detection ==========
    current_hour = datetime.utcnow().hour
    test_case = pd.DataFrame([{
        "amount": tx.amount,
        "hour": current_hour,
        "is_new_recipient": 1 if is_new_recipient else 0
    }])
    ml_prediction = model.predict(test_case)[0]
    is_ml_flagged = bool(ml_prediction == -1)  # ========== Convert to Python bool ==========

    # ========== Combine: flag if either rule or ML detects fraud ==========
    is_flagged = is_rule_flagged or is_ml_flagged

    # ========== Store transaction ==========
    db_tx = Transaction(
        user_id=tx.user_id,
        amount=tx.amount,
        recipient=tx.recipient,
        timestamp=datetime.utcnow(),
        is_flagged=is_flagged,
        status="Pending"
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    # ========== Send USSD ==========
    if is_flagged:
        message = f"Suspicious transfer ZMW {tx.amount} to {tx.recipient}. Reply 1=Approve, 2=Cancel"
    else:
        message = f"Transfer ZMW {tx.amount} to {tx.recipient} OK"
    send_ussd(user.phone, message)

    return {"tx_id": db_tx.tx_id, "status": "Logged", "flagged": is_flagged}

@app.get("/user/{user_id}/transactions")
async def get_transactions(user_id: int, db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return [{"tx_id": tx.tx_id, "amount": tx.amount, "recipient": tx.recipient, "status": tx.status} for tx in txs]

@app.post("/ussd_response")
async def handle_ussd_response(resp: USSDResponse, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.tx_id == resp.tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if resp.response == "1":
        tx.status = "Approved"
    elif resp.response == "2":
        tx.status = "Cancelled"
    else:
        raise HTTPException(status_code=400, detail="Invalid response")
    db.commit()
    user = db.query(User).filter(User.user_id == tx.user_id).first()
    send_ussd(user.phone, f"Transaction {tx.tx_id} {tx.status}")
    return {"tx_id": tx.tx_id, "status": tx.status}

@app.post("/check_sms")
async def check_sms(sms: SMSCheck, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == sms.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    scam_keywords = ["win", "prize", "urgent", "send", "claim", "job offer", "free", "award", "click"]
    sms_text = sms.sms_text.lower()
    # ========== Keyword check ==========
    has_keywords = any(keyword in sms_text for keyword in scam_keywords)
    # ========== URL check ==========
    has_url = bool(re.search(r'http[s]?://[^\s]+|www\.[^\s]+', sms_text))
    is_phishing = has_keywords or has_url
    if is_phishing:
        message = "Warning: Possible scam SMS. Do not click links or send money."
        send_ussd(user.phone, message)
        return {"status": "Phishing detected", "message": message}
    return {"status": "No phishing detected"}

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, db: Session = Depends(get_db)):
    flagged_txs = db.query(Transaction).filter(Transaction.is_flagged == True).all()
    total_count = db.query(Transaction).count()
    flagged_count = len(flagged_txs)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "transactions": flagged_txs,
        "total_count": total_count,
        "flagged_count": flagged_count
    })