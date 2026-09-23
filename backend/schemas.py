from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password:str

class AnimalReportCreate(BaseModel):
    animal_type: str
    description: str
    address: str
    latitude: float
    longitude: float
    condition: str
    photo_path: str | None = None

class ResponderCreate(BaseModel):
    name: str
    email: str
    phone: str
    responder_type: str
    organization: str | None = None
    address: str
    latitude: float | None = None
    longitude: float | None = None
    password: str

class ResponderLogin(BaseModel):
    email:str
    password:str
