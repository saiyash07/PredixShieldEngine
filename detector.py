import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, window_size=50, baseline_points=300):
        self.window_size = window_size
        self.baseline_points = baseline_points
        self.history = []
        
        # Isolation Forest instance
        self.clf = IsolationForest(contamination=0.03, random_state=42)
        self.is_clf_fitted = False
        self.baseline_data = []

    def fit_baseline(self, simulator):
        """
        Generates a baseline of normal data points and fits the Isolation Forest.
        """
        import random
        print("Gathering baseline data and fitting Isolation Forest model...")
        
        # Keep track of original step
        original_step = simulator.step
        
        # Sample points randomly across step phases to capture the full cyclical state space
        for _ in range(self.baseline_points):
            simulator.step = random.randint(0, 1000)
            point = simulator.generate_point(anomaly_type="normal")
            self.baseline_data.append([
                point["temperature"],
                point["vibration"],
                point["pressure"]
            ])
            
        # Restore simulator step
        simulator.step = original_step
        
        # Seed the rolling window history with normal sequential points
        for _ in range(self.window_size):
            point = simulator.generate_point(anomaly_type="normal")
            self.history.append(point)
            
        # Fit model
        self.clf.fit(self.baseline_data)
        self.is_clf_fitted = True
        print("Isolation Forest baseline fitting complete!")

    def process_point(self, point):
        """
        Processes a single incoming data point and determines anomaly status.
        """
        # Append to history, keep window size
        self.history.append(point)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        # Convert history to DataFrame for rolling stats
        df = pd.DataFrame(self.history)
        
        # Calculate Rolling Z-Scores for the current point
        z_scores = {}
        features = ["temperature", "vibration", "pressure"]
        current_features = [point[f] for f in features]
        
        for f in features:
            mean = df[f].mean()
            std = df[f].std()
            val = point[f]
            
            # Prevent tiny noise from blowing up Z-score on very flat signals
            # We set a sensible minimum standard deviation for each metric
            min_std = {"temperature": 1.0, "vibration": 0.15, "pressure": 0.8}.get(f, 0.5)
            effective_std = max(std, min_std) if (not pd.isna(std) and std > 0.001) else min_std
            
            z = (val - mean) / effective_std
            z_scores[f] = round(float(z), 2)
            
        # Isolation Forest prediction
        if self.is_clf_fitted:
            # Reshape for single sample prediction
            sample = np.array(current_features).reshape(1, -1)
            # predict returns 1 for inliers, -1 for outliers
            if_pred = int(self.clf.predict(sample)[0])
            is_if_anomaly = (if_pred == -1)
        else:
            is_if_anomaly = False
            
        # Determine Severity Level
        max_abs_z = max(abs(z) for z in z_scores.values())
        
        severity = "normal"
        reasons = []
        
        if max_abs_z >= 4.0:
            severity = "high"
            reasons.append("Z-Score critical threshold exceeded")
        elif max_abs_z >= 3.0:
            severity = "medium"
            reasons.append("Z-Score warning threshold exceeded")
        elif is_if_anomaly and max_abs_z >= 2.0:
            severity = "medium"
            reasons.append("Isolation Forest outlier + moderate Z-Score deviation")
        elif is_if_anomaly:
            severity = "low"
            reasons.append("Isolation Forest outlier detected")
        elif max_abs_z >= 2.0:
            severity = "low"
            reasons.append("Minor statistical deviation")
            
        # Only count medium and high severity as active anomalies
        anomaly_detected = severity in ["medium", "high"]
            
        return {
            "z_scores": z_scores,
            "max_z": round(max_abs_z, 2),
            "is_if_anomaly": is_if_anomaly,
            "anomaly_detected": anomaly_detected,
            "severity": severity,
            "reasons": ", ".join(reasons) if reasons else "Normal conditions"
        }

if __name__ == "__main__":
    from data_generator import IndustrialSensorSimulator
    
    sim = IndustrialSensorSimulator()
    detector = AnomalyDetector(window_size=30, baseline_points=50)
    detector.fit_baseline(sim)
    
    print("\nTesting single anomaly point (spike):")
    spike_point = sim.generate_point("spike")
    print(f"Point: {spike_point}")
    res = detector.process_point(spike_point)
    print(f"Result: {res}")
