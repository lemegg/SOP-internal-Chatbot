import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_admin_flag(email, password):
    print(f"Testing user: {email}")
    # 1. Login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if login_res.status_code != 200:
        print(f"Login failed for {email}")
        return
    token = login_res.json()["access_token"]
    
    # 2. Get profile
    headers = {"Authorization": f"Bearer {token}"}
    me_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Profile: {json.dumps(me_res.json(), indent=2)}")

if __name__ == "__main__":
    # Ensure users exist in local DB
    import os
    import sys
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from app.core.database import SessionLocal
    from app.models.models import User
    from app.core.auth import get_password_hash
    
    db = SessionLocal()
    for email in ["b@theaffordableorganicstore.com", "c@theaffordableorganicstore.com"]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating user {email}")
            db.add(User(email=email, hashed_password=get_password_hash("password123")))
    db.commit()
    db.close()

    test_admin_flag("b@theaffordableorganicstore.com", "password123")
    test_admin_flag("c@theaffordableorganicstore.com", "password123")
