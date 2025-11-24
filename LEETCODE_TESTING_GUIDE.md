# LeetCode-Style Testing Guide

## Overview

The platform now uses LeetCode-style function-based testing. Users implement a specific function signature, and test cases call that function with typed arguments.

## How to Test the Implementation

### Step 1: Run Database Migration

In **Supabase SQL Editor**, run:
```sql
-- Add function_signature column
ALTER TABLE problems 
ADD COLUMN IF NOT EXISTS function_signature TEXT;

UPDATE problems 
SET function_signature = 'def solution(input_data: str) -> str:'
WHERE function_signature IS NULL;

ALTER TABLE problems 
ALTER COLUMN function_signature SET NOT NULL;
```

### Step 2: Restart Docker

```bash
docker-compose down
docker-compose up --build
```

### Step 3: Create a Test Problem

1. **Go to** http://localhost:5173 and login
2. **Create New Problem**:
   - **Title:** Two Sum
   - **Description:** Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.
   - **Function Signature:** `def two_sum(nums: list[int], target: int) -> list[int]:`
   - **Example Input:** `[[2,7,11,15], 9]`
   - **Example Output:** `[0, 1]`

3. **Add Test Cases:**
   - Test 1:
     - Input: `[[2,7,11,15], 9]`
     - Output: `[0, 1]`
   - Test 2:
     - Input: `[[3,2,4], 6]`
     - Output: `[1, 2]`
   - Test 3:
     - Input: `[[3,3], 6]`
     - Output: `[0, 1]`

4. **Write Solution:**
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

5. **Run Tests** - All should pass! ✅

## Edge Cases to Test

### 1. Different Parameter Types

**Problem:** Add Numbers
- **Signature:** `def add(a: int, b: int) -> int:`
- **Input:** `[2, 3]`
- **Output:** `5`

### 2. String Parameters

**Problem:** Reverse String
- **Signature:** `def reverse(s: str) -> str:`
- **Input:** `["hello"]`
- **Output:** `"olleh"`

### 3. List Return Types

**Problem:** Range Array
- **Signature:** `def range_array(n: int) -> list[int]:`
- **Input:** `[5]`
- **Output:** `[0, 1, 2, 3, 4]`

### 4. Multiple Parameters with Mixed Types

**Problem:** Repeat String
- **Signature:** `def repeat(s: str, n: int) -> str:`
- **Input:** `["hi", 3]`
- **Output:** `"hihihi"`

### 5. Complex Nested Structures

**Problem:** Find Max in Matrix
- **Signature:** `def find_max(matrix: list[list[int]]) -> int:`
- **Input:** `[[[1,2,3],[4,5,6],[7,8,9]]]`
- **Output:** `9`

## Error Cases to Verify

### Invalid Function Name
- User implements `def wrong_name():` instead of the required function
- **Expected:** Error message: "Function 'two_sum' not found"

### Wrong Number of Parameters
- Function signature: `def add(a: int, b: int) -> int:`
- Test input: `[1, 2, 3]` (3 args instead of 2)
- **Expected:** Error: "Expected 2 arguments, got 3"

### Invalid JSON Input
- Test input: `[1, 2, "hello` (malformed JSON)
- **Expected:** Error: "Invalid JSON input"

### Runtime Exception
- Code raises an exception
- **Expected:** Error message with exception details

### Type Mismatch
- Function expects `int`, receives `"hello"`
- **Expected:** Error: "Type conversion error"

## Admin Testing

1. **Submit a solution** as a regular user
2. **Login as admin**
3. **Go to Admin Dashboard**
4. **Review the submission**
5. **Edit a test case** (change input or output)
6. **Click "Rerun Tests"**
7. **Verify** new results show correctly
8. **Approve or Reject**

## Success Criteria

✅ Problem creation with function signature works  
✅ Solution editor pre-populates with function signature  
✅ Test cases use JSON format  
✅ Multi-parameter functions work correctly  
✅ Different types (int, str, list, dict) all work  
✅ Error messages are clear and helpful  
✅ Admin can edit test cases and rerun  
✅ Submissions work end-to-end  

## Common Issues & Fixes

**"Function not found" error:**
- User forgot to implement the exact function name
- Check the function signature matches

**"Invalid JSON" error:**
- Test input is not valid JSON
- Use `[1, 2]` not `1, 2`
- Use `["hello"]` not `"hello"` for single args

**Type conversion errors:**
- Usually means test data doesn't match expected type
- Verify JSON types match function signature

**Tests fail but should pass:**
- Check return value exactly matches expected output
- Lists/dicts must match exactly (order matters for lists)

---

**The LeetCode-style testing system is now fully implemented!** 🎉

