from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import get_current_user
from app.models import SolutionCreate, SolutionUpdate, SolutionResponse
import uuid
from datetime import datetime

router = APIRouter()


@router.post("", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
async def create_solution(
    solution: SolutionCreate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create or update a solution for a problem
    """
    try:
        # Check if solution already exists for this problem and user
        existing = supabase.table("solutions").select("*").eq("problem_id", solution.problem_id).eq("user_id", user.id).execute()
        
        if existing.data:
            # Update existing solution
            updated_data = {
                "solution_code": solution.solution_code,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = supabase.table("solutions").update(updated_data).eq("id", existing.data[0]["id"]).execute()
            return result.data[0]
        else:
            # Create new solution
            solution_data = {
                "id": str(uuid.uuid4()),
                "problem_id": solution.problem_id,
                "user_id": user.id,
                "solution_code": solution.solution_code
            }
            result = supabase.table("solutions").insert(solution_data).execute()
            return result.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{problem_id}", response_model=SolutionResponse)
async def get_solution(
    problem_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get solution for a specific problem
    """
    try:
        result = supabase.table("solutions").select("*").eq("problem_id", problem_id).eq("user_id", user.id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

