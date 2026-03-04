import pandas as pd
from typing import Dict, List, Any

class HealthAIEngine:
    def __init__(self):
        # Disease risk weights from target HTML
        self.risk_factors = {
            'diabetes': 25,
            'type 2 diabetes': 25,
            'hypertension': 20,
            'heart disease': 35,
            'kidney disease': 30,
            'thyroid disorder': 10,
            'anemia': 10,
            'cholesterol': 15,
            'asthma': 8,
            'obesity': 12
        }
        
        # Vital thresholds
        self.vital_thresholds = {
            "heart_rate": {"high": 100, "low": 60},
            "blood_pressure_sys": {"high": 140, "low": 90},
            "blood_sugar": {"high": 140, "low": 70}
        }
        
    def analyze_vitals(self, user_info: Dict[str, Any], vitals: Dict[str, float]) -> Dict[str, Any]:
        score = 0
        reasons = []
        
        # 1. Base score from conditions (target logic)
        conditions = user_info.get('conditions', '').lower()
        condition_list = [c.strip() for c in conditions.split(',')]
        
        for c in condition_list:
            if c in self.risk_factors:
                score += self.risk_factors[c]
                reasons.append(f"Diagnosed {c.title()}")
            elif any(k in c for k in self.risk_factors):
                # Partial match
                for k, v in self.risk_factors.items():
                    if k in c:
                        score += v
                        reasons.append(f"Diagnosed {c.title()}")
                        break

        # 2. Age factor (target logic)
        age = user_info.get('age', 30)
        if age > 60:
            score += 20
        elif age > 45:
            score += 10
        elif age > 30:
            score += 5

        # 3. Vital-based dynamic adjustments
        if vitals.get('heart_rate', 70) > self.vital_thresholds['heart_rate']['high']:
            score += 30  # Increased from 15
            reasons.append(f"High Heart Rate ({vitals['heart_rate']} bpm)")
        
        if vitals.get('blood_pressure_sys', 120) > self.vital_thresholds['blood_pressure_sys']['high']:
            score += 30  # Increased from 15
            reasons.append(f"High Blood Pressure ({vitals['blood_pressure_sys']} mmHg)")
            
        if vitals.get('blood_sugar', 100) > self.vital_thresholds['blood_sugar']['high']:
            score += 30  # Increased from 15
            reasons.append(f"High Blood Sugar ({vitals['blood_sugar']} mg/dL)")

        # 4. Multipliers (target logic)
        if 'diabetes' in conditions and 'hypertension' in conditions:
            score = int(score * 1.4)
            reasons.append("Co-morbidity: Diabetes + Hypertension")
            
        if 'heart' in conditions:
            score = int(score * 1.3)

        score = min(score, 100)
        
        # Risk level determination
        if score < 30:
            level = "Low"
        elif score < 60:
            level = "Medium"
        else:
            level = "High"
            
        return {
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons,
            "action": "Immediate attention required" if level == "High" else "Monitor closely" if level == "Medium" else "Maintain lifestyle"
        }

    def analyze_medical_report(self, filename: str, content: str = "") -> Dict[str, str]:
        """Simulated AI OCR and Analysis"""
        name_lower = filename.lower()
        
        if any(term in name_lower for term in ['blood', 'sugar', 'glucose']):
            return {
                "status": "Needs Attention",
                "analysis": "Glucose levels are slightly elevated (145 mg/dL). Clinical correlation with HbA1c recommended."
            }
        elif any(term in name_lower for term in ['heart', 'ecg', 'cardio']):
            return {
                "status": "Critical",
                "analysis": "Evidence of sinus tachycardia and mild ST-segment depression. Immediate cardiology consultation advised."
            }
        elif any(term in name_lower for term in ['mri', 'scan', 'report']):
            return {
                "status": "Stable",
                "analysis": "No acute findings. Degenerative changes consistent with age noted in L4-L5."
            }
        else:
            return {
                "status": "Stable",
                "analysis": "Report processed. Vital parameters within normal physiological limits for the specified age group."
            }

ai_engine = HealthAIEngine()
