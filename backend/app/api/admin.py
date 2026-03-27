from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Any
import httpx
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.models import User

router = APIRouter()

CLERK_API_BASE = "https://api.clerk.com/v1"

def get_admin_headers():
    return {
        "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

async def check_is_admin(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have administrative privileges."
        )
    return current_user

@router.get("/users")
async def list_access_control(admin: User = Depends(check_is_admin)):
    headers = get_admin_headers()
    async with httpx.AsyncClient() as client:
        # Fetch active users
        users_resp = await client.get(f"{CLERK_API_BASE}/users", headers=headers)
        # Fetch pending invitations
        invites_resp = await client.get(f"{CLERK_API_BASE}/invitations", headers=headers)
        
        if users_resp.status_code != 200 or invites_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch data from Clerk")
            
        users = users_resp.json()
        invites = invites_resp.json()
        
        # Filter invites to only show 'pending' ones
        pending_invites = [i for i in invites if i.get("status") == "pending"]
        
        return {
            "active_users": [
                {
                    "id": u["id"],
                    "email": u["email_addresses"][0]["email_address"] if u["email_addresses"] else "N/A",
                    "joined_at": u["created_at"],
                    "last_active": u["last_active_at"]
                } for u in users
            ],
            "pending_invites": [
                {
                    "id": i["id"],
                    "email": i["email_address"],
                    "sent_at": i["created_at"]
                } for i in pending_invites
            ]
        }

@router.post("/invite")
async def invite_user(payload: Dict[str, str], request: Request, admin: User = Depends(check_is_admin)):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Try to determine the actual origin of the app for the invitation link
    # This avoids using placeholder domains like 'your-app-domain.up.railway.app'
    redirect_url = settings.FRONTEND_ORIGIN
    
    # If FRONTEND_ORIGIN is a placeholder or default, try to use the request host
    if "your-app-domain" in redirect_url or "localhost" in redirect_url:
        origin = request.headers.get("origin") or request.headers.get("referer")
        if origin:
            # Strip trailing slash and path if it's referer
            from urllib.parse import urlparse
            parsed = urlparse(origin)
            redirect_url = f"{parsed.scheme}://{parsed.netloc}"
        
    headers = get_admin_headers()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{CLERK_API_BASE}/invitations",
            headers=headers,
            json={"email_address": email, "redirect_url": redirect_url}
        )
        
        if resp.status_code != 200:
            error_detail = resp.json().get("errors", [{"message": "Invitation failed"}])[0]["message"]
            raise HTTPException(status_code=resp.status_code, detail=error_detail)
            
        return resp.json()

@router.delete("/users/{user_id}")
async def revoke_user_access(user_id: str, admin: User = Depends(check_is_admin)):
    # Prevent admin from deleting themselves (optional but safer)
    # Note: current_user.id is local DB ID, we'd need Clerk ID for this check
    
    headers = get_admin_headers()
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{CLERK_API_BASE}/users/{user_id}", headers=headers)
        
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to delete user from Clerk")
            
        return {"message": "User access revoked successfully"}

@router.post("/invitations/{invitation_id}/revoke")
async def revoke_invitation(invitation_id: str, admin: User = Depends(check_is_admin)):
    headers = get_admin_headers()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{CLERK_API_BASE}/invitations/{invitation_id}/revoke", headers=headers)
        
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to revoke invitation")
            
        return {"message": "Invitation revoked successfully"}
