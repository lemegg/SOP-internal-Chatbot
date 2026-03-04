import requests
import json

# Local testing script for feedback feature
# Assumes backend is running locally on port 8000

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "anurag@theaffordableorganicstore.com"
PASSWORD = "password123" # Use a valid password for your local test user

def test_feedback():
    # 1. Login to get token
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Send a chat to get a query_log_id
    print("Sending chat message...")
    chat_res = requests.post(
        f"{BASE_URL}/api/chat", 
        headers=headers, 
        json={"query": "test query for feedback"}
    )
    if chat_res.status_code != 200:
        print(f"Chat failed: {chat_res.text}")
        return
    
    chat_data = chat_res.json()
    query_log_id = chat_data["query_log_id"]
    print(f"Received query_log_id: {query_log_id}")

    # 3. Submit feedback
    print(f"Submitting 'like' feedback for id {query_log_id}...")
    feedback_res = requests.post(
        f"{BASE_URL}/api/feedback",
        headers=headers,
        json={"query_log_id": query_log_id, "feedback": "like"}
    )
    print(f"Feedback Status: {feedback_res.status_code}")
    print(f"Feedback Response: {feedback_res.text}")

    # 4. Try duplicate feedback
    print("Testing duplicate feedback prevention...")
    dup_res = requests.post(
        f"{BASE_URL}/api/feedback",
        headers=headers,
        json={"query_log_id": query_log_id, "feedback": "dislike"}
    )
    print(f"Duplicate Status (should be 400): {dup_res.status_code}")
    print(f"Duplicate Response: {dup_res.text}")

if __name__ == "__main__":
    try:
        test_feedback()
    except Exception as e:
        print(f"Test Error: {e}")
