"""
Run Database Migrations - Sync version for Alembic
"""
import os
import sys
from pathlib import Path

# IMPORTANT: Set environment variables BEFORE importing anything
# This ensures pydantic can validate settings properly
os.environ.setdefault('DATABASE_URL', 'sqlite:///./job_hunting_ats.db')
os.environ.setdefault('SECRET_KEY', 'migration-secret-key-min-32-chars-here!!')
os.environ.setdefault('JWT_SECRET_KEY', 'migration-jwt-secret-key-32-chars-min!!')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'dummy')
os.environ.setdefault('TELEGRAM_CHAT_ID', 'dummy')

sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import after setting the env vars
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
