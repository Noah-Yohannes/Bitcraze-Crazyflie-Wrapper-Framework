# Crazyflie AR Mission Planning 🛰️🕹️

This module enables **AR-guided flight control of Crazyflie drones**, integrating motion capture or AR headset input to plan and execute trajectories in real-time.  

The system is designed using a **client-server architecture**:

- **Client**: The AR headset worn by the operator, which sends motion or gesture commands.  
- **Server**: The device with the Crazyflie dongle, which receives commands from the client and communicates with the drone to execute the planned trajectory.

---

## Folder Contents

| File | Description |
|------|-------------|
| `ar_python_client.py` | AR headset client script. Captures position/gesture input and sends it to the server. |
| `ar_server.py` | Server script. Receives AR input and translates it into drone commands using Crazyflie APIs. |
| `ar_to_ips_coordinates.py` | Converts AR coordinates into the Indoor Positioning System (IPS) coordinates used by the drone. |
| `parse_ar_coordinates.py` | Utility for parsing raw AR headset data into usable 3D coordinates. |
| `translate_AR_to_IPS.py` | Maps AR headset positions to IPS coordinates in real-time. |
| `translate_sketch_to_IPS.py` | Optional: translates predefined sketch trajectories into IPS coordinates for automated flight. |

---

## System Architecture

### 1. Client-Server Communication
- **Client (AR headset)**:
  - Tracks user's position, gestures, or hand-drawn trajectories.
  - Sends AR coordinates over the network to the server.
  - Can provide real-time updates to dynamically guide the drone.

- **Server (Drone interface)**:
  - Runs on the device connected to the Crazyflie dongle.
  - Receives AR coordinates from the client.
  - Converts AR coordinates to IPS coordinates suitable for Crazyflie control.
  - Sends motion commands to the drone using the **PositionCommander** or **MotionCommander** API.

---

### 2. Workflow

1. **Start the Server**  
   ```bash
   python ar_server.py