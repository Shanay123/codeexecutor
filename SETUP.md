# Quick Setup Guide

Get the Code Execution Platform running locally in 5 minutes!

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- Supabase account (sign up at [supabase.com](https://supabase.com))

## Step-by-Step Setup

### 1. Get Supabase Credentials

1. Go to [supabase.com](https://supabase.com) and sign in
2. Create a new project (or use existing)
3. Go to **Project Settings** → **API**
4. Copy these values:
   - Project URL
   - anon/public key
   - service_role key (click "Reveal" to see it)

### 2. Set Up Database

1. In your Supabase project, go to **SQL Editor**
2. Open the file `database/schema.sql` from this project
3. Copy all the SQL content
4. Paste into Supabase SQL Editor and click **Run**
5. Verify tables were created in **Table Editor**

### 3. Configure Environment Variables

Edit the `.env` file in the project root:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
SECRET_KEY=supersecretkey_change_in_production_12345
```

Edit `backend/.env`:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
SECRET_KEY=supersecretkey_change_in_production_12345
FRONTEND_URL=http://localhost:5173
PORT=8000
```

Edit `frontend/.env`:
```env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
VITE_API_URL=http://localhost:8000
```

### 4. Start the Application

Open a terminal in the project root and run:

```bash
docker-compose up --build
```

Wait for both services to start. You'll see:
```
backend_1   | INFO:     Application startup complete.
frontend_1  | VITE v5.x.x  ready in xxx ms
```

### 5. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## First Time Use

### Create Your Account

1. Go to http://localhost:5173
2. Click "Sign Up"
3. Enter email and password
4. You're logged in!

### Create an Admin User (Optional)

To access admin features:

1. Sign up through the app
2. Go to Supabase Dashboard → **Authentication** → **Users**
3. Copy your user ID
4. Go to **SQL Editor** and run:

```sql
INSERT INTO user_roles (id, user_id, role)
VALUES (uuid_generate_v4(), 'YOUR_USER_ID_HERE', 'admin');
```

5. Log out and log back in
6. You'll see "Admin" in the navigation!

### Try It Out

1. **Create a Problem:**
   - Click "Create New Problem"
   - Title: "Add Two Numbers"
   - Description: "Write a function that adds two numbers"
   - Example Input: `2 3`
   - Example Output: `5`

2. **Write a Solution:**
   - Click on your problem
   - Write Python code:
   ```python
   a, b = map(int, input().split())
   print(a + b)
   ```

3. **Add Test Cases:**
   - Input: `2 3`, Output: `5`
   - Input: `10 20`, Output: `30`
   - Click "Add Test Case"

4. **Run Tests:**
   - Click "Run Tests"
   - See results!

5. **Submit for Review:**
   - When all tests pass, click "Submit for Review"
   - Check "Submissions" page to see status

## Stopping the Application

Press `Ctrl+C` in the terminal, then run:

```bash
docker-compose down
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 5173 are busy:

```bash
# Check what's using the port
lsof -i :8000
lsof -i :5173

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Error

- Verify Supabase credentials are correct
- Check if schema.sql was executed
- Make sure Supabase project is active

### Can't Access Frontend

- Try http://127.0.0.1:5173 instead of localhost
- Check Docker logs: `docker-compose logs frontend`
- Clear browser cache

### Code Execution Fails

- Ensure Python 3 is available in the backend container
- Check backend logs: `docker-compose logs backend`
- Verify solution code syntax

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the API at http://localhost:8000/docs
- Create more problems and test solutions!

## Need Help?

- Check backend logs: `docker-compose logs backend`
- Check frontend logs: `docker-compose logs frontend`
- Restart everything: `docker-compose restart`
- Clean rebuild: `docker-compose down -v && docker-compose up --build`

---

Happy coding! 🚀

