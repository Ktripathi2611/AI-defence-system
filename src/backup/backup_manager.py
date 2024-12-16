import os
import boto3
import pytz
import shutil
from datetime import datetime
from botocore.exceptions import ClientError
from ..utils.monitoring import MonitoringService
from ..config import Config
from sqlalchemy import create_engine
import subprocess
import logging
from typing import Optional, List, Dict

class BackupManager:
    def __init__(self):
        self.monitoring = MonitoringService()
        self.config = Config()
        self.s3_client = self._init_s3_client()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for backup operations"""
        logger = logging.getLogger('backup_manager')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('backup.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _init_s3_client(self) -> boto3.client:
        """Initialize S3 client for cloud backups"""
        return boto3.client(
            's3',
            aws_access_key_id=self.config.AWS_ACCESS_KEY,
            aws_secret_access_key=self.config.AWS_SECRET_KEY,
            region_name=self.config.AWS_REGION
        )

    def create_database_backup(self) -> Optional[str]:
        """Create PostgreSQL database backup"""
        try:
            timestamp = datetime.now(pytz.UTC).strftime('%Y%m%d_%H%M%S')
            backup_file = f'database_backup_{timestamp}.sql'
            backup_path = os.path.join(self.config.BACKUP_DIR, backup_file)

            # Ensure backup directory exists
            os.makedirs(self.config.BACKUP_DIR, exist_ok=True)

            # Create database backup using pg_dump
            cmd = [
                'pg_dump',
                f'--host={self.config.DB_HOST}',
                f'--port={self.config.DB_PORT}',
                f'--username={self.config.DB_USER}',
                f'--dbname={self.config.DB_NAME}',
                f'--file={backup_path}'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.DB_PASSWORD
            
            subprocess.run(cmd, env=env, check=True)
            
            self.logger.info(f'Database backup created: {backup_file}')
            return backup_path
        except Exception as e:
            self.logger.error(f'Database backup failed: {str(e)}')
            self.monitoring.record_error('database_backup', str(e))
            return None

    def backup_ai_models(self) -> List[str]:
        """Backup AI model files"""
        try:
            timestamp = datetime.now(pytz.UTC).strftime('%Y%m%d_%H%M%S')
            model_backup_dir = os.path.join(self.config.BACKUP_DIR, f'models_backup_{timestamp}')
            os.makedirs(model_backup_dir, exist_ok=True)
            
            backed_up_files = []
            
            # Backup each model file
            for model_file in os.listdir(self.config.MODEL_DIR):
                if model_file.endswith('.pt') or model_file.endswith('.pth'):
                    src = os.path.join(self.config.MODEL_DIR, model_file)
                    dst = os.path.join(model_backup_dir, model_file)
                    shutil.copy2(src, dst)
                    backed_up_files.append(dst)
            
            self.logger.info(f'AI models backed up to: {model_backup_dir}')
            return backed_up_files
        except Exception as e:
            self.logger.error(f'AI model backup failed: {str(e)}')
            self.monitoring.record_error('model_backup', str(e))
            return []

    def backup_to_s3(self, file_path: str, bucket: str) -> bool:
        """Upload backup file to S3"""
        try:
            file_name = os.path.basename(file_path)
            self.s3_client.upload_file(file_path, bucket, file_name)
            self.logger.info(f'File uploaded to S3: {file_name}')
            return True
        except ClientError as e:
            self.logger.error(f'S3 upload failed: {str(e)}')
            self.monitoring.record_error('s3_upload', str(e))
            return False

    def cleanup_old_backups(self, max_age_days: int = 30) -> None:
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now(pytz.UTC).timestamp() - (max_age_days * 86400)
            
            for root, _, files in os.walk(self.config.BACKUP_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getctime(file_path) < cutoff_date:
                        os.remove(file_path)
                        self.logger.info(f'Removed old backup: {file}')
                        
            # Cleanup empty directories
            for root, dirs, _ in os.walk(self.config.BACKUP_DIR, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        self.logger.info(f'Removed empty backup directory: {dir_name}')
                        
        except Exception as e:
            self.logger.error(f'Backup cleanup failed: {str(e)}')
            self.monitoring.record_error('backup_cleanup', str(e))

    def perform_full_backup(self) -> Dict[str, bool]:
        """Perform full system backup"""
        results = {
            'database': False,
            'models': False,
            's3_upload': False
        }
        
        try:
            # Database backup
            db_backup_path = self.create_database_backup()
            if db_backup_path:
                results['database'] = True
                results['s3_upload'] = self.backup_to_s3(
                    db_backup_path,
                    self.config.S3_BACKUP_BUCKET
                )
            
            # AI models backup
            model_backup_files = self.backup_ai_models()
            if model_backup_files:
                results['models'] = True
                for file_path in model_backup_files:
                    self.backup_to_s3(file_path, self.config.S3_BACKUP_BUCKET)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            self.logger.info('Full backup completed successfully')
            self.monitoring.record_metric('backup_success', 1)
            
        except Exception as e:
            self.logger.error(f'Full backup failed: {str(e)}')
            self.monitoring.record_error('full_backup', str(e))
            self.monitoring.record_metric('backup_failure', 1)
            
        return results
