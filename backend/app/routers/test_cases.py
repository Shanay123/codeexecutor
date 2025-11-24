from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import get_current_user, get_current_user_role
from app.models import TestCaseCreate, TestCaseResponse
from typing import List
import uuid

router = APIRouter()


@router.post("", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a new test case for a problem
    """
    try:
        # Check if user is admin
        role = await get_current_user_role(user, supabase)
        
        # Verify user owns the problem (admins can skip this check)
        if role != "admin":
            problem = supabase.table("problems").select("*").eq("id", test_case.problem_id).eq("user_id", user.id).execute()
            
            if not problem.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to add test cases to this problem"
                )
        
        test_case_data = {
            "id": str(uuid.uuid4()),
            "problem_id": test_case.problem_id,
            "input_data": test_case.input_data,
            "expected_output": test_case.expected_output
        }
        
        result = supabase.table("test_cases").insert(test_case_data).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{problem_id}", response_model=List[TestCaseResponse])
async def get_test_cases(
    problem_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get all test cases for a problem
    """
    try:
        # Check if user is admin
        role = await get_current_user_role(user, supabase)
        
        # Verify user owns the problem (admins can access any problem)
        if role != "admin":
            problem = supabase.table("problems").select("*").eq("id", problem_id).eq("user_id", user.id).execute()
            
            if not problem.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view test cases for this problem"
                )
        
        result = supabase.table("test_cases").select("*").eq("problem_id", problem_id).order("created_at").execute()
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{test_case_id}")
async def delete_test_case(
    test_case_id: str,
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a test case
    """
    try:
        # Get test case to verify ownership through problem
        test_case = supabase.table("test_cases").select("*, problems(user_id)").eq("id", test_case_id).execute()
        
        if not test_case.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        # Verify ownership
        if test_case.data[0]["problems"]["user_id"] != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this test case"
            )
        
        supabase.table("test_cases").delete().eq("id", test_case_id).execute()
        return {"message": "Test case deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

