from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://postgres:qwerty12@localhost:5432/zmobilemoney"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True)
    name = Column(String)

class Transaction(Base):
    __tablename__ = "transactions"
    tx_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    recipient = Column(String)
    timestamp = Column(DateTime)
    is_flagged = Column(Boolean, default=False)
    status = Column(String, default="Pending")

# Create tables
Base.metadata.create_all(engine)

# Add Mary if she doesn't exist
def add_mary():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.user_id == 1).first()
        if not existing_user:
            mary = User(user_id=1, phone="0971234567", name="Mary")
            db.add(mary)
            db.commit()
            print("Added Mary to users")
        else:
            print("Mary already exists")
    except Exception as e:
        db.rollback()
        print(f"Error adding Mary: {e}")
    finally:
        db.close()

# Add sample transactions for Mary
def add_sample_transactions():
    db = SessionLocal()
    try:
        mary = db.query(User).filter(User.user_id == 1).first()
        if not mary:
            print("Mary not found, cannot add transactions")
            return

        existing_txs = db.query(Transaction).filter(Transaction.user_id == 1).count()
        if existing_txs == 0:
            txs = [
                Transaction(
                    user_id=1,
                    amount=200,
                    recipient="0961234567",
                    timestamp=datetime.utcnow(),
                    is_flagged=False,
                    status="Approved"
                ),
                Transaction(
                    user_id=1,
                    amount=150,
                    recipient="0961234567",
                    timestamp=datetime.utcnow(),
                    is_flagged=False,
                    status="Approved"
                )
            ]
            db.add_all(txs)
            db.commit()
            print("Added sample transactions for Mary")
        else:
            print("Sample transactions already exist")
    except Exception as e:
        db.rollback()
        print(f"Error adding transactions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_mary()
    add_sample_transactions()