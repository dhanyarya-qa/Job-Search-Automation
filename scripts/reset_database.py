"""
Reset Database - Delete old database and run migrations fresh
"""
import os
import sys
from pathlib import Path

# Set sync SQLite URL BEFORE importing anything
os.environ['DATABASE_URL'] = 'sqlite:///./job_hunting_ats.db'

sys.path.insert(0, str(Path(__file__).parent.parent))


def reset_database():
    """Delete old database and run migrations"""
    print("=" * 60)
    print("🗑️  RESETTING DATABASE")
    print("=" * 60)
    
    db_file = Path("job_hunting_ats.db")
    
    # Delete old database
    if db_file.exists():
        print(f"Deleting old database: {db_file}")
        db_file.unlink()
        print("✅ Old database deleted")
    else:
        print("No existing database found")
    
    print()
    print("=" * 60)
    print("🔄 RUNNING MIGRATIONS")
    print("=" * 60)
    
    # Run migrations
    from alembic.config import Config
    from alembic import command
    
    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option('sqlalchemy.url', 'sqlite:///./job_hunting_ats.db')
        
        print("📦 Creating database with all migrations...")
        command.upgrade(alembic_cfg, "head")
        
        print()
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ RESET FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
