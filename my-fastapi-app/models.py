from sqlalchemy import Column, String, Integer
from database import Base

# Model for storing doctor details (based on Government ID)
class RegistrationGovernmentID(Base):
    __tablename__ = 'registration_government_ids'

    gov_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    degree = Column(String)
    practitioner_type = Column(String)
    phone_number = Column(String)



# Model for storing user details
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    gov_id = Column(String)
