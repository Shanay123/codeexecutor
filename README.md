# Code Execution Platform

A full-stack web application for creating and solving coding problems with automated test validation and admin review system.

## Features

- Create coding problems with function signatures
- Write and test Python solutions with Monaco code editor
- LeetCode-style typed function testing with JSON inputs
- Automated test case validation
- Submission and review workflow
- Admin dashboard for reviewing submissions

## Tech Stack

### Backend
- FastAPI (Python 3.11)
- Supabase (PostgreSQL + Auth)
- Python subprocess execution with timeout handling

### Frontend
- React 18 with Vite
- TailwindCSS
- Monaco Editor
- React Router v6
- Axios

### DevOps
- Docker & Docker Compose
- Railway deployment

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── auth.py         # Authentication middleware
│   │   ├── config.py       # Settings
│   │   ├── database.py     # Supabase client
│   │   ├── executor.py     # Code execution engine
│   │   ├── main.py         # FastAPI app
│   │   └── models.py       # Pydantic models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── config/
│   │   ├── context/
│   │   └── pages/
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Environment Variables

### Backend
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:5173
PORT=8000
```

### Frontend
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

## Getting Started

### Prerequisites
- Docker Desktop
- Supabase account

### Setup

1. Clone repository
2. Run database migration in Supabase SQL Editor (see `database/` folder)
3. Configure environment variables
4. Start with Docker:
```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing Format

Problems use LeetCode-style function signatures with typed arguments:

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

Test cases use JSON format:
- Input: `[[2,7,11,15], 9]`
- Expected Output: `[0, 1]`

## Deployment

### Backend (Railway)
1. Push code to GitHub
2. Create new Railway project from GitHub
3. Set root directory to `backend`
4. Add environment variables
5. Deploy

### Frontend (Vercel)
1. Import GitHub repository
2. Set framework to Vite
3. Set root directory to `frontend`
4. Add environment variables
5. Deploy

Update backend `FRONTEND_URL` with deployed frontend URL.

## Creating Admin Users

1. Sign up through the application
2. Get user ID from Supabase Dashboard
3. Run in Supabase SQL Editor:
```sql
INSERT INTO user_roles (id, user_id, role)
VALUES (uuid_generate_v4(), 'USER_ID_HERE', 'admin');
```

## API Endpoints

### Authentication
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Problems
- `POST /api/problems`
- `GET /api/problems`
- `GET /api/problems/{id}`

### Solutions
- `POST /api/solutions`
- `GET /api/solutions/{problem_id}`

### Test Cases
- `POST /api/test-cases`
- `GET /api/test-cases/{problem_id}`
- `DELETE /api/test-cases/{id}`

### Execution
- `POST /api/execute`

### Submissions
- `POST /api/submissions`
- `GET /api/submissions/my`

### Admin
- `GET /api/admin/submissions`
- `GET /api/admin/submissions/{id}`
- `PUT /api/admin/submissions/{id}`
- `PUT /api/admin/test-cases/{id}`
- `POST /api/admin/rerun/{submission_id}`

## License

MIT
