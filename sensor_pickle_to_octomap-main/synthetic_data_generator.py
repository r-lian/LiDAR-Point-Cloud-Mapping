import numpy as np
import pickle
from db_utils import LiDARDatabase
import os

class SyntheticLiDARGenerator:
    def __init__(self, altitude_angles=32, encoder_angles=512):
        self.altitude_angles = altitude_angles
        self.encoder_angles = encoder_angles
        
    def generate_environment(self, num_objects=5, max_distance=10.0):
        """Generate a synthetic environment with random objects"""
        # Initialize empty environment
        scan_data = np.ones((self.altitude_angles, self.encoder_angles)) * max_distance
        
        # Add random "objects" by modifying distances
        for _ in range(num_objects):
            # Random object position
            alt_idx = np.random.randint(0, self.altitude_angles)
            enc_idx = np.random.randint(0, self.encoder_angles)
            
            # Random object size
            size = np.random.randint(3, 10)
            distance = np.random.uniform(1.0, max_distance-1)
            
            # Create object by setting distances
            for i in range(max(0, alt_idx-size), min(self.altitude_angles, alt_idx+size)):
                for j in range(max(0, enc_idx-size), min(self.encoder_angles, enc_idx+size)):
                    # Add some noise to make it more realistic
                    noise = np.random.normal(0, 0.1)
                    scan_data[i, j] = distance + noise
        
        return scan_data

    def generate_multiple_scans(self, num_scans=5):
        """Generate multiple synthetic scans"""
        scans = []
        for _ in range(num_scans):
            scan = self.generate_environment()
            scans.append(scan)
        return scans

def save_synthetic_data(scans, output_dir="synthetic_data"):
    """Save synthetic scans as pickle files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, scan in enumerate(scans):
        filename = os.path.join(output_dir, f"synthetic_scan_{i}.pickle")
        with open(filename, "wb") as f:
            pickle.dump(scan, f)
        print(f"Saved scan to {filename}")

def store_synthetic_data_in_db(scans):
    """Store synthetic scans in the database"""
    db = LiDARDatabase()
    
    for scan in scans:
        # Store raw scan
        scan_id = db.store_raw_scan(scan, scan.shape[0], scan.shape[1])
        
        # Generate and store point cloud data
        points = []
        for alt_idx in range(scan.shape[0]):
            for enc_idx in range(scan.shape[1]):
                # Convert to cartesian coordinates (simplified version)
                radius = scan[alt_idx, enc_idx]
                encoder_angle = enc_idx * (2 * np.pi / scan.shape[1])
                altitude_angle = (alt_idx - scan.shape[0]/2) * (np.pi / scan.shape[0])
                
                x = radius * np.cos(encoder_angle) * np.cos(altitude_angle)
                y = radius * np.sin(encoder_angle) * np.cos(altitude_angle)
                z = radius * np.sin(altitude_angle)
                
                points.append((x, y, z))
        
        # Store point cloud
        db.store_point_cloud(scan_id, points)
        print(f"Stored scan {scan_id} in database")

if __name__ == "__main__":
    # Generate synthetic data
    generator = SyntheticLiDARGenerator()
    synthetic_scans = generator.generate_multiple_scans(num_scans=10)  # Increased from 3 to 10
    
    # Save to files
    save_synthetic_data(synthetic_scans)
    
    # Store in database
    store_synthetic_data_in_db(synthetic_scans)
    print("Synthetic data generation and storage complete!")
