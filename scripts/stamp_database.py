"""
Stamp Database - Mark migrations as applied
"""
import os
import sys
from pathlib import Path

# Set sync SQLite URL BEFORE importing anything
os.environ['DATABASE_URL'] = 'sqlite:///./job_hunting_ats.db'

sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command


def stamp_database():
    """Stamp database with current version"""
    print("=" * 60)
    print("🏷️  STAMPING DATABASE")
    print("=" * 60)
    print(f"Database: sqlite:///./job_hunting_ats.db")
    print(f"Marking as version: 004")
    print()
    
    try:
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        # Force sync SQLite URL
        alembic_cfg.set_main_option('sqlalchemy.url', 'sqlite:///./job_hunting_ats.db')
        
        # Stamp database
        print("📦 Stamping database...")
        command.stamp(alembic_cfg, "004")
        
        print()
        print("=" * 60)
        print("✅ DATABASE STAMPED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ STAMP FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = stamp_database()
    sys.exit(0 if success else 1)
