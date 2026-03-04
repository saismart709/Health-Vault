import unittest
from app.ai_engine import HealthAIEngine

class TestHealthAI(unittest.TestCase):
    def setUp(self):
        self.engine = HealthAIEngine()

    def test_normal_vitals(self):
        vitals = {
            "heart_rate": 70,
            "blood_pressure_sys": 120,
            "blood_pressure_dia": 80,
            "blood_sugar": 90,
            "temperature": 98.6
        }
        result = self.engine.analyze_vitals(vitals)
        self.assertEqual(result["risk_level"], "Low")
        self.assertEqual(result["risk_score"], 0)

    def test_high_risk_vitals(self):
        vitals = {
            "heart_rate": 110, # +20
            "blood_pressure_sys": 150, # +20
            "blood_pressure_dia": 95, # +20
            "blood_sugar": 150, # +20
            "temperature": 101 # +20
        }
        result = self.engine.analyze_vitals(vitals)
        self.assertEqual(result["risk_level"], "High")
        self.assertTrue(result["risk_score"] >= 40)

    def test_trend_analysis(self):
        history = [
            {"heart_rate": 70},
            {"heart_rate": 80},
            {"heart_rate": 90}
        ]
        trend = self.engine.predict_emergency_trend(history)
        self.assertIn("Increasing heart rate", trend)

if __name__ == "__main__":
    unittest.main()
