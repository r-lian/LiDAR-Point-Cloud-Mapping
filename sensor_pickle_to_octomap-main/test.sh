#!/bin/sh

./sensor_pickle_to_xyz_csv.py ./test.pickle > test_xyz.csv
./my_point_cloud_reader --xyz_csv ./test_xyz.csv --out test.bt
octovis test.bt
