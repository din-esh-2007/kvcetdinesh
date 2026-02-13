"""
Feature Engineering Service
Computes behavioral features from raw calendar and activity data
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from backend.models.feature_model import BehavioralFeature, CalendarEvent
from backend.models.user_model import DailyCheckIn
from loguru import logger


class FeatureEngineeringService:
    """Compute behavioral features from raw data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_workload_features(
        self,
        user_id: str,
        date: datetime,
        events: List[CalendarEvent],
        checkin: Optional[DailyCheckIn] = None
    ) -> Dict:
        """Compute workload-related features"""
        
        # Filter events for the specific date
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_events = [
            e for e in events
            if day_start <= e.start_time < day_end
        ]
        
        # Meeting metrics
        meeting_events = [e for e in day_events if e.event_type == "meeting"]
        meeting_count = len(meeting_events)
        meeting_hours = sum(e.duration_minutes for e in meeting_events) / 60.0
        
        # Total work hours (estimate from calendar + check-in)
        calendar_hours = sum(e.duration_minutes for e in day_events) / 60.0
        
        if checkin and checkin.work_hours_planned:
            total_work_hours = checkin.work_hours_planned
        else:
            # Estimate: calendar time + 2 hours for non-calendared work
            total_work_hours = max(calendar_hours + 2.0, 8.0)
        
        # After-hours work (events outside 9 AM - 6 PM)
        work_start = day_start.replace(hour=9)
        work_end = day_start.replace(hour=18)
        
        after_hours_events = [
            e for e in day_events
            if e.start_time < work_start or e.end_time > work_end
        ]
        after_hours_work = sum(e.duration_minutes for e in after_hours_events) / 60.0
        
        # Task metrics (estimated from meeting density and check-in)
        if checkin:
            task_assigned_count = checkin.meeting_count_expected * 2  # Rough estimate
        else:
            task_assigned_count = meeting_count * 2
        
        task_completed_count = int(task_assigned_count * np.random.uniform(0.7, 0.95))
        
        # Deadline compression (higher meeting density = more compressed)
        deadline_compression_ratio = min(meeting_hours / max(total_work_hours, 1), 1.0)
        
        # Task switching rate (meetings per hour)
        task_switching_rate = meeting_count / max(total_work_hours, 1)
        
        # Communication volume (estimated)
        email_volume = int(meeting_count * np.random.uniform(5, 10))
        slack_messages = int(meeting_count * np.random.uniform(8, 15))
        
        # Response latency (estimated from meeting density)
        response_latency_avg = 15 * (1 + deadline_compression_ratio)
        
        return {
            "total_work_hours": round(total_work_hours, 2),
            "meeting_hours": round(meeting_hours, 2),
            "meeting_count": meeting_count,
            "after_hours_work": round(after_hours_work, 2),
            "task_assigned_count": task_assigned_count,
            "task_completed_count": task_completed_count,
            "deadline_compression_ratio": round(deadline_compression_ratio, 3),
            "task_switching_rate": round(task_switching_rate, 2),
            "email_volume": email_volume,
            "slack_message_count": slack_messages,
            "response_latency_avg": round(response_latency_avg, 1)
        }
    
    def compute_recovery_features(
        self,
        user_id: str,
        date: datetime,
        events: List[CalendarEvent],
        checkin: Optional[DailyCheckIn] = None,
        workload: Dict = None
    ) -> Dict:
        """Compute recovery-related features"""
        
        # Sleep hours from check-in or default
        if checkin:
            sleep_hours = checkin.sleep_hours
            sleep_consistency_score = 0.8  # Could compute from history
        else:
            sleep_hours = 7.5
            sleep_consistency_score = 0.7
        
        # Focus blocks (gaps between meetings)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_events = [
            e for e in events
            if day_start <= e.start_time < day_end and e.event_type == "meeting"
        ]
        
        # Sort events by start time
        day_events.sort(key=lambda e: e.start_time)
        
        # Calculate gaps between meetings
        gaps = []
        for i in range(len(day_events) - 1):
            gap_minutes = (day_events[i + 1].start_time - day_events[i].end_time).total_seconds() / 60
            if gap_minutes > 0:
                gaps.append(gap_minutes)
        
        longest_focus_block = max(gaps) if gaps else 120.0
        recovery_gap = np.mean(gaps) if gaps else 60.0
        
        # Weekend work ratio
        is_weekend = date.weekday() >= 5
        weekend_work_ratio = 0.3 if is_weekend and workload and workload["total_work_hours"] > 2 else 0.0
        
        # HRV index (estimated from sleep and stress)
        if checkin:
            stress_factor = checkin.stress_level / 10.0
            hrv_base = 60 * (1 - stress_factor * 0.3)
        else:
            hrv_base = 60
        
        hrv_index = hrv_base + (sleep_hours - 7.5) * 5
        hrv_index = np.clip(hrv_index, 20, 100)
        
        return {
            "longest_focus_block_minutes": round(longest_focus_block, 1),
            "recovery_gap_minutes": round(recovery_gap, 1),
            "weekend_work_ratio": round(weekend_work_ratio, 3),
            "sleep_hours": round(sleep_hours, 2),
            "sleep_consistency_score": round(sleep_consistency_score, 3),
            "hr_variability_index": round(hrv_index, 1)
        }
    
    def compute_performance_features(
        self,
        user_id: str,
        date: datetime,
        workload: Dict,
        recovery: Dict,
        checkin: Optional[DailyCheckIn] = None
    ) -> Dict:
        """Compute performance-related features"""
        
        # Fatigue factor from sleep deficit
        fatigue_factor = max(0, 7.5 - recovery["sleep_hours"]) / 5.0
        
        # Error rate increases with fatigue and task switching
        error_rate = 0.05 * fatigue_factor * (1 + workload["task_switching_rate"] / 10)
        error_rate = np.clip(error_rate, 0, 0.5)
        
        # Revision count
        revision_count = int(error_rate * 20 + np.random.poisson(1))
        
        # Decision reversals
        decision_reversals = int(error_rate * 10)
        
        # Output score (affected by energy level if available)
        if checkin:
            energy_factor = checkin.energy_level / 10.0
            output_base = 80 * energy_factor
        else:
            output_base = 75
        
        output_score = output_base - fatigue_factor * 10 - workload["task_switching_rate"] * 2
        output_score = np.clip(output_score, 40, 100)
        
        # Productivity volatility
        volatility = 0.15 + fatigue_factor * 0.1 + workload["task_switching_rate"] * 0.02
        volatility = np.clip(volatility, 0.05, 0.5)
        
        return {
            "error_rate": round(error_rate, 4),
            "revision_count": revision_count,
            "decision_reversal_count": decision_reversals,
            "output_score": round(output_score, 2),
            "productivity_volatility_index": round(volatility, 3)
        }
    
    def compute_derived_features(
        self,
        workload: Dict,
        recovery: Dict,
        performance: Dict
    ) -> Dict:
        """Compute derived composite features"""
        
        # Meeting density
        meeting_density = workload["meeting_count"] / max(workload["total_work_hours"], 1)
        
        # Load accumulation
        load_accumulation = (workload["total_work_hours"] - 8) / 8
        load_accumulation += workload["after_hours_work"] / 8
        load_accumulation = max(0, load_accumulation)
        
        # Recovery deficit
        sleep_deficit = max(0, 7.5 - recovery["sleep_hours"]) / 7.5
        focus_deficit = max(0, 90 - recovery["longest_focus_block_minutes"]) / 90
        recovery_deficit = (sleep_deficit + focus_deficit) / 2
        
        # Instability index
        instability = (
            workload["task_switching_rate"] / 10 * 0.3 +
            recovery_deficit * 0.3 +
            performance["error_rate"] * 10 * 0.2 +
            meeting_density * 0.2
        )
        instability = np.clip(instability, 0, 1)
        
        # Volatility acceleration
        volatility_accel = performance["productivity_volatility_index"] * load_accumulation
        
        return {
            "meeting_density_ratio": round(meeting_density, 3),
            "load_accumulation_rate": round(load_accumulation, 3),
            "recovery_deficit_score": round(recovery_deficit, 3),
            "instability_index": round(instability, 3),
            "volatility_acceleration": round(volatility_accel, 4)
        }
    
    def compute_all_features(
        self,
        user_id: str,
        date: datetime,
        events: List[CalendarEvent],
        checkin: Optional[DailyCheckIn] = None
    ) -> BehavioralFeature:
        """Compute all features and create BehavioralFeature object"""
        
        logger.info(f"Computing features for user {user_id} on {date.date()}")
        
        # Compute feature groups
        workload = self.compute_workload_features(user_id, date, events, checkin)
        recovery = self.compute_recovery_features(user_id, date, events, checkin, workload)
        performance = self.compute_performance_features(user_id, date, workload, recovery, checkin)
        derived = self.compute_derived_features(workload, recovery, performance)
        
        # Determine data source
        if checkin:
            data_source = "hybrid"
        else:
            data_source = "calendar"
        
        # Create BehavioralFeature object
        feature = BehavioralFeature(
            user_id=user_id,
            feature_date=date,
            day_index=0,  # Will be set by caller
            data_source=data_source,
            **workload,
            **recovery,
            **performance,
            **derived
        )
        
        logger.info(f"Features computed - Instability: {derived['instability_index']:.3f}")
        
        return feature
    
    def save_features(self, feature: BehavioralFeature) -> BehavioralFeature:
        """Save features to database"""
        
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        
        logger.info(f"Features saved for user {feature.user_id} on {feature.feature_date.date()}")
        
        return feature
