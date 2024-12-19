from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.responses import JSONResponse

# Database connection settings
DATABASE_URL = "postgresql://postgres:gaurav76@localhost:5432/patient_health_record"  # Replace with your actual DB URL
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class RemarkRequest(BaseModel):
    patient_phone: str
    doctor_usernames: list  # Now accepting a list of doctor usernames

class RemarkResponse(BaseModel):
    patient_phone: str
    doctor_username: str
    remark: str
    created_at: int  # Timestamp (integer)

    class Config:
        orm_mode = True

# SQLAlchemy model (No 'id' column)
class Remark(Base):
    __tablename__ = 'remarks'

    patient_phone = Column(String, primary_key=True, index=True)
    doctor_username = Column(String, primary_key=True, index=True)
    remark = Column(Text)

# FastAPI instance
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoint to fetch remarks for multiple doctors
@app.post("/remarks/", response_model=dict)
async def get_remarks(request: RemarkRequest, db: Session = Depends(get_db)):
    # Query the database for remarks based on patient_phone and the list of doctor_usernames
    remarks = db.query(Remark).filter(
        Remark.patient_phone == request.patient_phone,
        Remark.doctor_username.in_(request.doctor_usernames)  # Use IN for multiple doctor usernames
    ).all()

    if not remarks:
        raise HTTPException(status_code=404, detail="No remarks found for this patient and the given doctors")

    # Convert remarks to a structured response, including remarks and additional metadata
    remarks_response = [
        {
            "patient_phone": remark.patient_phone,
            "doctor_username": remark.doctor_username,
            "remark": remark.remark,
            # Optional: "created_at": remark.created_at,
        }
        for remark in remarks
    ]

    return JSONResponse(content={"remarks": remarks_response})

# If you have any more routes like /add-access, /remove-access, etc., you can add them below.
router = APIRouter()
app.include_router(router)
