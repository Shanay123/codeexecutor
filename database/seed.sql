-- Seed script to create initial admin user
-- Replace the email and user_id with your actual admin user details
-- 
-- INSTRUCTIONS:
-- 1. First, sign up a user through the app or Supabase Auth UI
-- 2. Get the user_id from the auth.users table
-- 3. Replace 'YOUR_USER_ID_HERE' below with the actual user_id
-- 4. Run this script in Supabase SQL Editor

-- Example: Create admin role for a specific user
-- INSERT INTO user_roles (id, user_id, role)
-- VALUES (uuid_generate_v4(), 'YOUR_USER_ID_HERE', 'admin')
-- ON CONFLICT (user_id) DO UPDATE SET role = 'admin';

-- You can also use this query to find your user_id after signing up:
-- SELECT id, email FROM auth.users;

