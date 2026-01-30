import asyncio
from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from app.models.context import LinkMappingDef

def init_db():
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
