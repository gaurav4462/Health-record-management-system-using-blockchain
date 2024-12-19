# userlogin.py
from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
import bcrypt

DATABASE_URL = "postgresql://postgres:gaurav76@localhost/users_signup"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    username: str
    password: str

# Create a FastAPI router
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register/")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Create a new user instance
    new_user = User(
        name=user.name,
        address=user.address,
        phone=user.phone,
        email=user.email,
        username=user.username,
        password=hashed_password.decode('utf-8')  # Store as a string
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}

@router.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful", "user_id": db_user.id}

app = FastAPI()

# Include the router in the app
app.include_router(router)
