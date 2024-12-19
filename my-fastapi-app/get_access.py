from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# FastAPI app
app = FastAPI()

# Database URL (update with your actual Postgres URL)
DATABASE_URL = "postgresql://postgres:gaurav76@localhost/users_signup"

# SQLAlchemy base class
Base = declarative_base()

# Define the FileAccess table
class FileAccess(Base):
    __tablename__ = 'file_access'
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_gov_id = Column(String, index=True)
    user_id = Column(Integer, index=True)
    access = Column(String)

# Create the database engine
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Session maker for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Use the session in your endpoints
    finally:
        db.close()  # Ensure the session is closed when done

# Endpoint to check if user has access to the doctor
@app.get("/check-access/")
async def check_access(doctor_gov_id: str, user_id: int, db: Session = Depends(get_db)):
    # Query the file_access table to check for access
    access_record = db.query(FileAccess).filter(
        FileAccess.doctor_gov_id == doctor_gov_id,
        FileAccess.user_id == user_id
    ).first()

    if access_record and access_record.access == "yes":
        return {"has_access": True}
    else:
        return {"has_access": False}

router = APIRouter()
app.include_router(router)