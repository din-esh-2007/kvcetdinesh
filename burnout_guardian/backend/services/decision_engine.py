"""
Decision Engine
Autonomous intervention decision-making based on risk thresholds
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models.stability_model import StabilityAssessment
from backend.models.forecast_model import BurnoutForecast
from backend.models.intervention_model import Intervention, AuditLog
from backend.models.user_model import User
from backend.config import settings
from loguru import logger


class DecisionEngine:
    """Autonomous decision-making for interventions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_intervention_need(
        self,
        assessment: StabilityAssessment,
        forecast: Optional[BurnoutForecast] = None
    ) -> Tuple[bool, str, Dict]:
        """Evaluate if intervention is needed"""
        
        risk_prob = assessment.risk_probability
        
        # Check forecast for escalating risk
        if forecast and forecast.tipping_point_detected:
            logger.warning(f"Tipping point detected on {forecast.tipping_point_date}")
            risk_prob = max(risk_prob, forecast.tipping_point_probability or 0)
        
        # Determine intervention type based on risk level
        if risk_prob >= settings.RISK_THRESHOLD_ALERT:
            intervention_type = "alert"
            action_params = {
                "alert_type": "manager",
                "urgency": "critical",
                "reason": "Critical burnout risk detected"
            }
            needs_intervention = True
            
        elif risk_prob >= settings.RISK_THRESHOLD_REDISTRIBUTE:
            intervention_type = "redistribute"
            action_params = {
                "workload_reduction": 0.3,
                "reason": "High burnout risk - workload redistribution recommended"
            }
            needs_intervention = True
            
        elif risk_prob >= settings.RISK_THRESHOLD_BUFFER:
            intervention_type = "buffer"
            action_params = {
                "buffer_duration": settings.BUFFER_DURATION_MINUTES,
                "reason": "Moderate burnout risk - focus buffer needed"
            }
            needs_intervention = True
            
        else:
            intervention_type = "none"
            action_params = {}
            needs_intervention = False
        
        logger.info(f"Intervention evaluation: needs={needs_intervention}, type={intervention_type}, risk={risk_prob:.2%}")
        
        return needs_intervention, intervention_type, action_params
    
    def check_intervention_limits(
        self,
        user_id: str,
        current_date: datetime
    ) -> bool:
        """Check if user has exceeded daily intervention limit"""
        
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Count interventions today
        from sqlalchemy import and_
        count = self.db.query(Intervention).filter(
            and_(
                Intervention.user_id == user_id,
                Intervention.intervention_date >= day_start,
                Intervention.intervention_date < day_end,
                Intervention.status != "cancelled"
            )
        ).count()
        
        if count >= settings.MAX_DAILY_INTERVENTIONS:
            logger.warning(f"User {user_id} has reached daily intervention limit ({count}/{settings.MAX_DAILY_INTERVENTIONS})")
            return False
        
        return True
    
    def create_intervention_record(
        self,
        user_id: str,
        intervention_type: str,
        assessment: StabilityAssessment,
        action_params: Dict
    ) -> Intervention:
        """Create intervention record"""
        
        # Generate action description
        if intervention_type == "buffer":
            action_description = f"Insert {action_params['buffer_duration']}-minute focus buffer in calendar"
        elif intervention_type == "redistribute":
            action_description = f"Suggest {action_params['workload_reduction']*100:.0f}% workload redistribution"
        elif intervention_type == "alert":
            action_description = f"Send {action_params['alert_type']} alert for critical risk"
        else:
            action_description = "Unknown intervention"
        
        intervention = Intervention(
            user_id=user_id,
            intervention_date=assessment.assessment_date,
            intervention_type=intervention_type,
            trigger_risk_level=assessment.risk_level,
            trigger_risk_probability=assessment.risk_probability,
            trigger_stability_index=assessment.stability_index,
            action_description=action_description,
            action_parameters=action_params,
            status="pending",
            pre_stability_index=assessment.stability_index,
            pre_volatility=assessment.volatility,
            pre_risk_probability=assessment.risk_probability,
            is_autonomous=True,
            created_by="system"
        )
        
        self.db.add(intervention)
        self.db.commit()
        self.db.refresh(intervention)
        
        logger.info(f"Intervention record created: {intervention.id} - {intervention_type}")
        
        return intervention
    
    def execute_intervention(
        self,
        intervention: Intervention
    ) -> bool:
        """Execute the intervention"""
        
        logger.info(f"Executing intervention {intervention.id} - {intervention.intervention_type}")
        
        try:
            if intervention.intervention_type == "buffer":
                success = self._execute_buffer_intervention(intervention)
            elif intervention.intervention_type == "redistribute":
                success = self._execute_redistribute_intervention(intervention)
            elif intervention.intervention_type == "alert":
                success = self._execute_alert_intervention(intervention)
            else:
                logger.error(f"Unknown intervention type: {intervention.intervention_type}")
                success = False
            
            if success:
                intervention.status = "executed"
                intervention.execution_timestamp = datetime.utcnow()
                logger.info(f"Intervention {intervention.id} executed successfully")
            else:
                intervention.status = "failed"
                logger.error(f"Intervention {intervention.id} execution failed")
            
            self.db.commit()
            
            # Create audit log
            self._create_audit_log(intervention, success)
            
            return success
            
        except Exception as e:
            logger.error(f"Intervention execution error: {e}")
            intervention.status = "failed"
            self.db.commit()
            return False
    
    def _execute_buffer_intervention(self, intervention: Intervention) -> bool:
        """Execute calendar buffer insertion"""
        
        # This will be implemented by calendar_service
        # For now, mark as executed
        logger.info(f"Buffer intervention: {intervention.action_parameters['buffer_duration']} minutes")
        
        # Set buffer times (next available slot)
        buffer_start = intervention.intervention_date + timedelta(hours=2)
        buffer_duration = intervention.action_parameters['buffer_duration']
        buffer_end = buffer_start + timedelta(minutes=buffer_duration)
        
        intervention.buffer_start_time = buffer_start
        intervention.buffer_end_time = buffer_end
        intervention.buffer_duration_minutes = buffer_duration
        
        return True
    
    def _execute_redistribute_intervention(self, intervention: Intervention) -> bool:
        """Execute workload redistribution suggestion"""
        
        logger.info(f"Redistribute intervention: {intervention.action_parameters['workload_reduction']*100:.0f}% reduction")
        
        # In production, this would integrate with project management tools
        # For now, log the suggestion
        intervention.tasks_redistributed = 5  # Placeholder
        intervention.workload_reduction_percentage = intervention.action_parameters['workload_reduction']
        
        return True
    
    def _execute_alert_intervention(self, intervention: Intervention) -> bool:
        """Execute manager/HR alert"""
        
        logger.info(f"Alert intervention: {intervention.action_parameters['alert_type']}")
        
        # In production, this would send email/Slack notification
        alert_message = f"""
        BURNOUT RISK ALERT
        
        Employee: {intervention.user_id}
        Risk Level: {intervention.trigger_risk_level.upper()}
        Risk Probability: {intervention.trigger_risk_probability:.1%}
        
        Reason: {intervention.action_parameters['reason']}
        
        Immediate action recommended.
        """
        
        intervention.alert_sent_to = intervention.action_parameters['alert_type']
        intervention.alert_message = alert_message
        
        return True
    
    def _create_audit_log(self, intervention: Intervention, success: bool):
        """Create audit log entry"""
        
        audit = AuditLog(
            user_id=intervention.user_id,
            actor_type="system",
            action_type=f"intervention_{intervention.intervention_type}",
            action_description=intervention.action_description,
            action_parameters=intervention.action_parameters,
            target_type="intervention",
            target_id=intervention.id,
            result="success" if success else "failure"
        )
        
        self.db.add(audit)
        self.db.commit()
    
    def process_assessment(
        self,
        user_id: str,
        assessment: StabilityAssessment,
        forecast: Optional[BurnoutForecast] = None
    ) -> Optional[Intervention]:
        """Main decision pipeline"""
        
        logger.info(f"Processing assessment for user {user_id}")
        
        # Evaluate intervention need
        needs_intervention, intervention_type, action_params = self.evaluate_intervention_need(
            assessment,
            forecast
        )
        
        if not needs_intervention:
            logger.info("No intervention needed")
            return None
        
        # Check intervention limits
        if not self.check_intervention_limits(user_id, assessment.assessment_date):
            logger.warning("Intervention limit reached for today")
            return None
        
        # Create intervention record
        intervention = self.create_intervention_record(
            user_id,
            intervention_type,
            assessment,
            action_params
        )
        
        # Execute intervention
        self.execute_intervention(intervention)
        
        return intervention
