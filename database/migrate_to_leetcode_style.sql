-- Migration: Add function signature support for LeetCode-style problems
-- Run this in Supabase SQL Editor

-- Add function_signature column to problems table
ALTER TABLE problems 
ADD COLUMN IF NOT EXISTS function_signature TEXT;

-- Update existing problems with a default signature
-- (existing problems will need to be recreated or manually updated)
UPDATE problems 
SET function_signature = 'def solution(input_data: str) -> str:'
WHERE function_signature IS NULL;

-- Make it required for new problems
ALTER TABLE problems 
ALTER COLUMN function_signature SET NOT NULL;

-- Add a helpful comment
COMMENT ON COLUMN problems.function_signature IS 
'Function signature that users must implement (e.g., "def two_sum(nums: list[int], target: int) -> list[int]:")';

