
import json 

def parse_ar_coordinates(ar_json_file):
    """A function to parse AR coordinates (provided in the left-hand cartesian coordinates) to the IPS cartesian cartesian axes/coordinates.
     
    It will do two things: first parse the coordinates and then return the coordinates in normal IPS cartesian axes directions instead of Unity's left-hand
    directions axis. """

    print("Inside the parse_ar_coordinates")
    

    extracted_ar_coordinates = []


    data = json.loads(ar_json_file)
    positions = data['positions']

    for coord_dict in positions:
        # First we will get the coordinates as they are in Unity's left-hand coordiante system
        ar_x = coord_dict['x']
        ar_y = coord_dict['y']
        ar_z = coord_dict['z']

        # Then we will reassign the axes to align with IPS's normal cartesian coordinate system 

        extracted_ar_coordinates.append((ar_x,ar_z, ar_y))
    
    return extracted_ar_coordinates
     


# parse_ar_coordinates()
