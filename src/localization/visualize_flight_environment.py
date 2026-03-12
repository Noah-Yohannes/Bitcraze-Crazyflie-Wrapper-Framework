
import plotly.express as px

import pandas as pd


""" 
The goal of this script is to visualize the drone flight areas to identify where the drone is localized well,
and specially to identify blind spots where the lasers don't reach. 

To this end, we observe the lighthouse log variable including which base stations are available, which are providing useful information
and which have sent expected calibration to the crazyflie. 

We will first check closest timestamp.

"""

def visualize_log(dataframe_in, choice):
    print("Inside the visualization function")
    fig = px.scatter_3d(dataframe_in, x='x', y='y', z='z',
                color=choice)
    fig
    fig.show()

visualization_options = ["status", "bsActive", "bsCalCon", "bsAvailable"]
choice = ""

# num_choice = input("Select what you want to visualize: 1. status\n2. bsActive\n3. bsCalCon\n4. light_bsAvailable\n")
# if num_choice == 1:
#     choice = "status"
# elif num_choice == 2:
#     choice = "bsActive"
# elif num_choice == 3:
#     choice = "bsCalCon"
# elif num_choice == 4:
#     choice = "bsAvailable"

choice = "bsAvailable"
if choice != "":
        
    log_name = f"light_{choice}.json"
    df = pd.read_json(f'{log_name}')
    visualize_log(df, choice)
