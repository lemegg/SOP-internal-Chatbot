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
        
        print(f"DEBUG: Clerk Auth - Payload keys: {list(payload.keys())}", flush=True)
        
        # Try different possible email keys in Clerk
        email = (
            payload.get("email") or 
            payload.get("email_address") or 
            payload.get("primary_email_address") or
            payload.get("preferred_username")
        )
        
        # If we still don't have an email, but 'sub' looks like an email
        if not email and payload.get("sub") and "@" in payload.get("sub"):
            email = payload.get("sub")

        if not email:
            # Fallback to sub but warn it's an ID
            email = payload.get("sub") 
            
        print(f"DEBUG: Clerk Auth - Final Email used for check: {email}", flush=True)

        # Sync with local database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, hashed_password="CLERK_AUTHED")
            db.add(user)
            db.commit()
            db.refresh(user)

        # Check if user is admin
        # Check allowed_emails (case-insensitive)
        email_is_allowed = False
        if email:
            email_is_allowed = email.lower() in [e.lower() for e in settings.allowed_emails]
            
        is_admin = email_is_allowed
        
        print(f"DEBUG: Clerk Auth - is_admin result: {is_admin} (email allowed: {email_is_allowed})", flush=True)

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
