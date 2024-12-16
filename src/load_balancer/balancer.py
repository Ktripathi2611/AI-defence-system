import psutil
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import torch
from ..utils.monitoring import MonitoringService
import logging

class LoadBalancer:
    def __init__(self):
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()
        self.worker_nodes = {}
        self.task_history = []
        self.max_history_size = 1000

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for load balancer"""
        logger = logging.getLogger('load_balancer')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('load_balancer.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def register_worker(self, worker_id: str, capabilities: Dict) -> bool:
        """Register a new worker node"""
        try:
            self.worker_nodes[worker_id] = {
                'capabilities': capabilities,
                'current_load': 0,
                'tasks_processed': 0,
                'last_heartbeat': datetime.now(),
                'status': 'active',
                'gpu_memory': self._get_gpu_memory() if capabilities.get('gpu') else None
            }
            self.logger.info(f'Registered new worker: {worker_id}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to register worker {worker_id}: {str(e)}')
            self.monitoring.record_error('worker_registration', str(e))
            return False

    def _get_gpu_memory(self) -> Optional[Dict]:
        """Get GPU memory status"""
        try:
            if torch.cuda.is_available():
                return {
                    'total': torch.cuda.get_device_properties(0).total_memory,
                    'allocated': torch.cuda.memory_allocated(),
                    'cached': torch.cuda.memory_cached()
                }
            return None
        except Exception as e:
            self.logger.error(f'Failed to get GPU memory: {str(e)}')
            return None

    def update_worker_status(self, worker_id: str, status: Dict) -> bool:
        """Update worker node status"""
        try:
            if worker_id in self.worker_nodes:
                self.worker_nodes[worker_id].update({
                    'current_load': status.get('load', 0),
                    'last_heartbeat': datetime.now(),
                    'cpu_usage': status.get('cpu_usage'),
                    'memory_usage': status.get('memory_usage'),
                    'gpu_memory': status.get('gpu_memory')
                })
                return True
            return False
        except Exception as e:
            self.logger.error(f'Failed to update worker status {worker_id}: {str(e)}')
            self.monitoring.record_error('worker_status_update', str(e))
            return False

    def select_worker(self, task_requirements: Dict) -> Optional[str]:
        """Select the most suitable worker for a task"""
        try:
            suitable_workers = []
            for worker_id, info in self.worker_nodes.items():
                if self._is_worker_suitable(info, task_requirements):
                    suitable_workers.append((worker_id, self._calculate_worker_score(info)))

            if not suitable_workers:
                return None

            # Sort by score (higher is better) and return the best worker
            return max(suitable_workers, key=lambda x: x[1])[0]
        except Exception as e:
            self.logger.error(f'Failed to select worker: {str(e)}')
            self.monitoring.record_error('worker_selection', str(e))
            return None

    def _is_worker_suitable(self, worker_info: Dict, requirements: Dict) -> bool:
        """Check if worker meets task requirements"""
        if worker_info['status'] != 'active':
            return False

        if requirements.get('gpu') and not worker_info['capabilities'].get('gpu'):
            return False

        if requirements.get('min_memory'):
            available_memory = worker_info['capabilities'].get('memory', 0) * (1 - worker_info['memory_usage'])
            if available_memory < requirements['min_memory']:
                return False

        return True

    def _calculate_worker_score(self, worker_info: Dict) -> float:
        """Calculate worker suitability score"""
        score = 100.0

        # Penalize based on current load
        score -= worker_info['current_load'] * 50

        # Penalize based on CPU usage
        score -= worker_info.get('cpu_usage', 0) * 30

        # Penalize based on memory usage
        score -= worker_info.get('memory_usage', 0) * 20

        # Bonus for GPU availability if present
        if worker_info['capabilities'].get('gpu'):
            gpu_memory = worker_info.get('gpu_memory', {})
            if gpu_memory:
                gpu_usage = gpu_memory.get('allocated', 0) / gpu_memory.get('total', 1)
                score += (1 - gpu_usage) * 20

        return max(0, score)

    def assign_task(self, task_id: str, worker_id: str) -> bool:
        """Assign task to worker"""
        try:
            if worker_id not in self.worker_nodes:
                return False

            self.worker_nodes[worker_id]['current_load'] += 1
            self.worker_nodes[worker_id]['tasks_processed'] += 1

            self.task_history.append({
                'task_id': task_id,
                'worker_id': worker_id,
                'timestamp': datetime.now(),
                'status': 'assigned'
            })

            # Maintain history size
            if len(self.task_history) > self.max_history_size:
                self.task_history = self.task_history[-self.max_history_size:]

            self.logger.info(f'Assigned task {task_id} to worker {worker_id}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to assign task {task_id}: {str(e)}')
            self.monitoring.record_error('task_assignment', str(e))
            return False

    def complete_task(self, task_id: str, worker_id: str, status: str = 'completed') -> bool:
        """Mark task as completed"""
        try:
            if worker_id in self.worker_nodes:
                self.worker_nodes[worker_id]['current_load'] = max(
                    0, self.worker_nodes[worker_id]['current_load'] - 1
                )

                for task in self.task_history:
                    if task['task_id'] == task_id:
                        task['status'] = status
                        task['completion_time'] = datetime.now()
                        break

                self.logger.info(f'Completed task {task_id} on worker {worker_id}')
                return True
            return False
        except Exception as e:
            self.logger.error(f'Failed to complete task {task_id}: {str(e)}')
            self.monitoring.record_error('task_completion', str(e))
            return False

    def get_worker_stats(self) -> Dict:
        """Get statistics about worker nodes"""
        try:
            return {
                'total_workers': len(self.worker_nodes),
                'active_workers': sum(1 for w in self.worker_nodes.values() if w['status'] == 'active'),
                'total_tasks_processed': sum(w['tasks_processed'] for w in self.worker_nodes.values()),
                'current_load': {
                    worker_id: info['current_load']
                    for worker_id, info in self.worker_nodes.items()
                }
            }
        except Exception as e:
            self.logger.error(f'Failed to get worker stats: {str(e)}')
            self.monitoring.record_error('worker_stats', str(e))
            return {}
