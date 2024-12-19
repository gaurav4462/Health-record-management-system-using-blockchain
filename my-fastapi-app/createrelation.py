from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os

# Database URLs (Replace with actual credentials)
DOC_SIGNUP_DB_URL = os.getenv("DOC_SIGNUP_DB_URL", "postgresql://postgres:gaurav76@localhost/doc_signup")
USERS_SIGNUP_DB_URL = os.getenv("USERS_SIGNUP_DB_URL", "postgresql://postgres:gaurav76@localhost/users_signup")
ADMIN_LOGIN_DB_URL = os.getenv("ADMIN_LOGIN_DB_URL", "postgresql://postgres:gaurav76@localhost/admin_login")

# Create separate SQLAlchemy engines for each database
doc_signup_engine = create_engine(DOC_SIGNUP_DB_URL)
users_signup_engine = create_engine(USERS_SIGNUP_DB_URL)
admin_login_engine = create_engine(ADMIN_LOGIN_DB_URL)

# Session maker for each database
SessionLocalDoc = sessionmaker(autocommit=False, autoflush=False, bind=doc_signup_engine)
SessionLocalUser = sessionmaker(autocommit=False, autoflush=False, bind=users_signup_engine)
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=admin_login_engine)

# Models for admin_login table (to be created in admin_login database)
metadata = MetaData()

admin_table = Table(
    'admin_login', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('doctor_username', String, index=True),
    Column('user_username', String, index=True),
)

# Create the admin_login table if it doesn't exist
metadata.create_all(admin_login_engine)

# FastAPI app
app = FastAPI()
router = APIRouter()

# Dependency to get DB session for doc_signup, users_signup, and admin_login
def get_db_doc():
    db = SessionLocalDoc()
    try:
        yield db
    finally:
        db.close()

def get_db_user():
    db = SessionLocalUser()
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

# Pydantic models for validation
class AdminLoginRequest(BaseModel):
    doctor_username: str
    user_username: str

class Doctor(BaseModel):
    username: str

class User(BaseModel):
    username: str

# Fetch doctors from doc_signup database
def get_doctors(db: Session):
    try:
        doctors = db.execute(text("SELECT username FROM doctors")).fetchall()
        if not doctors:
            raise HTTPException(status_code=404, detail="No doctors found")
        return doctors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctors: {str(e)}")

# Fetch users from users_signup database
def get_users(db: Session):
    try:
        users = db.execute(text("SELECT username FROM users")).fetchall()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# Add record to admin_login table
def add_admin_record(db: Session, doctor_username: str, user_username: str):
    try:
        # Check if the record already exists
        existing_record = db.execute(
            text("SELECT * FROM admin_login WHERE doctor_username = :doctor_username AND user_username = :user_username"),
            {"doctor_username": doctor_username, "user_username": user_username}
        ).fetchone()

        if existing_record:
            raise HTTPException(status_code=400, detail="Record already exists.")

        # Insert the new record
        db.execute(
            text("INSERT INTO admin_login (doctor_username, user_username) VALUES (:doctor_username, :user_username)"),
            {"doctor_username": doctor_username, "user_username": user_username}
        )
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding record: {str(e)}")

# API Endpoints
@app.get("/admin/doctors")
def get_doctor_list(db: Session = Depends(get_db_doc)):
    return [{"username": doctor[0]} for doctor in get_doctors(db)]

@app.get("/admin/users")
def get_user_list(db: Session = Depends(get_db_user)):
    return [{"username": user[0]} for user in get_users(db)]

@app.post("/admin/add-record")
def add_record(request: AdminLoginRequest, db: Session = Depends(get_db_admin)):
    add_admin_record(db, request.doctor_username, request.user_username)
    return {"detail": "Record added successfully"}

app.include_router(router)
