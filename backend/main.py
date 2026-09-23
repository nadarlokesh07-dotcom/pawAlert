from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from firebase import db as firestore_db
from fastapi import UploadFile, File
import os
import shutil

from database import engine, Base, get_db
import models
from schemas import UserCreate, UserLogin, AnimalReportCreate,ResponderCreate,ResponderLogin
from auth import create_access_token,get_current_user
from pwdlib import PasswordHash

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

password_hash = PasswordHash.recommended()


@app.get("/")
def home():
    return {"message": "PawAlert backend is running"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        user.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(existing_user.id)}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/profile")
def profile(user_id: str = Depends(get_current_user)):
    return{
        "message":"you are logged in!",
        "user_id": user_id
    }

@app.post("/reports")
def create_report(
    report: AnimalReportCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    # Save report to SQLite
    new_report = models.AnimalReport(
    animal_type=report.animal_type,
    description=report.description,
    condition=report.condition,
    address=report.address,
    latitude=str(report.latitude),
    longitude=str(report.longitude),
    photo_path=report.photo_path,
    status="Reported"
)


    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Save report to Firestore
    firestore_data = {
        "report_id": new_report.id,
        "reported_by": user_id,
        "animal_type": report.animal_type,
        "description": report.description,
        "condition": report.condition,
        "address": report.address,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "photopath": report.photo_path,
        "status": "Reported"
    }

    firestore_db.collection("reports").add(firestore_data)

    return {
        "message": "Animal report created successfully",
        "report_id": new_report.id,
        "reported_by": user_id,
        "status": new_report.status
    }

@app.post("/upload-photo")
def upload_photo(
    file: UploadFile = File(...)
):
    # Create uploads folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Create a safe filename
    filename = os.path.basename(file.filename)

    # Save file path
    file_path = os.path.join("uploads", filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Photo uploaded successfully",
        "filename": filename,
        "file_path": file_path
    }
@app.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    reports = db.query(models.AnimalReport).all()

    return reports

@app.get("/reports/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    report = db.query(models.AnimalReport).filter(
        models.AnimalReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report

@app.post("/responders/register")
def register_responder(
    responder: ResponderCreate,
    db: Session = Depends(get_db)
):
    existing_responder = db.query(
        models.Responder
    ).filter(
        models.Responder.email == responder.email
    ).first()

    if existing_responder:
        raise HTTPException(
            status_code=400,
            detail="Responder with this email already exists"
        )

    hashed_password = password_hash.hash(
        responder.password
    )

    new_responder = models.Responder(
        name=responder.name,
        email=responder.email,
        phone=responder.phone,
        responder_type=responder.responder_type,
        organization=responder.organization,
        address=responder.address,
        latitude=str(responder.latitude)
        if responder.latitude is not None else None,
        longitude=str(responder.longitude)
        if responder.longitude is not None else None,
        availability="Available",
        verification_status="Pending",
        password=hashed_password
    )

    db.add(new_responder)
    db.commit()
    db.refresh(new_responder)

    return {
        "message": "Responder registration submitted successfully",
        "responder_id": new_responder.id,
        "verification_status": new_responder.verification_status
    }

@app.post("/responders/login")
def responder_login(
    responder: ResponderLogin,
    db: Session = Depends(get_db)
):
    existing_responder = db.query(
        models.Responder
    ).filter(
        models.Responder.email == responder.email
    ).first()

    if not existing_responder:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        responder.password,
        existing_responder.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if existing_responder.verification_status != "Approved":
        raise HTTPException(
            status_code=403,
            detail="Your responder account is not approved yet"
        )

    access_token = create_access_token(
        data={
            "sub": str(existing_responder.id),
            "role": "responder"
        }
    )

    return {
        "message": "Responder login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "responder_id": existing_responder.id
    }

@app.put("/admin/responders/{responder_id}/verify")
def verify_responder(
    responder_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    responder = db.query(
        models.Responder
    ).filter(
        models.Responder.id == responder_id
    ).first()

    if not responder:
        raise HTTPException(
            status_code=404,
            detail="Responder not found"
        )

    if status not in ["Approved", "Rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Approved or Rejected"
        )

    responder.verification_status = status

    db.commit()
    db.refresh(responder)

    return {
        "message": f"Responder {status.lower()} successfully",
        "responder_id": responder.id,
        "verification_status": responder.verification_status
    }

@app.get("/responders")
def get_responders(
    responder_type: str | None = None,
    availability: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Responder).filter(
        models.Responder.verification_status == "Approved"
    )

    if responder_type:
        query = query.filter(
            models.Responder.responder_type == responder_type
        )

    if availability:
        query = query.filter(
            models.Responder.availability == availability
        )

    responders = query.all()

    return responders

@app.get("/responders/{responder_id}")
def get_responder_profile(
    responder_id: int,
    db: Session = Depends(get_db)
):
    responder = db.query(
        models.Responder
    ).filter(
        models.Responder.id == responder_id,
        models.Responder.verification_status == "Approved"
    ).first()

    if not responder:
        raise HTTPException(
            status_code=404,
            detail="Responder not found"
        )

    return responder

@app.put("/responders/{responder_id}/availability")
def update_responder_availability(
    responder_id: int,
    availability: str,
    db: Session = Depends(get_db)
):
    if availability not in ["Available", "Busy", "Offline"]:
        raise HTTPException(
            status_code=400,
            detail="Availability must be Available, Busy, or Offline"
        )

    responder = db.query(
        models.Responder
    ).filter(
        models.Responder.id == responder_id
    ).first()

    if not responder:
        raise HTTPException(
            status_code=404,
            detail="Responder not found"
        )

    responder.availability = availability

    db.commit()
    db.refresh(responder)

    return {
        "message": "Availability updated successfully",
        "responder_id": responder.id,
        "availability": responder.availability
    }