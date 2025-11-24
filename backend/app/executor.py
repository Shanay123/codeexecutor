import time
import tempfile
import os
import json
import ast
import re
import subprocess
from typing import Dict, Any, List, Tuple


def parse_function_signature(signature: str, language: str = "python") -> Tuple[str, List[Tuple[str, str]], str]:
    """Parse function signature for Python or JavaScript"""
    if language == "javascript":
        return parse_javascript_signature(signature)
    return parse_python_signature(signature)


def parse_python_signature(signature: str) -> Tuple[str, List[Tuple[str, str]], str]:
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


def parse_javascript_signature(signature: str) -> Tuple[str, List[Tuple[str, str]], str]:
    """Parse JavaScript function signature
    Supports: function name(param1, param2) { or const name = (param1, param2) => {
    """
    signature = signature.strip()
    
    # Match: function funcName(params) or const funcName = (params) => or function funcName(params)
    patterns = [
        r'function\s+(\w+)\s*\((.*?)\)',
        r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
        r'(\w+)\s*=\s*function\s*\((.*?)\)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, signature)
        if match:
            func_name = match.group(1)
            params_str = match.group(2).strip()
            
            params = []
            if params_str:
                param_list = [p.strip() for p in params_str.split(',')]
                for param in param_list:
                    # JavaScript doesn't have type annotations in function signatures typically
                    params.append((param, "Any"))
            
            return func_name, params, "Any"
    
    raise ValueError(f"Invalid JavaScript function signature: {signature}")


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


def execute_javascript(code: str, input_data: str, expected_output: str, timeout: int = 5, function_signature: str = None) -> Dict:
    """Execute JavaScript code with test cases"""
    start_time = time.time()
    
    if not function_signature:
        return {
            "passed": False,
            "error": "Function signature is required for JavaScript execution",
            "execution_time": time.time() - start_time
        }
    
    try:
        func_name, params, return_type = parse_javascript_signature(function_signature)
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
    
    # Create a test harness that calls the user's function
    test_harness = f"""
{code}

// Test harness
try {{
    const args = {json.dumps(args)};
    const result = {func_name}(...args);
    console.log(JSON.stringify(result));
}} catch (error) {{
    console.error('ERROR: ' + error.message);
    process.exit(1);
}}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_harness)
        temp_file = f.name
    
    try:
        # Execute with Node.js
        result = subprocess.run(
            ['node', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if error_msg.startswith('ERROR: '):
                error_msg = error_msg[7:]
            return {
                "passed": False,
                "error": f"Runtime error: {error_msg}",
                "execution_time": execution_time
            }
        
        # Parse the output
        output = result.stdout.strip()
        try:
            actual_output = json.loads(output)
        except json.JSONDecodeError:
            return {
                "passed": False,
                "error": f"Function returned invalid JSON: {output}",
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
        
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "error": f"Execution timed out after {timeout} seconds",
            "execution_time": timeout
        }
    except FileNotFoundError:
        return {
            "passed": False,
            "error": "Node.js is not installed or not in PATH",
            "execution_time": time.time() - start_time
        }
    except Exception as e:
        return {
            "passed": False,
            "error": f"Execution error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def execute_code(code: str, input_data: str, expected_output: str, timeout: int = 5, function_signature: str = None, language: str = "python") -> Dict:
    """Route to appropriate language executor"""
    start_time = time.time()
    
    # Route to JavaScript executor
    if language == "javascript":
        return execute_javascript(code, input_data, expected_output, timeout, function_signature)
    
    # Python execution (default)
    if not function_signature:
        return execute_code_legacy(code, input_data, expected_output, timeout)
    
    try:
        func_name, params, return_type = parse_function_signature(function_signature, language)
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
