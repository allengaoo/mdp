"""
Dynamic function execution engine.
Executes user-defined Python code stored in FunctionDefinition.code_content.
"""
import ast
import traceback
from typing import Dict, Any, Optional
from sqlmodel import Session

from app.core.logger import logger
from app.engine.meta_crud import get_function_definition


def validate_syntax(code_content: str) -> tuple[bool, Optional[str]]:
    """
    Validate Python code syntax without executing it.
    
    Args:
        code_content: Python code string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, error_message)
    """
    try:
        ast.parse(code_content)
        return True, None
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f"\n  {e.text.strip()}"
        return False, error_msg
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def execute_function(
    session: Session,
    function_id: str,
    context: Dict[str, Any]
) -> Any:
    """
    Execute a user-defined function from FunctionDefinition.
    
    Args:
        session: Database session
        function_id: UUID of the FunctionDefinition to execute
        context: Context dictionary passed to the user's main() function
                 Typically contains: {"source": {...}, "target": {...}, ...}
        
    Returns:
        Result from the user's main(context) function
        
    Raises:
        ValueError: If function not found or main() function not defined
        RuntimeError: If user code execution fails
    """
    # Step 1: Fetch FunctionDefinition from DB
    logger.info(f"Fetching FunctionDefinition: {function_id}")
    function_def = get_function_definition(session, function_id)
    
    if not function_def:
        error_msg = f"FunctionDefinition not found: {function_id}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Executing Function: {function_def.api_name} | ID: {function_id}")
    logger.debug(f"Function code length: {len(function_def.code_content or '')} characters")
    logger.debug(f"Input context: {context}")
    
    # Step 2: Validate syntax (optional but good practice)
    if function_def.code_content:
        is_valid, syntax_error = validate_syntax(function_def.code_content)
        if not is_valid:
            error_msg = f"Syntax error in function '{function_def.api_name}': {syntax_error}"
            logger.error(error_msg)
            raise SyntaxError(error_msg)
    else:
        error_msg = f"FunctionDefinition '{function_def.api_name}' has no code_content"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Step 3: Prepare sandbox environment
    # Note: For MVP, we use exec() directly. In production, consider using
    # more restrictive sandboxing (e.g., RestrictedPython, PySandbox)
    # Prepare restricted builtins (allow safe operations, block dangerous ones)
    restricted_builtins = {
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'min': min,
        'max': max,
        'sum': sum,
        'abs': abs,
        'round': round,
        'sorted': sorted,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'isinstance': isinstance,
        'type': type,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'print': print,  # Allow print for debugging
    }
    
    globals_dict = {
        '__builtins__': restricted_builtins,
        # Common math operations (if needed by user code)
        'math': __import__('math'),
    }
    locals_dict = {}
    
    # Step 4: Compile and load user code
    try:
        logger.debug(f"Compiling function code for: {function_def.api_name}")
        exec(function_def.code_content, globals_dict, locals_dict)
    except SyntaxError as e:
        error_msg = f"Syntax error in function '{function_def.api_name}': {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Syntax error traceback:\n{traceback.format_exc()}")
        raise SyntaxError(error_msg)
    except Exception as e:
        error_msg = f"Error compiling function '{function_def.api_name}': {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Compilation error traceback:\n{traceback.format_exc()}")
        raise RuntimeError(error_msg)
    
    # Step 5: Check if main() function exists
    if 'main' not in locals_dict:
        error_msg = (
            f"Function '{function_def.api_name}' does not define a 'main(context)' function. "
            f"Available names: {list(locals_dict.keys())}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    main_func = locals_dict['main']
    if not callable(main_func):
        error_msg = f"'main' in function '{function_def.api_name}' is not callable"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Step 6: Execute the main() function with context
    try:
        logger.debug(f"Calling main(context) for function: {function_def.api_name}")
        result = main_func(context)
        logger.debug(f"Function execution result: {result}")
        logger.info(f"Function '{function_def.api_name}' executed successfully")
        return result
    except Exception as e:
        error_msg = (
            f"Runtime error in function '{function_def.api_name}': {str(e)}\n"
            f"Error type: {type(e).__name__}"
        )
        logger.error(error_msg)
        logger.debug(f"Runtime error traceback:\n{traceback.format_exc()}")
        
        # Re-raise as RuntimeError with user-friendly message
        raise RuntimeError(f"Function execution failed: {str(e)}") from e
