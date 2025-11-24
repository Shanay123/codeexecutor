-- Create tables for the Code Execution Platform
-- Run this script in your Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create problems table
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    example_input TEXT NOT NULL,
    example_output TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create solutions table
CREATE TABLE IF NOT EXISTS solutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    solution_code TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create test_cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    solution_id UUID NOT NULL REFERENCES solutions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    test_results JSONB NOT NULL,
    admin_notes TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES auth.users(id)
);

-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
    UNIQUE(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_problems_user_id ON problems(user_id);
CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions(problem_id);
CREATE INDEX IF NOT EXISTS idx_solutions_user_id ON solutions(user_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_problem_id ON test_cases(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE solutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for problems
CREATE POLICY "Users can view their own problems"
    ON problems FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own problems"
    ON problems FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own problems"
    ON problems FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own problems"
    ON problems FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for solutions
CREATE POLICY "Users can view their own solutions"
    ON solutions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own solutions"
    ON solutions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own solutions"
    ON solutions FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own solutions"
    ON solutions FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for test_cases
-- Users can only access test cases for their own problems
CREATE POLICY "Users can view test cases for their problems"
    ON test_cases FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM problems
            WHERE problems.id = test_cases.problem_id
            AND problems.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create test cases for their problems"
    ON test_cases FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM problems
            WHERE problems.id = test_cases.problem_id
            AND problems.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update test cases for their problems"
    ON test_cases FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM problems
            WHERE problems.id = test_cases.problem_id
            AND problems.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete test cases for their problems"
    ON test_cases FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM problems
            WHERE problems.id = test_cases.problem_id
            AND problems.user_id = auth.uid()
        )
    );

-- Admins can view and modify all test cases
CREATE POLICY "Admins can view all test cases"
    ON test_cases FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_roles.user_id = auth.uid()
            AND user_roles.role = 'admin'
        )
    );

CREATE POLICY "Admins can update all test cases"
    ON test_cases FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_roles.user_id = auth.uid()
            AND user_roles.role = 'admin'
        )
    );

-- RLS Policies for submissions
CREATE POLICY "Users can view their own submissions"
    ON submissions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own submissions"
    ON submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Admins can view all submissions
CREATE POLICY "Admins can view all submissions"
    ON submissions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_roles.user_id = auth.uid()
            AND user_roles.role = 'admin'
        )
    );

-- Admins can update all submissions (for review)
CREATE POLICY "Admins can update all submissions"
    ON submissions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_roles.user_id = auth.uid()
            AND user_roles.role = 'admin'
        )
    );

-- RLS Policies for user_roles
CREATE POLICY "Users can view their own role"
    ON user_roles FOR SELECT
    USING (auth.uid() = user_id);

-- Only admins can view all roles
CREATE POLICY "Admins can view all roles"
    ON user_roles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id = auth.uid()
            AND ur.role = 'admin'
        )
    );

-- Only service role can insert/update roles (done through backend)
CREATE POLICY "Service role can manage roles"
    ON user_roles FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update updated_at on solutions
CREATE TRIGGER update_solutions_updated_at BEFORE UPDATE ON solutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

