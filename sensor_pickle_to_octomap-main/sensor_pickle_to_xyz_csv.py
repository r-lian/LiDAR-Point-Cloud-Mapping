#!/bin/python3
import sys
import matplotlib.pyplot as plt
import pickle
import math
import numpy
from db_utils import LiDARDatabase

def sensor_data_to_cartesian_coordinates(sensor_data):
    cartesian_coordinates = [[],[],[]]
    for altitude_angle_index, data in enumerate(sensor_data):
        for encoder_angle_index, item in enumerate(data):

            radius = item
            encoder_angle = encoder_angle_index * math.pi / 512
            # encoder_angle = 2 * math.pi * ( 1 - encoder_angle_index / 90112 )
            altitude_angle = ( -22 + altitude_angle_index * ( ( 21.4764 * 2 + 1 ) / 32 ) ) * math.pi / 180
            # altitude_angle = altitude_angle_index * 0.4 * math.pi / 180
            # altitude_angle = altitude_angle_index * 0.5 * math.pi / 180
            # altitude_angle = altitude_angle_index * ( 94 / 32 ) * math.pi / 180
            # altitude_angle = altitude_angle_index * ( 1.4 ) * math.pi / 180

            x = radius * math.cos(encoder_angle) * math.cos(altitude_angle)
            y = radius * math.sin(encoder_angle) * math.cos(altitude_angle)
            z = -1.0 * radius * math.sin(altitude_angle)

            coordinates = [x,y,z]
            # print(coordinates)
            
            cartesian_coordinates[0].append(x)
            cartesian_coordinates[1].append(y)
            cartesian_coordinates[2].append(z)


    return cartesian_coordinates


def main():
    file_names = sys.argv
    file_names.pop(0)
    cartesian_coordinates = [[],[],[]]
    db = LiDARDatabase()

    for file_name in file_names:

        sensor_data_pickle = open(r"./" + file_name, "rb")
        sensor_data = pickle.load(sensor_data_pickle)

        # Store raw scan in database
        scan_id = db.store_raw_scan(sensor_data, len(sensor_data), len(sensor_data[0]))

        _cartesian_coordinates = sensor_data_to_cartesian_coordinates(sensor_data)
        
        # Prepare points for database storage
        points = list(zip(_cartesian_coordinates[0], _cartesian_coordinates[1], _cartesian_coordinates[2]))
        db.store_point_cloud(scan_id, points)

        cartesian_coordinates[0].extend(_cartesian_coordinates[0])
        cartesian_coordinates[1].extend(_cartesian_coordinates[1])
        cartesian_coordinates[2].extend(_cartesian_coordinates[2])


    xs = cartesian_coordinates[0]
    ys = cartesian_coordinates[1]
    zs = cartesian_coordinates[2]

    print("x,y,z")
    for index,x in enumerate(xs):
        line = str(x) + "," + str(ys[index]) + "," + str(zs[index])
        print(line)


    # fig = plt.figure()
    # ax = fig.add_subplot(projection='3d')
    # ax.scatter3D(cartesian_coordinates[0],cartesian_coordinates[1],cartesian_coordinates[2])

    # plt.show()

main()
