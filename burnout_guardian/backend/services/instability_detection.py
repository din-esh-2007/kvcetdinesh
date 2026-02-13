"""
Instability Detection Service
Real-time detection using Isolation Forest and Bayesian change-point detection
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from backend.models.feature_model import BehavioralFeature
from backend.models.stability_model import StabilityAssessment, BaselineMetric
from backend.models.user_model import User
from backend.config import settings
from loguru import logger


class InstabilityDetectionService:
    """Detect instability patterns using ML"""
    
    def __init__(self, db: Session):
        self.db = db
        self.isolation_forest = None
    
    def get_baseline_window(
        self,
        user_id: str,
        current_date: datetime,
        window_days: int = 7
    ) -> List[BehavioralFeature]:
        """Get baseline window features"""
        
        window_start = current_date - timedelta(days=window_days)
        
        features = self.db.query(BehavioralFeature).filter(
            and_(
                BehavioralFeature.user_id == user_id,
                BehavioralFeature.feature_date >= window_start,
                BehavioralFeature.feature_date < current_date
            )
        ).order_by(BehavioralFeature.feature_date).all()
        
        return features
    
    def compute_baseline_metrics(
        self,
        user_id: str,
        current_date: datetime,
        window_days: int = 7
    ) -> Optional[BaselineMetric]:
        """Compute and store baseline metrics"""
        
        features = self.get_baseline_window(user_id, current_date, window_days)
        
        if len(features) < 3:
            logger.warning(f"Insufficient data for baseline (need 3+ days, have {len(features)})")
            return None
        
        # Extract metrics
        work_hours = [f.total_work_hours for f in features]
        meeting_hours = [f.meeting_hours for f in features]
        task_switching = [f.task_switching_rate for f in features]
        sleep_hours = [f.sleep_hours for f in features]
        focus_blocks = [f.longest_focus_block_minutes for f in features]
        recovery_gaps = [f.recovery_gap_minutes for f in features]
        error_rates = [f.error_rate for f in features]
        output_scores = [f.output_score for f in features]
        
        # Compute stability and volatility from features
        instability_indices = [f.instability_index for f in features]
        volatility_indices = [f.productivity_volatility_index for f in features]
        
        # Create baseline metric
        baseline = BaselineMetric(
            user_id=user_id,
            window_start=features[0].feature_date,
            window_end=features[-1].feature_date,
            window_days=window_days,
            mean_stability=1 - np.mean(instability_indices),
            std_stability=np.std(instability_indices),
            mean_volatility=np.mean(volatility_indices),
            std_volatility=np.std(volatility_indices),
            mean_work_hours=np.mean(work_hours),
            mean_meeting_hours=np.mean(meeting_hours),
            mean_task_switching=np.mean(task_switching),
            mean_sleep_hours=np.mean(sleep_hours),
            mean_focus_block=np.mean(focus_blocks),
            mean_recovery_gap=np.mean(recovery_gaps),
            mean_error_rate=np.mean(error_rates),
            mean_output_score=np.mean(output_scores)
        )
        
        # Save to database
        self.db.add(baseline)
        self.db.commit()
        
        logger.info(f"Baseline computed for user {user_id}: stability={baseline.mean_stability:.3f}")
        
        return baseline
    
    def detect_anomaly_isolation_forest(
        self,
        user_id: str,
        current_feature: BehavioralFeature,
        baseline_features: List[BehavioralFeature]
    ) -> Tuple[int, float]:
        """Detect anomalies using Isolation Forest"""
        
        if len(baseline_features) < 3:
            return 0, 0.0
        
        # Extract feature vectors
        def feature_to_vector(f: BehavioralFeature) -> np.ndarray:
            return np.array([
                f.total_work_hours,
                f.meeting_hours,
                f.meeting_count,
                f.task_switching_rate,
                f.sleep_hours,
                f.longest_focus_block_minutes,
                f.error_rate * 100,
                f.instability_index,
                f.productivity_volatility_index,
                f.recovery_deficit_score
            ])
        
        # Build training data from baseline
        X_train = np.array([feature_to_vector(f) for f in baseline_features])
        
        # Current feature
        X_current = feature_to_vector(current_feature).reshape(1, -1)
        
        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=settings.ISOLATION_FOREST_CONTAMINATION,
            random_state=42,
            n_estimators=100
        )
        iso_forest.fit(X_train)
        
        # Predict
        prediction = iso_forest.predict(X_current)[0]
        anomaly_score = -iso_forest.score_samples(X_current)[0]
        
        # prediction: -1 for anomaly, 1 for normal
        is_anomaly = 1 if prediction == -1 else 0
        
        logger.info(f"Anomaly detection: is_anomaly={is_anomaly}, score={anomaly_score:.3f}")
        
        return is_anomaly, float(anomaly_score)
    
    def detect_change_point_bayesian(
        self,
        user_id: str,
        current_feature: BehavioralFeature,
        baseline_features: List[BehavioralFeature]
    ) -> Tuple[int, float]:
        """Detect change points using Bayesian approach"""
        
        if len(baseline_features) < 5:
            return 0, 0.0
        
        # Use instability index as the signal
        baseline_values = np.array([f.instability_index for f in baseline_features])
        current_value = current_feature.instability_index
        
        # Compute statistics
        baseline_mean = np.mean(baseline_values)
        baseline_std = np.std(baseline_values)
        
        if baseline_std == 0:
            baseline_std = 0.01
        
        # Z-score
        z_score = abs(current_value - baseline_mean) / baseline_std
        
        # Bayesian probability of change point
        # Using normal distribution assumption
        change_prob = 1 - stats.norm.cdf(z_score)
        
        # Threshold for change point (3 sigma)
        is_change_point = 1 if z_score > 3 else 0
        
        logger.info(f"Change point detection: is_change={is_change_point}, prob={change_prob:.3f}, z={z_score:.2f}")
        
        return is_change_point, float(change_prob)
    
    def compute_volatility_acceleration(
        self,
        user_id: str,
        current_feature: BehavioralFeature,
        baseline_features: List[BehavioralFeature]
    ) -> float:
        """Compute rate of change in volatility"""
        
        if len(baseline_features) < 2:
            return 0.0
        
        # Get recent volatility values
        recent_volatility = [f.productivity_volatility_index for f in baseline_features[-3:]]
        recent_volatility.append(current_feature.productivity_volatility_index)
        
        # Compute acceleration (second derivative approximation)
        if len(recent_volatility) >= 3:
            acceleration = recent_volatility[-1] - 2 * recent_volatility[-2] + recent_volatility[-3]
        else:
            acceleration = recent_volatility[-1] - recent_volatility[-2]
        
        return float(acceleration)
    
    def identify_top_contributors(
        self,
        current_feature: BehavioralFeature,
        baseline: Optional[BaselineMetric]
    ) -> List[str]:
        """Identify top contributing factors to instability"""
        
        contributors = []
        
        if baseline:
            # Compare current vs baseline
            if current_feature.meeting_density_ratio > 0.5:
                contributors.append("meeting_density")
            
            if current_feature.recovery_deficit_score > 0.5:
                contributors.append("recovery_deficit")
            
            if current_feature.task_switching_rate > baseline.mean_task_switching * 1.5:
                contributors.append("task_switching_rate")
            
            if current_feature.sleep_hours < baseline.mean_sleep_hours - 1:
                contributors.append("sleep_deficit")
            
            if current_feature.after_hours_work > 2:
                contributors.append("after_hours_work")
            
            if current_feature.error_rate > baseline.mean_error_rate * 1.5:
                contributors.append("error_rate")
        else:
            # Use absolute thresholds
            if current_feature.meeting_density_ratio > 0.5:
                contributors.append("meeting_density")
            if current_feature.recovery_deficit_score > 0.5:
                contributors.append("recovery_deficit")
            if current_feature.task_switching_rate > 5:
                contributors.append("task_switching_rate")
        
        return contributors[:5]  # Top 5
    
    def calculate_risk_probability(
        self,
        current_feature: BehavioralFeature,
        baseline: Optional[BaselineMetric],
        is_anomaly: int,
        is_change_point: int,
        volatility_accel: float
    ) -> Tuple[float, str]:
        """Calculate collapse risk probability"""
        
        # Base risk from instability index
        base_risk = current_feature.instability_index
        
        # Boost from anomaly detection
        if is_anomaly == 1:
            base_risk *= 1.3
        
        # Boost from change point
        if is_change_point == 1:
            base_risk *= 1.2
        
        # Boost from volatility acceleration
        if volatility_accel > 0.1:
            base_risk *= 1.15
        
        # Boost from recovery deficit
        base_risk += current_feature.recovery_deficit_score * 0.2
        
        # Boost from error rate
        base_risk += current_feature.error_rate * 2
        
        # Clip to [0, 1]
        risk_probability = np.clip(base_risk, 0, 1)
        
        # Determine risk level
        if risk_probability >= 0.85:
            risk_level = "critical"
        elif risk_probability >= 0.75:
            risk_level = "high"
        elif risk_probability >= 0.60:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return float(risk_probability), risk_level
    
    def detect_instability(
        self,
        user_id: str,
        current_date: datetime,
        current_feature: BehavioralFeature
    ) -> StabilityAssessment:
        """Main instability detection pipeline"""
        
        logger.info(f"Running instability detection for user {user_id} on {current_date.date()}")
        
        # Get baseline window
        baseline_features = self.get_baseline_window(
            user_id,
            current_date,
            settings.STABILITY_WINDOW_DAYS
        )
        
        # Compute baseline metrics
        baseline = self.compute_baseline_metrics(
            user_id,
            current_date,
            settings.STABILITY_WINDOW_DAYS
        )
        
        # Anomaly detection
        is_anomaly, anomaly_score = self.detect_anomaly_isolation_forest(
            user_id,
            current_feature,
            baseline_features
        )
        
        # Change point detection
        is_change_point, change_prob = self.detect_change_point_bayesian(
            user_id,
            current_feature,
            baseline_features
        )
        
        # Volatility acceleration
        volatility_accel = self.compute_volatility_acceleration(
            user_id,
            current_feature,
            baseline_features
        )
        
        # Calculate risk
        risk_probability, risk_level = self.calculate_risk_probability(
            current_feature,
            baseline,
            is_anomaly,
            is_change_point,
            volatility_accel
        )
        
        # Identify contributors
        top_contributors = self.identify_top_contributors(current_feature, baseline)
        
        # Compute stability index (inverse of instability)
        stability_index = 1 - current_feature.instability_index
        
        # Baseline deviation
        if baseline:
            baseline_deviation = abs(stability_index - baseline.mean_stability)
        else:
            baseline_deviation = 0.0
        
        # Create assessment
        assessment = StabilityAssessment(
            user_id=user_id,
            assessment_date=current_date,
            stability_index=stability_index,
            volatility=current_feature.productivity_volatility_index,
            acceleration=volatility_accel,
            risk_probability=risk_probability,
            risk_level=risk_level,
            top_contributors=top_contributors,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            is_change_point=is_change_point,
            change_point_probability=change_prob,
            baseline_deviation=baseline_deviation,
            baseline_window_start=baseline.window_start if baseline else None,
            baseline_window_end=baseline.window_end if baseline else None,
            behavioral_score=risk_probability,
            confidence_score=0.85
        )
        
        # Save assessment
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        logger.info(f"Instability detected - Risk: {risk_level} ({risk_probability:.2%})")
        
        return assessment
