import psutil
import torch
import uuid
import requests
from typing import Dict, Optional
import logging
from ..utils.monitoring import MonitoringService
from datetime import datetime
import threading
import time

class Worker:
    def __init__(self, master_url: str):
        self.worker_id = str(uuid.uuid4())
        self.master_url = master_url
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()
        self.capabilities = self._detect_capabilities()
        self.current_task = None
        self.heartbeat_interval = 10  # seconds
        self._stop_heartbeat = False
        self._start_heartbeat_thread()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for worker"""
        logger = logging.getLogger(f'worker_{self.worker_id}')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f'worker_{self.worker_id}.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _detect_capabilities(self) -> Dict:
        """Detect worker capabilities"""
        try:
            capabilities = {
                'cpu_cores': psutil.cpu_count(),
                'memory': psutil.virtual_memory().total,
                'gpu': torch.cuda.is_available(),
                'gpu_info': None
            }

            if capabilities['gpu']:
                capabilities['gpu_info'] = {
                    'name': torch.cuda.get_device_name(0),
                    'count': torch.cuda.device_count(),
                    'memory': torch.cuda.get_device_properties(0).total_memory
                }

            return capabilities
        except Exception as e:
            self.logger.error(f'Failed to detect capabilities: {str(e)}')
            self.monitoring.record_error('capability_detection', str(e))
            return {}

    def _start_heartbeat_thread(self) -> None:
        """Start heartbeat thread"""
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to master"""
        while not self._stop_heartbeat:
            try:
                self.send_heartbeat()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f'Heartbeat error: {str(e)}')
                time.sleep(self.heartbeat_interval)

    def send_heartbeat(self) -> bool:
        """Send heartbeat to master"""
        try:
            status = self._get_current_status()
            response = requests.post(
                f'{self.master_url}/worker/heartbeat',
                json={
                    'worker_id': self.worker_id,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f'Failed to send heartbeat: {str(e)}')
            self.monitoring.record_error('heartbeat', str(e))
            return False

    def _get_current_status(self) -> Dict:
        """Get current worker status"""
        try:
            status = {
                'cpu_usage': psutil.cpu_percent() / 100,
                'memory_usage': psutil.virtual_memory().percent / 100,
                'load': 1 if self.current_task else 0,
                'task_id': self.current_task,
                'gpu_memory': None
            }

            if torch.cuda.is_available():
                status['gpu_memory'] = {
                    'total': torch.cuda.get_device_properties(0).total_memory,
                    'allocated': torch.cuda.memory_allocated(),
                    'cached': torch.cuda.memory_cached()
                }

            return status
        except Exception as e:
            self.logger.error(f'Failed to get status: {str(e)}')
            self.monitoring.record_error('status_check', str(e))
            return {}

    def register_with_master(self) -> bool:
        """Register worker with master node"""
        try:
            response = requests.post(
                f'{self.master_url}/worker/register',
                json={
                    'worker_id': self.worker_id,
                    'capabilities': self.capabilities
                }
            )
            success = response.status_code == 200
            if success:
                self.logger.info('Successfully registered with master')
            else:
                self.logger.error('Failed to register with master')
            return success
        except Exception as e:
            self.logger.error(f'Failed to register with master: {str(e)}')
            self.monitoring.record_error('registration', str(e))
            return False

    def process_task(self, task: Dict) -> Optional[Dict]:
        """Process a task"""
        try:
            self.current_task = task['task_id']
            self.logger.info(f'Processing task: {self.current_task}')

            # Process the task based on its type
            if task['type'] == 'scan':
                result = self._process_scan_task(task)
            elif task['type'] == 'analyze':
                result = self._process_analysis_task(task)
            else:
                raise ValueError(f"Unknown task type: {task['type']}")

            self.current_task = None
            return result
        except Exception as e:
            self.logger.error(f'Failed to process task: {str(e)}')
            self.monitoring.record_error('task_processing', str(e))
            self.current_task = None
            return None

    def _process_scan_task(self, task: Dict) -> Dict:
        """Process a scan task"""
        # Implement scan-specific processing
        pass

    def _process_analysis_task(self, task: Dict) -> Dict:
        """Process an analysis task"""
        # Implement analysis-specific processing
        pass

    def shutdown(self) -> None:
        """Shutdown worker gracefully"""
        try:
            self._stop_heartbeat = True
            if self.heartbeat_thread:
                self.heartbeat_thread.join()
            
            # Notify master of shutdown
            requests.post(
                f'{self.master_url}/worker/shutdown',
                json={'worker_id': self.worker_id}
            )
            
            self.logger.info('Worker shutdown complete')
        except Exception as e:
            self.logger.error(f'Error during shutdown: {str(e)}')
            self.monitoring.record_error('shutdown', str(e))
