import pytest
import numpy as np
import torch
from src.ai_modules.deepfake.model import DeepfakeDetector
from src.ai_modules.malware.static_analyzer import StaticAnalyzer
from src.ai_modules.malware.dynamic_analyzer import DynamicAnalyzer
from src.ai_modules.threat.detector import ThreatDetector

@pytest.fixture
def deepfake_detector():
    return DeepfakeDetector()

@pytest.fixture
def static_analyzer():
    return StaticAnalyzer()

@pytest.fixture
def dynamic_analyzer():
    return DynamicAnalyzer()

@pytest.fixture
def threat_detector():
    return ThreatDetector()

def test_deepfake_detector_inference(deepfake_detector):
    # Create dummy image data
    dummy_image = np.random.rand(224, 224, 3)
    dummy_image = torch.tensor(dummy_image).float().permute(2, 0, 1).unsqueeze(0)
    
    # Run inference
    with torch.no_grad():
        prediction = deepfake_detector.predict(dummy_image)
    
    assert isinstance(prediction, dict)
    assert 'is_deepfake' in prediction
    assert 'confidence' in prediction
    assert isinstance(prediction['confidence'], float)
    assert 0 <= prediction['confidence'] <= 1

def test_static_analyzer(static_analyzer, tmp_path):
    # Create test file
    test_file = tmp_path / "test.exe"
    test_file.write_bytes(b"MZ" + b"\x00" * 1024)  # Simple PE file header
    
    # Run analysis
    results = static_analyzer.analyze(str(test_file))
    
    assert isinstance(results, dict)
    assert 'file_type' in results
    assert 'signatures' in results
    assert 'risk_score' in results
    assert isinstance(results['risk_score'], (int, float))

def test_dynamic_analyzer(dynamic_analyzer, tmp_path):
    # Create test file
    test_file = tmp_path / "test.exe"
    test_file.write_bytes(b"MZ" + b"\x00" * 1024)
    
    # Run analysis
    results = dynamic_analyzer.analyze(str(test_file))
    
    assert isinstance(results, dict)
    assert 'behaviors' in results
    assert 'network_activity' in results
    assert 'file_operations' in results

def test_threat_detector_integration(threat_detector, tmp_path):
    # Create test file
    test_file = tmp_path / "test.jpg"
    test_file.write_bytes(b"JFIF" + b"\x00" * 1024)  # Simple JPEG header
    
    # Run full threat analysis
    results = threat_detector.analyze_threat(str(test_file))
    
    assert isinstance(results, dict)
    assert 'threat_level' in results
    assert 'threats_found' in results
    assert isinstance(results['threats_found'], list)
    assert 'analysis_time' in results

def test_model_performance(deepfake_detector):
    # Test model performance with batch processing
    batch_size = 4
    dummy_batch = torch.randn(batch_size, 3, 224, 224)
    
    # Measure inference time
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    
    start_time.record()
    with torch.no_grad():
        predictions = deepfake_detector.predict_batch(dummy_batch)
    end_time.record()
    
    torch.cuda.synchronize()
    inference_time = start_time.elapsed_time(end_time)
    
    assert inference_time < 1000  # Less than 1 second for batch
    assert len(predictions) == batch_size

def test_threat_detection_accuracy(threat_detector, tmp_path):
    # Create test files with known patterns
    malware_file = tmp_path / "malware.exe"
    malware_file.write_bytes(b"MZ" + b"malicious_pattern" + b"\x00" * 1024)
    
    clean_file = tmp_path / "clean.exe"
    clean_file.write_bytes(b"MZ" + b"clean_pattern" + b"\x00" * 1024)
    
    # Test malware detection
    malware_results = threat_detector.analyze_threat(str(malware_file))
    assert malware_results['threat_level'] > 70  # High threat level
    
    # Test clean file
    clean_results = threat_detector.analyze_threat(str(clean_file))
    assert clean_results['threat_level'] < 30  # Low threat level
