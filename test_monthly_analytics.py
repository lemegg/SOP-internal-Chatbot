import requests
import json

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "anurag@theaffordableorganicstore.com"
PASSWORD = "password123"

def test_monthly_log():
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching monthly query log...")
    log_res = requests.get(f"{BASE_URL}/api/analytics/query-log/monthly", headers=headers)
    
    print(f"Status: {log_res.status_code}")
    if log_res.status_code == 200:
        data = log_res.json()
        print(f"Logs found: {len(data['logs'])}")
        if data['logs']:
            print("First log entry:")
            print(json.dumps(data['logs'][0], indent=2))
    else:
        print(f"Error: {log_res.text}")

if __name__ == "__main__":
    test_monthly_log()
