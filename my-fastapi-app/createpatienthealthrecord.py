from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "postgresql://postgres:gaurav76@localhost/patient_health_record"  # Replace with your PostgreSQL credentials

app = FastAPI()
router = APIRouter()

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Defining the Remark model with a composite primary key and other columns
class Remark(Base):
    __tablename__ = 'remarks'
    
    # Composite primary key
    doctor_username = Column(String, primary_key=True, index=True)
    patient_phone = Column(String, primary_key=True)  # Part of composite key
    remark = Column(Text)

Base.metadata.create_all(bind=engine)

# Pydantic models for input validation
class RemarkRequest(BaseModel):
    doctorUsername: str
    patientPhone: str
    remark: str

class RemarkUpdateRequest(RemarkRequest):
    pass

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensures the session is closed after use

# Route to add or update a remark for a patient
@app.post("/add_or_update_remark")
async def add_or_update_remark(request: RemarkRequest, db: Session = Depends(get_db)):
    # Check if the remark already exists for the doctor and patient
    remark = db.query(Remark).filter(Remark.doctor_username == request.doctorUsername, Remark.patient_phone == request.patientPhone).first()
    
    if remark:
        # If remark exists, update it
        remark.remark = request.remark
        db.commit()  # Commit the update
        return {"message": "Remark updated successfully!"}
    else:
        # If remark does not exist, create a new one
        new_remark = Remark(
            doctor_username=request.doctorUsername,
            patient_phone=request.patientPhone,
            remark=request.remark
        )
        db.add(new_remark)
        db.commit()  # Commit the new remark
        return {"message": "Remark added successfully!"}

# Route to update the remark for an existing patient (alternative, if needed)
@app.post("/update_remark")
async def update_remark(request: RemarkUpdateRequest, db: Session = Depends(get_db)):
    remark = db.query(Remark).filter(Remark.doctor_username == request.doctorUsername, Remark.patient_phone == request.patientPhone).first()
    if not remark:
        raise HTTPException(status_code=404, detail="Remark not found for the patient by this doctor.")
    remark.remark = request.remark
    db.commit()  # Commit the update to the database
    return {"message": "Remark updated successfully!"}

app.include_router(router)
