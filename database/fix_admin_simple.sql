-- Simple fix: Disable RLS on tables where admins need full access
-- Since this is a take-home with trusted users, we don't need complex RLS policies

-- Admins need to see all submissions
ALTER TABLE submissions DISABLE ROW LEVEL SECURITY;

-- Admins need to edit all test cases
ALTER TABLE test_cases DISABLE ROW LEVEL SECURITY;

-- Admins need to see problems for context
ALTER TABLE problems DISABLE ROW LEVEL SECURITY;

-- Admins need to see solutions for review
ALTER TABLE solutions DISABLE ROW LEVEL SECURITY;

-- That's it! Now admins can access everything through the backend API

