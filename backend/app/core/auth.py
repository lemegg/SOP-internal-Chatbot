import httpx
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# Cache for JWKS
_jwks_cache = None
_jwks_last_fetch = 0

async def get_jwks():
    global _jwks_cache, _jwks_last_fetch
    now = time.time()
    # Refresh cache every hour
    if _jwks_cache is None or (now - _jwks_last_fetch) > 3600:
        jwks_url = f"{settings.CLERK_ISSUER_URL}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            _jwks_cache = response.json()
            _jwks_last_fetch = now
    return _jwks_cache

from app.models.models import User
from app.core.database import get_db
from sqlalchemy.orm import Session

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        jwks = await get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER_URL,
            options={"verify_aud": False}
        )
        
        # In Clerk Session tokens, email is often in 'email' or we might need to use 'sub'
        # Let's check common Clerk payload keys
        email = payload.get("email")
        if not email:
            # Try to get from metadata if you mapped it, or just use sub as a fallback
            # But for allowed_emails check, we REALLY need the email.
            # If email is missing from JWT, we might need to fetch it from Clerk API (slow)
            # OR ensure it's in the Session Token via Clerk Dashboard.
            email = payload.get("sub") # Fallback to ID
            
        print(f"DEBUG: Full Clerk Payload Keys: {list(payload.keys())}", flush=True)
        print(f"DEBUG: Clerk Auth - Email: {email}, Metadata: {payload.get('public_metadata')}", flush=True)

        # Sync with local database to maintain compatibility with existing models
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # If we only have the ID (sub), the allowed_emails check will fail.
            user = User(email=email, hashed_password="CLERK_AUTHED")
            db.add(user)
            db.commit()
            db.refresh(user)

        # Check if user is admin
        metadata = payload.get("public_metadata", {})
        is_admin = metadata.get("role") == "admin" or email.lower() in settings.allowed_emails

        # Attach is_admin to the user object temporarily for this request
        user.is_admin = is_admin
        return user
    except JWTError as e:
        print(f"JWT Error: {e}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Auth Error: {e}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error"
        )
