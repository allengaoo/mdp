"""
SQL Execution Guard for Chat2App Module.
MDP Platform V3.1

Provides safe SQL execution with strict validation.
Only SELECT statements are allowed.
"""

import re
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.core.db import instance_engine


class SQLValidationError(Exception):
    """Raised when SQL validation fails."""
    pass


class SQLExecutionError(Exception):
    """Raised when SQL execution fails."""
    pass


# Dangerous SQL patterns (case-insensitive)
FORBIDDEN_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCALL\b",
    r"\bSET\b",
    r"\bINTO\s+OUTFILE\b",
    r"\bLOAD_FILE\b",
    r"\bSLEEP\b",
    r"\bBENCHMARK\b",
    r"--",  # SQL comments
    r"/\*",  # Block comments start
    r";.*\bSELECT\b",  # Chained queries
]


def validate_sql(sql: str) -> bool:
    """
    Validate SQL statement for safety.
    
    Rules:
    1. Must start with SELECT
    2. Cannot contain dangerous keywords
    3. Cannot contain multiple statements
    
    Args:
        sql: SQL statement to validate
        
    Returns:
        True if valid
        
    Raises:
        SQLValidationError: If validation fails
    """
    if not sql or not sql.strip():
        raise SQLValidationError("SQL statement cannot be empty")
    
    # Normalize whitespace
    normalized = " ".join(sql.split()).upper()
    
    # Must start with SELECT
    if not normalized.startswith("SELECT"):
        raise SQLValidationError(
            "Only SELECT queries are allowed. "
            f"Got: {normalized[:50]}..."
        )
    
    # Check for forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            raise SQLValidationError(
                f"Forbidden SQL pattern detected: {pattern}"
            )
    
    # Check for multiple statements (semicolon followed by non-whitespace)
    if re.search(r";\s*\S", sql):
        raise SQLValidationError(
            "Multiple SQL statements are not allowed"
        )
    
    logger.info(f"SQL validation passed: {sql[:100]}...")
    return True


async def execute_safe_sql(
    sql: str,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Execute a validated SQL query with row limit.
    
    Args:
        sql: SQL SELECT statement
        limit: Maximum rows to return (default 100)
        
    Returns:
        Dict with 'columns', 'rows', and 'row_count'
    """
    # Validate first
    validate_sql(sql)
    
    # Add LIMIT if not present
    normalized = sql.strip().upper()
    if "LIMIT" not in normalized:
        sql = f"{sql.rstrip().rstrip(';')} LIMIT {limit}"
    
    try:
        async with instance_engine.connect() as conn:
            logger.info(f"Executing SQL: {sql[:200]}...")
            
            result = await conn.execute(text(sql))
            
            # Get column names
            columns = list(result.keys())
            
            # Fetch all rows
            rows = [dict(row._mapping) for row in result.fetchall()]
            
            logger.info(f"Query returned {len(rows)} rows")
            
            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "sql": sql
            }
            
    except SQLAlchemyError as e:
        logger.error(f"SQL execution error: {e}")
        raise SQLExecutionError(f"Database error: {str(e)}")
