from firebase import db

test_data = {
    "animal_type": "Dog",
    "condition": "Test",
    "description": "PawAlert Firebase connection test",
    "latitude": 17.3850,
    "longitude": 78.4867,
    "status": "Reported"
}

doc_ref = db.collection("reports").add(test_data)

print("Firebase connected successfully!")
print("Document ID:", doc_ref[1].id)