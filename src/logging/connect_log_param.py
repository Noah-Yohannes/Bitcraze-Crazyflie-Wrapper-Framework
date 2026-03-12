
import cflib 
import logging 
import time 

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
import json
import pandas as pd
import csv 
import os
import pandas as pd

#----------------------------      Define log variables dataframes  -------------------
state_estimator_df = pd.DataFrame(columns=["timestamp", "x", "y", "z"])
lighthouse_df = pd.DataFrame(columns=["timestamp","status", "bsActive", "bsAvailable", "bsCalCon"])

# -------------     Creating CSV file to store log variables in -------------------------
dataframe_name = "log_variables.csv"
field_names = ["timestamp", "pos_x", "pos_y", "pos_z", "l_status", "l_active", "l_available", "l_calibrated",
                   "sys_canfly", "sys_isflying", "pm_battery", "pm_state"]

log_df = pd.DataFrame(columns=field_names)



def int_to_binary(input_num):
    num = bin(input_num)  # returns a string of binary format
    num = num.split('b')[1]  # taking only the binary format 

# ---------------------------        Log callback functions     --------------------------------------
def log_all_callback(timestamp, data, logonf):
    # print("Inside the all callback function")
    position_x = data['stateEstimate.x']

    pos_x = data['stateEstimate.x'] ; pos_y = data['stateEstimate.y'] ; pos_z = data['stateEstimate.z']
     
    l_status = data['lighthouse.status'] ; l_active = data['lighthouse.bsActive'] ; l_available = data['lighthouse.bsAvailable']; l_calibrated = data['lighthouse.bsCalCon']
    sys_canfly = data['sys.canfly'] ; sys_isflying = data['sys.isFlying']
    pm_battery = data['pm.batteryLevel'] ;  pm_state = data['pm.state']

    field_names = ["timestamp", "pos_x", "pos_y", "pos_z", "l_status", "l_active", "l_available", "l_calibrated",
                   "sys_canfly", "sys_isflying", "pm_battery", "pm_state"]

    csv_file = "log_variables.csv"
    # field_names = ["timestamp", "pos_x", "pos_y", "pos_z", "l_status", "l_active", "l_available", "l_calibrated"
    #                "sys_canfly", "sys_isflying", "pm_battery", "pm_state"]
    row_entry = [timestamp, pos_x, pos_y, pos_z, l_status, l_active, l_available, l_calibrated, sys_canfly, sys_isflying, pm_battery, pm_state]
    # print("dataframe columns are : ", log_df.columns)
    # print("Length of the row entry is : ", len(row_entry))
    log_df.loc[len(log_df)] = row_entry

    log_df.to_csv(csv_file)

    
def log_stab_callback(timestamp, data, logconf):

    print("timestamp is :", timestamp)
    print(f"\r x: {data['stateEstimate.x']:.2f}   y: {data['stateEstimate.y']:.2f}   z: {data['stateEstimate.z']:.2f}", end='')    # time.sleep(0)

    entries_list = [timestamp, round(data['stateEstimate.x'], 3),round(data['stateEstimate.y'], 3), round(data['stateEstimate.z'],3)]

    state_estimator_df.loc[len(state_estimator_df)] = entries_list

    state_estimator_df.to_json('statestimation_json.json', orient='records')
    print("S_Json file is updated")

def log_status_callback(timestamp, data, logconf):
    # battery, position, state, 
    # print("Actual data is : ", data)
    # Since we are expecting bit-level data

    # Convert int to binary using bin(_)
    print(f"\r L_status: {data['lighthouse.status']}   L_Active: {data['lighthouse.bsActive']}   L_Available: {data['lighthouse.bsAvailable']}   L_Calibre: {data['lighthouse.bsCalCon']}", end='', flush=True)    # time.sleep(0)
    # if data['lighthouse.status'] & 1: 
    #     print("\n ✅ Tracking active!\n")
    # else: 
    #     print("\n❌ Tracking not started\n")
    # print("L_status: ", data['lighthouse.status'])
    # print(f"\r L_status: {data['lighthouse.status']}   L_Active: {data['lighthouse.bsActive']}   L_Available: {data['lighthouse.bsAvailable']}   L_Calibre: {data['lighthouse.bsCalCon']}", end='', flush=True)    # time.sleep(0)

    entries_list = [timestamp, data['lighthouse.status'], data['lighthouse.bsActive'], data['lighthouse.bsAvailable'], data['lighthouse.bsCalCon']]
    
    lighthouse_df.loc[len(lighthouse_df)] = entries_list 

    lighthouse_df.to_json('lighthouse_json.json', orient='records')
    print("L_Json file is updated. ")
    # time.sleep(0.1)
    # print(f"\r L_status: {data['lighthouse.status']}   L_Active: {data['lighthouse.bsActive']}   L_Available: {data['lighthouse.bsAvailable']}   L_Calibre: {data['lighthouse.bsCalCon']}", end='')    # time.sleep(0)

def log_flying_status_callback(timestamp, data, logconf):
    # battery, position, state, 
    print(f"\r x: {data['sys.canfly']}   y: {data['sys.isFlying']}", end='')    # time.sleep(0)
  
def log_power_status_callback(timestamp, data, logconf):

    # battery, position, state, 
    print(f"\r BatteryLevel: {data['pm.batteryLevel']}   Power_state: {data['pm.state']} ", end='')    # time.sleep(0)

def log_loco_callback(timestamp, data, logconf):

    # battery, position, state, 
    print(f"\r Loco_mode: {data['loco.mode']}", end='')    # time.sleep(0)

# ------------------------------          Parameter callback functions        ----------------------------------
# Parameters function  that uses asynchronous implementation
def param_stab_est_callback (name, value):
    print('The crazyflie has parameter '+name+ ' set at number: '+ value)

def simple_param_async(scf, groupstr, namestr):
    """Function to get or set parameter values using group names and string, which make up the full string name. """

    cf = scf.cf
    full_name = groupstr + "." + namestr

    # Getting the value of a parameter
    # cf.param.add_update_callback(group= groupstr, name=namestr, cb=param_stab_est_callback)   

    # Setting the value of a parameter 
    # cf.param.set_value(full_name, 2)    # the default value = 2, so needs to be changed back to this
    time.sleep(1)

    cf.param.set_value(full_name, 1)
    time.sleep(1)


def simple_log_async(cf, logconf, mode):
    """Function to implement asynchronous logging"""
    # if mode =="internal":
    #     cf = scf.cf 
    # else: 
    #     cf = scf

    # Adding the logo configurations
    cf.log.add_config(logconf)

    # configuring logconf where to send each type of log feedback
    logconf.data_received_cb.add_callback(log_all_callback)
   
    # Sending signal to crazyflie that it can start sending log info now
    logconf.start()
    # lg_status.start()
    # lg_flying_status.start()
    # lg_power_status.start()
    # lg_loco.start()
    time.sleep(180)     # it will be sending log info for 60 seconds 
    logconf.stop()
    # lg_status.stop()
    # lg_flying_status.stop()
    # lg_power_status.stop()
    # lg_loco.stop()

    # ----      Group-level configurations   ------

    # # Adding the logo configurations
    # cf.log.add_config(logconf)
    # cf.log.add_config(lg_status)
    # # cf.log.add_config(lg_flying_status)
    # # cf.log.add_config(lg_power_status)
    # # cf.log.add_config(lg_loco)

    # # configuring logconf where to send each type of log feedback
    # logconf.data_received_cb.add_callback(log_stab_callback)
    # lg_status.data_received_cb.add_callback(log_status_callback)
    # # lg_flying_status.data_received_cb.add_callback(log_flying_status_callback)
    # # lg_power_status.data_received_cb.add_callback(log_power_status_callback)
    # # lg_loco.data_received_cb.add_callback(log_loco_callback)

    # # Sending signal to crazyflie that it can start sending log info now
    # logconf.start()
    # lg_status.start()
    # # lg_flying_status.start()
    # # lg_power_status.start()
    # # lg_loco.start()
    # time.sleep(180)     # it will be sending log info for 60 seconds 
    # logconf.stop()
    # lg_status.stop()
    # # lg_flying_status.stop()
    # # lg_power_status.stop()
    # # lg_loco.stop()

def simple_log(scf, logconf):
    with SyncLogger(scf, lg_stab) as logger:
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2] 

            print("[%d] [%s]: %s"%(timestamp, logconf_name, data))
            break

            # Getting accelerator logging info 
            # timestamp = log_entry[0]
            # data = log_entry[1]
            # logconf_name = log_entry[2] 
            # print("\nData in total is : ", data, '\n')
            # print("[%d] [%s]: Acc_x: %d | Acc_y: %d | Acc_z: %d"%(timestamp, logconf_name, data['acc.x'], data['acc.y'], data['acc.z']))
            # time.sleep(1.5)
            # break

def simple_connect():

    print("Yeah, I'm connected! : D")
    time.sleep(3)
    print("Now I will disconnect  :'(")

# def Fetch_Log_info():
#     """
#     A function that gets essential log info before a flight. 
#     """
    
#     initialize_log()  
    
def initialize_log(cf, stop_event=None, mode="internal"):

    # Combined group log info / variables ------------------------
    lg_all = LogConfig(name="combined_log", period_in_ms=10)   
    lg_all.add_variable("stateEstimate.x", 'float')
    lg_all.add_variable("stateEstimate.y", 'float')
    lg_all.add_variable("stateEstimate.z", 'float')
    # Status
    lg_all.add_variable("lighthouse.status", 'uint8_t')
    lg_all.add_variable("lighthouse.bsActive", 'uint16_t')   # bit field indicating which base stations are providing useful data to the estimator
    lg_all.add_variable("lighthouse.bsAvailable", 'uint16_t')  # bit field indicating which base stations are available
    lg_all.add_variable("lighthouse.bsCalCon", 'uint16_t')  # which base stations have received calibration data over the air
    # System Flying 
    lg_all.add_variable("sys.canfly", 'uint8_t')   # Nonzero if the system is ready to fly
    lg_all.add_variable("sys.isFlying", 'uint8_t')  # Nonzero if the system thinks it is flying
    # Battery Status 
    lg_all.add_variable("pm.batteryLevel", 'uint8_t')  # battery level
    lg_all.add_variable("pm.state", 'uint8_t')  # state of power management 

    #-------------------------------------------------
    simple_log_async(cf, lg_all, mode)



if __name__ == '__main__':
    uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')
    # Only output errors from the logging framework
    logging.basicConfig(level=logging.ERROR)

    # initialize the low-level drivers
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # simple_connect()
        # simple_log(scf, lg_stab)
        initialize_log(scf.cf)
        # simple_log_async(scf, lg_stab, lg_status, lg_flying_status, lg_power_status, lg_loco)
        # simple_param_async(scf, group, name)
        # initialize_log()


    

#   ----------    Group level Log receiving   ---------------------------
# ------------------------------------------------------------------------
# if __name__ == '__main__':
#     # initialize the low-level drivers
#     cflib.crtp.init_drivers()

#     # Define the logging configuration 
#     # lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
#     # lg_stab.add_variable("stabilizer.roll", 'float')
#     # lg_stab.add_variable("stabilizer.pitch", 'float')
#     # lg_stab.add_variable("stabilizer.yaw", 'float')

#     # Drone Position
#     lg_stab = LogConfig(name="stateEstimate", period_in_ms=10)   
#     # the data we get as log depends on the variables we add here
#     lg_stab.add_variable("stateEstimate.x", 'float')
#     lg_stab.add_variable("stateEstimate.y", 'float')
#     lg_stab.add_variable("stateEstimate.z", 'float')

#     # Status
#     lg_status = LogConfig(name="lighthouse", period_in_ms=10)
#     lg_status.add_variable("lighthouse.status", 'uint8_t')
#     lg_status.add_variable("lighthouse.bsActive", 'uint16_t')   # bit field indicating which base stations are providing useful data to the estimator
#     lg_status.add_variable("lighthouse.bsAvailable", 'uint16_t')  # bit field indicating which base stations are available
#     lg_status.add_variable("lighthouse.bsCalCon", 'uint16_t')  # which base stations have received calibration data over the air

#     # System Flying 
#     lg_flying_status = LogConfig(name="sys", period_in_ms=10)
#     lg_flying_status.add_variable("sys.canfly", 'uint8_t')   # Nonzero if the system is ready to fly
#     lg_flying_status.add_variable("sys.isFlying", 'uint8_t')  # Nonzero if the system thinks it is flying

#     # Battery Status 
#     lg_power_status = LogConfig(name="pm", period_in_ms=10)
#     lg_power_status.add_variable("pm.batteryLevel", 'uint8_t')  # battery level
#     lg_power_status.add_variable("pm.state", 'uint8_t')  # state of power management 

#     # Loco
#     lg_loco = LogConfig(name="loco", period_in_ms=10)
#     lg_loco.add_variable("loco.mode")   # current mode of the loco positioning system


#     # lg_stab = LogConfig(name="lighthouse", period_in_ms=10)
#     # lg_stab.add_variable("lighthouse.x", 'float')
#     # lg_stab.add_variable("lighthouse.y", 'float')
#     # lg_stab.add_variable("lighthouse.z", 'float')
#     # lg_stab = LogConfig(name="acc", period_in_ms=10)
#     # lg_stab.add_variable("acc.x", 'float')
#     # lg_stab.add_variable("acc.y", 'float')
#     # lg_stab.add_variable("acc.z", 'float')

#     # add group parameter name
#     # group = "stabilizer"
#     # name = "estimator"

#     with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
#         # simple_connect()
#         # simple_log(scf, lg_stab)
#         simple_log_async(scf, lg_stab, lg_status, lg_flying_status, lg_power_status, lg_loco)
#         # simple_param_async(scf, group, name)

