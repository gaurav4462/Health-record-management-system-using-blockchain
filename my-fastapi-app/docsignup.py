from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from twilio.rest import Client
import random
import time
from pydantic import BaseModel, EmailStr

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:gaurav76@localhost/doc_gov_id"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

OTP_EXPIRATION_TIME = 30000 
time_to_compare = time.time()
otp_to_compare = 0

# Define the database models
class RegistrationGovernmentID(Base):
    __tablename__ = 'registration_government_ids'

    gov_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    degree = Column(String)
    practitioner_type = Column(String)
    phone_number = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    gov_id = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

#  get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class GovernmentIDCheck(BaseModel):
    gov_id: str

class IDCheckResponse(BaseModel):
    message: str
    phone_number: str

class UserCreate(BaseModel):
    gov_id: str
    username: str
    email: EmailStr
    password: str

class OTPVerifyRequest(UserCreate):
    otp: str

router = APIRouter()

#  generate a random OTP
def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

#send OTP via Twilio SMS
def send_otp_via_twilio(phone_number: str):
    try:
        generated_otp = generate_otp()
        global otp_to_compare
        otp_to_compare = generated_otp

        global time_to_compare
        time_to_compare = time.time()

        message = twilio_client.messages.create(
            body=f"Your verification code is {generated_otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        return {"message": "OTP sent", "otp": generated_otp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

def verify_otp(otp: str):
    current_time = time.time()
    if current_time - time_to_compare > OTP_EXPIRATION_TIME:
        raise HTTPException(status_code=400, detail="OTP has expired")

    if otp_to_compare == otp:
        return "OTP verified successfully"
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

@router.post("/check-government-id/", response_model=IDCheckResponse)
def check_government_id(id_check: GovernmentIDCheck, db: Session = Depends(get_db)):
    db_entry = db.query(RegistrationGovernmentID).filter(RegistrationGovernmentID.gov_id == id_check.gov_id).first()

    if db_entry:
        phone_number = db_entry.phone_number
        send_status = send_otp_via_twilio(phone_number)
        return {"message": "OTP sent", "otp_status": send_status, "phone_number": phone_number}
    else:
        raise HTTPException(status_code=404, detail="ID does not match or not found")

# Endpoint to verify OTP
@router.post("/verify-otp/")
def verify_otp_endpoint(otp: str = Form()):
    verification_status = verify_otp(otp)
    return {"message": verification_status}
