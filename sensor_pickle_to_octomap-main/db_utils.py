import sqlite3
from datetime import datetime
import numpy as np

class LiDARDatabase:
    def __init__(self, db_path="lidar_data.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Create table for raw LiDAR scans
        c.execute('''
        CREATE TABLE IF NOT EXISTS raw_scans (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            altitude_angle_count INTEGER NOT NULL,
            encoder_angle_count INTEGER NOT NULL,
            data BLOB NOT NULL
        )
        ''')

        # Create table for processed point cloud data
        c.execute('''
        CREATE TABLE IF NOT EXISTS point_clouds (
            point_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            z REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES raw_scans (scan_id)
        )
        ''')

        # Create table for octomap metadata
        c.execute('''
        CREATE TABLE IF NOT EXISTS octomaps (
            map_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            resolution REAL NOT NULL,
            file_path TEXT NOT NULL,
            point_count INTEGER NOT NULL
        )
        ''')

        conn.commit()
        conn.close()

    def store_raw_scan(self, scan_data, altitude_angle_count, encoder_angle_count):
        """Store raw LiDAR scan data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Convert numpy array to bytes for storage
        data_bytes = scan_data.tobytes()
        
        c.execute('''
        INSERT INTO raw_scans (timestamp, altitude_angle_count, encoder_angle_count, data)
        VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), altitude_angle_count, encoder_angle_count, data_bytes))
        
        scan_id = c.lastrowid
        conn.commit()
        conn.close()
        return scan_id

    def store_point_cloud(self, scan_id, points):
        """Store processed point cloud data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Points should be a list of (x, y, z) tuples
        point_data = [(scan_id, x, y, z, timestamp) for x, y, z in points]
        
        c.executemany('''
        INSERT INTO point_clouds (scan_id, x, y, z, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', point_data)
        
        conn.commit()
        conn.close()

    def store_octomap(self, resolution, file_path, point_count):
        """Store octomap metadata"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        INSERT INTO octomaps (timestamp, resolution, file_path, point_count)
        VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), resolution, file_path, point_count))
        
        map_id = c.lastrowid
        conn.commit()
        conn.close()
        return map_id

    def get_latest_scans(self, limit=10):
        """Retrieve latest scans with metadata"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        SELECT scan_id, timestamp, altitude_angle_count, encoder_angle_count
        FROM raw_scans
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (limit,))
        
        results = c.fetchall()
        conn.close()
        return results

    def get_point_cloud_by_scan_id(self, scan_id):
        """Retrieve point cloud data for a specific scan"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        SELECT x, y, z
        FROM point_clouds
        WHERE scan_id = ?
        ''', (scan_id,))
        
        points = c.fetchall()
        conn.close()
        return points

    def get_raw_scan_data(self, scan_id):
        """Retrieve raw scan data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        SELECT data, altitude_angle_count, encoder_angle_count
        FROM raw_scans
        WHERE scan_id = ?
        ''', (scan_id,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            data_bytes, alt_count, enc_count = result
            # Convert bytes back to numpy array
            data = np.frombuffer(data_bytes).reshape(alt_count, enc_count)
            return data
        return None
