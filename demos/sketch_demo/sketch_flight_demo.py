
# Main Script to set up everything 
import cflib.crtp  # for scanning Crazyflie instances 
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from src.control.crazyflie_wrapper import Crazyflie_Wrapper  # Importing the wrapper class
from demos.sketch_pattern_gui import launch_flightmaker
from src.read_save_sequences import read_sequences_from_file

# List of special safety buttons to control flight:
"""
- Home, home key, authorizes the drone to take-off and execute its planned mission. Without this authorization the drone won't fly
- the down arrow key, instructs the drone to descend smoothly (gracefully) at any point during its flight
- Esc, escape key, shutts of all motors and the drone falls of instantly. Use this only when necessary because a hard fall could damage the drone's parts. 
- end, end key, computes and sends the maneuver challenge to the drone at any point of its flight
"""

# Initialize the drivers 
cflib.crtp.init_drivers()

# First, lets set up the drone and configure it properly, such as assigning its URI  

# assigning the radio URI address of the drone
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E9')   # each drone is labelled with its uri address, if need be this address can be changed in the cfclient console

# setting a starting position to visually understand the drone's successful take-off
starting_position = (1.5,2.5,1.0)   

# Option 2: In this demo, we are sketching the pattern we want and let the wrapper fly the drone according to our pattern and selected flight axis


pattern_saved_file_name, mission_coordinates  = launch_flightmaker()


""" 
    Observe the Log variables such as drone's position printed in the terminal, authorize flight (home button) and only if the values are stable and reasonable. 
    If not, refer to the documentation (readMe page or wiki js) or hover over the class to identify the cause and fix it to ensure a stable flight.  
"""

# The with keyword here is essential for safe resource allocation and deallocation, the Crazyflie and the syncCrazyflie won't work as expected without
with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

    # Initialize the wrapper object with the connected scf
    drone_obj = Crazyflie_Wrapper(scf, default_height=0.5, motion_controller = "PID")   
    
    # Ensuring the drone is ready to take off to the mission_coordinates whenever we give it the authorization signal  
    drone_obj.automatic_coordinate_based(mission_coordinates, starting_position)   



