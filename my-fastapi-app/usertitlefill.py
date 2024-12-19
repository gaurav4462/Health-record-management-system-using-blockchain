from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List

# Database URLs
DATABASE_URL_ADMIN = "postgresql://postgres:gaurav76@localhost/admin_login"
DATABASE_URL_USERS = "postgresql://postgres:gaurav76@localhost/users_signup"
DATABASE_URL_DOCS = "postgresql://postgres:gaurav76@localhost/doc_signup"

# Create engines and sessions
engine_admin = create_engine(DATABASE_URL_ADMIN)
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=engine_admin)

engine_users = create_engine(DATABASE_URL_USERS)
SessionLocalUsers = sessionmaker(autocommit=False, autoflush=False, bind=engine_users)

engine_docs = create_engine(DATABASE_URL_DOCS)
SessionLocalDocs = sessionmaker(autocommit=False, autoflush=False, bind=engine_docs)

# Declare the Base for ORM models
Base = declarative_base()

# SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    email = Column(String)

class Doctor(Base):
    __tablename__ = "doctors"
    username = Column(String, primary_key=True)
    gov_id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    degree = Column(String)
    practitioner_type = Column(String)  # Add practitioner_type here

class AdminLogin(Base):
    __tablename__ = 'admin_login'
    id = Column(Integer, primary_key=True, index=True)
    doctor_username = Column(String, ForeignKey('doctors.username'))
    user_username = Column(String, ForeignKey('users.username'))

# Pydantic models for response
class UserInfo(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    email: str

    class Config:
        from_attributes = True

class DoctorInfo(BaseModel):
    username: str
    gov_id : str
    name: str
    email: str
    degree: str
    practitioner_type: str  # Include practitioner_type here

    class Config:
        from_attributes = True

class UserWithDoctorsResponse(BaseModel):
    user: UserInfo
    doctors: List[DoctorInfo]

# Dependencies
def get_db_users():
    db = SessionLocalUsers()
    try:
        yield db
    finally:
        db.close()

def get_db_admin():
    db = SessionLocalAdmin()
    try:
        yield db
    finally:
        db.close()

def get_db_docs():
    db = SessionLocalDocs()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI()

# Endpoint to fetch user details and associated doctor details
@app.get("/user/{username}/doctors", response_model=UserWithDoctorsResponse)
async def get_user_and_doctors(
    username: str,
    db_users: Session = Depends(get_db_users),
    db_admin: Session = Depends(get_db_admin),
    db_docs: Session = Depends(get_db_docs)
):
    # Fetch user details
    user = db_users.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch associated doctors
    admin_records = db_admin.query(AdminLogin).filter(AdminLogin.user_username == username).all()
    doctors_info = []
    for record in admin_records:
        doctor = db_docs.query(Doctor).filter(Doctor.username == record.doctor_username).first()
        if doctor:
            doctors_info.append(DoctorInfo(
                username=doctor.username,
                gov_id = doctor.gov_id,
                name=doctor.name,
                email=doctor.email,
                degree=doctor.degree,
                practitioner_type=doctor.practitioner_type  # Include practitioner_type here
            ))

    return UserWithDoctorsResponse(
        user=UserInfo(
            id=user.id,
            name=user.name,
            address=user.address,
            phone=user.phone,
            email=user.email
        ),
        doctors=doctors_info
    )
