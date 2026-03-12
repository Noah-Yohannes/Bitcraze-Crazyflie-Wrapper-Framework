

# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2018 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
This script shows the basic use of the PositionHlCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system.

The PositionHlCommander uses position setpoints.

Change the URI variable to your Crazyflie configuration.
"""
import logging
import time
import time
import keyboard
from pynput import keyboard
import threading
from functools import partial

import cflib.crtp
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


# Log info retriever
from connect_log_param import initialize_log

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')
uri_address = 'radio://0/80/2M/E7E7E7E7E8'  
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')


graceful_landing = False     # signals the system to land gracefully 
proceed_automated_flight = False   # signals to the system whether to proceed with automated flight or not based on observed log 
stop_log_event = threading.Event() 
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

print("Connected ")
time.sleep(1)


def graceful_landing_on_press(mc, cf, key):
    global graceful_landing
    global proceed_automated_flight
    try:
        # if key.char == 'esc':  # Press 's' to stop
        if key == keyboard.Key.esc:  # Press 's' to stop
            print("✅  Emergency landing triggered!")
            graceful_landing = True 
            cf.platform.send_arming_request(False)
        elif key == keyboard.Key.home:
            print("\n✅  Permission to proceed with automated flight granted !!!!")
            proceed_automated_flight = True
            # stop_log_event.set()
        elif key == keyboard.Key.down:
            print("Graceful landing triggered")
            mc.land()
            time.sleep(4)
            cf.platform.send_arming_request(False)
            
    except AttributeError:
        pass

def slightly_more_complex_usage():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        with PositionHlCommander(
                scf,
                x=0.0, y=0.0, z=0.0,
                default_velocity=0.3,
                default_height=0.5,
                controller=PositionHlCommander.CONTROLLER_PID) as pc:
            # Go to a coordinate
            pc.go_to(1.0, 1.0, 1.0)

            # Move relative to the current position
            pc.right(1.0)

            # Go to a coordinate and use default height
            pc.go_to(0.0, 0.0)

            # Go slowly to a coordinate
            pc.go_to(1.0, 1.0, velocity=0.2)

            # Set new default velocity and height
            pc.set_default_velocity(0.3)
            pc.set_default_height(1.0)
            pc.go_to(0.0, 0.0)


def land_on_elevated_surface():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        with PositionHlCommander(scf,
                                 default_height=0.5,
                                 default_velocity=0.2,
                                 default_landing_height=0.35,
                                 controller=PositionHlCommander.CONTROLLER_PID) as pc:
            # fly onto a landing platform at non-zero height (ex: from floor to desk, etc)
            pc.forward(1.0)
            pc.left(1.0)
            # land() will be called on context exit, gradually lowering to default_landing_height, then stopping motors

def get_battery_level(scf):
    lg = LogConfig(name='Battery', period_in_ms=100)
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
    scf.cf.log.add_config(lg)
    with SyncLogger(scf, lg) as logger:
        for _, data, _ in logger:
            return data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z'],\
                    data['lighthouse.status'],data['lighthouse.bsActive'], data['lighthouse.bsAvailable'],data['lighthouse.bsCalCon'],\
                    data['sys.canfly'],data['sys.isFlying'], \
                    data['pm.batteryLevel'], data['pm.state']
        

def battery_level_monitor(scf, pc):
    while True: 
        pos_x, pos_y, pos_z, l_status, l_activate, ls_available, ls_calibrated, sys_can_fly, sys_is_flying, battery_level_m, battery_state = \
                get_battery_level(scf)
        
        print(f"Inside monitor \n\n\n X : {round(pos_x,2)}\nY : {round(pos_y,2)}\nZ : {round(pos_z,2)}\nBattery Level : {battery_level_m}\nSys_is_flying : {sys_is_flying}")

        if battery_level_m <=30:
            print("Critical Battery !!! Battery level mid-flight is less 30 so we trigger graceful landing.")
            graceful_landing_key = keyboard.Key.down
            graceful_landing_on_press(pc, scf.cf, graceful_landing_key)   # triggers graceful landing
            break
        else: 
            print("Battery levle is not critical.")
        time.sleep(1.5)

def simple_sequence():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        cf = scf.cf 
        # Arm the Crazyflie
        cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # ----------   Printing log variables  ----------------
        pos_x, pos_y, pos_z, l_status, l_activate, ls_available, ls_calibrated, sys_can_fly, sys_is_flying, battery_level, battery_state = \
              get_battery_level(scf)

        pc = PositionHlCommander(scf,
                                    x=pos_x,
                                    y=pos_y, 
                                    z=pos_z,
                                    default_height=0.5,
                                    default_velocity=0.2,
                                    default_landing_height=0,
                                    controller=PositionHlCommander.CONTROLLER_PID)  # CONTROLLER_MELLINGER - 
                                    # If we want to not use PID controller for fast movements and tracking we will use the CONTROLLER_MELLINGER
                                    # The mellinger focuses on smooth, dynamically feasible trajectories by minimizing the snap,
                                    # the fourth derivative of position (i.e., the rate of change of jerk). 
                                    # It was specially designed for tracjectory tracking quadrotors 

        # ----- Starting off battery controlling thread    ---------------------
        battery_thread = threading.Thread(target=battery_level_monitor, args=(scf,pc))
        battery_thread.start()
        print('Started the logging thread. ')
        time.sleep(2)
        
        # Proceeding to 
        if battery_level > 40 : 
            print("Battery level is safe so we continue to fly safely. ")
            print(f"X : {round(pos_x,2)}\nY : {round(pos_y,2)}\nZ : {round(pos_z,2)}\nBattery Level : {battery_level}\nSys_is_flying : {sys_is_flying}")

            # -----------       Waiting for signal to proceed     ----------------------
                  

            # Initializing the keyboard listener -------
            callback = partial(graceful_landing_on_press, pc, cf)
            listener = keyboard.Listener(on_press=callback)
            listener.start()
            
            pram_name = "stabilizer.estimator"
            cf.param.set_value(pram_name, '2')
            time.sleep(2.5) 
            cf.param.set_value('kalman.resetEstimation', '1')
            time.sleep(1)
            print("Set Stabilizer.estimator parameter to 2 & kalman.resetEstimation to 1")

            # ----------     Wait for permission to arm & send commands ------ 

            print("Waiting for confirmation to proceed with flight after checking log info.\n")
            while not proceed_automated_flight:  
                pos_x, pos_y, pos_y, l_status, l_activate, ls_available, ls_calibrated, sys_can_fly, sys_is_flying,battery_level, battery_state = \
              get_battery_level(scf)
                
                print(f"X : {round(pos_x,2)}\nY : {round(pos_y,2)}\nZ : {round(pos_z,2)}\nBattery Level : {battery_level}\nSys_is_flying : {sys_is_flying} \n\n\n")
                time.sleep(1)
            # -------------      Flying drone after permission is granted   --------------
            # Arm the Crazyflie
            cf.platform.send_arming_request(True)  
            print("Should fly now")


            pc.take_off(height=0.5)  # this is very useful.
          
            
            print("Choose a flight: \n 1: Reference flight\n2: Longer flight\n3: Shorter flight\n4: Higher elevation\n" \
            "5: Shorter & higher elevation flight\n6: Wobbly flight\n7: No response\n8: Deviation flight\n 9: Far away drone flight")
            # input_choice = input(": ")
            input_choice = 1 
 
            #  --------   Reference Flight    ------------
            if input_choice == 1:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.0971)   # 1m
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 1.5, velocity=0.0971)  # 0.707 m 
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.0971)    # 0.707 m
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.0971)   # 0.5 m  - 0.1m/s  
                # TOTAL DISTANCE = 1+0.7+0.5 = 2.2 m, velocity = 2.2m / 30seconds = 0.0733
                pc.land()

            # ----------   Longer flight ------------------
            elif input_choice == 2:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.04856)   # 1m
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 1.5, velocity=0.04856)  # 0.35 m 
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.04856)    # 0.35
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.04856)   # 0.5   
                # TOTAL DISTANCE = 1+0.7+0.5 = 2.2 m, velocity = 2.2m / 30seconds = 0.0733
                pc.land()

            # ----------   Shorter flight ------------------
            elif input_choice == 3:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.19427 )  # 0.1m/s
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 1.5, velocity=0.19427)
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.19427)
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.19427)
                pc.land()
            # ----------   Higher elevation flight ------------------
            elif input_choice == 4:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.1245)   # 1m
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 2.0, velocity=0.1245)  # 1.118 m 
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.1245)    # 1.118 m
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.1245)   # 0.5 m  
                # TOTAL DISTANCE = 3.736 -  3.736m / 30seconds = 0.0733
                pc.land()
            # ----------   Short & high elevation flight ------------------
            elif input_choice == 5:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.248 )  # 1m - 0.1m/s
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 2.0, velocity=0.248)   # 1.11m
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.248)  # 1.11m 
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.248)  # 0.5
                pc.land()
            # ----------   wobbly flight - realistic variation------------------    
            elif input_choice == 7:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 0.2, 1.0, velocity=0.127)   # 0.2m
                # time.sleep(2)
                pc.go_to(0.5, 0.2, 1.2, velocity=0.127)   # 0.2m 
                # time.sleep(2)
                pc.go_to(0.5, 0.3, 1.2, velocity=0.127)   # 0.1m
                # time.sleep(2)
                pc.go_to(0.5, 0.3, 1.3, velocity=0.127)   # 0.1m
                # time.sleep(2)
                pc.go_to(0.5, 0.5, 1.3, velocity=0.127)  # 0.2 m 
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 1.8, velocity=0.127)  # 1.11m
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.3, velocity=0.127)    # 1.11 m - downward 
                # time.sleep(2)
                pc.go_to(0.5, 2.2, 1.3, velocity=0.127)    # 0.2m
                # time.sleep(2)
                pc.go_to(0.5, 2.2, 1.2, velocity=0.127)    # 0.1 m 
                # time.sleep(2)
                pc.go_to(0.5, 2.3, 1.2, velocity=0.127)    # 0.1 m 
                # time.sleep(2)
                pc.go_to(0.5, 2.3, 1.0, velocity=0.127)    # 0.2 m 
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.127)   # 0.2m
                # time.sleep(2)
                # TOTAL DISTANCE = 3.82 , velocity = 3.82m / 30seconds = 0.127
                pc.land()
            # ----------  No response flight--------------------------
            elif input_choice == 8:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.0833)   # 1m
                # time.sleep(2)
                pc.land()
        
            # ----------   Deviation flight   --------------------------
            elif input_choice == 9:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.0934)   # 1m
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 2, velocity=0.0934)   # 1m
                # time.sleep(2)
                pc.land()
                # total distance = 2.802m / 30 seconds  - speed = 

            # ----------   Far away drone flight
            elif input_choice == 10:
                # pc.go_to()
                pc.go_to(0.5, 0, 1.0)    
                # time.sleep(2)
                pc.go_to(0.5, 1, 1.0, velocity=0.0971)   # 1m
                # time.sleep(2)
                pc.go_to(0.5, 1.5, 1.5, velocity=0.0971)  # 0.707 m 
                # time.sleep(2)
                pc.go_to(0.5, 2, 1.0, velocity=0.0971)    # 0.707 m
                # time.sleep(2)
                pc.go_to(0.5, 2.5, 1.0, velocity=0.0971)   # 0.5 m  - 0.1m/s  
                # TOTAL DISTANCE = 1+0.7+0.5 = 2.2 m, velocity = 2.2m / 30seconds = 0.0733
                pc.land()
        else: 
            print("Low battery so the drone can't fly. Battery leve is at ",battery_level)

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    simple_sequence()
    # slightly_more_complex_usage()
    # land_on_elevated_surface()
