"""
MandiSense Firebase / Supabase Authentication Service
======================================================
Provides server-side verification of authentication tokens (JWT)
for both Firebase and Supabase systems.
"""

import os
from typing import Optional, Dict, Any
from app.utils.http_client import get_async_client

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("VITE_SUPABASE_ANON_KEY", "")
FIREBASE_API_KEY = os.getenv("VITE_FIREBASE_API_KEY", "")
FIREBASE_PROJECT_ID = os.getenv("VITE_FIREBASE_PROJECT_ID", "")

class AuthServiceError(Exception):
    """Custom exception class for auth service issues."""
    def __init__(self, message: str, status_code: int = 401, error_type: str = "AUTH_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type

async def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verifies a Supabase JWT token by calling Supabase's GoTrue Auth server.
    """
    sb_url = os.getenv("VITE_SUPABASE_URL", "") or SUPABASE_URL
    sb_key = os.getenv("VITE_SUPABASE_ANON_KEY", "") or SUPABASE_ANON_KEY
    
    if not sb_url or "your-project" in sb_url:
        raise AuthServiceError("Supabase URL is not configured on the server.", 500, "CONFIG_ERROR")
        
    client = get_async_client()
    url = f"{sb_url}/auth/v1/user"
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        res = await client.get(url, headers=headers)
        if res.status_code == 401:
            raise AuthServiceError("Invalid Supabase authorization token.", 401, "INVALID_TOKEN")
        elif res.status_code != 200:
            raise AuthServiceError(f"Supabase auth server returned status {res.status_code}", 503, "AUTH_SERVER_FAILURE")
            
        return res.json() # Returns user profile data
    except httpx.RequestError as exc:
        raise AuthServiceError(f"Network error verifying Supabase token: {exc}", 503, "NETWORK_FAILURE")
    except Exception as e:
        if isinstance(e, AuthServiceError):
            raise e
        raise AuthServiceError(f"Unexpected authentication error: {str(e)}", 500, "GENERIC_ERROR")

async def verify_firebase_token(token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token by calling Firebase Identity Toolkit lookup.
    """
    fb_key = os.getenv("VITE_FIREBASE_API_KEY", "") or FIREBASE_API_KEY
    if not fb_key or "your-firebase" in fb_key:
        raise AuthServiceError("Firebase API Key is not configured on the server.", 500, "CONFIG_ERROR")
        
    client = get_async_client()
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={fb_key}"
    payload = {"idToken": token}
    
    try:
        res = await client.post(url, json=payload)
        if res.status_code == 400:
            # Bad Request usually means expired/invalid token
            err_data = res.json()
            err_message = err_data.get("error", {}).get("message", "INVALID_ID_TOKEN")
            raise AuthServiceError(f"Firebase token verification failed: {err_message}", 401, "INVALID_TOKEN")
        elif res.status_code != 200:
            raise AuthServiceError(f"Firebase auth server returned status {res.status_code}", 503, "AUTH_SERVER_FAILURE")
            
        users = res.json().get("users", [])
        if not users:
            raise AuthServiceError("No user profile found for Firebase token.", 401, "USER_NOT_FOUND")
            
        return users[0]
    except httpx.RequestError as exc:
        raise AuthServiceError(f"Network error verifying Firebase token: {exc}", 503, "NETWORK_FAILURE")
    except Exception as e:
        if isinstance(e, AuthServiceError):
            raise e
        raise AuthServiceError(f"Unexpected authentication error: {str(e)}", 500, "GENERIC_ERROR")

import httpx

async def get_authenticated_user(authorization_header: Optional[str]) -> Dict[str, Any]:
    """
    Middleware dependency parser. Resolves authorization headers.
    Falls back to a default mock vendor profile if authentication is not configured in settings.
    """
    # Check if either service is configured
    sb_url = os.getenv("VITE_SUPABASE_URL", "")
    fb_key = os.getenv("VITE_FIREBASE_API_KEY", "")
    
    has_supabase = sb_url and "your-project" not in sb_url
    has_firebase = fb_key and "your-firebase" not in fb_key
    
    # Define fallback mock user
    mock_user = {
        "uid": "mock_vendor_777",
        "email": "vendor@mandisense.in",
        "name": "MandiSense Partner",
        "role": "vendor",
        "is_mock": True
    }
    
    if not has_supabase and not has_firebase:
        return mock_user
        
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthServiceError("Missing or invalid Authorization header scheme.", 401, "MISSING_HEADER")
        
    token = authorization_header.split(" ")[1]
    
    if has_supabase:
        try:
            user_data = await verify_supabase_token(token)
            return {
                "uid": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("user_metadata", {}).get("full_name", "Supabase Vendor"),
                "role": "vendor",
                "is_mock": False
            }
        except AuthServiceError as e:
            raise e
            
    if has_firebase:
        try:
            user_data = await verify_firebase_token(token)
            return {
                "uid": user_data.get("localId"),
                "email": user_data.get("email"),
                "name": user_data.get("displayName", "Firebase Vendor"),
                "role": "vendor",
                "is_mock": False
            }
        except AuthServiceError as e:
            raise e
            
    return mock_user
