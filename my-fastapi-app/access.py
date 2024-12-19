from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


app = FastAPI()

# Database URL 
DATABASE_URL = "postgresql://postgres:gaurav76@localhost/users_signup"  # Update this with your DB credentials


Base = declarative_base()

# Define the table
class FileAccess(Base):
    __tablename__ = 'file_access'
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_gov_id = Column(String, index=True)
    user_id = Column(Integer, index=True)
    access = Column(String)

# Create the database engine 
engine = create_engine(DATABASE_URL)  

# Create the tables if they do not exist
Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FileAccessRequest(BaseModel):
    doctor_gov_id: str
    user_id: int

# get the database session
def get_db():
    db = SessionLocal()  
    try:
        yield db  
    finally:
        db.close()  

# POST endpoint to handle adding or updating access
@app.post("/add-access/")
async def add_access(request: FileAccessRequest, db: Session = Depends(get_db)):
    # Check if the access record already exists
    existing_access = db.query(FileAccess).filter(
        FileAccess.doctor_gov_id == request.doctor_gov_id,
        FileAccess.user_id == request.user_id
    ).first()

    if existing_access:
        # If access is "no", change to "yes"
        if existing_access.access == "no":
            existing_access.access = "yes"
            db.commit()
            return {"message": "Access granted successfully", "data": existing_access}
        else:
            raise HTTPException(status_code=400, detail="Access already granted for this doctor")

    # If no existing access, create a new one and set it to "yes"
    new_access = FileAccess(
        doctor_gov_id=request.doctor_gov_id,
        user_id=request.user_id,
        access="yes"  # Initially grant access
    )

    db.add(new_access)  # Add the new access record to the session
    db.commit()  # Commit the session to save changes to the database

    return {"message": "Access granted successfully", "data": new_access}

# DELETE endpoint to handle removing access (changing "yes" to "no")
@app.delete("/remove-access/")
async def remove_access(request: FileAccessRequest, db: Session = Depends(get_db)):
    # Check if the access record exists
    existing_access = db.query(FileAccess).filter(
        FileAccess.doctor_gov_id == request.doctor_gov_id,
        FileAccess.user_id == request.user_id
    ).first()

    if not existing_access:
        raise HTTPException(status_code=404, detail="Access record not found")

    # If access is already "no", we don't need to update it
    if existing_access.access == "yes":
        existing_access.access = "no"
        db.commit()  # Commit the changes to the database
        return {"message": "Access revoked successfully", "data": existing_access}
    else:
        raise HTTPException(status_code=400, detail="Access is already revoked")

# Include the router (optional, can be used for modular structure)
router = APIRouter()
app.include_router(router)
