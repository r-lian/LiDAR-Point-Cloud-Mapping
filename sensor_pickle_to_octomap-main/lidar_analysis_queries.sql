-- LiDAR Data Analysis Queries
-- These queries demonstrate various analyses and data retrieval operations
-- on the LiDAR point cloud database

-- 1. Basic Scan Information
-- Get all scans with their basic metadata
SELECT 
    scan_id,
    timestamp,
    altitude_angle_count,
    encoder_angle_count
FROM raw_scans
ORDER BY timestamp DESC;

-- 2. Point Cloud Statistics by Scan
-- Calculate basic statistics for each scan's point cloud
SELECT 
    pc.scan_id,
    rs.timestamp,
    COUNT(*) as point_count,
    ROUND(AVG(x), 2) as avg_x,
    ROUND(AVG(y), 2) as avg_y,
    ROUND(AVG(z), 2) as avg_z,
    ROUND(MIN(x), 2) as min_x,
    ROUND(MAX(x), 2) as max_x,
    ROUND(MIN(y), 2) as min_y,
    ROUND(MAX(y), 2) as max_y,
    ROUND(MIN(z), 2) as min_z,
    ROUND(MAX(z), 2) as max_z
FROM point_clouds pc
JOIN raw_scans rs ON pc.scan_id = rs.scan_id
GROUP BY pc.scan_id
ORDER BY rs.timestamp DESC;

-- 3. Time-based Analysis
-- Get scans and point counts within a specific time range
SELECT 
    rs.scan_id,
    rs.timestamp,
    COUNT(pc.point_id) as point_count
FROM raw_scans rs
LEFT JOIN point_clouds pc ON rs.scan_id = pc.scan_id
WHERE rs.timestamp BETWEEN '2025-01-22T00:00:00' AND '2025-01-23T23:59:59'
GROUP BY rs.scan_id
ORDER BY rs.timestamp;

-- 4. Octomap Generation Analysis
-- Track octomap generation details with associated point clouds
SELECT 
    o.map_id,
    o.timestamp as map_timestamp,
    o.resolution,
    o.file_path,
    o.point_count as total_points,
    COUNT(DISTINCT rs.scan_id) as num_scans_used
FROM octomaps o
LEFT JOIN raw_scans rs ON DATE(o.timestamp) = DATE(rs.timestamp)
GROUP BY o.map_id
ORDER BY o.timestamp DESC;

-- 5. Point Distribution Analysis
-- Analyze the distribution of points in 3D space
SELECT 
    scan_id,
    ROUND(x/5.0) * 5 as x_bucket,
    ROUND(y/5.0) * 5 as y_bucket,
    COUNT(*) as point_density
FROM point_clouds
GROUP BY scan_id, x_bucket, y_bucket
ORDER BY scan_id, point_density DESC;

-- 6. Scan Quality Metrics
-- Calculate metrics to assess scan quality
SELECT 
    pc.scan_id,
    rs.timestamp,
    COUNT(*) as total_points,
    ROUND(MAX(SQRT(x*x + y*y + z*z)), 2) as max_distance,
    ROUND(AVG(SQRT(x*x + y*y + z*z)), 2) as avg_distance,
    ROUND(SQRT(AVG(x*x) + AVG(y*y) + AVG(z*z)), 2) as rms_distance
FROM point_clouds pc
JOIN raw_scans rs ON pc.scan_id = rs.scan_id
GROUP BY pc.scan_id
ORDER BY rs.timestamp DESC;

-- 7. Sequential Scan Comparison
-- Compare consecutive scans to analyze changes
WITH scan_stats AS (
    SELECT 
        pc.scan_id,
        rs.timestamp,
        AVG(SQRT(x*x + y*y + z*z)) as avg_distance
    FROM point_clouds pc
    JOIN raw_scans rs ON pc.scan_id = rs.scan_id
    GROUP BY pc.scan_id
)
SELECT 
    s1.scan_id as scan_id,
    s1.timestamp,
    s1.avg_distance,
    s2.scan_id as prev_scan_id,
    s2.avg_distance as prev_avg_distance,
    ROUND(ABS(s1.avg_distance - s2.avg_distance), 2) as distance_change
FROM scan_stats s1
LEFT JOIN scan_stats s2 ON s1.scan_id = s2.scan_id + 1
ORDER BY s1.scan_id;

-- 8. Point Cloud Density Analysis
-- Analyze point density in different spatial regions
SELECT 
    scan_id,
    CASE 
        WHEN SQRT(x*x + y*y) <= 2 THEN 'near'
        WHEN SQRT(x*x + y*y) <= 5 THEN 'medium'
        ELSE 'far'
    END as distance_category,
    COUNT(*) as point_count,
    ROUND(AVG(SQRT(x*x + y*y + z*z)), 2) as avg_distance
FROM point_clouds
GROUP BY scan_id, distance_category
ORDER BY scan_id, distance_category;

-- 9. Temporal Analysis
-- Analyze scanning patterns over time
SELECT 
    strftime('%Y-%m-%d', timestamp) as scan_date,
    COUNT(*) as scans_per_day,
    SUM(altitude_angle_count * encoder_angle_count) as total_points_captured
FROM raw_scans
GROUP BY scan_date
ORDER BY scan_date DESC;

-- 10. Data Quality Check
-- Identify potential anomalies in point cloud data
SELECT 
    pc.scan_id,
    rs.timestamp,
    COUNT(*) as anomaly_points
FROM point_clouds pc
JOIN raw_scans rs ON pc.scan_id = rs.scan_id
WHERE ABS(x) > 100 OR ABS(y) > 100 OR ABS(z) > 100  -- Unrealistic distances
    OR SQRT(x*x + y*y + z*z) < 0.1  -- Too close (potential noise)
GROUP BY pc.scan_id
HAVING anomaly_points > 0
ORDER BY anomaly_points DESC;
