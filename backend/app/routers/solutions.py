from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import get_current_user
from app.models import SolutionCreate, SolutionResponse
import uuid
from datetime import datetime

router = APIRouter()


@router.post("", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
async def create_solution(
    solution: SolutionCreate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    existing = supabase.table("solutions").select("*").eq("problem_id", solution.problem_id).eq("user_id", user.id).execute()
    
    # Get problem to inherit language if not specified
    problem = supabase.table("problems").select("language").eq("id", solution.problem_id).execute()
    language = solution.language if solution.language else (problem.data[0].get("language", "python") if problem.data else "python")
    
    if existing.data:
        updated_data = {
            "solution_code": solution.solution_code,
            "language": language,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("solutions").update(updated_data).eq("id", existing.data[0]["id"]).execute()
        return result.data[0]
    
    solution_data = {
        "id": str(uuid.uuid4()),
        "problem_id": solution.problem_id,
        "user_id": user.id,
        "solution_code": solution.solution_code,
        "language": language
    }
    result = supabase.table("solutions").insert(solution_data).execute()
    return result.data[0]


@router.get("/{problem_id}", response_model=SolutionResponse)
async def get_solution(
    problem_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    result = supabase.table("solutions").select("*").eq("problem_id", problem_id).eq("user_id", user.id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    
    return result.data[0]
