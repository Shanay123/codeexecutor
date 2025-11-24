from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.models import ExecuteRequest, ExecuteResponse, TestResult
from app.executor import execute_code
from typing import List, Optional

router = APIRouter()


@router.post("", response_model=ExecuteResponse)
async def execute_solution(
    request: ExecuteRequest,
    function_signature: Optional[str] = None,
    user = Depends(get_current_user)
):
    """
    Execute Python code against test cases
    """
    try:
        results: List[TestResult] = []
        all_passed = True
        
        for test_case in request.test_cases:
            result = execute_code(
                code=request.solution_code,
                input_data=test_case.input_data,
                expected_output=test_case.expected_output,
                timeout=5,
                function_signature=function_signature
            )
            
            test_result = TestResult(
                test_case_id=test_case.id,
                passed=result["passed"],
                actual_output=result.get("actual_output"),
                error=result.get("error"),
                execution_time=result.get("execution_time")
            )
            
            results.append(test_result)
            
            if not result["passed"]:
                all_passed = False
        
        return ExecuteResponse(results=results, all_passed=all_passed)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )

