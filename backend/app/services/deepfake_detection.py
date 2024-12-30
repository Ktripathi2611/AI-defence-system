from typing import Dict, List, Optional
import imghdr
from backend.app.core.config import settings

class DeepfakeDetectionService:
    def __init__(self):
        # Initialize basic detection rules
        self.suspicious_image_sizes = {
            'small': 50 * 1024,  # 50KB
            'large': 10 * 1024 * 1024  # 10MB
        }
        
        self.valid_image_types = {'jpeg', 'png', 'gif', 'bmp'}
        self.valid_video_types = {'mp4', 'avi', 'mov', 'wmv'}
        
        self.stats = {
            'images_analyzed': 0,
            'videos_analyzed': 0,
            'deepfakes_detected': 0
        }
    
    async def analyze_image(self, image_content: bytes, file_name: str, metadata: dict = {}) -> Dict:
        """
        Analyze an image for potential deepfake manipulation
        """
        try:
            self.stats['images_analyzed'] += 1
            
            # Basic checks
            file_ext = file_name[file_name.rfind('.'):].lower() if '.' in file_name else ''
            file_size = len(image_content)
            detected_type = imghdr.what(None, image_content)
            
            # Collect anomalies
            anomalies = []
            
            # Check file size
            if file_size < self.suspicious_image_sizes['small']:
                anomalies.append("Suspiciously small file size")
            elif file_size > self.suspicious_image_sizes['large']:
                anomalies.append("Unusually large file size")
            
            # Check file type
            if not detected_type:
                anomalies.append("Unable to determine image type")
            elif detected_type not in self.valid_image_types:
                anomalies.append(f"Unsupported image type: {detected_type}")
            elif file_ext[1:] != detected_type:
                anomalies.append(f"File extension mismatch: {file_ext} vs {detected_type}")
            
            # Calculate manipulation score
            manipulation_score = len(anomalies) / 3  # Normalize by number of checks
            is_deepfake = manipulation_score > 0.3
            
            if is_deepfake:
                self.stats['deepfakes_detected'] += 1
            
            return {
                "is_deepfake": is_deepfake,
                "confidence": manipulation_score,
                "details": {
                    "anomalies": anomalies,
                    "file_info": {
                        "name": file_name,
                        "size": file_size,
                        "detected_type": detected_type
                    }
                },
                "safety_recommendations": [
                    "Verify the image source",
                    "Look for visual inconsistencies",
                    "Check metadata for editing traces"
                ]
            }
        except Exception as e:
            raise Exception(f"Error in image analysis: {str(e)}")

    async def analyze_video(self, video_content: bytes, file_name: str, metadata: dict = {}) -> Dict:
        """
        Analyze a video for potential deepfake manipulation
        """
        try:
            self.stats['videos_analyzed'] += 1
            
            # Basic checks
            file_ext = file_name[file_name.rfind('.'):].lower() if '.' in file_name else ''
            file_size = len(video_content)
            
            # Collect anomalies
            anomalies = []
            
            # Check file extension
            if file_ext[1:] not in self.valid_video_types:
                anomalies.append(f"Unsupported video format: {file_ext}")
            
            # Check file size
            if file_size < 100 * 1024:  # 100KB
                anomalies.append("Suspiciously small video size")
            elif file_size > 100 * 1024 * 1024:  # 100MB
                anomalies.append("Unusually large video size")
            
            # Calculate manipulation score
            manipulation_score = len(anomalies) / 2  # Normalize by number of checks
            is_deepfake = manipulation_score > 0.3
            
            if is_deepfake:
                self.stats['deepfakes_detected'] += 1
            
            return {
                "is_deepfake": is_deepfake,
                "confidence": manipulation_score,
                "details": {
                    "anomalies": anomalies,
                    "file_info": {
                        "name": file_name,
                        "size": file_size,
                        "format": file_ext[1:] if file_ext else "unknown"
                    }
                },
                "safety_recommendations": [
                    "Verify the video source",
                    "Look for audio-visual sync issues",
                    "Check for unnatural movements",
                    "Be cautious of viral videos from unknown sources"
                ]
            }
        except Exception as e:
            raise Exception(f"Error in video analysis: {str(e)}")

    async def get_stats(self) -> Dict[str, int]:
        """
        Get deepfake detection statistics
        """
        return self.stats

# Create a singleton instance
deepfake_detection_service = DeepfakeDetectionService()
