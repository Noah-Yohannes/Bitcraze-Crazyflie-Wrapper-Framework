

# Main script that kicks of the whole wrapper. 

import logging
import time
import time
import keyboard
from pynput import keyboard
import threading
from functools import partial
from typing import Union
import csv 
from collections import deque
import os 

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper

# importing libraries for cflib
import cflib.crtp    # for scanning Crazyflie instances 
from cflib.crazyflie import Crazyflie   # class used to connect/receive ans send data from Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie   # wrapper around Crazyflie to handle asynchronous nature of  Crazyflie API, 
                                                            # that is ensuring a connection is first setup before trying to communicate-send/receive with the Crazyflie instance 
from cflib.utils import uri_helper 

#------  importing libraries to read logging variables
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig    # a class representation of one log configuration that enables logging from the Crazyflie
from cflib.crazyflie.syncLogger import SyncLogger   # class provides synchronous access to log data from the Crazyflie.

from src.control.led_controller import LEDController

class Crazyflie_Wrapper():
    """BitCraze wrapper class that wrapps the bitcraze api. This class implements the following functionalities in high-level: 
    - Getting log variables in real-time.
    - Setting crazyflie parameters. 
    - Automated flights in 2 modes : using a sequence of directions or 3D coordinates. 
    - Safety measures : emergency and graceful landing using keyboard keys. 

    
    List of special buttons:
    - Home, home key, authorizes the drone to take-off and execute its planned mission. Without this authorization the drone won't fly
    - the down arrow key, instructs the drone to descend smoothly (gracefully) at any point during its flight
    - Esc, escape key, shutts of all motors and the drone falls of instantly. Use this only when necessary because a hard fall could damage the drone's parts. 
    - end, end key, computes and sends the maneuver challenge to the drone at any point of its flight


    Steps to check/follow before taking off (I came with these points just solely based on multiple trials)

    - Open cfclient console, in the flight control tab observe if the horizon level is stable. As long as the drone is placed on a flat surface, the horizon should be stable. 
    - If not, the drone's parameters either the positioning in IPS or the yaw/roll/pitch are unstable and the drone will not be able to fly/take-off successfully. 
    - In the lighhouse position tab, check if the drone is communicating with the beacons (green status), there should be fully green columns (a column represents each beacon)
    
    If either of the two checks above fail, the causes might be: 
    -  Either the sensors in the header board in the drone are dusty: so wipe the four sensors using a soft tissue. 
    - The header sensor board might be loose: so gently push the header board downard to fit/connect properly to the drone. 

    - Orient the drone parallel to the x-axis, with the head away from the origin (twoards +x-axis). This ensures easy take-off instead of the drone spining until it gets the right orientation itself.
    - Don't put the drone in either of the drone cage corners, they are blind spots and might not receive the laser signal from either of the beacons.  

     
    """
    def __init__(self, scf, default_height, motion_controller):

        self.scf = scf 
        self.cf = self.scf.cf

        if  motion_controller == "PID":
            controller_choice = PositionHlCommander.CONTROLLER_PID
        else : 
            controller_choice = PositionHlCommander.CONTROLLER_MELLINGER

        self.led = LEDController(self.cf)

        # --------    Global variables --------------------
        self.graceful_landing = False     # signals the system to land gracefully 
        self.proceed_automated_flight = False   # signals to the system whether to proceed with automated flight or not based on observed log 
        self.interrupt_mission = False    # set to true whenever graceful landing or emergency landing is pressed to prevent the drone from continuing to execute mission
        self.monitoring = True    # boolean variable to indicate when we should stop monitoring for battery level
        self.lab_maximum_x = 6.8
        self.lab_maximum_y = 5.3

        self.challenge_interrupt_signal = False 

        self.average_battery_level = 100
        self.aggregate_battery_level = [] # list to store the latest 10 battery levels to take the average 
        # self.aggregate_battery_counter = 0

        # Output log related 
        self.csv_file_path = "log_output.csv"
        field_names = ["pos_x", "pos_y", "pos_z", "pm_battery", "pm_state", "sys_canfly", "sys_isflying","l_status", "l_active", "l_available", "l_calibrated" ]
        if os.path.exists(self.csv_file_path):
            os.remove(self.csv_file_path)
            print(f"File '{self.csv_file_path}' deleted successfully.")
        else:
            print(f"File '{self.csv_file_path}' does not exist.")
            print("Starting the constructor function")

        
        # self.cf.platform.send_arming_request(True)

        # self.cf.
        time.sleep(1.0)

        # ----------   Printing log variables  ----------------
        self.pos_x, self.pos_y, self.pos_z,_, _, _, _, _, _, battery_level, _ = \
            self.get_log()

        # Only output errors from the logging framework
        # self.logging.basicConfig(level=logging.ERROR)

        self.pc = PositionHlCommander(
                                self.scf,
                                x=self.pos_x,
                                y=self.pos_y, 
                                z=self.pos_z,
                                default_height=default_height,
                                default_velocity=0.2,
                                default_landing_height=0,
                                controller=controller_choice)  # CONTROLLER_MELLINGER - 
                                    # If we want to not use PID controller for fast movements and tracking we will use the CONTROLLER_MELLINGER
                                    # The mellinger focuses on smooth, dynamically feasible trajectories by minimizing the snap,
                                    # the fourth derivative of position (i.e., the rate of change of jerk). 
                                    # It was specially designed for tracjectory tracking quadrotors 

        # -----  Defining state estimators for stable estimation  ------------
        pram_name = "stabilizer.estimator"
        self.cf.param.set_value(pram_name, '2')
        time.sleep(2.5) 
        self.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(1)
        print("Set Stabilizer.estimator parameter to 2 & kalman.resetEstimation to 1")
        
        # ----- Starting off battery controlling thread    ---------------------
        battery_thread = threading.Thread(target=self.monitor_battery_level, args=())
        battery_thread.start()
        print('Started the logging thread. ')

        # -----   save log variables thread   ------------------
        save_log_thread = threading.Thread(target=self.save_log, args=())
        save_log_thread.start()
        time.sleep(2)
    
    # ---------    Set up   ----------------------
    def connect(self):
        pass 
    

    # --------- Take off & Landing options -----------------------
    def takeoff(self, mode = "coordinates", set_of_coordinates = [], initial_position=(), light_drone_LED = False):
        """Function to take off the drone. As the drone takes off, we initialize the
        listener_function that listens to keyboard presses so that if anything goes wrong
        we can land either gracefully or in emergency mode. This is crucial because the drone
        won't take off without our permission, which we give by pressing a key. 
        
        Additionally, we check if the drone has sufficient battery before taking off. If not, it won't and return 
        notification. """

        
        # Initializing the keyboard listener -------
        callback = partial(self.key_pressed_event_listener, self.pc, self.cf)
        listener = keyboard.Listener(on_press=callback)
        listener.start()

        # Checking if we actually want to control the drone's LED
        if light_drone_LED:
            self.led.identify_drone()  # this will ensur
        
        
        pram_name = "stabilizer.estimator"
        self.cf.param.set_value(pram_name, '2')
        time.sleep(2) 
        self.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(1.5)
        print("Set Stabilizer.estimator parameter to 2 & kalman.resetEstimation to 1")

        # Clearing the Kalman filter before we authorize the flight 
        self.cf.param.set_value('stabilizer.estimator', '2')
        self.cf.param.set_value('kalman.resetEstimation', '1')

        # ----------     Wait for permission to arm & send commands ------ 

        print("Waiting for confirmation to proceed with flight after checking log info.\n")
        while not self.proceed_automated_flight:  
            pos_x, pos_y, pos_z, _, _, _, _, _, sys_is_flying,battery_level, _ = self.get_log() 
            
            print(f"X : {round(pos_x,2)}\nY : {round(pos_y,2)}\nZ : {round(pos_z,2)}\nBattery Level : {battery_level}\nSys_is_flying : {sys_is_flying} \n\n\n")
            time.sleep(1.5)

        # Checking if battery is low or the drone is charging 
        if self.drone_is_charging == 1:
            print("🔋⚡ Selected drone is charging, so it is not taking off. ")
            return None
        
        if self.drone_is_charging == 1:
            print("🔋⚡ Selected drone is charging, so it is not taking off. ")
            return None
        
        # -------------      Flying drone after permission is granted   --------------
        # Arm the Crazyflie
        self.cf.platform.send_arming_request(True)  
        time.sleep(2)
        print("Should fly now")

        self.pc.take_off(height=0.5)  # this is very useful.
        print("After successful take off. ")
        print("Well here are the initial positions : ", initial_position[0],' ', initial_position[1], ' ',initial_position[2])
        if not self.interrupt_mission: 
            self.pc.go_to(initial_position[0], initial_position[1], initial_position[2])
        else: 
            print("❌ ❌ Flight aborted due to pressed interrupt button. ")
            # Emptying all the remaining lists to ensure the drone doesn't fly 
            set_of_coordinates = []
            dynamic_challenge_coord = []
            set_of_remaining_coordiantes = []

        last_coordinate = []  # a list to store the last visited coordinate 
        for coord in set_of_coordinates:

            # Flying to the next waypoint coordinate 
            if not self.interrupt_mission: 
                # If interrupt signal is not sent, the drone continues on its mission
                print("Well here are the current positions : ", coord[0],' ', coord[1], ' ',coord[2])
                self.pc.go_to(coord[0], coord[1], coord[2], velocity=coord[3])
                last_coordinate = coord  # saving the last visited coordinate
            else: 
                print("❌ ❌ Flight aborted due to pressed interrupt button. ")
                # Emptying all the remaining lists to ensure the drone doesn't fly 
                set_of_coordinates = []
                set_of_remaining_coordiantes = []

                self.pc.land()
                break
                

            # time.sleep(2)
            # print("Successfully completed this coordinate. ")
        print("Just before landing")
        self.pc.land()
        self.monitoring = False

    # ------   Safety Measures & Flight Authorization   --------------------------------
    def key_pressed_event_listener(self, mc, cf, key):
        """A crucial function that listens to which keys in the keyboard are pressed and
        sends signals to the system. It does three things: 
        
        1. Sends signal to take-off after we authorize flight. 
        2. In case of emergency landing, it invokes the emergency landing. 
        3. In other cases, it invokes graceful landing by not killing the motors right but landing gently. 
        """

        try:
            # if key.char == 'esc':  
            if key == keyboard.Key.esc:  
                print("✅  Emergency landing triggered!")
                graceful_landing = True 
                cf.platform.send_arming_request(False) 
                self.monitoring = False               
                self.interrupt_mission = True   # signal to stop flying right away 

            elif key == keyboard.Key.home:
                print("\n✅  Permission to proceed with automated flight granted !!!!")
                self.proceed_automated_flight = True
                # stop_log_event.set()
            elif key == keyboard.Key.down:
                print("Graceful landing triggered")
                mc.land()
                self.monitoring = False 
                self.interrupt_mission = True     # signal drone to stop flying right away 
                time.sleep(1)
                # mc.land()
                # cf.platform.send_arming_request(False)
                
            elif key == keyboard.Key.end:
                self.challenge_interrupt_signal = True 
                # Sending the challenge to the drone and asking it to execute the 
                # new movement. 
                pass
                
        except AttributeError:
            pass

    # ----------   Listing & Getting log info  --------------
    def list_log(self):
        """A function to list all of BitCraze log variables. """
        pass
    def get_specific_log(scf, group_and_var_name:Union[str, list, None], variable_type:Union[str, list, None]):
        """A function to get specific log variables. The get_log returns the basic and most commonly 
        used log variables; whereas this function returns specialized log variables not listed.
        
        That is, the user could either specify a single log they want by providing a string of the variable
        and its data type or it could be a list of multiple log variables they want to check.  
        
        If the group_and_var_name is a single string, then the output_log is also a single log value;
        however if it is a list, then the output_log is a list of the string log variables. 
        If the group_and_var_name is invalid or empty, then we thrown an error and return None
        """

        # Check the type : is it a string or a list of strings
        if (type(group_and_var_name) is str) and (type(variable_type) is str):
            # we fetch only a single variable
            output_log = 0  # initializing the output log variable
            pass 
        elif (type(group_and_var_name) is list) and (type(variable_type) is list):
            # we will iterate, add all variables to a logconfig variable, fetch the log and return a list output
            output_log = []  # initializing the output log list
        else: 
            output_log = None 
        return output_log

    def get_log(self):
        """Get the basic log variables, bare requirements such as the battery level, before trying to take off the drone. """
                
        lg = LogConfig(name='Basic Log info', period_in_ms=100)
        lg.add_variable("stateEstimate.x", 'float')
        lg.add_variable("stateEstimate.y", 'float')
        lg.add_variable("stateEstimate.z", 'float')
        
        # Status
        lg.add_variable("lighthouse.status", 'uint8_t')
        lg.add_variable("lighthouse.bsActive", 'uint16_t')   # bit field indicating which base stations are providing useful data to the estimator
        lg.add_variable("lighthouse.bsAvailable", 'uint16_t')  # bit field indicating which base stations are available
        lg.add_variable("lighthouse.bsCalCon", 'uint16_t')  # which base stations have received calibration data over the air
        # System Flying 
        lg.add_variable("sys.canfly", 'uint8_t')   # Nonzero if the system is ready to fly
        lg.add_variable("sys.isFlying", 'uint8_t')  # Nonzero if the system thinks it is flying
        # Battery Status 
        lg.add_variable("pm.batteryLevel", 'uint8_t')  # battery level
        lg.add_variable("pm.state", 'uint8_t')  # state of power management 
        self.cf.log.add_config(lg)
       

        with SyncLogger(self.scf, lg) as logger:
            for _, data, _ in logger:

                # Checking battery status 
                self.drone_is_charging = data["pm.state"]   # checkin if the drone is charging 

                # Removing the oldest value from the list
                if len(self.aggregate_battery_level)==5:
                    self.aggregate_battery_level.pop(0)  # removing the oldest battery value recording 

                # Updating global battery level  
                self.aggregate_battery_level.append(data['pm.batteryLevel'])
                # self.aggregate_battery_counter += 1
                
                # if self.aggregate_battery_counter !=0 :
                self.average_battery_level = sum(self.aggregate_battery_level) / len(self.aggregate_battery_level)
                
                

                return data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z'],\
                        data['lighthouse.status'],data['lighthouse.bsActive'], data['lighthouse.bsAvailable'],data['lighthouse.bsCalCon'],\
                        data['sys.canfly'],data['sys.isFlying'], \
                        data['pm.batteryLevel'], data['pm.state']
    
    def save_log(self):
        """
        A function to get and save log variables. Almost identical to the get_log function but this function doesn't wait, so it gets log variables
        information every 10ms and as soon as it gets the batch of the log variables, it writes to a csv file right away. 
        """
        lg = LogConfig(name='Save basic logo', period_in_ms=100)
        lg.add_variable("stateEstimate.x", 'float')
        lg.add_variable("stateEstimate.y", 'float')
        lg.add_variable("stateEstimate.z", 'float')
     
        # Status
        lg.add_variable("lighthouse.status", 'uint8_t')
        lg.add_variable("lighthouse.bsActive", 'uint16_t')   # bit field indicating which base stations are providing useful data to the estimator
        lg.add_variable("lighthouse.bsAvailable", 'uint16_t')  # bit field indicating which base stations are available
        lg.add_variable("lighthouse.bsCalCon", 'uint16_t')  # which base stations have received calibration data over the air
        # System Flying 
        lg.add_variable("sys.canfly", 'uint8_t')   # Nonzero if the system is ready to fly
        lg.add_variable("sys.isFlying", 'uint8_t')  # Nonzero if the system thinks it is flying
        # Battery Status 
        lg.add_variable("pm.batteryLevel", 'uint8_t')  # battery level
        lg.add_variable("pm.state", 'uint8_t')  # 
        self.cf.log.add_config(lg)
        
        with SyncLogger(self.scf, lg) as logger:
            for _, data, _ in logger:

                pos_x = data['stateEstimate.x'] ; pos_y = data['stateEstimate.y'] ; pos_z = data['stateEstimate.z']
                l_status = data['lighthouse.status'] ; l_active = data['lighthouse.bsActive'] ; l_available = data['lighthouse.bsAvailable']; l_calibrated = data['lighthouse.bsCalCon']
                sys_canfly = data['sys.canfly'] ; sys_isflying = data['sys.isFlying']
                pm_battery = data['pm.batteryLevel'] ;  pm_state = data['pm.state'] 
        
                # writing the output variables to the csv file 
                row_entry = [pos_x, pos_y, pos_z, pm_battery, pm_state, sys_canfly, sys_isflying, l_status, l_active, l_available, l_calibrated]
                # print("dataframe columns are : ", log_df.columns)
                # print("Length of the row entry is : ", len(row_entry))

                with open(self.csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row_entry)
            

    # ---------- Listing & Setting parameters  ---------------------
    def list_parameters(self):
        pass
    def set_parameters(self):
        pass 
    # ---------   Automate flight ----------------------------
    def automatic_directional_flight(self, sequence_of_directions, initial_position):
        """ 
        This function implements automated flight using sequence of directions. 
        It takes in the sequence of directions, the initial_position (3D), which we want
        the drone to start flying from.
        """
        return None


    def automatic_coordinate_based(self, set_of_coordinates, initial_position, light_drone_LED=False):
        """
        This function implements automated flight using a set of 3D coordinates. 
        It takes in the set of 3D points and the initial_position (3D) coordiante, which 
        we want the drone to start flying from. 
        """
        coordinates_validity = self.check_boundary_values_validity (set_of_coordinates, initial_position)
        # If all of the coordinates are valid and lie within the drone-cage
        if coordinates_validity: 
            self.takeoff("coordinates",set_of_coordinates, initial_position, light_drone_LED) 
        else: 
            print("!!!!  Incorrect set of coordiantes or initial_posiiton. \n Please revise the values ")

    def check_boundary_values_validity(self, set_of_coordinates, initial_position):
        """A function that checks if the coordinate-waypoints are within the bound/dimensions of the drone lab cage. 
        It returns a boolean variable, true if all coordinates are valid and false otherwise"""

        # Defining our lab dimensions - this should be updated with the extreme dimension values of your IPS system. 
        self.lab_maximum_x = 6.8
        self.lab_maximum_y = 5.3
        self.lab_maximum_z = 2.7

        validity_boolean = False 

        # Check validity of the initial_position
        x = initial_position[0]
        y = initial_position[1]
        z = initial_position[2]
        # Check validity of initial position
        if (x>=0 and x<=self.lab_maximum_x) and (y>=0 and y<=self.lab_maximum_y) and (z<=self.lab_maximum_z):
            validity_boolean = True 
        else: 
            validity_boolean = False 
            return False

        for i in set_of_coordinates:
            x = i[0]
            y = i[1]
            z = i[2]

            # Check validity of waypoint coordinates
            if (x>=0 and x<=self.lab_maximum_x) and (y>=0 and y<=self.lab_maximum_y) and (z<=self.lab_maximum_z):
                validity_boolean = True 
            else: 
                validity_boolean = False 
                print("!!! Waypoint coordinate value is larger than the lab dimensions. Please Recheck", flush=True)
                break
        
        return validity_boolean
            

    # --------   Monitor Battery level in-flight ----------------------
    def monitor_battery_level(self):
        """
        Constantly checks battery level at the beginning and while in-flight. Accordingly, it prevents take off if the drone is attempting to fly or and lands gracefully if it 
        is already flying. It calls the get_log function, that prints the log variables. 
        """

      
        while self.monitoring: 
            
            if self.average_battery_level <=20:
                print(f"🪫Critical Battery !!! Battery level mid-flight is less 30, {self.average_battery_level} to be precise so we trigger graceful landing.", flush=True)
                self.interrupt_mission = True   # to prevent the drone from flying while battery level is low 
                time.sleep(1)
                graceful_landing_key = keyboard.Key.down
                self.key_pressed_event_listener(self.pc, self.cf, graceful_landing_key)   # triggers graceful landing
                break
            else: 
                print("Battery level is not critical and actually at level : ", self.average_battery_level)
            time.sleep(4)
    
        
 

  