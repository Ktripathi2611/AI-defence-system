from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .backup_manager import BackupManager
from ..utils.monitoring import MonitoringService
import logging
from typing import Optional

class BackupScheduler:
    def __init__(self):
        self.backup_manager = BackupManager()
        self.scheduler = BackgroundScheduler()
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for scheduler operations"""
        logger = logging.getLogger('backup_scheduler')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('backup_scheduler.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def start(self) -> None:
        """Start the backup scheduler"""
        try:
            # Schedule daily database backup at 2 AM
            self.scheduler.add_job(
                self.backup_manager.create_database_backup,
                CronTrigger(hour=2),
                id='daily_db_backup',
                name='Daily Database Backup'
            )

            # Schedule weekly full backup on Sunday at 3 AM
            self.scheduler.add_job(
                self.backup_manager.perform_full_backup,
                CronTrigger(day_of_week='sun', hour=3),
                id='weekly_full_backup',
                name='Weekly Full Backup'
            )

            # Schedule monthly cleanup on 1st of every month at 4 AM
            self.scheduler.add_job(
                self.backup_manager.cleanup_old_backups,
                CronTrigger(day=1, hour=4),
                id='monthly_cleanup',
                name='Monthly Backup Cleanup'
            )

            self.scheduler.start()
            self.logger.info('Backup scheduler started successfully')
            self.monitoring.record_metric('scheduler_start', 1)

        except Exception as e:
            self.logger.error(f'Failed to start backup scheduler: {str(e)}')
            self.monitoring.record_error('scheduler_start', str(e))
            raise

    def stop(self) -> None:
        """Stop the backup scheduler"""
        try:
            self.scheduler.shutdown()
            self.logger.info('Backup scheduler stopped')
            self.monitoring.record_metric('scheduler_stop', 1)
        except Exception as e:
            self.logger.error(f'Failed to stop backup scheduler: {str(e)}')
            self.monitoring.record_error('scheduler_stop', str(e))

    def add_custom_backup_job(
        self,
        func: callable,
        trigger: str,
        **trigger_args: dict
    ) -> Optional[str]:
        """Add a custom backup job to the scheduler"""
        try:
            job = self.scheduler.add_job(
                func,
                trigger,
                **trigger_args
            )
            self.logger.info(f'Added custom backup job: {job.id}')
            return job.id
        except Exception as e:
            self.logger.error(f'Failed to add custom backup job: {str(e)}')
            self.monitoring.record_error('add_custom_job', str(e))
            return None

    def remove_backup_job(self, job_id: str) -> bool:
        """Remove a backup job from the scheduler"""
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f'Removed backup job: {job_id}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to remove backup job {job_id}: {str(e)}')
            self.monitoring.record_error('remove_job', str(e))
            return False

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get the status of a backup job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger)
                }
            return None
        except Exception as e:
            self.logger.error(f'Failed to get job status for {job_id}: {str(e)}')
            self.monitoring.record_error('get_job_status', str(e))
            return None

    def list_all_jobs(self) -> list:
        """List all scheduled backup jobs"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger)
                })
            return jobs
        except Exception as e:
            self.logger.error(f'Failed to list backup jobs: {str(e)}')
            self.monitoring.record_error('list_jobs', str(e))
            return []

    def pause_job(self, job_id: str) -> bool:
        """Pause a backup job"""
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f'Paused backup job: {job_id}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to pause job {job_id}: {str(e)}')
            self.monitoring.record_error('pause_job', str(e))
            return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused backup job"""
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f'Resumed backup job: {job_id}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to resume job {job_id}: {str(e)}')
            self.monitoring.record_error('resume_job', str(e))
            return False
