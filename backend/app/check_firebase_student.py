"""
Check Firebase student comprehensive data
"""
import os
import json
import sys
from pathlib import Path
from firebase_admin import credentials, db, initialize_app

# Load credentials
service_account_path = Path(__file__).parent.parent / "serviceAccountKey.json"
with open(service_account_path) as f:
    cred_data = json.load(f)

os.environ['FIREBASE_PROJECT_ID'] = cred_data['project_id']
os.environ['FIREBASE_PRIVATE_KEY'] = cred_data['private_key']
os.environ['FIREBASE_CLIENT_EMAIL'] = cred_data['client_email']
database_url = f"https://{cred_data['project_id']}-default-rtdb.firebaseio.com"

# Initialize Firebase
cred = credentials.Certificate(cred_data)
initialize_app(cred, {'databaseURL': database_url})

# Fetch a sample student
ref = db.reference('students/AGRI2023A001')
student = ref.get()

print("="*60)
print("Sample Student Data from Firebase")
print("="*60)
print(json.dumps(student, indent=2))
print("\n" + "="*60)
print(f"Total fields: {len(student.keys() if student else {})}")
print("="*60)
