from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase_client
from supabase import Client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return user.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )


async def get_current_user_role(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        result = supabase.table("user_roles").select("role").eq("user_id", user.id).execute()
        return result.data[0]["role"] if result.data else "user"
    except Exception:
        return "user"


async def require_admin(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    role = await get_current_user_role(user, supabase)
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user
