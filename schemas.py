
from pydantic import BaseModel

class RegistrationSchema(BaseModel):
    name: str
    email: str
    event: str

    class Config:
        from_attributes = True
