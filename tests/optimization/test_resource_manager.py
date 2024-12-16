import pytest
from unittest.mock import Mock, patch
import psutil
import torch
import threading
import time
from src.optimization.resource_manager import ResourceManager

@pytest.fixture
def resource_manager():
    """Create a resource manager instance"""
    return ResourceManager()

class TestResourceManager:
    def test_cpu_stats(self, resource_manager):
        """Test CPU statistics collection"""
        with patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.cpu_count') as mock_count, \
             patch('psutil.getloadavg') as mock_load, \
             patch('psutil.cpu_times') as mock_times:
            
            mock_cpu.return_value = 50.0
            mock_count.return_value = 8
            mock_load.return_value = (1.5, 1.2, 1.0)
            mock_times.return_value = Mock(
                user=1000.0,
                system=500.0,
                idle=2000.0
            )

            stats = resource_manager._get_cpu_stats()
            
            assert stats['percent'] == 50.0
            assert stats['cores'] == 8
            assert stats['load_avg'] == (1.5, 1.2, 1.0)
            assert stats['times']['user'] == 1000.0
            assert stats['times']['system'] == 500.0
            assert stats['times']['idle'] == 2000.0

    def test_memory_stats(self, resource_manager):
        """Test memory statistics collection"""
        with patch('psutil.virtual_memory') as mock_vm, \
             patch('psutil.swap_memory') as mock_swap:
            
            mock_vm.return_value = Mock(
                total=16000000000,
                available=8000000000,
                used=8000000000,
                percent=50.0
            )
            mock_swap.return_value = Mock(
                total=8000000000,
                used=1000000000,
                percent=12.5
            )

            stats = resource_manager._get_memory_stats()
            
            assert stats['total'] == 16000000000
            assert stats['available'] == 8000000000
            assert stats['used'] == 8000000000
            assert stats['percent'] == 50.0
            assert stats['swap']['total'] == 8000000000
            assert stats['swap']['used'] == 1000000000
            assert stats['swap']['percent'] == 12.5

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_stats(self, resource_manager):
        """Test GPU statistics collection"""
        stats = resource_manager._get_gpu_stats()
        
        assert stats['available'] is True
        assert 'device_count' in stats
        assert isinstance(stats['devices'], dict)
        
        for device_id, device_stats in stats['devices'].items():
            assert 'name' in device_stats
            assert 'memory_total' in device_stats
            assert 'memory_used' in device_stats
            assert 'memory_free' in device_stats
            assert 'compute_capability' in device_stats

    def test_disk_stats(self, resource_manager):
        """Test disk statistics collection"""
        with patch('psutil.disk_usage') as mock_usage, \
             patch('psutil.disk_io_counters') as mock_io:
            
            mock_usage.return_value = Mock(
                total=1000000000000,
                used=400000000000,
                free=600000000000,
                percent=40.0
            )
            mock_io.return_value = Mock(
                read_bytes=1000000,
                write_bytes=500000,
                read_count=1000,
                write_count=500
            )

            stats = resource_manager._get_disk_stats()
            
            assert stats['total'] == 1000000000000
            assert stats['used'] == 400000000000
            assert stats['free'] == 600000000000
            assert stats['percent'] == 40.0
            assert stats['io']['read_bytes'] == 1000000
            assert stats['io']['write_bytes'] == 500000
            assert stats['io']['read_count'] == 1000
            assert stats['io']['write_count'] == 500

    def test_network_stats(self, resource_manager):
        """Test network statistics collection"""
        with patch('psutil.net_io_counters') as mock_net, \
             patch('psutil.net_connections') as mock_conn:
            
            mock_net.return_value = Mock(
                bytes_sent=1000000,
                bytes_recv=2000000,
                packets_sent=1000,
                packets_recv=2000
            )
            mock_conn.return_value = [Mock() for _ in range(100)]

            stats = resource_manager._get_network_stats()
            
            assert stats['bytes_sent'] == 1000000
            assert stats['bytes_recv'] == 2000000
            assert stats['packets_sent'] == 1000
            assert stats['packets_recv'] == 2000
            assert stats['connections'] == 100

    def test_resource_monitoring(self, resource_manager):
        """Test resource monitoring thread"""
        # Start monitoring
        resource_manager._start_monitoring_thread()
        
        # Let it run for a bit
        time.sleep(2)
        
        # Check if monitoring is active
        assert resource_manager.monitor_thread.is_alive()
        
        # Shutdown
        resource_manager.shutdown()
        
        # Verify thread has stopped
        assert not resource_manager.monitor_thread.is_alive()

    def test_resource_limits(self, resource_manager):
        """Test resource limit checking"""
        with patch.object(resource_manager, 'get_resource_stats') as mock_stats:
            mock_stats.return_value = {
                'cpu': {'percent': 90},
                'memory': {'percent': 95},
                'gpu': {
                    'available': True,
                    'devices': {
                        0: {'memory_used': 8000, 'memory_total': 8192}
                    }
                }
            }

            # This should trigger warnings
            resource_manager._check_resource_limits(mock_stats.return_value)

    def test_optimize_resources(self, resource_manager):
        """Test resource optimization recommendations"""
        with patch.object(resource_manager, 'get_resource_stats') as mock_stats:
            mock_stats.return_value = {
                'cpu': {'percent': 85},
                'memory': {'percent': 90},
                'gpu': {
                    'available': True,
                    'devices': {
                        0: {'memory_used': 7500, 'memory_total': 8192}
                    }
                },
                'disk': {'percent': 90}
            }

            recommendations = resource_manager.optimize_resources()
            
            assert len(recommendations) > 0
            assert any('CPU' in rec for rec in recommendations)
            assert any('memory' in rec.lower() for rec in recommendations)
            assert any('GPU' in rec for rec in recommendations)
            assert any('Disk' in rec for rec in recommendations)

    def test_error_handling(self, resource_manager):
        """Test error handling in resource management"""
        with patch('psutil.cpu_percent', side_effect=Exception("CPU error")), \
             patch('psutil.virtual_memory', side_effect=Exception("Memory error")):
            
            # Should handle errors gracefully
            stats = resource_manager.get_resource_stats()
            assert isinstance(stats, dict)

    def test_concurrent_resource_access(self, resource_manager):
        """Test concurrent access to resource statistics"""
        def get_stats():
            return resource_manager.get_resource_stats()

        # Create multiple threads to access resources
        threads = []
        results = []
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(get_stats()))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all threads got valid results
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)

    def test_resource_manager_shutdown(self, resource_manager):
        """Test clean shutdown of resource manager"""
        # Start monitoring
        resource_manager._start_monitoring_thread()
        
        # Verify monitoring is running
        assert resource_manager.monitor_thread.is_alive()
        
        # Shutdown
        resource_manager.shutdown()
        
        # Verify monitoring has stopped
        assert not resource_manager.monitor_thread.is_alive()
        assert resource_manager._stop_monitoring is True
