import time
import random
import math
from datetime import datetime

class IndustrialSensorSimulator:
    def __init__(self):
        self.step = 0
        
        # Base normal values
        self.base_temp = 50.0
        self.base_vibration = 2.0
        self.base_pressure = 30.0
        
        # Drift states (accumulate over time when active)
        self.temp_drift = 0.0
        self.vibration_drift = 0.0
        self.pressure_drift = 0.0

    def generate_point(self, anomaly_type="normal"):
        """
        Generates a single time-series data point.
        Supported anomaly_types: 'normal', 'spike', 'drift', 'dropout'
        """
        self.step += 1
        timestamp = datetime.now().isoformat()
        
        # 1. Normal cyclical patterns (using sine/cosine waves)
        cycle_temp = 3.0 * math.sin(self.step * 0.05)
        cycle_vib = 0.4 * math.cos(self.step * 0.08)
        cycle_pres = 1.5 * math.sin(self.step * 0.03)
        
        # 2. Add normal random noise
        noise_temp = random.normalvariate(0, 0.3)
        noise_vib = random.normalvariate(0, 0.05)
        noise_pres = random.normalvariate(0, 0.2)
        
        # Compute baseline readings
        temp = self.base_temp + cycle_temp + noise_temp
        vib = self.base_vibration + cycle_vib + noise_vib
        pres = self.base_pressure + cycle_pres + noise_pres
        
        # 3. Apply anomalies
        anomaly_flag = "normal"
        
        if anomaly_type == "spike":
            # Sudden extreme spike/dip
            spike_select = random.choice(["temp", "vib", "pres", "all"])
            anomaly_flag = f"spike_{spike_select}"
            
            if spike_select == "temp" or spike_select == "all":
                temp += random.choice([15.0, 20.0, -15.0])
            if spike_select == "vib" or spike_select == "all":
                vib += random.choice([2.5, 3.5])
            if spike_select == "pres" or spike_select == "all":
                pres += random.choice([12.0, 18.0, -10.0])
                
        elif anomaly_type == "drift":
            # Accumulate wear and tear drift
            self.temp_drift += 0.2
            self.vibration_drift += 0.03
            self.pressure_drift += 0.1
            
            temp += self.temp_drift
            vib += self.vibration_drift
            pres += self.pressure_drift
            anomaly_flag = "drift"
            
        elif anomaly_type == "dropout":
            # Sensor loses power or drops to flatline
            dropout_select = random.choice(["temp", "vib", "pres", "all"])
            anomaly_flag = f"dropout_{dropout_select}"
            
            if dropout_select == "temp" or dropout_select == "all":
                temp = 0.0
            if dropout_select == "vib" or dropout_select == "all":
                vib = 0.0
            if dropout_select == "pres" or dropout_select == "all":
                pres = 0.0
                
        else:
            # Reset drifts if we are normal
            self.temp_drift = max(0.0, self.temp_drift - 0.5)
            self.vibration_drift = max(0.0, self.vibration_drift - 0.05)
            self.pressure_drift = max(0.0, self.pressure_drift - 0.2)
            
        return {
            "timestamp": timestamp,
            "temperature": round(temp, 2),
            "vibration": round(vib, 2),
            "pressure": round(pres, 2),
            "anomaly_injected": anomaly_flag
        }

if __name__ == "__main__":
    # Test script outputting a mix of data
    sim = IndustrialSensorSimulator()
    print("Starting sensor simulation test...")
    for i in range(10):
        # Inject an anomaly at step 5
        mode = "normal"
        if i == 4:
            mode = "spike"
        elif i == 8:
            mode = "dropout"
        point = sim.generate_point(mode)
        print(point)
        time.sleep(0.1)
