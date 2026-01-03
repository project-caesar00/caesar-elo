"""
Authentication module for Caesar ELO.
Handles Google OAuth and JWT session management.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleTokenRequest(BaseModel):
    """Request with Google OAuth credential."""
    credential: str  # Google ID token


class UserInfo(BaseModel):
    """User info from Google."""
    email: str
    name: str
    picture: Optional[str] = None


class AuthResponse(BaseModel):
    """Auth response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


async def verify_google_token(credential: str) -> Optional[dict]:
    """Verify Google ID token and return user info."""
    try:
        # Verify with Google's tokeninfo endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": credential}
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Verify the token is for our app
            if data.get("aud") != settings.google_client_id:
                return None
            
            return {
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture"),
            }
    except Exception:
        return None


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """Get current user from JWT token. Returns None if not authenticated."""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        email = payload.get("email")
        if email is None:
            return None
        return payload
    except JWTError:
        return None


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Require authentication. Raises 401 if not authenticated."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleTokenRequest):
    """
    Authenticate with Google OAuth.
    Accepts the Google ID token (credential) from Google Sign-In.
    Returns a JWT access token for subsequent API calls.
    """
    user_info = await verify_google_token(request.credential)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Create JWT token
    access_token = create_access_token({
        "email": user_info["email"],
        "name": user_info["name"],
    })
    
    return AuthResponse(
        access_token=access_token,
        user=UserInfo(**user_info)
    )


@router.get("/me", response_model=UserInfo)
async def get_me(user: dict = Depends(require_auth)):
    """Get current authenticated user info."""
    return UserInfo(
        email=user.get("email", ""),
        name=user.get("name", ""),
    )
