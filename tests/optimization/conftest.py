import pytest
import redis
import psutil
import torch
from unittest.mock import Mock, patch

@pytest.fixture(autouse=True)
def mock_redis_client():
    """Mock Redis client for all tests"""
    with patch('redis.from_url') as mock:
        mock.return_value = Mock(spec=redis.Redis)
        yield mock

@pytest.fixture(autouse=True)
def mock_psutil():
    """Mock psutil for all tests"""
    with patch.multiple(psutil,
        cpu_percent=Mock(return_value=50.0),
        cpu_count=Mock(return_value=8),
        getloadavg=Mock(return_value=(1.5, 1.2, 1.0)),
        cpu_times=Mock(return_value=Mock(user=1000.0, system=500.0, idle=2000.0)),
        virtual_memory=Mock(return_value=Mock(
            total=16000000000,
            available=8000000000,
            used=8000000000,
            percent=50.0
        )),
        swap_memory=Mock(return_value=Mock(
            total=8000000000,
            used=1000000000,
            percent=12.5
        )),
        disk_usage=Mock(return_value=Mock(
            total=1000000000000,
            used=400000000000,
            free=600000000000,
            percent=40.0
        )),
        disk_io_counters=Mock(return_value=Mock(
            read_bytes=1000000,
            write_bytes=500000,
            read_count=1000,
            write_count=500
        )),
        net_io_counters=Mock(return_value=Mock(
            bytes_sent=1000000,
            bytes_recv=2000000,
            packets_sent=1000,
            packets_recv=2000
        )),
        net_connections=Mock(return_value=[Mock() for _ in range(100)])
    ):
        yield

@pytest.fixture(autouse=True)
def mock_torch():
    """Mock PyTorch for all tests"""
    if not hasattr(torch, 'cuda'):
        torch.cuda = Mock()
    
    torch.cuda.is_available = Mock(return_value=True)
    torch.cuda.device_count = Mock(return_value=2)
    torch.cuda.get_device_properties = Mock(return_value=Mock(
        name='NVIDIA Test GPU',
        total_memory=8589934592,  # 8GB
        major=8,
        minor=0
    ))
    torch.cuda.memory_stats = Mock(return_value={
        'allocated_bytes.all.current': 2147483648  # 2GB
    })
    
    yield torch

@pytest.fixture
def sample_query():
    """Sample SQL query for testing"""
    return """
    SELECT u.name, o.order_date, p.product_name
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date > '2024-01-01'
    """

@pytest.fixture
def sample_query_plan():
    """Sample query execution plan"""
    return [
        "Nested Loop  (cost=0.00..32.97 rows=1 width=551)",
        "  ->  Index Scan using users_pkey on users  (cost=0.00..8.27 rows=1 width=551)",
        "  ->  Index Only Scan using orders_user_id_idx on orders  (cost=0.00..8.27 rows=1 width=551)",
        "Planning Time: 0.152 ms",
        "Execution Time: 0.258 ms"
    ]
