"""
Action execution engine with logging.
"""
from loguru import logger
from typing import Optional, Dict, Any


async def execute_action(
    action_id: str,
    target_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute an action with comprehensive logging.
    
    Args:
        action_id: The ID of the action to execute
        target_id: Optional target object ID
        parameters: Optional action parameters
        
    Returns:
        Dictionary with execution results
    """
    logger.info(f"Executing Action: {action_id}")
    
    if target_id:
        logger.info(f"Target: {target_id}")
    
    if parameters:
        logger.debug(f"Action Parameters: {parameters}")
    
    try:
        # Example: Execute Strike Action
        if "strike" in action_id.lower():
            target_name = parameters.get("target_name", "Unknown") if parameters else "Unknown"
            logger.info(f"Executing Action: Strike on Target: {target_name}")
            
            # Simulate action execution
            logger.debug(f"Calculating strike parameters for target: {target_name}")
            
            # Business logic here...
            result = {
                "success": True,
                "action_id": action_id,
                "target": target_name,
                "damage": 100,
                "message": f"Strike executed on {target_name}"
            }
            
            logger.info(f"Action completed successfully: {action_id}")
            logger.debug(f"Action result: {result}")
            
            return result
        
        # Example: Execute Refuel Action
        elif "refuel" in action_id.lower():
            fighter_id = parameters.get("fighter_id", "Unknown") if parameters else "Unknown"
            fuel_amount = parameters.get("fuel_amount", 0) if parameters else 0
            
            logger.info(f"Executing Action: Refuel for Fighter: {fighter_id}")
            logger.info(f"Fuel Amount: {fuel_amount}L")
            
            # Business logic here...
            result = {
                "success": True,
                "action_id": action_id,
                "fighter_id": fighter_id,
                "fuel_added": fuel_amount,
                "message": f"Refueled {fighter_id} with {fuel_amount}L"
            }
            
            logger.info(f"Refuel action completed: {fighter_id}")
            return result
        
        # Default action execution
        else:
            logger.warning(f"Unknown action type: {action_id}")
            return {
                "success": False,
                "action_id": action_id,
                "error": f"Unknown action type: {action_id}"
            }
            
    except Exception as e:
        logger.error(f"Action execution failed: {action_id} | Error: {str(e)}")
        logger.exception(e)  # Log full exception traceback
        
        return {
            "success": False,
            "action_id": action_id,
            "error": str(e)
        }


async def validate_action(action_id: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
    """
    Validate action parameters before execution.
    
    Args:
        action_id: The ID of the action to validate
        parameters: Optional action parameters
        
    Returns:
        True if action is valid, False otherwise
    """
    logger.debug(f"Validating action: {action_id}")
    
    if not action_id:
        logger.warning("Action validation failed: action_id is empty")
        return False
    
    if parameters:
        logger.debug(f"Validating parameters: {parameters}")
    
    logger.info(f"Action validated successfully: {action_id}")
    return True

