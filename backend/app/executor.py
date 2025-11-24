import time
import tempfile
import os
import json
import ast
from typing import Dict, Any, List, Tuple


def parse_function_signature(signature: str) -> Tuple[str, List[Tuple[str, str]], str]:
    signature = signature.strip()
    if not signature.endswith(':'):
        signature = signature + ':'
    
    full_function = signature + '\n    pass'
    
    try:
        tree = ast.parse(full_function)
        func_def = tree.body[0]
        
        if not isinstance(func_def, ast.FunctionDef):
            raise ValueError("Not a valid function definition")
        
        func_name = func_def.name
        params = []
        
        for arg in func_def.args.args:
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            params.append((arg.arg, param_type))
        
        return_type = ast.unparse(func_def.returns) if func_def.returns else "Any"
        
        return func_name, params, return_type
    except Exception as e:
        raise ValueError(f"Invalid function signature: {str(e)}")


def convert_type(value: Any, target_type: str) -> Any:
    type_map = {
        "int": lambda v: int(v),
        "float": lambda v: float(v),
        "str": lambda v: str(v),
        "bool": lambda v: v.lower() in ('true', '1', 'yes') if isinstance(v, str) else bool(v)
    }
    
    if target_type in type_map:
        return type_map[target_type](value)
    
    if target_type.startswith("list"):
        if not isinstance(value, list):
            raise ValueError(f"Expected list, got {type(value).__name__}")
        return value
    
    if target_type.startswith("dict"):
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict, got {type(value).__name__}")
        return value
    
    return value


def execute_code(code: str, input_data: str, expected_output: str, timeout: int = 5, function_signature: str = None) -> Dict:
    start_time = time.time()
    
    if not function_signature:
        return execute_code_legacy(code, input_data, expected_output, timeout)
    
    try:
        func_name, params, return_type = parse_function_signature(function_signature)
    except ValueError as e:
        return {
            "passed": False,
            "error": f"Invalid function signature: {str(e)}",
            "execution_time": time.time() - start_time
        }
    
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
    
    try:
        expected = json.loads(expected_output)
    except json.JSONDecodeError as e:
        return {
            "passed": False,
            "error": f"Invalid JSON expected output: {str(e)}",
            "execution_time": time.time() - start_time
        }
    
    if len(args) != len(params):
        return {
            "passed": False,
            "error": f"Expected {len(params)} arguments, got {len(args)}",
            "execution_time": time.time() - start_time
        }
    
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
            return {
                "passed": False,
                "error": f"Error loading code: {str(e)}",
                "execution_time": time.time() - start_time
            }
        
        if func_name not in namespace:
            return {
                "passed": False,
                "error": f"Function '{func_name}' not found. Please define: {function_signature}",
                "execution_time": time.time() - start_time
            }
        
        user_func = namespace[func_name]
        
        try:
            converted_args = []
            for arg_val, (param_name, param_type) in zip(args, params):
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
            
            if execution_time > timeout:
                return {
                    "passed": False,
                    "error": f"Execution timed out after {timeout} seconds",
                    "execution_time": execution_time
                }
            
            passed = actual_output == expected
            actual_str = json.dumps(actual_output) if not isinstance(actual_output, str) else actual_output
            expected_str = json.dumps(expected) if not isinstance(expected, str) else expected
            
            return {
                "passed": passed,
                "actual_output": actual_str,
                "expected_output": expected_str,
                "execution_time": execution_time
            }
        except Exception as e:
            return {
                "passed": False,
                "error": f"Runtime error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def execute_code_legacy(code: str, input_data: str, expected_output: str, timeout: int = 5) -> Dict:
    start_time = time.time()
    
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
            return {
                "passed": False,
                "error": f"Error loading code: {str(e)}",
                "execution_time": time.time() - start_time
            }
        
        if 'solution' not in namespace:
            return {
                "passed": False,
                "error": "No 'solution' function found",
                "execution_time": time.time() - start_time
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
            
            passed = actual_output.strip() == expected_output.strip()
            
            return {
                "passed": passed,
                "actual_output": actual_output.strip(),
                "expected_output": expected_output.strip(),
                "execution_time": execution_time
            }
        except Exception as e:
            return {
                "passed": False,
                "error": f"Runtime error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
