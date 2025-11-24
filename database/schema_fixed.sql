-- Fixed Schema - Run this to fix the infinite recursion issue
-- First, let's drop the problematic policies and recreate them correctly

-- Drop existing user_roles policies
DROP POLICY IF EXISTS "Users can view their own role" ON user_roles;
DROP POLICY IF EXISTS "Admins can view all roles" ON user_roles;
DROP POLICY IF EXISTS "Service role can manage roles" ON user_roles;

-- Recreate user_roles policies WITHOUT recursion
-- Users can always view their own role (no recursion)
CREATE POLICY "Users can view their own role"
    ON user_roles FOR SELECT
    USING (auth.uid() = user_id);

-- Only allow inserts/updates/deletes when bypassing RLS (service role from backend)
-- This prevents the recursion issue
CREATE POLICY "Allow service role to manage roles"
    ON user_roles FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Now fix the problematic policies that check admin status
-- Drop the existing admin policies that cause recursion
DROP POLICY IF EXISTS "Admins can view all test cases" ON test_cases;
DROP POLICY IF EXISTS "Admins can update all test cases" ON test_cases;
DROP POLICY IF EXISTS "Admins can view all submissions" ON submissions;
DROP POLICY IF EXISTS "Admins can update all submissions" ON submissions;

-- We'll handle admin checks in the backend code instead of RLS
-- This is cleaner and avoids recursion
-- The backend already has the require_admin middleware that does this check

-- For test_cases, keep user access but remove admin policies (backend handles this)
-- For submissions, keep user access but remove admin policies (backend handles this)

-- That's it! The backend code with require_admin middleware will handle admin checks
-- This way we avoid the RLS recursion issue entirely

