import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings

print(f"RAW ANALYTICS_ALLOWED_EMAILS: '{settings.ANALYTICS_ALLOWED_EMAILS}'")
print(f"PARSED allowed_emails: {settings.allowed_emails}")
print(f"CURRENT WORKING DIRECTORY: {os.getcwd()}")
print(f".env EXISTS in CWD: {os.path.exists('.env')}")
