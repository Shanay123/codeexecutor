from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, problems, solutions, test_cases, execute, submissions, admin

app = FastAPI(title="Code Execution Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(solutions.router, prefix="/api/solutions", tags=["solutions"])
app.include_router(test_cases.router, prefix="/api/test-cases", tags=["test-cases"])
app.include_router(execute.router, prefix="/api/execute", tags=["execute"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Code Execution Platform API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

