from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext

# Database configuration
DATABASE_URL = "postgresql://postgres:gaurav76@localhost/doc_signup"  # Update with your database credentials

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing setup (using passlib with bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database model for doctor signup (assuming it already exists in your `doc_signup` table)
class Doctor(Base):
    __tablename__ = "doctors"  # This should match the table where doctors are signed up
    gov_id = Column(String, primary_key=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)  # This stores the hashed password

# Pydantic model for the login request
class DocLoginRequest(BaseModel):
    username: str
    password: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensure the database session is closed after use

# Function to verify the password (compare plain text password with hashed password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create a new API Router instance
router = APIRouter()

# Endpoint for doctor login
@router.post("/doctor/login")
def login(doc_login: DocLoginRequest, db: Session = Depends(get_db)):
    # Query the doctor by username (you can modify to support email or other identifiers as needed)
    user = db.query(Doctor).filter(Doctor.username == doc_login.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    # Verify the password using the hashed password stored in the database
    if not verify_password(doc_login.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    # Return a success message (You may also want to include a token, e.g., JWT, for authentication)
    return {"message": "Login successful!"}

# Create the FastAPI app instance
app = FastAPI()

# Include the router in the app
app.include_router(router)
