import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import os

class LiDARDataAnalyzer:
    def __init__(self, db_path="lidar_data.db", queries_path="lidar_analysis_queries.sql"):
        self.db_path = db_path
        self.queries_path = queries_path
        self.queries = self._load_queries()
        
    def _load_queries(self):
        """Load SQL queries from file"""
        with open(self.queries_path, 'r') as f:
            content = f.read()
            # Split queries and pair them with their descriptions
            queries = {}
            current_query = []
            current_num = None
            current_desc = None
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('--'):
                    # New query section
                    if current_num is not None and current_query:
                        queries[current_num] = {
                            'description': current_desc,
                            'query': '\n'.join(current_query)
                        }
                        current_query = []
                    
                    # Try to parse query number
                    try:
                        num_str = line.replace('--', '').strip().split('.')[0]
                        current_num = int(num_str)
                        current_desc = line.replace('--', '').strip()
                        print(f"Found query {current_num}: {current_desc}")
                    except (ValueError, IndexError):
                        if current_num is not None:
                            current_desc = (current_desc or '') + ' ' + line.replace('--', '').strip()
                else:
                    if current_num is not None:
                        current_query.append(line)
            
            # Add the last query
            if current_num is not None and current_query:
                queries[current_num] = {
                    'description': current_desc,
                    'query': '\n'.join(current_query)
                }
            
            print(f"Loaded {len(queries)} queries from file")
            return queries

    def run_query(self, query_number):
        """Run a specific query and return results as a pandas DataFrame"""
        if query_number not in self.queries:
            raise ValueError(f"Query number {query_number} not found")
        
        conn = sqlite3.connect(self.db_path)
        query = self.queries[query_number]['query']
        try:
            df = pd.read_sql_query(query, conn)
            print(f"Query returned {len(df)} rows")
            return df
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            print(f"Query was: {query}")
            return pd.DataFrame()
        finally:
            conn.close()

    def visualize_query_results(self, query_number):
        """Create appropriate visualizations for query results"""
        df = self.run_query(query_number)
        if df.empty:
            print(f"No data available for query {query_number}")
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            return fig
            
        description = self.queries[query_number]['description']
        print(f"Creating visualization for {len(df)} rows of data")
        
        plt.figure(figsize=(12, 6))
        plt.title(f"Query {query_number}: {description}")
        
        if query_number == 1:  # Basic Scan Information
            plt.scatter(df['timestamp'], df['altitude_angle_count'] * df['encoder_angle_count'])
            plt.xlabel('Timestamp')
            plt.ylabel('Total Points')
            plt.xticks(rotation=45)
            
        elif query_number == 2:  # Point Cloud Statistics
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            axes[0].plot(df['timestamp'], df['avg_x'], label='X')
            axes[0].plot(df['timestamp'], df['avg_y'], label='Y')
            axes[0].plot(df['timestamp'], df['avg_z'], label='Z')
            axes[0].set_xlabel('Timestamp')
            axes[0].set_ylabel('Average Position')
            axes[0].legend()
            axes[0].tick_params(axis='x', rotation=45)
            
            axes[1].bar(range(len(df)), df['point_count'])
            axes[1].set_xlabel('Scan ID')
            axes[1].set_ylabel('Point Count')
            
        elif query_number == 5:  # Point Distribution Analysis
            # Create a pivot table for the latest scan
            latest_scan = df['scan_id'].max()
            df_latest = df[df['scan_id'] == latest_scan]
            
            # Create a 2D matrix for the heatmap
            x_buckets = sorted(df_latest['x_bucket'].unique())
            y_buckets = sorted(df_latest['y_bucket'].unique())
            density_matrix = np.zeros((len(x_buckets), len(y_buckets)))
            
            # Fill the matrix
            for _, row in df_latest.iterrows():
                x_idx = x_buckets.index(row['x_bucket'])
                y_idx = y_buckets.index(row['y_bucket'])
                density_matrix[x_idx, y_idx] = row['point_density']
            
            fig, ax = plt.subplots(figsize=(12, 10))
            im = ax.imshow(density_matrix, cmap='viridis', origin='lower')
            plt.colorbar(im, ax=ax, label='Point Density')
            
            # Set tick labels
            ax.set_xticks(range(len(y_buckets)))
            ax.set_yticks(range(len(x_buckets)))
            ax.set_xticklabels([f"{y:.1f}" for y in y_buckets])
            ax.set_yticklabels([f"{x:.1f}" for x in x_buckets])
            
            plt.title(f"Point Distribution Analysis (Scan ID: {latest_scan})")
            plt.xlabel('Y Bucket (meters)')
            plt.ylabel('X Bucket (meters)')
            plt.tight_layout()
            
        elif query_number == 6:  # Scan Quality Metrics
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            axes[0].plot(df['timestamp'], df['max_distance'], label='Max')
            axes[0].plot(df['timestamp'], df['avg_distance'], label='Avg')
            axes[0].set_xlabel('Timestamp')
            axes[0].set_ylabel('Distance (m)')
            axes[0].legend()
            axes[0].tick_params(axis='x', rotation=45)
            
            axes[1].scatter(df['total_points'], df['rms_distance'])
            axes[1].set_xlabel('Total Points')
            axes[1].set_ylabel('RMS Distance (m)')
            
        elif query_number == 8:  # Point Cloud Density Analysis
            df_pivot = df.pivot(index='scan_id', columns='distance_category', values='point_count')
            df_pivot.plot(kind='bar', stacked=True)
            plt.xlabel('Scan ID')
            plt.ylabel('Point Count')
            plt.legend(title='Distance Category')
            plt.xticks(rotation=45)
            
        elif query_number == 9:  # Temporal Analysis
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            axes[0].plot(df['scan_date'], df['scans_per_day'])
            axes[0].set_xlabel('Date')
            axes[0].set_ylabel('Scans per Day')
            axes[0].tick_params(axis='x', rotation=45)
            
            axes[1].plot(df['scan_date'], df['total_points_captured'])
            axes[1].set_xlabel('Date')
            axes[1].set_ylabel('Total Points')
            axes[1].tick_params(axis='x', rotation=45)
            
        else:
            # Generic visualization for other queries
            if len(df.columns) > 1:
                df.plot(kind='bar')
                plt.xticks(rotation=45)
            else:
                plt.bar(range(len(df)), df[df.columns[0]])
                plt.xlabel('Index')
                plt.ylabel(df.columns[0])
        
        plt.tight_layout()
        return plt.gcf()

    def run_all_analyses(self, save_plots=True):
        """Run all analyses and optionally save plots"""
        # Create output directory if it doesn't exist
        if save_plots:
            output_dir = "analysis_output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
        for query_number in self.queries.keys():
            print(f"\nRunning Query {query_number}: {self.queries[query_number]['description']}")
            try:
                df = self.run_query(query_number)
                print("\nSample Results:")
                print(df.head())
                
                fig = self.visualize_query_results(query_number)
                if save_plots:
                    output_path = os.path.join(output_dir, f'query_{query_number}_visualization.png')
                    fig.savefig(output_path)
                    print(f"Saved visualization to: {output_path}")
                plt.close(fig)
                
            except Exception as e:
                print(f"Error analyzing query {query_number}: {str(e)}")

def main():
    # Create analyzer instance
    analyzer = LiDARDataAnalyzer()
    
    print("=== LiDAR Data Analysis ===")
    print("\nAvailable analyses:")
    for num, query_info in analyzer.queries.items():
        print(f"{num}. {query_info['description']}")
    
    # Run all analyses
    print("\nRunning all analyses...")
    analyzer.run_all_analyses()
    
    print("\nAnalysis complete! Visualization files have been saved.")

if __name__ == "__main__":
    main()
