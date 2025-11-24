from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase_client
from app.auth import require_admin
from app.models import SubmissionResponse, SubmissionReview, TestCaseUpdate, ExecuteResponse
from typing import List, Optional
from datetime import datetime
from app.executor import execute_code
from app.models import TestResult

router = APIRouter()


@router.get("/submissions", response_model=List[SubmissionResponse])
async def get_all_submissions(
    status_filter: Optional[str] = None,
    admin = Depends(require_admin),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get all submissions (admin only)
    """
    try:
        query = supabase.table("submissions").select(
            "*, problems(title, user_id), solutions(solution_code)"
        )
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        result = query.order("submitted_at", desc=True).execute()
        
        # Format the response
        submissions = []
        for item in result.data:
            submission = {
                **item,
                "problem_title": item["problems"]["title"] if item.get("problems") else None,
                "solution_code": item["solutions"]["solution_code"] if item.get("solutions") else None
            }
            submission.pop("problems", None)
            submission.pop("solutions", None)
            submissions.append(submission)
        
        return submissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission_detail(
    submission_id: str,
    admin = Depends(require_admin),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get detailed submission info (admin only)
    """
    try:
        result = supabase.table("submissions").select(
            "*, problems(title, description, example_input, example_output), solutions(solution_code)"
        ).eq("id", submission_id).execute()
        
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


@router.put("/submissions/{submission_id}", response_model=SubmissionResponse)
async def review_submission(
    submission_id: str,
    review: SubmissionReview,
    admin = Depends(require_admin),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Approve or reject a submission (admin only)
    """
    try:
        if review.status not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'approved' or 'rejected'"
            )
        
        update_data = {
            "status": review.status,
            "admin_notes": review.admin_notes,
            "reviewed_at": datetime.utcnow().isoformat(),
            "reviewed_by": admin.id
        }
        
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/test-cases/{test_case_id}")
async def update_test_case(
    test_case_id: str,
    test_case_update: TestCaseUpdate,
    admin = Depends(require_admin),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update a test case (admin only)
    """
    try:
        update_data = {
            "input_data": test_case_update.input_data,
            "expected_output": test_case_update.expected_output
        }
        
        result = supabase.table("test_cases").update(update_data).eq("id", test_case_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/rerun/{submission_id}", response_model=ExecuteResponse)
async def rerun_submission(
    submission_id: str,
    admin = Depends(require_admin),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Rerun a submission with current test cases (admin only)
    """
    try:
        # Get submission details including function signature
        submission = supabase.table("submissions").select(
            "*, solutions(solution_code), problems(id, function_signature)"
        ).eq("id", submission_id).execute()
        
        if not submission.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        submission_data = submission.data[0]
        solution_code = submission_data["solutions"]["solution_code"]
        problem_id = submission_data["problems"]["id"]
        function_signature = submission_data["problems"].get("function_signature")
        
        # Get current test cases
        test_cases = supabase.table("test_cases").select("*").eq("problem_id", problem_id).execute()
        
        if not test_cases.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No test cases found for this problem"
            )
        
        # Execute code against test cases
        results = []
        all_passed = True
        
        for test_case in test_cases.data:
            result = execute_code(
                code=solution_code,
                input_data=test_case["input_data"],
                expected_output=test_case["expected_output"],
                timeout=5,
                function_signature=function_signature
            )
            
            test_result = TestResult(
                test_case_id=test_case["id"],
                passed=result["passed"],
                actual_output=result.get("actual_output"),
                error=result.get("error"),
                execution_time=result.get("execution_time")
            )
            
            results.append(test_result)
            
            if not result["passed"]:
                all_passed = False
        
        # Update submission with new test results
        test_results_data = [r.dict() for r in results]
        supabase.table("submissions").update({
            "test_results": test_results_data
        }).eq("id", submission_id).execute()
        
        return ExecuteResponse(results=results, all_passed=all_passed)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rerun failed: {str(e)}"
        )

