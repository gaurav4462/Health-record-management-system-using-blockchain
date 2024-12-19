from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from sqlalchemy.exc import OperationalError

# Database URLs
DATABASE_URL_DOC_SIGNUP = "postgresql://postgres:gaurav76@localhost/doc_signup"
DATABASE_URL_DOC_GOV_ID = "postgresql://postgres:gaurav76@localhost/doc_gov_id"

# SQLAlchemy Setup for doc_signup (storing doctor info)
engine_doc_signup = create_engine(DATABASE_URL_DOC_SIGNUP)
SessionLocal_doc_signup = sessionmaker(autocommit=False, autoflush=False, bind=engine_doc_signup)

# SQLAlchemy Setup for doc_gov_id (fetching registration info)
engine_doc_gov_id = create_engine(DATABASE_URL_DOC_GOV_ID)
SessionLocal_doc_gov_id = sessionmaker(autocommit=False, autoflush=False, bind=engine_doc_gov_id)

Base = declarative_base()

# Password hashing setup using Passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Doctor model (SQLAlchemy)
class Doctor(Base):
    __tablename__ = "doctors"
    gov_id = Column(String, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)  # Encrypted password
    name = Column(String)
    degree = Column(String)
    phone_number = Column(String)
    practitioner_type = Column(String)

# Registration Government IDs model (SQLAlchemy) for doc_gov_id database
class RegistrationGovernmentID(Base):
    __tablename__ = "registration_government_ids"
    gov_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    degree = Column(String)
    phone_number = Column(String)
    practitioner_type = Column(String)

# Pydantic model for signup request validation
class SignupRequest(BaseModel):
    gov_id: str
    username: str
    email: EmailStr
    password: str

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# FastAPI app
app = FastAPI()

# Dependency to get the database session for doc_signup (doctor's data)
def get_db_doc_signup():
    db = SessionLocal_doc_signup()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the database session for doc_gov_id (registration data)
def get_db_doc_gov_id():
    db = SessionLocal_doc_gov_id()
    try:
        yield db
    finally:
        db.close()

# Function to create the doctors table if it doesn't exist
def create_doctors_table_if_not_exists():
    inspector = inspect(engine_doc_signup)
    if not inspector.has_table("doctors"):
        print("Creating doctors table as it does not exist...")
        Base.metadata.create_all(bind=engine_doc_signup)

@app.post("/signup/")
async def signup(request: SignupRequest, db_doc_signup: Session = Depends(get_db_doc_signup), db_doc_gov_id: Session = Depends(get_db_doc_gov_id)):
    # Ensure that the doctors table exists
    create_doctors_table_if_not_exists()

    # Check if a doctor already exists with the same government ID in doc_signup database
    existing_doctor = db_doc_signup.query(Doctor).filter(Doctor.gov_id == request.gov_id).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Doctor with this government ID already exists.")

    # Fetch the additional information from the registration_government_ids table in doc_gov_id database
    registration_info = db_doc_gov_id.query(RegistrationGovernmentID).filter(RegistrationGovernmentID.gov_id == request.gov_id).first()

    if not registration_info:
        raise HTTPException(status_code=400, detail="No registration information found for this government ID.")

    # Hash the password before storing it
    hashed_password = hash_password(request.password)

    # Create a new doctor record including the extra information
    new_doctor = Doctor(
        gov_id=request.gov_id,
        username=request.username,
        email=request.email,
        password=hashed_password,
        name=registration_info.name,
        degree=registration_info.degree,
        phone_number=registration_info.phone_number,
        practitioner_type=registration_info.practitioner_type
    )

    # Add the new doctor to the doc_signup database and commit the transaction
    db_doc_signup.add(new_doctor)
    db_doc_signup.commit()
    db_doc_signup.refresh(new_doctor)

    # Return success message
    return {"message": "Doctor signed up successfully!"}
