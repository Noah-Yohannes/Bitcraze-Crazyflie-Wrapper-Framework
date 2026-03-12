
""" In this script the values lighouse log varialbes are saved seprately with the 
statestimation position variables. Basically mapping/visualizing the log variables we want to observe
in 3D. """

import json
import pandas as pd

def process_json():
    light_status = pd.DataFrame(columns=[ "x", "y", "z", "status"])  # "timestamp",
    light_bsActive = pd.DataFrame(columns=[ "x", "y", "z", "bsActive"])   # "timestamp",
    light_bsAvailable = pd.DataFrame(columns=[ "x", "y", "z", "bsAvailable"])  # "timestamp",
    light_bsCalcon = pd.DataFrame(columns=[ "x", "y", "z", "bsCalCon"])   # "timestamp",

    # reading the two json files 
    with open('lighthouse_json.json', 'r') as file:
        light_data = json.load(file)

    with open('statestimation_json.json', 'r') as file:
        state_data = json.load(file)


    # Taking minimum length in case, the two json files are not synchronized and thus not of equal size, we will go with the smallest
    for i in range(min(len(light_data), len(state_data))):
        state_entry = state_data[i]
        light_entry = light_data[i]

        state_timestamp = state_entry["timestamp"]
        light_timestampp = light_entry["timestamp"] 
        
        # Checking if the timestamps are close enough before mapping the lighthouse and state estiamtion log info
        # We choose 15 because the difference between consecutive readings is supposed to be 10ms, adding 5ms for some delays
        if abs(state_timestamp-light_timestampp) <15:
            # print("state entry : ", state_entry)
            if  state_entry["x"]>=0 and state_entry["y"]>=0 and  state_entry["z"]>=0:
                light_status.loc[len(light_status)] = [ state_entry["x"], state_entry["y"], state_entry["z"],int(light_entry["status"]) ]   #state_timestamp,
                light_bsActive.loc[len(light_bsActive)] = [ state_entry["x"], state_entry["y"], state_entry["z"],int(light_entry["bsActive"] )]   #state_timestamp,
                light_bsAvailable.loc[len(light_bsAvailable)] = [state_entry["x"], state_entry["y"], state_entry["z"],int(light_entry["bsAvailable"]) ]   #state_timestamp,
                light_bsCalcon.loc[len(light_bsCalcon)] = [ state_entry["x"], state_entry["y"], state_entry["z"],int(light_entry["bsCalCon"]) ]   #state_timestamp,

    light_status.to_json('light_status.json', orient='records')
    light_bsActive.to_json('light_bsActive.json', orient='records')
    light_bsAvailable.to_json('light_bsAvailable.json', orient='records')
    light_bsCalcon.to_json('light_bsCalCon.json', orient='records')
process_json()


