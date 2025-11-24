import sys
import io
import time
import tempfile
import os
import json
import re
import ast
from typing import Dict, Any, List, Tuple
from contextlib import redirect_stdout, redirect_stderr


def parse_function_signature(signature: str) -> Tuple[str, List[Tuple[str, str]], str]:
    """
    Parse a function signature to extract function name, parameters, and return type
    
    Args:
        signature: Function signature string (e.g., "def add(a: int, b: int) -> int:")
    
    Returns:
        Tuple of (function_name, [(param_name, param_type), ...], return_type)
    
    Examples:
        "def add(a: int, b: int) -> int:" -> ("add", [("a", "int"), ("b", "int")], "int")
        "def reverse(s: str) -> str:" -> ("reverse", [("s", "str")], "str")
    """
    try:
        # Clean up the signature
        signature = signature.strip()
        
        # Ensure it ends with a colon
        if not signature.endswith(':'):
            signature = signature + ':'
        
        # Add a pass statement to make it valid Python for AST parsing
        full_function = signature + '\n    pass'
        
        # Parse using AST
        tree = ast.parse(full_function)
        func_def = tree.body[0]
        
        if not isinstance(func_def, ast.FunctionDef):
            raise ValueError("Not a valid function definition")
        
        func_name = func_def.name
        
        # Extract parameters and their types
        params = []
        for arg in func_def.args.args:
            param_name = arg.arg
            param_type = "Any"
            
            if arg.annotation:
                # Get the type annotation as string
                param_type = ast.unparse(arg.annotation)
            
            params.append((param_name, param_type))
        
        # Extract return type
        return_type = "Any"
        if func_def.returns:
            return_type = ast.unparse(func_def.returns)
        
        return func_name, params, return_type
    
    except Exception as e:
        raise ValueError(f"Invalid function signature: {str(e)}")


def convert_type(value: Any, target_type: str) -> Any:
    """
    Convert a value to the target type
    
    Args:
        value: Value to convert
        target_type: Target type as string (e.g., "int", "str", "list[int]")
    
    Returns:
        Converted value
    """
    # Direct type mappings
    if target_type == "int":
        return int(value)
    elif target_type == "float":
        return float(value)
    elif target_type == "str":
        return str(value)
    elif target_type == "bool":
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    elif target_type.startswith("list"):
        if not isinstance(value, list):
            raise ValueError(f"Expected list, got {type(value).__name__}")
        return value
    elif target_type.startswith("dict"):
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict, got {type(value).__name__}")
        return value
    else:
        # For complex types or Any, return as-is
        return value


def execute_code(code: str, input_data: str, expected_output: str, timeout: int = 5, function_signature: str = None) -> Dict:
    """
    Execute Python code by calling the user's function with parsed arguments
    
    Args:
        code: Python code containing user's function
        input_data: JSON-encoded list of arguments (e.g., '[2, 3]' or '["hello"]')
        expected_output: JSON-encoded expected return value
        timeout: Maximum execution time in seconds
        function_signature: Function signature (e.g., "def add(a: int, b: int) -> int:")
    
    Returns:
        Dictionary with execution results
    """
    start_time = time.time()
    
    # If no function signature provided, fall back to old solution() format
    if not function_signature:
        return execute_code_legacy(code, input_data, expected_output, timeout)
    
    try:
        # Parse the function signature
        try:
            func_name, params, return_type = parse_function_signature(function_signature)
        except ValueError as e:
            return {
                "passed": False,
                "error": f"Invalid function signature: {str(e)}",
                "execution_time": time.time() - start_time
            }
        
        # Parse input arguments from JSON
        try:
            args = json.loads(input_data)
            if not isinstance(args, list):
                args = [args]
        except json.JSONDecodeError as e:
            return {
                "passed": False,
                "error": f"Invalid JSON input: {str(e)}",
                "execution_time": time.time() - start_time
            }
        
        # Parse expected output from JSON
        try:
            expected = json.loads(expected_output)
        except json.JSONDecodeError as e:
            return {
                "passed": False,
                "error": f"Invalid JSON expected output: {str(e)}",
                "execution_time": time.time() - start_time
            }
        
        # Validate number of arguments
        if len(args) != len(params):
            return {
                "passed": False,
                "error": f"Expected {len(params)} arguments, got {len(args)}",
                "execution_time": time.time() - start_time
            }
        
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Prepare namespace for execution
            namespace = {}
            
            # Read and compile the code
            with open(temp_file, 'r') as f:
                user_code = f.read()
            
            # Execute the user's code to define the function
            try:
                exec(user_code, namespace)
            except Exception as e:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": f"Error loading code: {str(e)}",
                    "execution_time": execution_time
                }
            
            # Check if the function exists
            if func_name not in namespace:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": f"Function '{func_name}' not found. Please define: {function_signature}",
                    "execution_time": execution_time
                }
            
            user_func = namespace[func_name]
            
            # Call the function with arguments
            try:
                # Convert arguments to expected types if needed
                converted_args = []
                for i, (arg_val, (param_name, param_type)) in enumerate(zip(args, params)):
                    try:
                        converted_args.append(convert_type(arg_val, param_type))
                    except Exception as e:
                        return {
                            "passed": False,
                            "error": f"Type conversion error for parameter '{param_name}': {str(e)}",
                            "execution_time": time.time() - start_time
                        }
                
                actual_output = user_func(*converted_args)
                
                execution_time = time.time() - start_time
                
                # Check for timeout
                if execution_time > timeout:
                    return {
                        "passed": False,
                        "error": f"Execution timed out after {timeout} seconds",
                        "execution_time": execution_time
                    }
                
                # Compare outputs
                passed = actual_output == expected
                
                # For better error messages, serialize for display
                actual_str = json.dumps(actual_output) if not isinstance(actual_output, str) else actual_output
                expected_str = json.dumps(expected) if not isinstance(expected, str) else expected
                
                return {
                    "passed": passed,
                    "actual_output": actual_str,
                    "expected_output": expected_str,
                    "execution_time": execution_time
                }
                
            except Exception as e:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": f"Runtime error: {str(e)}",
                    "execution_time": execution_time
                }
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "passed": False,
            "error": f"Execution error: {str(e)}",
            "execution_time": execution_time
        }


def execute_code_legacy(code: str, input_data: str, expected_output: str, timeout: int = 5) -> Dict:
    """
    Legacy execution for old solution() format (for backwards compatibility)
    """
    start_time = time.time()
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            namespace = {}
            
            with open(temp_file, 'r') as f:
                user_code = f.read()
            
            try:
                exec(user_code, namespace)
            except Exception as e:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": f"Error loading code: {str(e)}",
                    "execution_time": execution_time
                }
            
            if 'solution' not in namespace:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": "No 'solution' function found",
                    "execution_time": execution_time
                }
            
            solution_func = namespace['solution']
            
            try:
                actual_output = solution_func(input_data)
                
                if not isinstance(actual_output, str):
                    actual_output = str(actual_output)
                
                execution_time = time.time() - start_time
                
                if execution_time > timeout:
                    return {
                        "passed": False,
                        "error": f"Execution timed out after {timeout} seconds",
                        "execution_time": execution_time
                    }
                
                actual_output = actual_output.strip()
                expected_output = expected_output.strip()
                
                passed = actual_output == expected_output
                
                return {
                    "passed": passed,
                    "actual_output": actual_output,
                    "expected_output": expected_output,
                    "execution_time": execution_time
                }
                
            except Exception as e:
                execution_time = time.time() - start_time
                return {
                    "passed": False,
                    "error": f"Runtime error: {str(e)}",
                    "execution_time": execution_time
                }
        
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "passed": False,
            "error": f"Execution error: {str(e)}",
            "execution_time": execution_time
        }
