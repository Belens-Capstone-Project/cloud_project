import os
import firebase_admin
from firebase_admin import credentials, auth
from pathlib import Path
import json

def initialize_firebase():
    try:
        print("Initializing Firebase...")
        
        # Get credentials from environment
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        
        if not firebase_creds:
            raise EnvironmentError("FIREBASE_CREDENTIALS environment variable not found")
            
        print("Parsing credentials from environment variable")
        creds_dict = json.loads(firebase_creds)
        
        print("Initializing Firebase Admin SDK")
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
        
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Firebase: {str(e)}")
        raise