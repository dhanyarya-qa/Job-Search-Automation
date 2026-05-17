"""
Run Database Migrations - Sync version for Alembic
"""
import os
import sys
from pathlib import Path

# IMPORTANT: Set sync SQLite URL BEFORE importing anything
os.environ['DATABASE_URL'] = 'sqlite:///./job_hunting_ats.db'

sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import after setting the env var
from alembic.config import Config
from alembic import command


def run_migrations():
    """Run all pending migrations"""
    print("=" * 60)
    print("🔄 RUNNING DATABASE MIGRATIONS")
    print("=" * 60)
    print(f"Database: sqlite:///./job_hunting_ats.db")
    print()
    
    try:
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        # Force sync SQLite URL
        alembic_cfg.set_main_option('sqlalchemy.url', 'sqlite:///./job_hunting_ats.db')
        
        # Run migrations
        print("📦 Upgrading database to latest version...")
        command.upgrade(alembic_cfg, "head")
        
        print()
        print("=" * 60)
        print("✅ MIGRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ MIGRATION FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
