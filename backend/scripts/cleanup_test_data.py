#!/usr/bin/env python
"""Clean up test data with empty api_name"""
import sys
sys.path.insert(0, ".")

from sqlmodel import Session, create_engine
from sqlalchemy import text
from app.core.config import settings

engine = create_engine(str(settings.database_url))
with Session(engine) as session:
    # Delete object types with empty api_name
    result = session.execute(text("""
        DELETE FROM ont_object_type WHERE api_name = ''
    """))
    session.commit()
    print(f"Deleted {result.rowcount} object types with empty api_name")
    
    # Delete orphan datasets
    result = session.execute(text("""
        DELETE FROM sys_dataset WHERE api_name LIKE 'dataset_%' AND storage_location LIKE 'virtual_%'
    """))
    session.commit()
    print(f"Deleted {result.rowcount} orphan datasets")

print("Cleanup completed!")
