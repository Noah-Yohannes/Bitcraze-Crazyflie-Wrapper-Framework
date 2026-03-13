# Crazyflie Python Wrapper Framework

A modular Python framework for interacting with **Bitcraze Crazyflie nano-quadcopters**, enabling automated flight control, mission planning, telemetry logging, and experimental drone interaction.

This repository implements a structured **Python wrapper around Bitcraze’s Crazyflie libraries** to simplify drone control workflows, automate missions, and support research experimentation.

<!-- # Demo Visualizations -->
# Demo Visualizations

Sample Crazyflie flight demonstrations:

<p align="center">
    <img src="media/wobble_gif.gif" />
  <!-- <img src="media/normal_flight_gif.gif" /> -->
  <!-- <img src="media/wobble_gif.gif" width="375" /> -->
</p>

<!-- Example: -->
<!-- ![Waypoint Flight](media/normal_flight_gif.gif)
![Sketch Flight Demo](media/wobble_gif.gif) -->


# Hardware Ecosystem

This project relies on the following hardware:

| Component                            | Description                      |
| ------------------------------------ | -------------------------------- |
| **Crazyflie 2.x**                    | Nano-quadcopter drone            |
| **Crazyradio USB Dongle**            | USB radio used for communication |
| **SteamVR Lighthouse Base Stations** | Indoor positioning system (IPS)  |

Terminology used in this repository:

| Term           | Meaning                                             |
| -------------- | --------------------------------------------------- |
| **Bitcraze**   | Company producing the Crazyflie ecosystem           |
| **Crazyflie**  | The nano-quadcopter drone                           |
| **Crazyradio** | USB radio dongle used to communicate with the drone |

# Repository Structure

```
.
├── automated_waypoints_flight_demo.py
├── config
│   ├── drone parameters
│   └── lighthouse calibration files
├── crazyflie_conda_environment.yml
├── data
│   ├── example telemetry logs
│   └── IPS sample datasets
├── demos
│   ├── sketch_flight_demo.py
│   └── sketch_pattern_gui.py
├── firmware
│   └── firmware-cf21bl-2025.09.zip
├── media/
├── README.md
├── setup.py
└── src
    ├── control
    │   ├── crazyflie_wrapper.py
    │   └── led_controller.py
    ├── Crazyflie_AR_Mission_Planning
    ├── Crazyflie_Automated_Flying_Documentation_based_practice
    ├── localization
    │   ├── dataframes_processing.py
    │   └── visualize_flight_environment.py
    ├── logging
    │   ├── connect_log_param.py
    │   └── Debugging_crazyflie.py
    └── helper modules
```

# Installation

Two installation approaches are supported.

# Option 1 — Installation Using setup.py

Clone the repository:

```
git clone https://github.com/Noah-Yohannes/Bitcraze-Crazyflie-Wrapper-Framework.git
cd Bitcraze_Wrapper
```

Install the framework in **editable mode**:

```
pip install -e .
```

I would recommend this installation method.

# Option 2 — Installation Using Conda Environment

Create the environment using the provided YAML file:

```
conda env create -f crazyflie_conda_environment.yml
```

Activate the environment:

```
conda activate crazyflie
```

This installs all dependencies used during development and ensures environment reproducibility.

# Running the Automated Waypoint Flight Demo

A simple automated flight demonstration can be launched using:

```
python automated_waypoints_flight_demo.py
```

This script will:

1. Connect to the Crazyflie drone via the Crazyradio dongle
2. Initialize the wrapper and flight parameters
3. Execute a waypoint-based mission
4. Perform a safe landing

# Sketch-Based Flight Demo

This repository includes an interface for drawing flight paths that the drone can follow.

Launch the sketch GUI:

```
python demos/sketch_pattern_gui.py
```

Execute the drawn trajectory:

```
python demos/sketch_flight_demo.py
```

The drawn sketch is converted into a sequence of 3D waypoints in the Lighthouse coordinate system.

# Wrapper Customization Options

When creating a `CrazyflieWrapper` instance, the following parameters can be customized:

1. Default starting height
2. Default velocity
3. Motion controller type (PID or Mellinger)
4. Starting position
5. Mission waypoint coordinates `(x, y, z, velocity)`
6. Maneuver challenge coordinates

The maneuver challenge may be computed dynamically during flight.

# Safety Checklist Before Flight

Before executing any flight script, perform the following checks:

### Verify Sensor Stability

Open the **Crazyflie Client (cfclient)**.

Navigate to:

Flight Control → Horizon Indicator

If the drone is placed on a flat surface, the horizon indicator should remain **stable**.

If it fluctuates:

* Clean the optical sensors with a soft cloth
* Ensure the sensor expansion board is properly attached

### Verify Lighthouse Tracking

In the **Lighthouse Position tab**:

* Base station columns should appear **green**
* Tracking should remain stable

If tracking fails:

* Verify base station orientation
* Ensure the drone is inside the Lighthouse tracking volume

### Drone Placement

Before takeoff:

* Align the drone **parallel to the x-axis**
* Ensure the drone nose faces the **positive x direction**

Avoid placing the drone in **flight cage corners**, as they may be Lighthouse blind spots.

# Flight Control Shortcuts

The control scripts support the following keyboard commands:

| Key              | Action                                   |
| ---------------- | ---------------------------------------- |
| **Home**         | Authorizes takeoff and mission execution |
| **↓ Down Arrow** | Smooth descent / graceful landing        |
| **End**          | Sends maneuver challenge coordinates     |
| **Esc**          | Emergency motor shutdown                 |

⚠ The **Esc key** immediately stops all motors and should only be used in emergencies.

# Data and Logging

The `data/` directory contains example datasets including:

* Crazyflie telemetry logs
* Lighthouse base station status
* IPS state estimation coordinates

These logs can be used with visualization tools in:

```
src/localization/
```

# Firmware

A compatible Crazyflie firmware version is included:

```
firmware/firmware-cf21bl-2025.09.zip
```

Ensure the drone firmware version matches the expected configuration.


# Research Notice

Some components related to **physical UAV authentication and identification** are part of ongoing research and are not included in this repository.

These modules will be released once the associated research work has been published.

# License

This project is intended primarily for **research and educational purposes**.
