from pydantic import BaseModel, EmailStr

# Schema for Government ID check request
class GovernmentIDCheck(BaseModel):
    gov_id: str

# Schema for Government ID check response
class IDCheckResponse(BaseModel):
    message: str
    phone_number: str

# Schema for user creation
class UserCreate(BaseModel):
    gov_id: str
    username: str
    email: EmailStr
    password: str

# Schema for OTP verification request
class OTPVerifyRequest(UserCreate):
    otp: str
