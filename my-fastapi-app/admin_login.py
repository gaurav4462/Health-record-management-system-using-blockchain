from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:gaurav76@localhost/admin_login")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Schemas
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    message: str
    username: str

app = FastAPI()
router = APIRouter()

# get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get admin by username
def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

# Admin login 
@app.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = get_admin_by_username(db, request.username)
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin.password != request.password:  # Consider using hashed passwords in production
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"message": "Login successful", "username": admin.username}

app.include_router(router)
