# Crazyflie Logging Utilities 🛠️

This module contains utilities for **connecting to the Crazyflie drone**, retrieving telemetry logs, and managing onboard parameters.  
It is primarily focused on **data acquisition and safe logging** of drone flight variables for subsequent analysis.

---

## Key Features

- Connect to Crazyflie drones and retrieve real-time telemetry.
- Save logs into structured CSV files for further analysis.
- Set or modify key parameters on the drone firmware.
- Ensure safe operation with checks for battery level and emergency landing.

---

## Files

### `connect_log_param.py`
- Main script for connecting to the Crazyflie and retrieving log variables.
- Writes log data to a CSV file containing telemetry information such as position, sensor readings, and beacon status.
- Allows setting of critical parameters before or during flight.

### `Debugging_crazyflie.py`
- Utility functions for debugging communication with the Crazyflie.
- Helps inspect which variables are available for logging and verify proper connections.

---

## Automated Flights

The `logging` module also contains **basic automated flight scripts**:

- `simple_movement.py`: Uses **MotionCommander** for discrete movements (up, down, left, right).  
- `simple_position_commander_final.py`: Uses **PositionCommander** to fly through **3D coordinates** safely.  

Safety features implemented:

- Permission-based flight execution.
- Graceful landing on unexpected movement.
- Emergency landing if drone is out of control.
- Battery-level checks to prevent long-term damage.

---

## Setup Requirements

1. Install Bitcraze Python libraries:

- [cflib / crazyflie-lib-python](https://github.com/bitcraze/crazyflie-lib-python)  
- [crazyflie-clients-python](https://github.com/bitcraze/crazyflie-clients-python)

2. Use the provided Conda environment for dependency consistency:

```bash
conda env create -f ../../crazyflie_conda_environment.yml