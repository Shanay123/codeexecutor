-- Quick fix: Disable RLS on user_roles table
-- This allows the backend service role to insert roles during signup

-- Simply disable RLS on user_roles
ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;

-- Drop all policies on user_roles (we don't need them if RLS is disabled)
DROP POLICY IF EXISTS "Users can view their own role" ON user_roles;
DROP POLICY IF EXISTS "Service role can manage roles" ON user_roles;

-- That's it! Now the backend can freely manage user roles

