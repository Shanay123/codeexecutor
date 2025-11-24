from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import get_current_user
from app.models import SubmissionCreate, SubmissionResponse
from typing import List
import uuid

router = APIRouter()


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionCreate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Submit a solution for review
    """
    try:
        # Verify user owns the problem and solution
        problem = supabase.table("problems").select("*").eq("id", submission.problem_id).eq("user_id", user.id).execute()
        solution = supabase.table("solutions").select("*").eq("id", submission.solution_id).eq("user_id", user.id).execute()
        
        if not problem.data or not solution.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid problem or solution"
            )
        
        submission_data = {
            "id": str(uuid.uuid4()),
            "problem_id": submission.problem_id,
            "solution_id": submission.solution_id,
            "user_id": user.id,
            "status": "pending",
            "test_results": submission.test_results
        }
        
        result = supabase.table("submissions").insert(submission_data).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my", response_model=List[SubmissionResponse])
async def get_my_submissions(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get all submissions by the current user
    """
    try:
        result = supabase.table("submissions").select(
            "*, problems(title), solutions(solution_code)"
        ).eq("user_id", user.id).order("submitted_at", desc=True).execute()
        
        # Format the response
        submissions = []
        for item in result.data:
            submission = {
                **item,
                "problem_title": item["problems"]["title"] if item.get("problems") else None,
                "solution_code": item["solutions"]["solution_code"] if item.get("solutions") else None
            }
            # Remove nested objects
            submission.pop("problems", None)
            submission.pop("solutions", None)
            submissions.append(submission)
        
        return submissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get a specific submission
    """
    try:
        result = supabase.table("submissions").select(
            "*, problems(title), solutions(solution_code)"
        ).eq("id", submission_id).eq("user_id", user.id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        item = result.data[0]
        submission = {
            **item,
            "problem_title": item["problems"]["title"] if item.get("problems") else None,
            "solution_code": item["solutions"]["solution_code"] if item.get("solutions") else None
        }
        submission.pop("problems", None)
        submission.pop("solutions", None)
        
        return submission
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

