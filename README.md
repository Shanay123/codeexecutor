# Code Execution Platform

A full-stack web application where users can create coding problems, write Python solutions, test them against defined test cases, and submit for admin review.

## 🚀 Live Demo

- **Frontend:** [Coming Soon - Deploy to Railway/Vercel]
- **Backend API:** [Coming Soon - Deploy to Railway]
- **Repository:** [Your GitHub Repository URL]

## 📋 Features

### For Users
- ✅ Create coding problems with descriptions and examples
- ✅ Write Python solutions using Monaco code editor
- ✅ Define custom test cases for validation
- ✅ Run code execution with real-time test results
- ✅ Submit solutions for review
- ✅ Track submission status (Pending, Approved, Rejected)
- ✅ View admin feedback on submissions

### For Admins
- ✅ View all user submissions
- ✅ Filter by status (Pending, Approved, Rejected)
- ✅ Review submitted code and test results
- ✅ Edit test cases for problems
- ✅ Rerun tests with updated test cases
- ✅ Approve or reject submissions with notes

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Supabase Auth
- **Code Execution:** subprocess with sandboxing

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** TailwindCSS
- **Code Editor:** Monaco Editor (VS Code engine)
- **Routing:** React Router v6
- **API Client:** Axios
- **Auth:** Supabase Client

### DevOps
- **Containerization:** Docker & Docker Compose
- **Deployment:** Railway (Backend & Frontend)
- **Version Control:** Git & GitHub

## 📦 Project Structure

```
aq-swe-take-home/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── auth.py         # Authentication middleware
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # Supabase client setup
│   │   ├── executor.py     # Code execution engine
│   │   ├── main.py         # FastAPI app entry point
│   │   └── models.py       # Pydantic models
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── config/         # API & Supabase config
│   │   ├── context/        # React context (Auth)
│   │   ├── pages/          # Page components
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── package.json
│   └── .env
├── database/               # Database setup
│   ├── schema.sql         # Tables & RLS policies
│   └── seed.sql           # Initial data
├── docker-compose.yml     # Local development setup
└── README.md              # This file
```

## 🔧 Environment Variables

### Backend (.env in /backend)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SECRET_KEY=your_secret_key_for_jwt
FRONTEND_URL=http://localhost:5173
PORT=8000
```

### Frontend (.env in /frontend)
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development without Docker)
- Python 3.11+ (for local development without Docker)
- Supabase account

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd aq-swe-take-home
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Project Settings → API to get your:
   - Project URL
   - Anon key
   - Service role key
3. Run the database schema:
   - Open SQL Editor in Supabase Dashboard
   - Copy contents of `database/schema.sql` and execute
4. Create an admin user (see instructions below)

### 3. Configure Environment Variables

Copy the example env files and fill in your credentials:

```bash
# Root directory
cp .env.example .env

# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your Supabase credentials
```

### 4. Run with Docker Compose (Recommended)

```bash
docker-compose up --build
```

This will start:
- Backend API at http://localhost:8000
- Frontend at http://localhost:5173

### 5. Run Locally Without Docker

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 👤 Creating an Admin User

1. Sign up a user through the application UI
2. Get the user's ID from Supabase:
   - Go to Authentication → Users in Supabase Dashboard
   - Copy the user's UUID
3. Run this SQL in Supabase SQL Editor:
   ```sql
   INSERT INTO user_roles (id, user_id, role)
   VALUES (uuid_generate_v4(), 'YOUR_USER_ID_HERE', 'admin')
   ON CONFLICT (user_id) DO UPDATE SET role = 'admin';
   ```
4. Log out and log back in to see admin features

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

#### Problems
- `POST /api/problems` - Create problem
- `GET /api/problems` - Get user's problems
- `GET /api/problems/{id}` - Get specific problem

#### Solutions
- `POST /api/solutions` - Create/update solution
- `GET /api/solutions/{problem_id}` - Get solution for problem

#### Test Cases
- `POST /api/test-cases` - Create test case
- `GET /api/test-cases/{problem_id}` - Get test cases
- `DELETE /api/test-cases/{id}` - Delete test case

#### Execution
- `POST /api/execute` - Run code against test cases

#### Submissions
- `POST /api/submissions` - Submit for review
- `GET /api/submissions/my` - Get user's submissions

#### Admin
- `GET /api/admin/submissions` - Get all submissions
- `GET /api/admin/submissions/{id}` - Get submission details
- `PUT /api/admin/submissions/{id}` - Approve/reject submission
- `PUT /api/admin/test-cases/{id}` - Update test case
- `POST /api/admin/rerun/{submission_id}` - Rerun tests

## 🚢 Deployment

### Deploy Backend to Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add a new service → Deploy from GitHub repo
4. Configure environment variables in Railway dashboard
5. Railway will automatically detect the Dockerfile and deploy

### Deploy Frontend to Railway/Vercel

#### Option 1: Railway
1. Add another service to your Railway project
2. Select the same repository
3. Set root directory to `/frontend`
4. Add environment variables
5. Deploy

#### Option 2: Vercel
1. Import project from GitHub
2. Set root directory to `frontend`
3. Add environment variables
4. Deploy

### Production Environment Variables

Make sure to update:
- `FRONTEND_URL` in backend to your deployed frontend URL
- `VITE_API_URL` in frontend to your deployed backend URL
- Use strong `SECRET_KEY` in production

## 🧪 Testing the Application

### User Flow
1. **Sign up** at `/signup`
2. **Create a problem** - define function signature (e.g., `def two_sum(nums: list[int], target: int) -> list[int]:`)
3. **Add test cases** - JSON arrays as inputs (e.g., `[[2,7,11], 9]`)
4. **Write solution** - implement the exact function signature
5. **Run tests** - function is called with typed arguments
6. **Submit for review** when all tests pass
7. **Check submissions** page for status

### LeetCode-Style Testing Format

**Create Problem:**
- Define exact function signature users must implement
- Test inputs are JSON arrays of arguments
- Expected outputs are JSON-encoded return values

**Example - Two Sum Problem:**

```python
# Function Signature (defined by problem creator):
def two_sum(nums: list[int], target: int) -> list[int]:
```

**Test Cases:**
- Input: `[[2, 7, 11, 15], 9]` → Output: `[0, 1]`
- Input: `[[3, 2, 4], 6]` → Output: `[1, 2]`

**User Solution:**
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

**More Examples:**

```python
# Simple function
def add(a: int, b: int) -> int:
    return a + b
# Test: Input=[2, 3], Output=5

# String manipulation
def reverse(s: str) -> str:
    return s[::-1]
# Test: Input=["hello"], Output="olleh"

# Complex types
def find_max(matrix: list[list[int]]) -> int:
    return max(max(row) for row in matrix)
# Test: Input=[[[1,2],[3,4]]], Output=4
```

### Admin Flow
1. Log in with admin account
2. Go to **Admin Dashboard**
3. Filter submissions by status
4. Click **Review** on a submission
5. View code, test results
6. Edit test cases if needed
7. Rerun tests
8. Approve or reject with notes

## 🐛 Troubleshooting

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build

# View logs
docker-compose logs backend
docker-compose logs frontend
```

### Backend Issues
- Ensure Python 3.11+ is installed
- Check Supabase credentials are correct
- Verify database tables are created

### Frontend Issues
- Clear browser cache
- Check console for errors
- Verify API URL is correct

## 🔒 Security Notes

- Code execution is isolated using subprocess with timeouts
- Row Level Security (RLS) is enabled on all tables
- Authentication uses Supabase JWT tokens
- Admin operations require admin role verification
- Never commit .env files to version control

## 📝 Database Schema

The application uses the following tables:
- `problems` - Coding problem definitions
- `solutions` - User solutions to problems
- `test_cases` - Test cases for validation
- `submissions` - Submitted solutions for review
- `user_roles` - User role assignments (user/admin)

All tables have Row Level Security (RLS) policies to ensure users can only access their own data, while admins have broader access for review purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is created for the AQ take-home assignment.

## 🙋 Support

For questions or issues:
- Open an issue on GitHub
- Contact: [Your Email]

## 🎯 Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Real-time collaboration
- [ ] Problem difficulty ratings
- [ ] User leaderboards
- [ ] Code plagiarism detection
- [ ] Integration with GitHub
- [ ] Email notifications for submission status
- [ ] Detailed analytics dashboard

---

Built with ❤️ using FastAPI, React, and Supabase
