# LiDAR Data Analysis and 3D Mapping Pipeline

A comprehensive system for converting 2D LiDAR data into 3D probabilistic occupancy maps (OctoMap) with integrated SQL database storage. This project implements advanced drone localization and mapping capabilities by combining 2D LiDAR measurements with sophisticated spatial transformation and probabilistic mapping techniques.

## Project Overview

This project implements a complete system for drone-based 3D environment mapping using 2D LiDAR sensors. The system consists of three main components:

1. **2D to 3D Conversion Pipeline**
   - Converts 2D LiDAR scans into 3D point clouds
   - Uses precise angular measurements and coordinate transformations
   - Handles 32 vertical positions and 512 horizontal points per revolution

2. **Probabilistic Mapping with OctoMap**
   - Implements OctoMap for 3D environment representation
   - Uses octree data structure for efficient spatial partitioning
   - Applies probabilistic updates for handling sensor uncertainty

3. **Data Analysis and Storage**
   - SQL database integration for data management
   - Comprehensive analysis tools and visualizations
   - Quality metrics and performance monitoring

### Key Features

- **2D LiDAR Integration**
  - Vertical scanning range: -22° to +21.5°
  - Horizontal coverage: 360° with 512-point resolution
  - 32 distinct altitude angles for vertical coverage

- **3D Mapping Capabilities**
  - Probabilistic occupancy mapping
  - Multi-resolution environment representation
  - Efficient memory usage through octree structure

- **Drone Integration**
  - Support for various flight patterns
  - Real-time mapping updates
  - Position estimation and path planning

## Technical Implementation

### 2D to 3D Conversion Process

The system converts 2D LiDAR data to 3D point clouds through:

1. **Data Collection**
   ```python
   # Angle calculations
   altitude_angle = altitude_angle_index * ((21.4764 * 2 + 1) / 32)
   encoder_angle = encoder_angle_index * math.pi / 512
   ```

2. **Coordinate Transformation**
   ```python
   # Polar to Cartesian conversion
   x = radius * math.cos(encoder_angle) * math.cos(altitude_angle)
   y = radius * math.sin(encoder_angle) * math.cos(altitude_angle)
   z = -1.0 * radius * math.sin(altitude_angle)
   ```

### OctoMap Integration

The system uses OctoMap for probabilistic 3D mapping:

1. **Octree Structure**
   - Recursive spatial subdivision into octants
   - Each node represents a volume of space
   - Leaf nodes store occupancy probabilities

2. **Probabilistic Updates**
   ```cpp
   // Creating octree with 10cm resolution
   OcTreeStamped tree(10);
   
   // Updating occupancy probability
   point3d end(x,y,z);
   tree.updateNode(end,true);
   
   // Optimizing the map
   tree.toMaxLikelihood();
   tree.updateInnerOccupancy();
   ```

3. **Binary Bayes Filter**
   The occupancy probability P(n|z1:t) for each node n is updated using:
   ```
   log-odds(P(n|z1:t)) = log-odds(P(n|zt)) + log-odds(P(n|z1:t-1)) - log-odds(P(n))
   ```

### Mapping Pipeline

1. **Data Flow**
   - Raw sensor data (pickle format)
   - Conversion to CSV with XYZ coordinates
   - OctoMap generation (.bt format)

2. **Memory Optimization**
   - Automatic pruning of empty volumes
   - Node merging at higher levels
   - Efficient storage of observed regions

3. **Multi-Resolution Features**
   - Variable resolution queries
   - Coarse-to-fine representation
   - Hierarchical spatial organization

## Repository Structure

### Core Components

- `db_utils.py`: Database utility class managing SQLite interactions
  - Handles raw scan storage
  - Manages point cloud data
  - Tracks OctoMap metadata
  - Provides query interfaces

- `synthetic_data_generator.py`: Generates synthetic LiDAR data
  - Creates random 3D environments
  - Simulates sensor noise
  - Generates consistent 32x512 resolution scans
  - Stores data in the database

- `sensor_pickle_to_xyz_csv.py`: Data format conversion utility
  - Converts pickle files to CSV format
  - Processes raw sensor data
  - Integrates with database storage

- `analyze_lidar_data.py`: Analysis and visualization tool
  - Executes SQL queries from `lidar_analysis_queries.sql`
  - Generates visualizations
  - Saves analysis results
  - Provides comprehensive data insights

- `test_pipeline.py`: Integration test script
  - Demonstrates complete workflow
  - Validates data processing
  - Tests database operations

### SQL Components

- `lidar_analysis_queries.sql`: Collection of analysis queries
  - Basic scan information
  - Point cloud statistics
  - Temporal analysis
  - Quality metrics
  - Distribution analysis

### Output Directories

- `analysis_output/`: Contains generated visualizations
  - Query result plots
  - Point distribution heatmaps
  - Temporal analysis graphs
  - Quality metric visualizations

- `synthetic_data/`: Stores generated test data
  - Raw scan files
  - Processed point clouds
  - Intermediate data products

## Data Analysis Capabilities

### 1. Basic Scan Information (Query 1)
- Tracks 16 scans with 512 encoder angles each
- Monitors horizontal resolution
- Validates scan parameter consistency

### 2. Point Cloud Statistics (Query 2)
- 16,384 points per scan (32x512 resolution)
- Coverage: -10 to +10 meter range
- Full 3D dimensional analysis

### 3. Temporal Analysis (Query 3)
- Multi-day scan tracking
- Consistent point count verification
- Distribution analysis over time

### 4. Point Distribution Analysis (Query 5)
- 2D heatmap visualization
- Spatial bucket distribution
- Density concentration mapping
- Center region analysis

### 5. Quality Metrics (Query 6)
- Average distances: 9.75-9.88 meters
- RMS distances: 9.83-9.90 meters
- Consistency validation

### 6. Point Cloud Density (Query 8)
- Distance-based categorization
  - Far: ~10,500 points
  - Medium: ~3,100 points
  - Near: ~2,700 points
- 360° coverage analysis

### 7. Temporal Patterns (Query 9)
- Daily scan counts
  - 2025-01-23: 13 scans
  - 2025-01-22: 3 scans
- Total point tracking: 262,144 points

### 8. Data Quality Assessment (Query 10)
- Anomaly detection
- Range validation
- Quality assurance metrics

## Installation and Usage

### Basic Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/sensor_pickle_to_octomap.git
cd sensor_pickle_to_octomap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Compiling Point Cloud Reader
```bash
./compile.sh
```

### Processing Pipeline
1. Convert sensor data:
   ```bash
   ./sensor_pickle_to_xyz_csv.py ./test.pickle > test_xyz.csv
   ```

2. Generate OctoMap:
   ```bash
   ./my_point_cloud_reader --xyz_csv ./test_xyz.csv --out test.bt
   ```

3. Visualize results:
   ```bash
   octovis test.bt
   ```

## Applications

### Drone Navigation
- Real-time obstacle detection
- Path planning at multiple resolutions
- Position estimation
- Dynamic environment mapping

### Environment Mapping
- 3D reconstruction of spaces
- Uncertainty handling
- Dynamic object tracking
- Memory-efficient representation

### Data Analysis
- LiDAR sensor calibration
- Point cloud analysis
- Coverage validation
- Quality assurance
- Temporal pattern analysis
- Spatial distribution studies

## Dependencies

- OctoMap library
- Python 3.7+
- NumPy
- Pandas
- Matplotlib
- Seaborn
- SQLite3

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Contributors to the project
- Open-source LiDAR processing community
- SQLite and Python ecosystem maintainers
- OctoMap library developers
