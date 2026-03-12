

from src.linear_mapping_normalization  import normalize_value

def ar_to_ips_coordinates(two_d_coordinates):
    """
    A function that takes in the AR coordinates in the virtual scale and translates it to the IPS dimensions scale.
    """

    x_min = 0.5 ; x_max = 6.0
    y_min = 0.5 ; y_max = 5.0
    z_min = 0.3 ; z_max = 2.5
    mid_x = 3.25
    mid_y = 4.5 #2.75
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
        with open("IPS_coordinates.txt", 'a') as file:
            file.write(str(coordinates_tuple))

    
    # Sampling few points every sampling_rate points from the list of translated coordinates 
    for index, value in enumerate(three_d_translated_coordinates):
        if (index%sampling_rate ==0):
            sampled_three_d_translated_coordinates.append(value)  
    
    return three_d_translated_coordinates, sampled_three_d_translated_coordinates


    