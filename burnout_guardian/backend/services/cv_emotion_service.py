"""
Computer Vision Emotion Detection Service
Uses DeepFace for webcam-based emotion detection
"""

import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models.user_model import EmotionCapture
from config import settings
from loguru import logger

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    logger.warning("DeepFace not available - CV features disabled")


class CVEmotionService:
    """Computer vision-based emotion detection"""
    
    def __init__(self, db: Session):
        self.db = db
        self.enabled = settings.CV_ENABLED and DEEPFACE_AVAILABLE
    
    def capture_emotion(
        self,
        user_id: str,
        image_path: Optional[str] = None,
        use_webcam: bool = True
    ) -> Optional[EmotionCapture]:
        """Capture and analyze emotion from image or webcam"""
        
        if not self.enabled:
            logger.warning("CV emotion detection is disabled")
            return None
        
        try:
            # Capture image
            if use_webcam and image_path is None:
                image_path = self._capture_from_webcam()
                if not image_path:
                    return None
            
            # Analyze emotions
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend=settings.DEEPFACE_BACKEND
            )
            
            if isinstance(result, list):
                result = result[0]
            
            emotions = result.get('emotion', {})
            
            # Calculate stress proxy (angry + fear + sad)
            stress_proxy = (
                emotions.get('angry', 0) +
                emotions.get('fear', 0) +
                emotions.get('sad', 0)
            ) / 100.0
            
            # Calculate emotional stability index
            # Higher neutral and happy = more stable
            emotional_stability = (
                emotions.get('happy', 0) * 0.5 +
                emotions.get('neutral', 0) * 0.3 +
                (100 - stress_proxy * 100) * 0.2
            ) / 100.0
            
            # Create emotion capture record
            capture = EmotionCapture(
                user_id=user_id,
                happy=emotions.get('happy', 0) / 100.0,
                sad=emotions.get('sad', 0) / 100.0,
                angry=emotions.get('angry', 0) / 100.0,
                neutral=emotions.get('neutral', 0) / 100.0,
                fear=emotions.get('fear', 0) / 100.0,
                surprise=emotions.get('surprise', 0) / 100.0,
                disgust=emotions.get('disgust', 0) / 100.0,
                stress_proxy=stress_proxy,
                emotional_stability_index=emotional_stability,
                confidence_score=result.get('face_confidence', 0.8),
                face_detected=True
            )
            
            # Save to database
            self.db.add(capture)
            self.db.commit()
            self.db.refresh(capture)
            
            logger.info(f"Emotion captured for user {user_id} - Stability: {emotional_stability:.2f}")
            
            return capture
            
        except Exception as e:
            logger.error(f"Emotion capture failed: {e}")
            return None
    
    def _capture_from_webcam(self) -> Optional[str]:
        """Capture image from webcam"""
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                logger.error("Cannot open webcam")
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.error("Cannot read frame from webcam")
                return None
            
            # Save temporary image
            temp_path = f".cache/webcam_capture_{datetime.utcnow().timestamp()}.jpg"
            cv2.imwrite(temp_path, frame)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Webcam capture failed: {e}")
            return None
    
    def get_emotion_history(
        self,
        user_id: str,
        days: int = 7
    ) -> list:
        """Get emotion capture history"""
        
        from datetime import timedelta
        from sqlalchemy import and_
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        captures = self.db.query(EmotionCapture).filter(
            and_(
                EmotionCapture.user_id == user_id,
                EmotionCapture.captured_at >= start_date
            )
        ).order_by(EmotionCapture.captured_at.desc()).all()
        
        return [c.to_dict() for c in captures]
