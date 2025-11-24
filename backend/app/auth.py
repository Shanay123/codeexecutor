from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase_client
from supabase import Client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Verify the JWT token from Supabase and return the current user
    """
    try:
        token = credentials.credentials
        
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )


async def get_current_user_role(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get the user's role from the user_roles table
    """
    try:
        result = supabase.table("user_roles").select("role").eq("user_id", user.id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["role"]
        else:
            # Default role is 'user'
            return "user"
    except Exception:
        return "user"


async def require_admin(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Require that the current user is an admin
    """
    role = await get_current_user_role(user, supabase)
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

