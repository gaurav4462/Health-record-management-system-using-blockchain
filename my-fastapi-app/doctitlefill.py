from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import logging

# Database URLs (make sure they match your PostgreSQL setup)
DATABASE_URL_ADMIN = "postgresql://postgres:gaurav76@localhost/admin_login"
DATABASE_URL_USERS = "postgresql://postgres:gaurav76@localhost/users_signup"
DATABASE_URL_DOCS = "postgresql://postgres:gaurav76@localhost/doc_signup"

# Engine and Session creation for each database
engine_admin = create_engine(DATABASE_URL_ADMIN)
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=engine_admin)

engine_users = create_engine(DATABASE_URL_USERS)
SessionLocalUsers = sessionmaker(autocommit=False, autoflush=False, bind=engine_users)

engine_docs = create_engine(DATABASE_URL_DOCS)
SessionLocalDocs = sessionmaker(autocommit=False, autoflush=False, bind=engine_docs)

# Declare the Base for ORM models
Base = declarative_base()

# FastAPI app initialization
app = FastAPI()
router = APIRouter()

# SQLAlchemy Model for Doctor (doc_signup DB)
class Doctor(Base):
    __tablename__ = "doctors"
    gov_id = Column(String, nullable=False)
    username = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    practitioner_type = Column(String, nullable=False)

    # Relationship to admin_login table
    admin_login = relationship("AdminLogin", back_populates="doctor")

# SQLAlchemy Model for User (Patient) (users_signup DB)
class UserSignup(Base):
    __tablename__ = "users"
    id = Column(String, nullable=False)
    username = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)

    # Relationship to admin_login table
    admin_login = relationship("AdminLogin", back_populates="user")

# SQLAlchemy Model for AdminLogin (admin_login DB)
class AdminLogin(Base):
    __tablename__ = 'admin_login'

    id = Column(Integer, primary_key=True, index=True)
    doctor_username = Column(String, ForeignKey('doctors.username'))
    user_username = Column(String, ForeignKey('users.username'))

    # Relationships
    doctor = relationship("Doctor", back_populates="admin_login")
    user = relationship("UserSignup", back_populates="admin_login")

# Pydantic schema for Doctor's information (response model)
class DoctorInfo(BaseModel):
    gov_id: str
    name: str
    email: str
    degree: str
    practitioner_type: str
    username: str

    class Config:
        orm_mode = True

# Pydantic schema for User's (Patient's) information (response model)
class UserInfo(BaseModel):
    id: str
    name: str
    address: str
    phone: str
    email: str

    class Config:
        orm_mode = True

# Dependency to get the database session for admin_login (Doctor-User relationship)
def get_db_admin():
    db = SessionLocalAdmin()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the database session for users_signup (Patient)
def get_db_users():
    db = SessionLocalUsers()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the database session for doctors (Doctor details)
def get_db_docs():
    db = SessionLocalDocs()
    try:
        yield db
    finally:
        db.close()

# Logger for debugging
logger = logging.getLogger(__name__)

# Endpoint to fetch doctor and patient information based on doctor_username
@router.get("/doctor/{doctor_username}/patients", response_model=dict)
async def get_doctor_patient_info(
    doctor_username: str,
    db_admin: Session = Depends(get_db_admin),
    db_users: Session = Depends(get_db_users),
    db_docs: Session = Depends(get_db_docs)
):
    # Log the request for debugging
    logger.info(f"Fetching doctor with username: {doctor_username}")
    
    # Fetch all relationship records from the admin_login table (doctor-patient)
    admin_records = db_admin.query(AdminLogin).filter(AdminLogin.doctor_username == doctor_username).all()
    
    if not admin_records:
        raise HTTPException(status_code=404, detail="No doctor-patient records found")
    
    # Fetch doctor information from the doc_signup table
    doctor = db_docs.query(Doctor).filter(Doctor.username == doctor_username).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Log the doctor data
    logger.info(f"Found doctor: {doctor.name}")
    
    # Prepare a list of patients based on the admin_login records
    patients_info = []
    for admin_record in admin_records:
        # Fetch patient information using user_username from the admin_login table
        user = db_users.query(UserSignup).filter(UserSignup.username == admin_record.user_username).first()
        if user:
            patients_info.append({
                "id":user.id,
                "name": user.name,
                "address": user.address,
                "phone": user.phone,
                "email": user.email,
            })
        else:
            # If user is not found, you can decide how to handle it (e.g., log a warning or skip)
            logger.warning(f"Patient with username {admin_record.user_username} not found")
            continue

    # Return both doctor and a list of patients' information
    return {
        "doctor": {
            "gov_id": doctor.gov_id,
            "name": doctor.name,
            "email": doctor.email,
            "degree": doctor.degree,
            "practitioner_type": doctor.practitioner_type,
        },
        "patients": patients_info
    }

# Include the router in the FastAPI app
app.include_router(router)
