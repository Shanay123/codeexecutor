# Deployment Guide

This guide will walk you through deploying the Code Execution Platform to production.

## Prerequisites

- Supabase project (already configured)
- Railway account (or alternative hosting platform)
- GitHub repository

## Step 1: Database Setup

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the schema from `database/schema.sql`
4. Verify all tables are created in the Table Editor

## Step 2: Create Admin User

1. Sign up through your application
2. Get your user ID from Supabase Dashboard → Authentication → Users
3. Run this SQL in Supabase SQL Editor:
   ```sql
   INSERT INTO user_roles (id, user_id, role)
   VALUES (uuid_generate_v4(), 'YOUR_USER_ID_HERE', 'admin')
   ON CONFLICT (user_id) DO UPDATE SET role = 'admin';
   ```

## Step 3: Deploy Backend to Railway

### Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add environment variables
railway variables set SUPABASE_URL="your_url"
railway variables set SUPABASE_ANON_KEY="your_key"
railway variables set SUPABASE_SERVICE_KEY="your_service_key"
railway variables set SECRET_KEY="your_secret"
railway variables set FRONTEND_URL="https://your-frontend.vercel.app"

# Deploy
railway up
```

### Using Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will detect the Dockerfile
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `SECRET_KEY`
   - `FRONTEND_URL`
   - `PORT` (Railway sets this automatically)
6. Deploy!

Your backend will be available at: `https://your-project.railway.app`

## Step 4: Deploy Frontend to Vercel

### Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel

# Add environment variables when prompted:
# VITE_SUPABASE_URL
# VITE_SUPABASE_ANON_KEY
# VITE_API_URL (your Railway backend URL)
```

### Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add environment variables:
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
   - `VITE_API_URL`: Your Railway backend URL (e.g., https://your-project.railway.app)
6. Deploy!

Your frontend will be available at: `https://your-project.vercel.app`

## Step 5: Update CORS Settings

After deploying, update the backend's CORS settings:

1. Go to Railway dashboard
2. Update `FRONTEND_URL` environment variable to your Vercel URL
3. Redeploy the backend

Or update in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        # ... other origins
    ],
    # ... rest of config
)
```

## Step 6: Test Production Deployment

1. Visit your frontend URL
2. Sign up for an account
3. Create a problem
4. Write and test a solution
5. Submit for review
6. Test admin features (if you have admin role)

## Alternative: Deploy Both on Railway

You can deploy both frontend and backend on Railway:

### Backend Service
- Use the existing Dockerfile
- Set environment variables
- Domain: `your-backend.railway.app`

### Frontend Service
- Create a new service in the same project
- Use `frontend/Dockerfile`
- Set environment variables:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_API_URL` (point to backend service)
- Domain: `your-frontend.railway.app`

## Monitoring and Maintenance

### Check Logs

**Railway:**
- View logs in Railway dashboard
- Or use CLI: `railway logs`

**Vercel:**
- View logs in Vercel dashboard
- Or use CLI: `vercel logs`

### Database Backups

Supabase automatically backs up your database. You can also:
1. Go to Database → Backups in Supabase
2. Download manual backups as needed

### Update Deployment

**Railway:**
- Push to GitHub → Railway auto-deploys
- Or use: `railway up`

**Vercel:**
- Push to GitHub → Vercel auto-deploys
- Or use: `vercel --prod`

## Troubleshooting

### Backend Issues

**500 Internal Server Error:**
- Check Railway logs
- Verify environment variables
- Test Supabase connection

**CORS Errors:**
- Ensure `FRONTEND_URL` is set correctly
- Check CORS middleware configuration

### Frontend Issues

**Can't connect to API:**
- Verify `VITE_API_URL` is correct
- Check if backend is running
- Test API health endpoint: `https://your-backend.railway.app/health`

**Authentication fails:**
- Check Supabase configuration
- Verify anon key is correct
- Check browser console for errors

### Database Issues

**RLS Policy Errors:**
- Verify schema.sql was executed correctly
- Check user roles are set properly
- Review RLS policies in Supabase

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Verify RLS policies are enabled
- [ ] Test that users can only access their own data
- [ ] Test admin permissions
- [ ] Enable Supabase database backups
- [ ] Set up monitoring/alerting
- [ ] Review CORS origins
- [ ] Test code execution sandbox

## Performance Tips

1. **Enable caching on Vercel/Cloudflare**
2. **Use Supabase connection pooling**
3. **Monitor API response times**
4. **Optimize database queries with indexes**
5. **Consider CDN for static assets**

## Scaling Considerations

As your platform grows:
- Monitor Railway usage and upgrade plan if needed
- Consider Redis for caching
- Implement rate limiting
- Add database read replicas
- Use background jobs for long-running tasks

---

Your Code Execution Platform is now live! 🎉

