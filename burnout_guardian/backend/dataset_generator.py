"""
Synthetic Dataset Generator
Generates realistic behavioral metadata for 200 employees over 120 days
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import random
from backend.config import settings

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)


class SyntheticDatasetGenerator:
    """Generate synthetic employee behavioral data"""
    
    def __init__(self, num_employees: int = 200, num_days: int = 120):
        self.num_employees = num_employees
        self.num_days = num_days
        self.roles = ['Engineer', 'Designer', 'Manager', 'Analyst', 'QA', 'DevOps']
        self.departments = ['Engineering', 'Product', 'Marketing', 'Sales', 'Operations']
        self.project_phases = ['Planning', 'Development', 'Testing', 'Launch', 'Maintenance']
        
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-x))
    
    def generate_employee_profile(self, emp_id: int) -> Dict:
        """Generate employee profile"""
        return {
            'employee_id': f'EMP{emp_id:04d}',
            'role': random.choice(self.roles),
            'department': random.choice(self.departments),
            'baseline_resilience': np.random.uniform(0.5, 0.9),
            'burnout_trajectory': random.choice(['stable', 'gradual', 'rapid', 'recovery'])
        }
    
    def generate_workload_signals(self, day: int, profile: Dict, phase: str) -> Dict:
        """Generate workload-related signals"""
        
        # Base workload varies by role and phase
        base_hours = {
            'Engineer': 8.5,
            'Designer': 8.0,
            'Manager': 9.0,
            'Analyst': 8.0,
            'QA': 8.5,
            'DevOps': 9.5
        }[profile['role']]
        
        # Phase multipliers
        phase_multiplier = {
            'Planning': 0.9,
            'Development': 1.1,
            'Testing': 1.2,
            'Launch': 1.3,
            'Maintenance': 0.8
        }[phase]
        
        # Burnout trajectory affects workload accumulation
        if profile['burnout_trajectory'] == 'rapid':
            trajectory_factor = 1 + (day / self.num_days) * 0.5
        elif profile['burnout_trajectory'] == 'gradual':
            trajectory_factor = 1 + (day / self.num_days) * 0.3
        elif profile['burnout_trajectory'] == 'recovery':
            trajectory_factor = 1.3 - (day / self.num_days) * 0.3
        else:  # stable
            trajectory_factor = 1 + np.random.uniform(-0.1, 0.1)
        
        total_hours = base_hours * phase_multiplier * trajectory_factor
        total_hours = np.clip(total_hours + np.random.normal(0, 0.5), 6, 14)
        
        # Meeting metrics
        meeting_count = int(np.random.poisson(4 * phase_multiplier))
        meeting_hours = meeting_count * np.random.uniform(0.5, 1.5)
        meeting_hours = min(meeting_hours, total_hours * 0.6)
        
        # After-hours work
        after_hours = max(0, total_hours - 9) + np.random.exponential(0.5) * trajectory_factor
        
        # Task metrics
        task_assigned = int(np.random.poisson(8 * phase_multiplier))
        task_completed = int(task_assigned * np.random.uniform(0.6, 1.0))
        
        # Deadline compression (higher = more compressed)
        deadline_compression = np.random.beta(2, 5) * trajectory_factor
        
        # Task switching rate (switches per hour)
        task_switching = np.random.gamma(3, 0.5) * phase_multiplier
        
        # Communication volume
        email_volume = int(np.random.poisson(30 * phase_multiplier))
        slack_messages = int(np.random.poisson(50 * phase_multiplier))
        response_latency = np.random.exponential(15) * trajectory_factor  # minutes
        
        return {
            'total_work_hours': round(total_hours, 2),
            'meeting_hours': round(meeting_hours, 2),
            'meeting_count': meeting_count,
            'after_hours_work': round(after_hours, 2),
            'task_assigned_count': task_assigned,
            'task_completed_count': task_completed,
            'deadline_compression_ratio': round(deadline_compression, 3),
            'task_switching_rate': round(task_switching, 2),
            'email_volume': email_volume,
            'slack_message_count': slack_messages,
            'response_latency_avg': round(response_latency, 1)
        }
    
    def generate_recovery_signals(self, day: int, profile: Dict, workload: Dict) -> Dict:
        """Generate recovery-related signals"""
        
        # Base sleep hours
        base_sleep = 7.5
        
        # Sleep degradation based on workload
        workload_impact = (workload['total_work_hours'] - 8) * 0.2
        sleep_hours = base_sleep - workload_impact + np.random.normal(0, 0.5)
        sleep_hours = np.clip(sleep_hours, 4, 9)
        
        # Sleep consistency (0-1, higher is better)
        sleep_consistency = profile['baseline_resilience'] * np.random.uniform(0.7, 1.0)
        
        # HRV index (0-100, higher is better)
        hrv_base = 60 * profile['baseline_resilience']
        hrv = hrv_base - (workload['total_work_hours'] - 8) * 5 + np.random.normal(0, 5)
        hrv = np.clip(hrv, 20, 100)
        
        # Focus blocks (minutes of uninterrupted work)
        longest_focus = 120 * profile['baseline_resilience'] / (1 + workload['task_switching_rate'] / 10)
        longest_focus = np.clip(longest_focus + np.random.normal(0, 15), 15, 180)
        
        # Recovery gap (minutes between meetings)
        if workload['meeting_count'] > 0:
            recovery_gap = (480 - workload['meeting_hours'] * 60) / workload['meeting_count']
        else:
            recovery_gap = 240
        recovery_gap = max(5, recovery_gap + np.random.normal(0, 10))
        
        # Weekend work ratio
        is_weekend = day % 7 in [5, 6]
        if is_weekend:
            weekend_work = np.random.uniform(0, 0.5) if np.random.random() < 0.3 else 0
        else:
            weekend_work = 0
        
        return {
            'longest_focus_block_minutes': round(longest_focus, 1),
            'recovery_gap_minutes': round(recovery_gap, 1),
            'weekend_work_ratio': round(weekend_work, 3),
            'sleep_hours': round(sleep_hours, 2),
            'sleep_consistency_score': round(sleep_consistency, 3),
            'hr_variability_index': round(hrv, 1)
        }
    
    def generate_performance_signals(self, day: int, profile: Dict, workload: Dict, recovery: Dict) -> Dict:
        """Generate performance-related signals"""
        
        # Error rate increases with fatigue
        fatigue_factor = (9 - recovery['sleep_hours']) / 5
        error_rate = 0.05 * fatigue_factor * (1 + workload['task_switching_rate'] / 10)
        error_rate = np.clip(error_rate + np.random.normal(0, 0.01), 0, 0.5)
        
        # Revision count
        revision_count = int(np.random.poisson(error_rate * 20))
        
        # Decision reversals (sign of instability)
        decision_reversals = int(np.random.poisson(error_rate * 10))
        
        # Output score (0-100)
        output_base = 80 * profile['baseline_resilience']
        output_score = output_base - fatigue_factor * 10 - workload['task_switching_rate'] * 2
        output_score = np.clip(output_score + np.random.normal(0, 5), 40, 100)
        
        # Productivity volatility (standard deviation of hourly output)
        volatility = 0.15 + fatigue_factor * 0.1 + workload['task_switching_rate'] * 0.02
        volatility = np.clip(volatility, 0.05, 0.5)
        
        return {
            'error_rate': round(error_rate, 4),
            'revision_count': revision_count,
            'decision_reversal_count': decision_reversals,
            'output_score': round(output_score, 2),
            'productivity_volatility_index': round(volatility, 3)
        }
    
    def generate_derived_signals(self, workload: Dict, recovery: Dict, performance: Dict) -> Dict:
        """Generate derived composite signals"""
        
        # Meeting density (meetings per work hour)
        meeting_density = workload['meeting_count'] / max(workload['total_work_hours'], 1)
        
        # Load accumulation rate (cumulative workload increase)
        load_accumulation = (workload['total_work_hours'] - 8) / 8
        load_accumulation += workload['after_hours_work'] / 8
        load_accumulation = max(0, load_accumulation)
        
        # Recovery deficit score
        sleep_deficit = max(0, 7.5 - recovery['sleep_hours']) / 7.5
        focus_deficit = max(0, 90 - recovery['longest_focus_block_minutes']) / 90
        recovery_deficit = (sleep_deficit + focus_deficit) / 2
        
        # Instability index
        instability = (
            workload['task_switching_rate'] / 10 * 0.3 +
            recovery_deficit * 0.3 +
            performance['error_rate'] * 10 * 0.2 +
            meeting_density * 0.2
        )
        instability = np.clip(instability, 0, 1)
        
        # Volatility acceleration (rate of change in volatility)
        volatility_accel = performance['productivity_volatility_index'] * load_accumulation
        
        return {
            'meeting_density_ratio': round(meeting_density, 3),
            'load_accumulation_rate': round(load_accumulation, 3),
            'recovery_deficit_score': round(recovery_deficit, 3),
            'instability_index': round(instability, 3),
            'volatility_acceleration': round(volatility_accel, 4)
        }
    
    def calculate_collapse_probability(self, derived: Dict, performance: Dict) -> float:
        """Calculate collapse probability using sigmoid formula"""
        
        logit = (
            settings.WEIGHT_INSTABILITY * derived['instability_index'] +
            settings.WEIGHT_RECOVERY_DEFICIT * derived['recovery_deficit_score'] +
            settings.WEIGHT_VOLATILITY * derived['volatility_acceleration'] +
            settings.WEIGHT_ERROR_RATE * performance['error_rate'] * 10
        )
        
        # Add some noise
        logit += np.random.normal(0, 0.1)
        
        probability = self.sigmoid(logit * 5 - 2.5)  # Scale and shift for 0-1 range
        
        return round(probability, 4)
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate complete synthetic dataset"""
        
        print(f"🔄 Generating synthetic dataset...")
        print(f"   Employees: {self.num_employees}")
        print(f"   Days: {self.num_days}")
        print(f"   Total rows: {self.num_employees * self.num_days:,}")
        
        all_rows = []
        
        # Generate employee profiles
        employees = [self.generate_employee_profile(i) for i in range(1, self.num_employees + 1)]
        
        # Generate daily data for each employee
        for emp_idx, employee in enumerate(employees):
            if (emp_idx + 1) % 20 == 0:
                print(f"   Progress: {emp_idx + 1}/{self.num_employees} employees")
            
            for day in range(self.num_days):
                # Determine project phase (changes every ~30 days)
                phase_idx = (day // 30) % len(self.project_phases)
                phase = self.project_phases[phase_idx]
                
                # Generate signals
                workload = self.generate_workload_signals(day, employee, phase)
                recovery = self.generate_recovery_signals(day, employee, workload)
                performance = self.generate_performance_signals(day, employee, workload, recovery)
                derived = self.generate_derived_signals(workload, recovery, performance)
                
                # Calculate target
                collapse_prob = self.calculate_collapse_probability(derived, performance)
                
                # Combine all data
                row = {
                    'employee_id': employee['employee_id'],
                    'role': employee['role'],
                    'department': employee['department'],
                    'day_index': day,
                    'project_phase': phase,
                    **workload,
                    **recovery,
                    **performance,
                    **derived,
                    'collapse_probability': collapse_prob
                }
                
                all_rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(all_rows)
        
        print(f"✅ Dataset generated successfully!")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {len(df.columns)}")
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, output_path: str = None):
        """Save dataset to CSV"""
        
        if output_path is None:
            output_path = settings.DATASET_OUTPUT_PATH
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df.to_csv(output_path, index=False)
        print(f"💾 Dataset saved to: {output_path}")
        
        # Print statistics
        print(f"\n📊 Dataset Statistics:")
        print(f"   Total rows: {len(df):,}")
        print(f"   Unique employees: {df['employee_id'].nunique()}")
        print(f"   Date range: Day 0 to Day {df['day_index'].max()}")
        print(f"   Avg collapse probability: {df['collapse_probability'].mean():.3f}")
        print(f"   High risk (>0.7): {(df['collapse_probability'] > 0.7).sum():,} rows ({(df['collapse_probability'] > 0.7).mean()*100:.1f}%)")
        print(f"   Critical risk (>0.85): {(df['collapse_probability'] > 0.85).sum():,} rows ({(df['collapse_probability'] > 0.85).mean()*100:.1f}%)")


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("🧠 BURNOUT GUARDIAN - SYNTHETIC DATASET GENERATOR")
    print("=" * 60)
    print()
    
    generator = SyntheticDatasetGenerator(
        num_employees=settings.DATASET_NUM_EMPLOYEES,
        num_days=settings.DATASET_NUM_DAYS
    )
    
    # Generate dataset
    df = generator.generate_dataset()
    
    # Save dataset
    generator.save_dataset(df)
    
    print()
    print("=" * 60)
    print("✨ Dataset generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
