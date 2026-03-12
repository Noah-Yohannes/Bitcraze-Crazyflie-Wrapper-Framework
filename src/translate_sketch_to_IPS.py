
"""The goal of this script is to convert normalized 2D pixel coordiantes sketch to actual IPS coordinates
    
    Given the 2D nature of the sketch, the motion will be performaned in the x-z or y-z plane, according to user's preference. 

    It saves the translated pixel coordinates in the format the Crazyflie expects, x,y,z, velocity. If for instance we select the x-z plane, 
    then we take a constant y coordinate (midpoint) as the third coordinate. 
"""
from src.linear_mapping_normalization import normalize_value

def translate_sketch_to_ips(two_d_coordinates):
    """A function maps normalized sketch pixel values to the the IPS coordinate system using linear mapping to the IPS boundary values. 

    The input list of pixel value is 2D since it originals from a sketch in a 2D frame. Thus, the movement will be displayed either in the x-z plane or 
    y-z plane in the drone cage. Which plane we want to use can be specified beforehand. 

    We sample the recorded brush/sketch points to a manageable set of points that the drone could travel to.  
    """
    x_min = 0.5 ; x_max = 6.0
    y_min = 0.5 ; y_max = 5.0
    z_min = 0.3 ; z_max = 2.5
    mid_x = 3.25
    mid_y = 2.75
    velocity = 0.2   

    motion_plane = "x_z"  # "y_z"
    sampling_rate = 20   # take/ sample every 40 points 

    three_d_translated_coordinates = []
    sampled_three_d_translated_coordinates = []

    for pixel_val in two_d_coordinates: 

        if motion_plane == "x_z":
            first_coordiante = normalize_value (pixel_val[0],0, 1, x_min, x_max)  
            second_coordinate = normalize_value(pixel_val[1], 0, 1, z_min, z_max)
            coordinates_tuple = (first_coordiante,mid_y, second_coordinate, velocity)
        else: 
            first_coordiante = normalize_value (pixel_val[0],0, 1, y_min, y_max)  
            second_coordinate = normalize_value(pixel_val[1], 0, 1, z_min, z_max)
            coordinates_tuple = (mid_x, first_coordiante, second_coordinate, velocity)

        three_d_translated_coordinates.append(coordinates_tuple)
    
    # Sampling few points every sampling_rate points from the list of translated coordinates 
    for index, value in enumerate(three_d_translated_coordinates):
        if (index%sampling_rate ==0):
            sampled_three_d_translated_coordinates.append(value)  
    
    return three_d_translated_coordinates, sampled_three_d_translated_coordinates


    





