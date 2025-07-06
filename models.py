from sqlalchemy import Column, Integer, String
from database import Base

class EventRegistration(Base):
    __tablename__ = "registrations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    event = Column(String)
