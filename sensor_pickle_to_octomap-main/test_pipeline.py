import os
from synthetic_data_generator import SyntheticLiDARGenerator, save_synthetic_data, store_synthetic_data_in_db
from db_utils import LiDARDatabase
import subprocess
import numpy as np

def run_pipeline_test():
    print("=== Starting LiDAR Data Pipeline Test ===")
    
    # 1. Generate synthetic data
    print("\n1. Generating synthetic LiDAR data...")
    generator = SyntheticLiDARGenerator()
    synthetic_scans = generator.generate_multiple_scans(num_scans=3)
    save_synthetic_data(synthetic_scans)
    
    # 2. Store in database
    print("\n2. Storing data in SQLite database...")
    store_synthetic_data_in_db(synthetic_scans)
    
    # 3. Process scans and create point clouds
    print("\n3. Processing scans to create point clouds...")
    db = LiDARDatabase()
    latest_scans = db.get_latest_scans(limit=3)
    
    print(f"Found {len(latest_scans)} scans in database:")
    for scan in latest_scans:
        scan_id, timestamp, alt_count, enc_count = scan
        print(f"Scan ID: {scan_id}, Timestamp: {timestamp}")
        
        # Get point cloud data
        points = db.get_point_cloud_by_scan_id(scan_id)
        print(f"Point cloud contains {len(points)} points")
        
        # Calculate some statistics
        points_array = np.array(points)
        if len(points) > 0:
            print(f"Point cloud bounds:")
            print(f"X: min={points_array[:,0].min():.2f}, max={points_array[:,0].max():.2f}")
            print(f"Y: min={points_array[:,1].min():.2f}, max={points_array[:,1].max():.2f}")
            print(f"Z: min={points_array[:,2].min():.2f}, max={points_array[:,2].max():.2f}")
    
    # 4. Create and store octomap
    print("\n4. Creating OctoMap from point cloud data...")
    # Write points to temporary CSV
    with open("temp_points.csv", "w") as f:
        f.write("x,y,z\n")
        for scan in latest_scans:
            points = db.get_point_cloud_by_scan_id(scan[0])
            for x, y, z in points:
                f.write(f"{x},{y},{z}\n")
    
    # Create octomap using the C++ tool
    octomap_file = "test_output.bt"
    try:
        subprocess.run(["./my_point_cloud_reader", "--xyz_csv", "temp_points.csv", "--out", octomap_file])
        print(f"Successfully created OctoMap: {octomap_file}")
        
        # Store octomap metadata in database
        point_count = sum(len(db.get_point_cloud_by_scan_id(scan[0])) for scan in latest_scans)
        db.store_octomap(resolution=10.0, file_path=octomap_file, point_count=point_count)
        
    except Exception as e:
        print(f"Error creating OctoMap: {e}")
    
    # Cleanup
    if os.path.exists("temp_points.csv"):
        os.remove("temp_points.csv")
    
    print("\n=== Pipeline Test Complete ===")

if __name__ == "__main__":
    run_pipeline_test()
