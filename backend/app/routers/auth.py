from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.models import SignupRequest, LoginRequest, UserResponse
import uuid

router = APIRouter()


@router.post("/signup", response_model=dict)
async def signup(
    request: SignupRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Register a new user
    """
    try:
        # Sign up with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Create user role entry (default: user)
        user_id = auth_response.user.id
        supabase.table("user_roles").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "role": "user"
        }).execute()
        
        return {
            "user": {
                "id": user_id,
                "email": auth_response.user.email,
                "role": "user"
            },
            "session": {
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "refresh_token": auth_response.session.refresh_token if auth_response.session else None
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=dict)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Login user
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Get user role
        role_result = supabase.table("user_roles").select("role").eq("user_id", auth_response.user.id).execute()
        role = role_result.data[0]["role"] if role_result.data else "user"
        
        return {
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": role
            },
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(supabase: Client = Depends(get_supabase_client)):
    """
    Logout user
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

