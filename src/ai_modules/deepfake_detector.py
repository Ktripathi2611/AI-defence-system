import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import time
import os

# Initialize the detector as a global instance
_detector = None

def get_detector():
    """Get or create the global detector instance"""
    global _detector
    if _detector is None:
        _detector = DeepFakeDetector()
    return _detector

def analyze_deepfake(filepath):
    """
    Analyze a file for potential deepfake content.
    This is the main function that should be imported by other modules.
    """
    detector = get_detector()
    return detector.analyze_media(filepath)

class DeepFakeDetector:
    def __init__(self):
        self.model = None  # Placeholder for ML model
        
    def analyze_media(self, filepath):
        """
        Analyze media file for potential deepfake artifacts
        Returns a dict with analysis results
        """
        media_type = self._get_media_type(filepath)
        
        if media_type == 'image':
            return self._analyze_image(filepath)
        elif media_type == 'video':
            return self._analyze_video(filepath)
        elif media_type == 'audio':
            return self._analyze_audio(filepath)
        else:
            raise ValueError(f"Unsupported media type for file: {filepath}")
    
    def _get_media_type(self, filepath):
        """Determine the type of media file"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv'}
        audio_extensions = {'.mp3', '.wav', '.m4a'}
        
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in image_extensions:
            return 'image'
        elif ext in video_extensions:
            return 'video'
        elif ext in audio_extensions:
            return 'audio'
        else:
            return 'unknown'
    
    def _analyze_image(self, filepath):
        """
        Analyze image for potential deepfake artifacts
        This is a placeholder implementation - replace with actual ML model
        """
        try:
            img = Image.open(filepath)
            img_array = np.array(img)
            
            # Perform various analyses
            noise_level = self._analyze_noise(img_array)
            blur_level = self._analyze_blur(img_array)
            pixel_inconsistencies = self._analyze_pixel_inconsistencies(img_array)
            
            # Calculate confidence score (placeholder)
            confidence_score = 0.8  # Example score
            
            return {
                'is_deepfake': confidence_score > 0.7,
                'confidence_score': confidence_score,
                'analysis_details': {
                    'noise_level': noise_level,
                    'blur_level': blur_level,
                    'pixel_inconsistencies': pixel_inconsistencies
                }
            }
            
        except Exception as e:
            return {
                'error': f"Failed to analyze image: {str(e)}",
                'is_deepfake': None,
                'confidence_score': None
            }
    
    def _analyze_video(self, filepath):
        """
        Analyze video for potential deepfake artifacts
        This is a placeholder implementation - replace with actual ML model
        """
        try:
            cap = cv2.VideoCapture(filepath)
            frame_scores = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Analyze frame
                noise_level = self._analyze_noise(frame_rgb)
                blur_level = self._analyze_blur(frame_rgb)
                pixel_inconsistencies = self._analyze_pixel_inconsistencies(frame_rgb)
                
                # Calculate frame score (placeholder)
                frame_score = 0.7  # Example score
                frame_scores.append(frame_score)
            
            cap.release()
            
            # Calculate overall video score
            if frame_scores:
                confidence_score = np.mean(frame_scores)
            else:
                confidence_score = 0.0
            
            return {
                'is_deepfake': confidence_score > 0.7,
                'confidence_score': confidence_score,
                'analysis_details': {
                    'frame_scores': frame_scores,
                    'analyzed_frames': len(frame_scores)
                }
            }
            
        except Exception as e:
            return {
                'error': f"Failed to analyze video: {str(e)}",
                'is_deepfake': None,
                'confidence_score': None
            }
    
    def _analyze_audio(self, filepath):
        """
        Analyze audio for potential deepfake artifacts
        This is a placeholder implementation - replace with actual ML model
        """
        return {
            'is_deepfake': False,
            'confidence_score': 0.1,
            'analysis_details': {
                'note': 'Audio analysis not yet implemented'
            }
        }
    
    def _analyze_noise(self, img_array):
        """Analyze noise patterns in the image"""
        try:
            # Convert to grayscale if it's a color image
            if len(img_array.shape) > 2:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply Laplacian filter
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            noise_score = np.var(laplacian)
            
            return noise_score
            
        except Exception:
            return 0.0
    
    def _analyze_blur(self, img_array):
        """Analyze blur levels in the image"""
        try:
            # Convert to grayscale if it's a color image
            if len(img_array.shape) > 2:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate variance of Laplacian
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return blur_score
            
        except Exception:
            return 0.0
    
    def _analyze_pixel_inconsistencies(self, img_array):
        """Analyze pixel-level inconsistencies"""
        try:
            # Convert to grayscale if it's a color image
            if len(img_array.shape) > 2:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply Sobel edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # Calculate inconsistency score
            inconsistency_score = np.mean(gradient_magnitude)
            
            return inconsistency_score
            
        except Exception:
            return 0.0
