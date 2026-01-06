#!/usr/bin/env python3
"""
Helper script to create .env file with database configuration.
"""
from pathlib import Path

ENV_CONTENT = """# Database Configuration (MySQL)
DATABASE_URL=mysql+pymysql://root:Ga0binGB@localhost:3306/ontology

# Application Settings
DEBUG=False
"""

def main():
    env_file = Path(__file__).parent / '.env'
    
    if env_file.exists():
        print(f"⚠ .env file already exists at: {env_file}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    try:
        env_file.write_text(ENV_CONTENT, encoding='utf-8')
        print(f"✓ .env file created successfully at: {env_file}")
        print(f"  Database: ontology")
        print(f"  Connection: mysql+pymysql://root:***@localhost:3306/ontology")
    except Exception as e:
        print(f"✗ Error creating .env file: {e}")
        print("\nPlease create .env file manually with the following content:")
        print("-" * 60)
        print(ENV_CONTENT)
        print("-" * 60)

if __name__ == '__main__':
    main()

