from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
from typing import List
import psycopg2

app = FastAPI()

# Database connection settings (you can use SQLAlchemy or another ORM as well)
DATABASE_URL = "postgresql://postgres:gaurav76@localhost:5432/admin_login"

# Pydantic model for the request body
class RemarksRequest(BaseModel):
    patient_username: str

@app.post("/doctor-usernames/")
async def get_doctor_usernames(request: RemarksRequest):
    try:
        # Establish database connection
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Fetch associated doctors for the given patient username
        cursor.execute("""
            SELECT doctor_username FROM admin_login
            WHERE user_username = %s;
        """, (request.patient_username,))

        doctors = cursor.fetchall()
        if not doctors:
            raise HTTPException(status_code=404, detail="No associated doctors found for this patient.")

        # Extract the doctor usernames from the result
        doctor_usernames = [doctor[0] for doctor in doctors]

        cursor.close()
        conn.close()

        return {"doctor_usernames": doctor_usernames}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
router = APIRouter()
app.include_router(router)