import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(
    cred,
    {
        "storageBucket": "YOUR_STORAGE_BUCKET"
    }
)

db = firestore.client()
bucket = storage.bucket()