"""
Forecasting Service
7-day burnout probability forecasting using Prophet and LSTM
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    class nn: 
        class Module: pass

from backend.models.feature_model import BehavioralFeature
from backend.models.stability_model import StabilityAssessment
from backend.models.forecast_model import BurnoutForecast, LSTMPrediction
from backend.config import settings
from loguru import logger


class LSTMModel(nn.Module):
    """LSTM model for time series forecasting"""
    
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=7):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return out


class ForecastingService:
    """Forecast burnout probability using Prophet and LSTM"""
    
    def __init__(self, db: Session):
        self.db = db
        self.lstm_model = None
    
    def get_historical_data(
        self,
        user_id: str,
        current_date: datetime,
        lookback_days: int = 30
    ) -> pd.DataFrame:
        """Get historical stability data for forecasting"""
        
        start_date = current_date - timedelta(days=lookback_days)
        
        assessments = self.db.query(StabilityAssessment).filter(
            and_(
                StabilityAssessment.user_id == user_id,
                StabilityAssessment.assessment_date >= start_date,
                StabilityAssessment.assessment_date <= current_date
            )
        ).order_by(StabilityAssessment.assessment_date).all()
        
        if not assessments:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for assessment in assessments:
            data.append({
                'ds': assessment.assessment_date,
                'y': assessment.risk_probability
            })
        
        df = pd.DataFrame(data)
        return df
    
    def forecast_prophet(
        self,
        user_id: str,
        current_date: datetime,
        horizon_days: int = 7
    ) -> Optional[Dict]:
        """Forecast using Prophet"""
        
        logger.info(f"Running Prophet forecast for user {user_id}")
        
        # Get historical data
        df = self.get_historical_data(user_id, current_date, lookback_days=30)
        
        if len(df) < 7:
            logger.warning(f"Insufficient data for Prophet (need 7+ days, have {len(df)})")
            return None
        
        try:
            # Initialize Prophet
            model = Prophet(
                changepoint_prior_scale=settings.PROPHET_CHANGEPOINT_PRIOR,
                interval_width=0.95,
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False
            )
            
            # Fit model
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=horizon_days)
            
            # Predict
            forecast = model.predict(future)
            
            # Extract forecast values (last horizon_days rows)
            forecast_values = forecast['yhat'].tail(horizon_days).tolist()
            forecast_dates = forecast['ds'].tail(horizon_days).tolist()
            lower_bound = forecast['yhat_lower'].tail(horizon_days).tolist()
            upper_bound = forecast['yhat_upper'].tail(horizon_days).tolist()
            
            # Clip to [0, 1]
            forecast_values = [np.clip(v, 0, 1) for v in forecast_values]
            lower_bound = [np.clip(v, 0, 1) for v in lower_bound]
            upper_bound = [np.clip(v, 0, 1) for v in upper_bound]
            
            # Find peak risk
            peak_idx = np.argmax(forecast_values)
            peak_risk_date = forecast_dates[peak_idx]
            peak_risk_prob = forecast_values[peak_idx]
            
            # Detect tipping point (probability crosses 0.85)
            tipping_point_detected = any(v >= 0.85 for v in forecast_values)
            if tipping_point_detected:
                tipping_idx = next(i for i, v in enumerate(forecast_values) if v >= 0.85)
                tipping_point_date = forecast_dates[tipping_idx]
                tipping_point_prob = forecast_values[tipping_idx]
            else:
                tipping_point_date = None
                tipping_point_prob = None
            
            result = {
                'forecast_values': [round(v, 4) for v in forecast_values],
                'forecast_dates': [d.isoformat() for d in forecast_dates],
                'lower_bound': [round(v, 4) for v in lower_bound],
                'upper_bound': [round(v, 4) for v in upper_bound],
                'peak_risk_date': peak_risk_date.isoformat() if peak_risk_date else None,
                'peak_risk_probability': round(peak_risk_prob, 4),
                'tipping_point_detected': tipping_point_detected,
                'tipping_point_date': tipping_point_date.isoformat() if tipping_point_date else None,
                'tipping_point_probability': round(tipping_point_prob, 4) if tipping_point_prob else None,
                'model_type': 'prophet'
            }
            
            logger.info(f"Prophet forecast complete - Peak risk: {peak_risk_prob:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Prophet forecasting failed: {e}")
            return None
    
    def forecast_lstm(
        self,
        user_id: str,
        current_date: datetime,
        horizon_days: int = 7
    ) -> Optional[Dict]:
        """Forecast using LSTM"""
        
        logger.info(f"Running LSTM forecast for user {user_id}")
        
        # Get historical data
        df = self.get_historical_data(user_id, current_date, lookback_days=30)
        
        if len(df) < settings.LSTM_SEQUENCE_LENGTH:
            logger.warning(f"Insufficient data for LSTM (need {settings.LSTM_SEQUENCE_LENGTH}+ days, have {len(df)})")
            return None
        
        try:
            # Prepare data
            values = df['y'].values
            
            # Normalize
            mean_val = np.mean(values)
            std_val = np.std(values)
            if std_val == 0:
                std_val = 1
            normalized_values = (values - mean_val) / std_val
            
            # Create sequences
            sequence_length = settings.LSTM_SEQUENCE_LENGTH
            X = normalized_values[-sequence_length:].reshape(1, sequence_length, 1)
            X_tensor = torch.FloatTensor(X)
            
            # Initialize or load model
            if self.lstm_model is None:
                self.lstm_model = LSTMModel(
                    input_size=1,
                    hidden_size=settings.LSTM_HIDDEN_SIZE,
                    num_layers=2,
                    output_size=horizon_days
                )
            
            # Predict
            self.lstm_model.eval()
            with torch.no_grad():
                predictions = self.lstm_model(X_tensor)
                predictions = predictions.numpy()[0]
            
            # Denormalize
            predictions = predictions * std_val + mean_val
            
            # Clip to [0, 1]
            predictions = np.clip(predictions, 0, 1)
            
            # Generate forecast dates
            forecast_dates = [current_date + timedelta(days=i+1) for i in range(horizon_days)]
            
            # Find peak risk
            peak_idx = np.argmax(predictions)
            peak_risk_date = forecast_dates[peak_idx]
            peak_risk_prob = predictions[peak_idx]
            
            # Detect tipping point
            tipping_point_detected = any(v >= 0.85 for v in predictions)
            if tipping_point_detected:
                tipping_idx = next(i for i, v in enumerate(predictions) if v >= 0.85)
                tipping_point_date = forecast_dates[tipping_idx]
                tipping_point_prob = predictions[tipping_idx]
            else:
                tipping_point_date = None
                tipping_point_prob = None
            
            result = {
                'forecast_values': [round(float(v), 4) for v in predictions],
                'forecast_dates': [d.isoformat() for d in forecast_dates],
                'peak_risk_date': peak_risk_date.isoformat() if peak_risk_date else None,
                'peak_risk_probability': round(float(peak_risk_prob), 4),
                'tipping_point_detected': tipping_point_detected,
                'tipping_point_date': tipping_point_date.isoformat() if tipping_point_date else None,
                'tipping_point_probability': round(float(tipping_point_prob), 4) if tipping_point_prob else None,
                'model_type': 'lstm'
            }
            
            logger.info(f"LSTM forecast complete - Peak risk: {peak_risk_prob:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"LSTM forecasting failed: {e}")
            return None
    
    def create_ensemble_forecast(
        self,
        prophet_result: Optional[Dict],
        lstm_result: Optional[Dict]
    ) -> Optional[Dict]:
        """Combine Prophet and LSTM forecasts"""
        
        if not prophet_result and not lstm_result:
            return None
        
        if not prophet_result:
            return lstm_result
        
        if not lstm_result:
            return prophet_result
        
        # Ensemble: weighted average (Prophet 60%, LSTM 40%)
        prophet_values = np.array(prophet_result['forecast_values'])
        lstm_values = np.array(lstm_result['forecast_values'])
        
        ensemble_values = 0.6 * prophet_values + 0.4 * lstm_values
        
        # Find peak risk
        peak_idx = np.argmax(ensemble_values)
        forecast_dates = [datetime.fromisoformat(d) for d in prophet_result['forecast_dates']]
        peak_risk_date = forecast_dates[peak_idx]
        peak_risk_prob = ensemble_values[peak_idx]
        
        # Detect tipping point
        tipping_point_detected = any(v >= 0.85 for v in ensemble_values)
        if tipping_point_detected:
            tipping_idx = next(i for i, v in enumerate(ensemble_values) if v >= 0.85)
            tipping_point_date = forecast_dates[tipping_idx]
            tipping_point_prob = ensemble_values[tipping_idx]
        else:
            tipping_point_date = None
            tipping_point_prob = None
        
        result = {
            'forecast_values': [round(float(v), 4) for v in ensemble_values],
            'forecast_dates': prophet_result['forecast_dates'],
            'lower_bound': prophet_result.get('lower_bound'),
            'upper_bound': prophet_result.get('upper_bound'),
            'peak_risk_date': peak_risk_date.isoformat() if peak_risk_date else None,
            'peak_risk_probability': round(float(peak_risk_prob), 4),
            'tipping_point_detected': tipping_point_detected,
            'tipping_point_date': tipping_point_date.isoformat() if tipping_point_date else None,
            'tipping_point_probability': round(float(tipping_point_prob), 4) if tipping_point_prob else None,
            'model_type': 'ensemble'
        }
        
        return result
    
    def generate_forecast(
        self,
        user_id: str,
        current_date: datetime,
        horizon_days: int = 7
    ) -> Optional[BurnoutForecast]:
        """Generate complete forecast"""
        
        logger.info(f"Generating {horizon_days}-day forecast for user {user_id}")
        
        # Run both models
        prophet_result = self.forecast_prophet(user_id, current_date, horizon_days)
        lstm_result = self.forecast_lstm(user_id, current_date, horizon_days)
        
        # Create ensemble
        ensemble_result = self.create_ensemble_forecast(prophet_result, lstm_result)
        
        if not ensemble_result:
            logger.warning("No forecast could be generated")
            return None
        
        # Create BurnoutForecast object
        forecast = BurnoutForecast(
            user_id=user_id,
            forecast_date=current_date,
            horizon_days=horizon_days,
            forecast_values=ensemble_result['forecast_values'],
            forecast_dates=ensemble_result['forecast_dates'],
            lower_bound=ensemble_result.get('lower_bound'),
            upper_bound=ensemble_result.get('upper_bound'),
            peak_risk_date=datetime.fromisoformat(ensemble_result['peak_risk_date']) if ensemble_result['peak_risk_date'] else None,
            peak_risk_probability=ensemble_result['peak_risk_probability'],
            tipping_point_detected=1 if ensemble_result['tipping_point_detected'] else 0,
            tipping_point_date=datetime.fromisoformat(ensemble_result['tipping_point_date']) if ensemble_result['tipping_point_date'] else None,
            tipping_point_probability=ensemble_result['tipping_point_probability'],
            model_type=ensemble_result['model_type'],
            confidence_score=0.85
        )
        
        # Save forecast
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        
        logger.info(f"Forecast saved - Peak risk: {forecast.peak_risk_probability:.2%} on {forecast.peak_risk_date}")
        
        return forecast
