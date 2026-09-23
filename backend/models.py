from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class AnimalReport(Base):
    __tablename__ = "animal_reports"

    id = Column(Integer, primary_key=True, index=True)
    animal_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    photo_path = Column(String,nullable=True)
    status = Column(String, default="Reported")

class Responder(Base):
    __tablename__ = "responders"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)

    responder_type = Column(String, nullable=False)
    # vet / shelter / volunteer

    organization = Column(String, nullable=True)

    address = Column(String, nullable=False)

    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    availability = Column(String, default="Available")

    verification_status = Column(
        String,
        default="Pending"
    )

    password = Column(String, nullable=False)