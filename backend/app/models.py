from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Auth models
class SignupRequest(BaseModel):
    email: str
    password: str
    username: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: Optional[str] = "user"


# Problem models
class ProblemCreate(BaseModel):
    title: str
    description: str
    example_input: str
    example_output: str
    function_signature: str


class ProblemResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    example_input: str
    example_output: str
    function_signature: str
    created_at: str


# Solution models
class SolutionCreate(BaseModel):
    problem_id: str
    solution_code: str


class SolutionUpdate(BaseModel):
    solution_code: str


class SolutionResponse(BaseModel):
    id: str
    problem_id: str
    user_id: str
    solution_code: str
    created_at: str
    updated_at: str


# Test case models
class TestCaseCreate(BaseModel):
    problem_id: str
    input_data: str
    expected_output: str


class TestCaseUpdate(BaseModel):
    input_data: str
    expected_output: str


class TestCaseResponse(BaseModel):
    id: str
    problem_id: str
    input_data: str
    expected_output: str
    created_at: str


# Execution models
class TestResult(BaseModel):
    test_case_id: str
    passed: bool
    actual_output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ExecuteRequest(BaseModel):
    solution_code: str
    test_cases: List[TestCaseResponse]


class ExecuteResponse(BaseModel):
    results: List[TestResult]
    all_passed: bool


# Submission models
class SubmissionCreate(BaseModel):
    problem_id: str
    solution_id: str
    test_results: List[dict]


class SubmissionReview(BaseModel):
    status: str  # 'approved' or 'rejected'
    admin_notes: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: str
    problem_id: str
    solution_id: str
    user_id: str
    status: str
    test_results: List[dict]
    admin_notes: Optional[str] = None
    submitted_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    problem_title: Optional[str] = None
    solution_code: Optional[str] = None

