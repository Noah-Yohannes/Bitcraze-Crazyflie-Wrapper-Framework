


import logging
import time
import time
import keyboard
from pynput import keyboard
import threading
import os
import sys

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
import pandas as pd
from functools import partial

# Log info retriever
from connect_log_param import initialize_log

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
            stop_log_event.set()
        elif key == keyboard.Key.down:
            print("Graceful landing triggered")
            mc.land()
            time.sleep(4)
            cf.platform.send_arming_request(False)
            
    except AttributeError:
        pass

def main():
    global proceed_automated_flight, graceful_landing

    print("Before activating the listener")
    time.sleep(1)
    # Start the keyboard listener in a background thread
    
    cflib.crtp.init_drivers()
    print("Just before the synccrazyflie loop")
    time.sleep(1)

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Inside the with block")

        # ----------    Get Log info here    ------------------------

        # Starting a log thread using the same context 
        log_thread = threading.Thread(target=initialize_log, args=(scf.cf,stop_log_event,"external"))
        log_thread.start()
        print('Started the logging thread. ')
        time.sleep(2)

        mc = MotionCommander(scf, default_height=0.55)
        time.sleep(1.5)
        # Setting the stabilizer.estimator parameter to 2 manually
        cf = scf.cf

        # ----- Listener -------
        callback = partial(graceful_landing_on_press, mc, cf)
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
            with open('log_variables.csv', 'r') as f:
                # header = "pos_x\tpos_y\tpos_z\tl_stat\tl_active\tl_avail\tl_calibr\tsys_canfly\tsys_isflying\tpm_battery\tpm_state"
                header = [
                    "pos_x", "pos_y", "pos_z", "l_stat", "l_active", "l_avail", "l_calibr",
                    "sys_canfly", "sys_isflying", "pm_battery", "pm_state"]
                
                try : 
                    line = f.readlines()[-1]
                    line = line.replace("\n",'')
                    line_s = line.split(",")
                    line_s = line_s[2:]
                    vals = [round(float(i), 2) for i in line_s]

                    for name, val in zip(header, vals):
                        print(f"{name}: {val}")
                    
                    print("\n\n")

                    # line_s = [str(j) for j in line_s]
                    # # print(line_s)
                    # special_char = "\t"
                    # final_log = special_char.join(line_s)

                    # print(final_log.strip())
                except:
                    pass
            
                          
            time.sleep(1.5)
            # log_df = pd.read_csv('log_variables.csv')
            # last_two = log_df.tail(2)
            # print(last_two)

            time.sleep(1.5)

        # Arm the Crazyflie
        cf.platform.send_arming_request(True)

        # ----------------   Motion Commander ---------------
        time.sleep(1.0)

        print("Sent arming packets")
        time.sleep(1)
        # We take off when the commander is created
        # with MotionCommander(scf, default_height=None) as mc:

        #-----    Sample flight test    -----------------     
        mc.take_off(height=0.4)
        # while not graceful_landing:
        print("No escpae so in movement. ")
        time.sleep(1)
        mc.up(distance_m=0.3, velocity=0.3)
        time.sleep(1)
        mc.right(distance_m=1, velocity=0.3)
        time.sleep(1)
        mc.down(distance_m=0.3, velocity=0.3)
        time.sleep(0.5)
        mc.land()
        cf.platform.send_arming_request(False)

        # # ----------------   Flight scenarios     ------------------

        scenario = "reference"

        if scenario=="reference":
            # 30 seconds log flight
            mc.take_off(height=0.4)
            # while not graceful_landing:
            print("No escpae so in movement. ")
            time.sleep(1)
            mc.up(distance_m=0.3, velocity=0.3)
            time.sleep(1)
            mc.right(distance_m=0.3, velocity=0.3)
            time.sleep(1)
            mc.down(distance_m=0.3, velocity=0.3)
            time.sleep(0.5)
        
        # elif scenario=="longer_flight":
        #     # 60 seconds log flight
        #     mc.take_off(height=0.4)
        #     # while not graceful_landing:
        #     print("No escpae so in movement. ")
        #     time.sleep(1)
        #     mc.up(distance_m=0.3, velocity=0.3)
        #     time.sleep(1)
        #     mc.right(distance_m=0.3, velocity=0.3)
        #     time.sleep(1)
        #     mc.down(distance_m=0.3, velocity=0.3)
        #     time.sleep(0.5)
            
        # elif scenario == "shorter_flight":
        #     # 15 seconds log flight
        # elif scenario == "higher_elevation":
        #     # 30 seconds log flight
        # elif scenario == "far_away":
        #     # 30 seconds log flight
        # elif scenario == "wobbly_flight":
        #     # 30 seconds log flight
        # elif scenario == "no_response":
        #     # 30 seconds log flight
        # elif scenario == "higher_elevation_shorter_flight":
        #     # 15 seconds log flight
        # elif scenario == "erratic_movement":
        #     # 30 seconds log flight

        # print("Landing...")
        # mc.land()
        # cf.platform.send_arming_request(False)

        
    # Once the Crazyflie disconnects, join the logger thread
    stop_log_event.set()
    log_thread.join()
    print("✅ Logging thread closed. Exiting...")
if __name__ == '__main__':
    main()