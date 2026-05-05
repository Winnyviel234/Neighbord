# Automated backup script for Neighbord Community System
# This script creates backups of the database and uploads directory

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import logging
from typing import Optional

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.modules.audit.service import AuditService
from app.modules.audit.repository import AuditRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        self.backup_dir = Path(backend_dir) / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.audit_service = AuditService(AuditRepository())

    def create_database_backup(self) -> Optional[str]:
        """Create a PostgreSQL database backup using pg_dump"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"neighbord_db_{timestamp}.sql"

            # Use the DATABASE_URL from settings
            db_url = settings.database_url
            if not db_url:
                logger.error("DATABASE_URL not configured")
                return None

            # Extract connection details from DATABASE_URL
            # Format: postgresql://user:password@host:port/database
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
            if not match:
                logger.error("Invalid DATABASE_URL format")
                return None

            user, password, host, port, database = match.groups()

            # Create pg_dump command
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={user}",
                f"--dbname={database}",
                f"--file={backup_file}",
                "--format=custom",  # Custom format for better compression
                "--compress=9",
                "--no-owner",
                "--no-privileges"
            ]

            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password

            logger.info(f"Starting database backup: {backup_file}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                file_size = backup_file.stat().st_size
                logger.info(f"Database backup completed: {backup_file} ({file_size} bytes)")
                return str(backup_file)
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return None

    def create_uploads_backup(self) -> Optional[str]:
        """Create a backup of the uploads directory"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"neighbord_uploads_{timestamp}.tar.gz"

            uploads_dir = backend_dir / "uploads"

            if not uploads_dir.exists():
                logger.warning("Uploads directory does not exist")
                return None

            # Create tar.gz archive
            import tarfile

            logger.info(f"Starting uploads backup: {backup_file}")
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(uploads_dir, arcname="uploads")

            file_size = backup_file.stat().st_size
            logger.info(f"Uploads backup completed: {backup_file} ({file_size} bytes)")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Error creating uploads backup: {e}")
            return None

    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

            for backup_file in self.backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Removed old backup: {backup_file}")

        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")

    async def run_backup(self, backup_type: str = "full") -> bool:
        """Run the complete backup process"""
        try:
            # Start audit logging
            backup_log = await self.audit_service.start_backup(
                backup_type=backup_type,
                metadata={"script": "automated_backup.py"}
            )
            backup_id = backup_log["id"]

            success = True
            db_backup_path = None
            uploads_backup_path = None

            # Create database backup
            if backup_type in ["full", "database"]:
                db_backup_path = self.create_database_backup()
                if not db_backup_path:
                    success = False

            # Create uploads backup
            if backup_type in ["full", "uploads"]:
                uploads_backup_path = self.create_uploads_backup()
                if not uploads_backup_path:
                    success = False

            # Calculate total size
            total_size = 0
            if db_backup_path:
                total_size += Path(db_backup_path).stat().st_size
            if uploads_backup_path:
                total_size += Path(uploads_backup_path).stat().st_size

            # Complete audit logging
            await self.audit_service.complete_backup(
                backup_id=backup_id,
                success=success,
                file_path=f"db:{db_backup_path or ''},uploads:{uploads_backup_path or ''}",
                file_size_bytes=total_size,
                error_message=None if success else "Backup failed"
            )

            # Cleanup old backups
            self.cleanup_old_backups()

            return success

        except Exception as e:
            logger.error(f"Backup process failed: {e}")
            return False

async def main():
    """Main backup function"""
    import argparse

    parser = argparse.ArgumentParser(description="Neighbord Backup Script")
    parser.add_argument(
        "--type",
        choices=["full", "database", "uploads"],
        default="full",
        help="Type of backup to perform"
    )
    parser.add_argument(
        "--cleanup-days",
        type=int,
        default=30,
        help="Days to keep old backups"
    )

    args = parser.parse_args()

    backup_manager = BackupManager()
    backup_manager.cleanup_old_backups(args.cleanup_days)

    success = await backup_manager.run_backup(args.type)

    if success:
        logger.info("Backup completed successfully")
        sys.exit(0)
    else:
        logger.error("Backup failed")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())