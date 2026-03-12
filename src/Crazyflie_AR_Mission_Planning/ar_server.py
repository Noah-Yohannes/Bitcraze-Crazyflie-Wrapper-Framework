
# Server will run on the drone contoller PC 


# Main Script to set up everything 
import cflib.crtp  # for scanning Crazyflie instances 
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from src.control.crazyflie_wrapper import Crazyflie_Wrapper  # Importing the wrapper class

# List of special buttons:
"""
- Home, home key, authorizes the drone to take-off and execute its planned mission. Without this authorization the drone won't fly
- ⬇️, down arrow key, instructs the drone to descend smoothly (gracefully) at any point during its flight
- Esc, escape key, shutts of all motors and the drone falls of instantly. Use this only when necessary because a hard fall could damage the drone's parts. 
- end, end key, computes and sends the maneuver challenge to the drone at any point of its flight
"""


import asyncio
from websockets.server import serve
from src.Crazyflie_AR_Mission_Planning.parse_ar_coordinates import parse_ar_coordinates
from src.Crazyflie_AR_Mission_Planning.ar_to_ips_coordinates import ar_to_ips_coordinates

# Initialize the drivers 
cflib.crtp.init_drivers()

#--------------------  Drone set up and configurations -----------------------------

# Set the radio URI address of the drone
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E9')   # each drone is labelled with its uri address, if need be this address can be changed in the cfclient console

async def echo(websocket):
    async for message in websocket:
        print("Client said: "+message)

        message = """{"positions":[{"x":0.00999999978,"y":0.994000018,"z":-0.128000006},{"x":-0.209999993,"y":0.994000018,"z":0.0260000005},
        {"x":-0.0980000049,"y":0.994000018,"z":0.203999996},{"x":0.0889999941,"y":0.994000018,"z":0.194000006},
        {"x":0.213999987,"y":0.994000018,"z":0.00400000019}]}"""

        # Parse the received message taking the Unity Cartesian left hand direction rule into consideration 
        parsed_details = parse_ar_coordinates (ar_json_file=message) 

        # Translate the received coordinates to IPS coordinates 
        ips_coordinates,_ = ar_to_ips_coordinates (parsed_details)

        # set starting position
        starting_position = ips_coordinates[0]

        mission_coordinates = ips_coordinates

        # The with keyword here is essential for safe resource allocation and deallocation, the Crazyflie and the syncCrazyflie won't work as expected without
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

            # Initialize the wrapper object with the connected scf
            drone_obj = Crazyflie_Wrapper(scf, default_height=0.5, motion_controller = "PID")   
            
            # Ensuring the drone is ready to take off to the mission_coordinates whenever we give it the authorization signal  
            drone_obj.automatic_coordinate_based(mission_coordinates, starting_position)   


        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())