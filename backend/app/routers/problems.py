from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import get_current_user
from app.models import ProblemCreate, ProblemResponse
from typing import List
import uuid

router = APIRouter()


@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem: ProblemCreate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a new coding problem
    """
    try:
        problem_data = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "title": problem.title,
            "description": problem.description,
            "example_input": problem.example_input,
            "example_output": problem.example_output,
            "function_signature": problem.function_signature
        }
        
        result = supabase.table("problems").insert(problem_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create problem"
            )
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ProblemResponse])
async def get_problems(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get all problems created by the current user
    """
    try:
        result = supabase.table("problems").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get a specific problem
    """
    try:
        result = supabase.table("problems").select("*").eq("id", problem_id).eq("user_id", user.id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

